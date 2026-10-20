#!/usr/bin/env python3
"""
MIT License

Schedule Management for YoLink Devices
======================================

This module provides schedule node classes for different device types:
- OnOffScheduleNode: For Switch, Outlet, Dimmer, Manipulator (on/off state)
- KeyScheduleNode: For InfraredRemoter (infrared key codes)
- MultiOutletScheduleNode: For MultiOutlet (per-channel on/off)
- SprinklerScheduleNode: For SprinklerV2/Sprinkler watering schedules
- WaterMeterScheduleNode: For WaterMeterController valve/leak schedules

Each class handles device-specific schedule parameters while sharing
common time-based schedule logic.
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

import time
import json

from yolink_mqtt_classV4 import YoLinkMQTTDevice


class BaseScheduleNode(udi_interface.Node):
    """
    Base class for all YoLink schedule nodes.
    
    Handles common schedule functionality:
    - Initialize schedule UI node
    - Parse schedule times (hours, minutes, optional seconds)
    - Update driver values for schedule display
    - Manage schedule activation/deactivation
    """
    
    from  udiYolinkLib import my_setDriver, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names

    def _schedule_actions(self):
        return (
            'getSchedules', 'setSchedules',
            'getLeakSchedules', 'setLeakSchedules',
            'getValveSchedules', 'setValveSchedules',
        )

    def _is_schedule_payload(self, payload):
        try:
            if not isinstance(payload, dict):
                return False

            for key in ('method', 'event'):
                action_value = payload.get(key)
                if not isinstance(action_value, str):
                    continue

                action_name = action_value.split('.')[-1]
                if action_name in self._schedule_actions():
                    return True
        except Exception:
            return False

        return False

    def _is_schedule_message(self, source):
        """True only when latest packet type/action is schedule-related."""
        try:
            if source is None:
                return False

            schedule_actions = self._schedule_actions()

            if hasattr(source, 'get_message_type'):
                msg_type, msg_action = source.get_message_type()
                if (
                    msg_type in ['method', 'event']
                    and isinstance(msg_action, str)
                    and msg_action in schedule_actions
                ):
                    return True

            data = getattr(source, 'data', {})
            if isinstance(data, dict):
                method = data.get('method', '')
                if isinstance(method, str):
                    if any(method.endswith(f'.{action}') for action in schedule_actions):
                        return True
                    if any(method == action for action in schedule_actions):
                        return True
        except Exception:
            return False

        return False

    def _success_without_support_seconds(self, source):
        """
        True when schedule response succeeded but omitted supportSeconds.

        YoLink responses with code 00000000 indicate valid data was returned.
        If supportSeconds is absent in that successful payload, treat it as False
        and stop retrying.
        """
        try:
            if source is None:
                return False

            raw_data = getattr(source, 'data', {})
            if not isinstance(raw_data, dict):
                return False

            code = raw_data.get('code')
            if code is None:
                data_block = raw_data.get('data', {})
                if isinstance(data_block, dict):
                    code = data_block.get('code')

            code_str = str(code).zfill(8) if code is not None else ''
            if code_str != '00000000':
                return False

            data_block = raw_data.get('data', {})
            if not isinstance(data_block, dict):
                return False

            if 'supportSeconds' in data_block:
                return False

            schedules_block = data_block.get('schedules')
            if isinstance(schedules_block, dict) and 'supportSeconds' in schedules_block:
                return False

            # If successful response contains schedule entries but no
            # supportSeconds field, resolve as False immediately.
            if len(data_block) > 0:
                return True

            return True
        except Exception:
            return False

    def _resolve_support_seconds_from_parent_node(self):
        """Check the already-created parent device node for supportSeconds."""
        try:
            parent_node = self.poly.getNode(self.primary)
        except Exception:
            return None

        if parent_node is None:
            return None

        candidate_attrs = (
            'yoSwitch', 'yoOutlet', 'yoDimmer', 'yoManipulator',
            'yoInfraredRemoter', 'yoMultiOutlet', 'yoSprinkler',
        )

        for attr in candidate_attrs:
            source = getattr(parent_node, attr, None)
            if source is None:
                continue

            if not self._is_schedule_message(source):
                continue

            try:
                val = source.get_data('supportSeconds')
                if isinstance(val, bool):
                    self._support_seconds_source = f'parent.{attr}.get_data(supportSeconds)'
                    return val
            except Exception:
                pass

            try:
                schedules = getattr(source, 'schedules', None)
                if isinstance(schedules, dict):
                    val = schedules.get('supportSeconds')
                    if isinstance(val, bool):
                        self._support_seconds_source = f'parent.{attr}.schedules.supportSeconds'
                        return val
            except Exception:
                pass

            try:
                raw_data = getattr(source, 'data', {})
                if isinstance(raw_data, dict):
                    data_block = raw_data.get('data', {})
                    if isinstance(data_block, dict):
                        val = data_block.get('supportSeconds')
                        if isinstance(val, bool):
                            self._support_seconds_source = f'parent.{attr}.data.data.supportSeconds'
                            return val
                        schedules_block = data_block.get('schedules')
                        if isinstance(schedules_block, dict):
                            val = schedules_block.get('supportSeconds')
                            if isinstance(val, bool):
                                self._support_seconds_source = f'parent.{attr}.data.data.schedules.supportSeconds'
                                return val
            except Exception:
                pass

            if self._success_without_support_seconds(source):
                self._support_seconds_source = f'parent.{attr}.code00000000.no_supportSeconds'
                return False

        return None

    def _refresh_parent_schedules(self):
        """Ask the parent device wrapper to refresh schedules (best effort)."""
        try:
            parent_node = self.poly.getNode(self.primary)
        except Exception:
            return False

        if parent_node is None:
            return False

        candidate_attrs = (
            'yoSwitch', 'yoOutlet', 'yoDimmer', 'yoManipulator',
            'yoInfraredRemoter', 'yoMultiOutlet', 'yoSprinkler',
        )

        for attr in candidate_attrs:
            source = getattr(parent_node, attr, None)
            if source is not None and hasattr(source, 'refreshSchedules'):
                try:
                    source.refreshSchedules()
                    return True
                except Exception:
                    pass

        return False

    def _resolve_support_seconds(self):
        """Best-effort detection of supportSeconds before node profile binding."""
        parent_val = self._resolve_support_seconds_from_parent_node()
        if isinstance(parent_val, bool):
            return parent_val

        if self._success_without_support_seconds(self.yoSchedule):
            self._support_seconds_source = 'schedule_wrapper.code00000000.no_supportSeconds'
            return False

        if not self._is_schedule_message(self.yoSchedule):
            return None

        try:
            val = self.yoSchedule.get_data('supportSeconds')
            logging.debug(f'Checked schedule_wrapper.get_data(supportSeconds): {val}')
            if isinstance(val, bool):
                self._support_seconds_source = 'schedule_wrapper.get_data(supportSeconds)'
                return val
        except Exception:
            pass

        try:
            raw_data = getattr(self.yoSchedule, 'data', {})
            if isinstance(raw_data, dict):
                data_block = raw_data.get('data', {})
                if isinstance(data_block, dict):
                    val = data_block.get('supportSeconds')
                    if isinstance(val, bool):
                        self._support_seconds_source = 'schedule_wrapper.data.data.supportSeconds'
                        return val

                    schedules_block = data_block.get('schedules')
                    if isinstance(schedules_block, dict):
                        val = schedules_block.get('supportSeconds')
                        if isinstance(val, bool):
                            self._support_seconds_source = 'schedule_wrapper.data.data.schedules.supportSeconds'
                            return val
        except Exception:
            pass

        try:
            val = getattr(self.yoSchedule, 'scheduleSec', None)
            if isinstance(val, bool):
                self._support_seconds_source = 'schedule_wrapper.scheduleSec'
                return val
        except Exception:
            pass

        return None
    
    def __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        logging.debug(f'{self.__class__.__name__} INIT - {deviceInfo["name"]}')
        
        # Store references before calling super().__init__()
        self.n_queue = []
        self.address = address
        self.primary = primary
        self.yoAccess = yoAccess
        self.devInfo = deviceInfo   
        self.yoSchedule = None
        self.node_ready = False
        self.system_ready=False
        self.schedule_selected = 0
        self.poly = polyglot
        self._support_seconds_source = 'unresolved'
        
        # Create yoSchedule wrapper and determine support_seconds BEFORE node initialization
        self.yoSchedule = self._create_yolink_schedule()
        # Do not call refreshSchedules or make API calls here; defer to post-startup refresh
        support_seconds = self._resolve_support_seconds()
        if not isinstance(support_seconds, bool):
            logging.debug('Could not determine supportSeconds during init, defaulting to False')
            support_seconds = False
            self._support_seconds_source = 'default_false'
        self.support_seconds = support_seconds
        logging.debug(
            f'Schedule support_seconds: {self.support_seconds} '
            f'(source: {self._support_seconds_source})'
        )
        # Resolve node ID BEFORE super().__init__(); do not mutate after init.
        resolved_id = self._set_id_for_seconds_support()
        if isinstance(resolved_id, str) and resolved_id:
            self.id = resolved_id
        # NOW call super().__init__() with correct id
        super().__init__(polyglot, primary, address, name)
        self.poly.subscribe(self.poly.START, self.start, self.address)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status=None, rename=True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True

    def _create_yolink_schedule(self):
        """
        Factory method to create the appropriate YoLink schedule device wrapper.
        Override in subclasses to return device-specific wrappers.
        """
        return YoLinkSchedule(self.yoAccess, self.devInfo, self.updateStatus)
    
    def _set_id_for_seconds_support(self):
        """
        Return the node ID based on seconds support.
        Base class defaults to current id - override in subclasses.
        """
        return getattr(self, 'id', None)
    
    def start(self):
        """Start schedule node and initialize drivers."""
        logging.info(f'start - {self.__class__.__name__}')
        self.system_ready=True

    def stop(self):
        """Stop schedule node cleanup."""
        logging.info(f'Stop {self.__class__.__name__}')
        self.my_setDriver('GV30', 0)
        if getattr(self, 'yoSchedule', None):
            self.yoSchedule.shut_down()

    def checkOnline(self):
        """Long-poll hook: refresh schedule data at long poll cadence."""
        self.updateData()

    def checkDataUpdate(self):
        """Short-poll hook: intentionally no-op for schedule refreshes."""
        return

    def updateStatus(self, deviceInfo):
        """Called when device status updates."""
        if isinstance(deviceInfo, dict) and not self._is_schedule_payload(deviceInfo):
            logging.debug(f'{self.__class__.__name__} ignoring non-schedule payload')
            return
        logging.info(f'{self.__class__.__name__} updateStatus')
        self.updateData()   

    def _parse_time_string(self, timestr):
        """
        Parse time string into components.
        Supports "HH:MM" (no seconds) or "HH:MM:SS" (with seconds).
        
        Args:
            timestr: Time string, e.g., "14:30" or "14:30:45"
            
        Returns:
            Dict with 'hour', 'minute', and optionally 'second' keys.
            Returns None if parsing fails.
        """
        if not timestr:
            return None
        
        try:
            timelist = timestr.split(':')
            result = {}
            
            if len(timelist) == 2:
                result['hour'] = int(timelist[0])
                result['minute'] = int(timelist[1])
            elif len(timelist) == 3:
                result['hour'] = int(timelist[0])
                result['minute'] = int(timelist[1])
                result['second'] = int(timelist[2])
            else:
                return None
            
            return result
        except (ValueError, IndexError):
            return None

    def _update_time_drivers(self, timestr, hour_driver, minute_driver, second_driver=None):
        """
        Update driver values for schedule time display.
        
        Args:
            timestr: Time string to parse
            hour_driver: Driver name for hour (e.g., 'GV15')
            minute_driver: Driver name for minute (e.g., 'GV16')
            second_driver: Optional driver name for second (e.g., 'GV21')
        """
        time_info = self._parse_time_string(timestr)
        
        if not time_info:
            self.my_setDriver(hour_driver, 99, 25)
            self.my_setDriver(minute_driver, 99, 25)
            if second_driver:
                self.my_setDriver(second_driver, 99, 25)
            return
        
        hour = time_info['hour']
        minute = time_info['minute']
        
        # 25:00 means "not set" in YoLink
        if hour == 25:
            self.my_setDriver(hour_driver, 98, 25)
            self.my_setDriver(minute_driver, 98, 25)
            if second_driver:
                self.my_setDriver(second_driver, 98, 25)
        else:
            self.my_setDriver(hour_driver, hour, 19)
            self.my_setDriver(minute_driver, minute, 44)
            if second_driver and 'second' in time_info:
                self.my_setDriver(second_driver, time_info['second'], 57)

    def _get_schedule_type_name(self):
        """Return the schedule type string. Override in subclasses."""
        return 'Base'

    def _normalize_schedule_info(self, sch_info, selected_schedule):
        """
        Normalize raw schedule payload into common display shape.

        Default shape used by shared UI rendering:
        - isValid: bool
        - on: HH:MM[:SS]
        - off: HH:MM[:SS]
        - week: int bitmask
        """
        return sch_info

    def update(self, command=None):
        """Update schedule data."""
        logging.info('Update Status Executed')
        self.yoSchedule.refreshSchedules()

    def lookup_schedule(self, command):
        """Select which schedule to view/edit."""
        logging.info(f'{self.__class__.__name__} lookup_schedule')
        self.schedule_selected = command.get('value')
        if isinstance(self.schedule_selected, str):
            self.schedule_selected = int(self.schedule_selected)
        self.yoSchedule.refreshSchedules()

    def control_schedule(self, command):
        """Activate or deactivate a schedule."""
        logging.info(f'{self.__class__.__name__} control_schedule')
        query = command.get("query")
        activated, schedule_selected = self.activate_schedule(query)
        self.yoSchedule.activateSchedule(schedule_selected, activated)

    def activate_schedule(self, query):
        """
        Parse activation command from UI.
        
        Returns:
            Tuple of (activated: bool, schedule_selected: int)
        """
        schedule_selected = query.get('index.uom25')
        if isinstance(schedule_selected, str):  
            schedule_selected = int(schedule_selected)
        
        tmp = query.get('active.uom25')
        activated = False
        if isinstance(tmp, str):
            activated = (int(tmp) == 1)    
        
        return (activated, schedule_selected)

    def updateData(self):
        """Update all schedule node drivers with current data."""
        logging.info(f'{self.__class__.__name__} updateData')
        self.update_schedule_data()

    def update_schedule_data(self, selected_schedule=None, source_device=None):
        """
        Backward-compatible schedule update entrypoint.

        Supports prior call styles from device nodes:
        - update_schedule_data(source_device=device)
        - update_schedule_data(selected_schedule)
        - update_schedule_data(raw_schedule_dict, selected_schedule)
        """
        if self.node is None:
            return
        while not self.node_ready or not self.system_ready:
            time.sleep(0.5)

        raw_schedule = None

        if isinstance(selected_schedule, dict):
            raw_schedule = selected_schedule
            if isinstance(source_device, int):
                selected_schedule = source_device
            else:
                selected_schedule = self.schedule_selected

        if selected_schedule is None:
            selected_schedule = self.schedule_selected

        if raw_schedule is None:
            if source_device is not None:
                raw_schedule = source_device.getScheduleInfo(selected_schedule)
            else:
                raw_schedule = self.yoSchedule.getScheduleInfo(selected_schedule)

        sch_info = self._normalize_schedule_info(raw_schedule, selected_schedule)
        self._update_schedule_display(sch_info, selected_schedule, source_device=source_device)

    def _count_schedules(self, schedules_payload):
        """Count real schedules while ignoring metadata keys like supportSeconds."""
        if isinstance(schedules_payload, list):
            return sum(1 for entry in schedules_payload if isinstance(entry, dict))

        if isinstance(schedules_payload, dict):
            count = 0
            for key, value in schedules_payload.items():
                if not isinstance(value, dict):
                    continue

                key_is_index = isinstance(key, str) and key.isdigit()
                looks_like_schedule = any(field in value for field in ('index', 'on', 'off', 'time'))
                if key_is_index or looks_like_schedule:
                    count += 1
            return count

        return 0

    def _update_schedule_display(self, sch_info, selected_schedule, source_device=None):
        """
        Update driver display with schedule information.
        
        Base implementation handles common time/weekday display.
        Override in subclasses for device-specific fields (key, channel, etc.).
        """
        # Update total schedules count from the same source payload used by getSchedules
        schedule_source = source_device if source_device is not None else self.yoSchedule
        schedules_payload = getattr(schedule_source, 'schedules', None)
        self.my_setDriver('GV23', self._count_schedules(schedules_payload))

        if not sch_info:
            logging.debug('No schedule exists for selected index')
            self._clear_schedule_display(selected_schedule)
            return
        
        logging.debug(f'Updating schedule display: {sch_info}')
        
        # Common schedule fields
        self.my_setDriver('GV13', selected_schedule)
        self.my_setDriver('GV14', 1 if sch_info.get('isValid', False) else 0)
        
        # Time parsing
        self._update_time_drivers(sch_info.get('on'), 'GV15', 'GV16', 'GV21' if self.support_seconds else None)
        self._update_time_drivers(sch_info.get('off'), 'GV17', 'GV18', 'GV22' if self.support_seconds else None)
        
        # Weekday mask
        self.my_setDriver('GV19', int(sch_info.get('week', 0)))

    def _clear_schedule_display(self, selected_schedule):
        """Clear all schedule drivers (no schedule selected)."""
        self.my_setDriver('GV13', selected_schedule) 
        self.my_setDriver('GV14', 99, 25)
        self.my_setDriver('GV15', 99, 25)
        self.my_setDriver('GV16', 99, 25)
        self.my_setDriver('GV17', 99, 25)
        self.my_setDriver('GV18', 99, 25)
        self.my_setDriver('GV19', 0)
        if self.support_seconds:
            self.my_setDriver('GV21', 99, 25)
            self.my_setDriver('GV22', 99, 25)

    def commands(self):
        """Return command dictionary. Override in subclasses."""
        return {
            'UPDATE': self.update,
            'LOOKUPSCH': self.lookup_schedule,
            'CTRLSCH': self.control_schedule,
        }

class OnOffScheduleNode(BaseScheduleNode):
    """
    Schedule node for on/off devices (Switch, Outlet, Dimmer, Manipulator).
    
    Handles schedules with on/off state transitions at specified times.
    """
    
    id = 'YOSCHEDULESEC'
    
    drivers = [
        {'driver': 'GV13', 'value': 0, 'uom': 25, 'name': 'Schedule Index'},     # Schedule index
        {'driver': 'GV14', 'value': 99, 'uom': 25, 'name': 'Activated'},    # Active (enabled)
        {'driver': 'GV23', 'value': 0, 'uom': 70, 'name': 'Total Schedules'},     # Total schedules
        {'driver': 'GV15', 'value': 99, 'uom': 25, 'name': 'On Hour'},    # On hour
        {'driver': 'GV16', 'value': 99, 'uom': 25, 'name': 'On Minute'},    # On minute
        {'driver': 'GV21', 'value': 99, 'uom': 25, 'name': 'On Sec'},    # On second
        {'driver': 'GV17', 'value': 99, 'uom': 25, 'name': 'Off Hour'},    # Off hour
        {'driver': 'GV18', 'value': 99, 'uom': 25, 'name': 'Off Minute'},    # Off minute
        {'driver': 'GV22', 'value': 99, 'uom': 25, 'name': 'Off Sec'},    # Off second
        {'driver': 'GV19', 'value': 0, 'uom': 25, 'name': 'Active Days'},     # Weekday mask
    ]

    def _set_id_for_seconds_support(self):
        """Set node ID based on seconds support."""
        if self.support_seconds:
            return 'YOSCHEDULESEC'
        return 'YOSCHEDULE'
    
    def prep_schedule(self, query):
        """Prepare schedule parameters from UI query."""
        try:
            logging.debug(f'OnOff prep_schedule: {query}')
            params = {}
            
            schedule_selected = query.get('index.uom25')
            if isinstance(schedule_selected, str):
                schedule_selected = int(schedule_selected)  
                params['index'] = str(schedule_selected)
           
            tmp = query.get('active.uom25') 
            if isinstance(tmp, str): 
                activated = (int(tmp) == 1)
                params['isValid'] = activated 
            
            # On time
            onH = query.get('onH.uom19')
            onM = query.get('onM.uom44')
            if isinstance(onH, int) and isinstance(onM, int):
                on_str = f'{onH}:{onM}'
                if self.support_seconds:
                    onS = query.get('onS.uom57')
                    if isinstance(onS, int):
                        on_str = f'{on_str}:{onS}'
                params['on'] = on_str

            # Off time
            offH = query.get('offH.uom19')
            offM = query.get('offM.uom44')  
            if isinstance(offH, int) and isinstance(offM, int):
                off_str = f'{offH}:{offM}'
                if self.support_seconds:
                    offS = query.get('offS.uom57')
                    if isinstance(offS, int):
                        off_str = f'{off_str}:{offS}'
                params['off'] = off_str 

            binDays = query.get('bindays.uom25')                    
            if isinstance(binDays, str):
                binDays = int(binDays)
                params['week'] = binDays
                
            return (schedule_selected, params)
        except Exception as e:
            logging.error(f'Exception in prep_schedule: {e}')
            return (None, None)

    def define_schedule(self, command):
        """Define or update a schedule."""
        logging.info('OnOff define_schedule')
        query = command.get("query")
        schedule_selected, params = self.prep_schedule(query)
        if schedule_selected is not None and params:
            self.yoSchedule.setSchedule(schedule_selected, params)

    def _get_schedule_type_name(self):
        return ('OnOff')

    commands = {
        'UPDATE': BaseScheduleNode.update,
        'LOOKUPSCH': BaseScheduleNode.lookup_schedule,
        'DEFINESCH': define_schedule,
        'CTRLSCH': BaseScheduleNode.control_schedule,
    }


class KeyScheduleNode(BaseScheduleNode):
    """
    Schedule node for infrared remote (InfraredRemoter).
    
    Handles schedules that trigger infrared key transmissions.
    Adds a 'key' parameter to on/off time schedules.
    """
    
    id = 'YOIRSCHEDULE'
    
    drivers = [
        {'driver': 'GV12', 'value': 99, 'uom': 25, 'name': 'Selected code/port'},     # Infrared key/channel
        {'driver': 'GV13', 'value': 0, 'uom': 25, 'name': 'Schedule Index'},      # Schedule index
        {'driver': 'GV14', 'value': 99, 'uom': 25, 'name': 'Activated'},     # Active (enabled)
        {'driver': 'GV23', 'value': 0, 'uom': 70, 'name': 'Total Schedules'},      # Total schedules
        {'driver': 'GV15', 'value': 99, 'uom': 25, 'name': 'On Hour'},     # On hour
        {'driver': 'GV16', 'value': 99, 'uom': 25, 'name': 'On Minute'},     # On minute
        {'driver': 'GV21', 'value': 99, 'uom': 25, 'name': 'On Sec'},     # On second
        {'driver': 'GV17', 'value': 99, 'uom': 25, 'name': 'Off Hour'},     # Off hour
        {'driver': 'GV18', 'value': 99, 'uom': 25, 'name': 'Off Minute'},     # Off minute
        {'driver': 'GV22', 'value': 99, 'uom': 25, 'name': 'Off Sec'},     # Off second
        {'driver': 'GV19', 'value': 0, 'uom': 25, 'name': 'Active Days'},      # Weekday mask
    ]

    def _set_id_for_seconds_support(self):
        if self.support_seconds:
            return 'YOIRSCHEDULESEC'
        return 'YOIRSCHEDULE'

    def prep_schedule(self, query):
        """Prepare infrared schedule parameters from UI query."""
        try:
            logging.debug(f'Key prep_schedule: {query}')
            params = {}
            
            key = query.get('outport.uom25')
            if isinstance(key, str):
                params['key'] = int(key) - 1

            schedule_selected = query.get('index.uom25')
            if isinstance(schedule_selected, str):
                schedule_selected = int(schedule_selected)  
                params['index'] = str(schedule_selected)
           
            tmp = query.get('active.uom25') 
            if isinstance(tmp, str): 
                activated = (int(tmp) == 1)
                params['isValid'] = activated 
            
            # On time (YoLink format: "HH:MM" or "HH:MM:SS")
            onH = query.get('onH.uom19')
            onM = query.get('onM.uom44')
            if isinstance(onH, int) and isinstance(onM, int):
                on_str = f'{onH}:{onM}'
                if self.support_seconds:
                    onS = query.get('onS.uom57')
                    if isinstance(onS, int):
                        on_str = f'{on_str}:{onS}'
                params['on'] = on_str

            # Note: For infrared remotes, 'off' time might not be used
            offH = query.get('offH.uom19')
            offM = query.get('offM.uom44')  
            if isinstance(offH, int) and isinstance(offM, int):
                off_str = f'{offH}:{offM}'
                if self.support_seconds:
                    offS = query.get('offS.uom57')
                    if isinstance(offS, int):
                        off_str = f'{off_str}:{offS}'
                params['off'] = off_str 

            binDays = query.get('bindays.uom25')                    
            if isinstance(binDays, str):
                binDays = int(binDays)
                params['week'] = binDays
                
            return (schedule_selected, params)
        except Exception as e:
            logging.error(f'Exception in Key prep_schedule: {e}')
            return (None, None)

    def define_schedule(self, command):
        """Define or update an infrared schedule."""
        logging.info('Key define_schedule')
        query = command.get("query")
        schedule_selected, params = self.prep_schedule(query)
        if schedule_selected is not None and params:
            self.yoSchedule.setSchedule(schedule_selected, params)

    def _update_schedule_display(self, sch_info, selected_schedule, source_device=None):
        """Update driver display, including key field."""
        if not sch_info:
            logging.debug('No schedule exists for selected index')
            self._clear_schedule_display(selected_schedule)
            return
        
        logging.debug(f'Updating key schedule display: {sch_info}')
        
        # Device-specific field: key
        if 'key' in sch_info:
            self.my_setDriver('GV12', int(sch_info['key']))
        
        # Call parent to update common fields
        super()._update_schedule_display(sch_info, selected_schedule, source_device=source_device)

    def _get_schedule_type_name(self):
        return 'Key'

    commands = {
        'UPDATE': BaseScheduleNode.update,
        'LOOKUPSCH': BaseScheduleNode.lookup_schedule,
        'DEFINESCH': define_schedule,
        'CTRLSCH': BaseScheduleNode.control_schedule,
    }


class MultiOutletScheduleNode(BaseScheduleNode):
    """
    Schedule node for multi-outlet devices.
    
    Handles per-channel schedules. Adds a 'channel' parameter
    to on/off time schedules to select which outlet is controlled.
    """
    
    id = 'YOMSCHEDULE'
    
    drivers = [
        {'driver': 'GV12', 'value': 99, 'uom': 25, 'name': 'Selected code/port'},     # Channel/outlet number
        {'driver': 'GV13', 'value': 0, 'uom': 25, 'name': 'Schedule Index'},      # Schedule index
        {'driver': 'GV14', 'value': 99, 'uom': 25, 'name': 'Activated'},     # Active (enabled)
        {'driver': 'GV23', 'value': 0, 'uom': 70, 'name': 'Total Schedules'},      # Total schedules
        {'driver': 'GV15', 'value': 99, 'uom': 25, 'name': 'On Hour'},     # On hour
        {'driver': 'GV16', 'value': 99, 'uom': 25, 'name': 'On Minute'},     # On minute
        {'driver': 'GV21', 'value': 99, 'uom': 25, 'name': 'On Sec'},     # On second
        {'driver': 'GV17', 'value': 99, 'uom': 25, 'name': 'Off Hour'},     # Off hour
        {'driver': 'GV18', 'value': 99, 'uom': 25, 'name': 'Off Minute'},     # Off minute
        {'driver': 'GV22', 'value': 99, 'uom': 25, 'name': 'Off Sec'},     # Off second
        {'driver': 'GV19', 'value': 0, 'uom': 25, 'name': 'Active Days'},      # Weekday mask
    ]

    def _set_id_for_seconds_support(self):
        if self.support_seconds:
            return 'YOMSCHEDULESEC'
        return 'YOMSCHEDULE'

    def prep_schedule(self, query):
        """Prepare multi-outlet schedule parameters from UI query."""
        try:
            logging.debug(f'MultiOutlet prep_schedule: {query}')
            params = {}
            
            port = query.get('outport.uom25')
            if isinstance(port, str):
                params['ch'] = int(port) - 1

            schedule_selected = query.get('index.uom25')
            if isinstance(schedule_selected, str):
                schedule_selected = int(schedule_selected)  
                params['index'] = str(schedule_selected)
           
            tmp = query.get('active.uom25') 
            if isinstance(tmp, str): 
                activated = (int(tmp) == 1)
                params['isValid'] = activated 
            
            # On time
            onH = query.get('onH.uom19')
            onM = query.get('onM.uom44')
            if isinstance(onH, int) and isinstance(onM, int):
                on_str = f'{onH}:{onM}'
                if self.support_seconds:
                    onS = query.get('onS.uom57')
                    if isinstance(onS, int):
                        on_str = f'{on_str}:{onS}'
                params['on'] = on_str

            # Off time
            offH = query.get('offH.uom19')
            offM = query.get('offM.uom44')  
            if isinstance(offH, int) and isinstance(offM, int):
                off_str = f'{offH}:{offM}'
                if self.support_seconds:
                    offS = query.get('offS.uom57')
                    if isinstance(offS, int):
                        off_str = f'{off_str}:{offS}'
                params['off'] = off_str 

            binDays = query.get('bindays.uom25')                    
            if isinstance(binDays, str):
                binDays = int(binDays)
                params['week'] = binDays
                
            return (schedule_selected, params)
        except Exception as e:
            logging.error(f'Exception in MultiOutlet prep_schedule: {e}')
            return (None, None)

    def define_schedule(self, command):
        """Define or update a multi-outlet schedule."""
        logging.info('MultiOutlet define_schedule')
        query = command.get("query")
        schedule_selected, params = self.prep_schedule(query)
        if schedule_selected is not None and params:
            self.yoSchedule.setSchedule(schedule_selected, params)

    def _update_schedule_display(self, sch_info, selected_schedule, source_device=None):
        """Update driver display, including channel field."""
        if not sch_info:
            logging.debug('No schedule exists for selected index')
            self._clear_schedule_display(selected_schedule)
            return
        
        logging.debug(f'Updating multi-outlet schedule display: {sch_info}')
        
        # Device-specific field: channel
        if 'ch' in sch_info:
            self.my_setDriver('GV12', int(sch_info['ch']))
        
        # Call parent to update common fields
        super()._update_schedule_display(sch_info, selected_schedule, source_device=source_device)

    def _get_schedule_type_name(self):
        return 'MultiOutlet'

    commands = {
        'UPDATE': BaseScheduleNode.update,
        'LOOKUPSCH': BaseScheduleNode.lookup_schedule,
        'DEFINESCH': define_schedule,
        'CTRLSCH': BaseScheduleNode.control_schedule,
    }


class SprinklerScheduleNode(OnOffScheduleNode):
    """
    Schedule node for sprinkler devices.

    SprinklerV2 schedules use fields such as:
    - time
    - valid
    - days.type / days.value
    - startDate / endDate
    - waterDelay.type / waterDelay.value

    This class maps those fields to/from the existing schedule UI drivers.
    """

    id = 'YOSPRINKLERSCHEDULE'

    def _set_id_for_seconds_support(self):
        if self.support_seconds:
            return 'YOSPRINKLERSCHEDULESEC'
        return 'YOSPRINKLERSCHEDULE'

    def _get_schedule_type_name(self):
        return 'Sprinkler'

    def _normalize_schedule_info(self, sch_info, selected_schedule):
        if not isinstance(sch_info, dict):
            return sch_info

        # Already in generic schedule shape.
        if 'on' in sch_info or 'off' in sch_info or 'isValid' in sch_info:
            return sch_info

        # SprinklerV2 shape -> generic display shape.
        valid = sch_info.get('valid')
        if valid is None:
            valid = sch_info.get('isValid', False)

        on_time = sch_info.get('time', '25:0')

        days_value = 0
        days_obj = sch_info.get('days')
        if isinstance(days_obj, dict):
            days_type = days_obj.get('type', 'weekly')
            if days_type == 'weekly':
                try:
                    days_value = int(days_obj.get('value', 0))
                except (TypeError, ValueError):
                    days_value = 0
            else:
                # UI currently supports weekly mask only.
                # Preserve device data on write, but display mask as 0.
                days_value = 0
        elif isinstance(days_obj, (int, str)):
            # Some payloads provide weekly mask directly as an integer.
            try:
                days_value = int(days_obj)
            except (TypeError, ValueError):
                days_value = 0

        return {
            'index': sch_info.get('index', selected_schedule),
            'isValid': bool(valid),
            'on': on_time,
            'off': '25:0',
            'week': days_value,
        }

    def prep_schedule(self, query):
        """Prepare SprinklerV2 schedule payload from the current UI query."""
        try:
            def _as_int(value):
                if isinstance(value, int):
                    return value
                if isinstance(value, str) and value.strip() != '':
                    return int(value)
                return None

            schedule_selected = query.get('index.uom25')
            schedule_selected = _as_int(schedule_selected)

            if not isinstance(schedule_selected, int):
                return (None, None)

            existing = self.yoSchedule.getScheduleInfo(schedule_selected)
            if not isinstance(existing, dict):
                existing = {}

            params = {}
            params['index'] = schedule_selected

            tmp = query.get('active.uom25')
            if isinstance(tmp, str):
                params['valid'] = (int(tmp) == 1)
            else:
                params['valid'] = bool(existing.get('valid', True))

            onH = _as_int(query.get('onH.uom19'))
            onM = _as_int(query.get('onM.uom44'))
            if isinstance(onH, int) and isinstance(onM, int):
                params['time'] = f'{onH}:{onM}'
            else:
                params['time'] = existing.get('time', '0:0')

            params['startDate'] = existing.get('startDate', '1-1')
            params['endDate'] = existing.get('endDate', '12-31')

            water_delay = existing.get('waterDelay')
            if not isinstance(water_delay, dict):
                water_delay = {'type': 'duration', 'value': 0}
            if 'type' not in water_delay:
                water_delay['type'] = 'duration'
            if 'value' not in water_delay:
                water_delay['value'] = 0
            params['waterDelay'] = water_delay

            binDays = query.get('bindays.uom25')
            parsed_days = _as_int(binDays)
            if isinstance(parsed_days, int):
                # UI edits use weekly mask, so mark repeat type accordingly.
                params['days'] = {'type': 'weekly', 'value': parsed_days}
            else:
                existing_days = existing.get('days')
                if isinstance(existing_days, dict):
                    # Preserve current repeat mode if UI did not provide weekly mask.
                    params['days'] = {
                        'type': existing_days.get('type', 'weekly'),
                        'value': existing_days.get('value', 0),
                    }
                else:
                    params['days'] = {'type': 'weekly', 'value': 0}

            return (schedule_selected, params)
        except Exception as e:
            logging.error(f'Exception in Sprinkler prep_schedule: {e}')
            return (None, None)

    def define_schedule(self, command):
        logging.info('Sprinkler define_schedule')
        query = command.get("query")
        schedule_selected, params = self.prep_schedule(query)
        if schedule_selected is not None and params:
            self.yoSchedule.setSchedule(schedule_selected, params)

    def control_schedule(self, command):
        """Toggle sprinkler schedule valid flag while preserving sprinkler fields."""
        logging.info('Sprinkler control_schedule')
        query = command.get("query")
        activated, schedule_selected = self.activate_schedule(query)
        if not isinstance(schedule_selected, int):
            return

        raw = self.yoSchedule.getScheduleInfo(schedule_selected)
        if not isinstance(raw, dict):
            raw = {
                'index': schedule_selected,
                'startDate': '1-1',
                'endDate': '12-31',
                'time': '0:0',
                'days': {'type': 'weekly', 'value': 0},
                'waterDelay': {'type': 'duration', 'value': 0},
            }
        raw['index'] = schedule_selected
        raw['valid'] = bool(activated)

        if 'startDate' not in raw:
            raw['startDate'] = '1-1'
        if 'endDate' not in raw:
            raw['endDate'] = '12-31'
        if 'time' not in raw:
            raw['time'] = '0:0'

        if 'days' not in raw or not isinstance(raw['days'], dict):
            raw['days'] = {'type': 'weekly', 'value': 0}
        if 'waterDelay' not in raw or not isinstance(raw['waterDelay'], dict):
            raw['waterDelay'] = {'type': 'duration', 'value': 0}

        self.yoSchedule.setSchedule(schedule_selected, raw)

    commands = {
        'UPDATE': BaseScheduleNode.update,
        'LOOKUPSCH': BaseScheduleNode.lookup_schedule,
        'DEFINESCH': define_schedule,
        'CTRLSCH': control_schedule,
    }


class WaterMeterScheduleNode(OnOffScheduleNode):
    """
    Schedule node for WaterMeterController schedules.

    WaterMeterController has valve schedules and leak schedules. Leak schedules
    include an additional `leakLimit` field in each schedule record. This node
    can manage either valve or leak schedules based on the schedule_type flag.
    
    schedule_type: 'valve' for valve control schedules, 'leak' for leak detection schedules
    """

    id = 'YOWMSCHEDULE'

    drivers = [
        {'driver': 'GV12', 'value': 99, 'uom': 56, 'name': 'Leak Limit'},    # Leak limit (or repurposed for data)
        {'driver': 'GV13', 'value': 0, 'uom': 25, 'name': 'Schedule Index'},     # Schedule index
        {'driver': 'GV14', 'value': 99, 'uom': 25, 'name': 'Activated'},    # Active (enabled)
        {'driver': 'GV23', 'value': 0, 'uom': 70, 'name': 'Total Schedules'},     # Total schedules
        {'driver': 'GV15', 'value': 99, 'uom': 25, 'name': 'On Hour'},    # On hour
        {'driver': 'GV16', 'value': 99, 'uom': 25, 'name': 'On Minute'},    # On minute
        {'driver': 'GV21', 'value': 99, 'uom': 25, 'name': 'On Sec'},    # On second
        {'driver': 'GV17', 'value': 99, 'uom': 25, 'name': 'Off Hour'},    # Off hour
        {'driver': 'GV18', 'value': 99, 'uom': 25, 'name': 'Off Minute'},    # Off minute
        {'driver': 'GV22', 'value': 99, 'uom': 25, 'name': 'Off Sec'},    # Off second
        {'driver': 'GV19', 'value': 0, 'uom': 25, 'name': 'Active Days'},     # Weekday mask
    ]

    def __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo, schedule_type='valve'):
        """
        Initialize WaterMeter schedule node.
        
        Args:
            schedule_type: 'valve' or 'leak' to determine which schedule methods to use
        """
        if schedule_type not in ['valve', 'leak']:
            logging.warning(f'Invalid schedule_type "{schedule_type}" for WaterMeterScheduleNode, defaulting to "valve"')
            schedule_type = 'valve' 
        self.schedule_type = schedule_type
        super().__init__(polyglot, primary, address, name, yoAccess, deviceInfo)

    def _set_id_for_seconds_support(self):
        """Set node ID based on schedule type and seconds support."""
        if self.schedule_type == 'leak':
            # Leak schedule nodes
            if self.support_seconds:
                return 'YOWMLKSCHEDULESEC'
            return 'YOWMLKSCHEDULE'
        else:
            # Valve schedule nodes (default)
            if self.support_seconds:
                return 'YOWMVLSCHEDULESEC'
            return 'YOWMVLSCHEDULE'

    def _get_schedule_type_name(self):
        return 'WaterMeter'

    def _update_schedule_display(self, sch_info, selected_schedule, source_device=None):
        """Update display including leakLimit when present."""
        super()._update_schedule_display(sch_info, selected_schedule, source_device=source_device)
        if isinstance(sch_info, dict) and 'leakLimit' in sch_info:
            try:
                self.my_setDriver('GV12', float(sch_info.get('leakLimit', 99)))
            except (TypeError, ValueError):
                self.my_setDriver('GV12', 99)
        else:
            self.my_setDriver('GV12', 99)

    def prep_schedule(self, query):
        """Prepare WaterMeter schedule payload while preserving leakLimit data."""
        try:
            schedule_selected, params = super().prep_schedule(query)
            if schedule_selected is None or not isinstance(params, dict):
                return (schedule_selected, params)

            existing = self.yoSchedule.getScheduleInfo(schedule_selected)

            leak_limit = None
            for key, value in query.items():
                if isinstance(key, str) and key.startswith('LLIMIT.uom'):
                    try:
                        leak_limit = float(value)
                    except (TypeError, ValueError):
                        leak_limit = None
                    break

            if leak_limit is not None:
                params['leakLimit'] = leak_limit
            if isinstance(existing, dict) and 'leakLimit' in existing and 'leakLimit' not in params:
                params['leakLimit'] = existing.get('leakLimit')

            return (schedule_selected, params)
        except Exception as e:
            logging.error(f'Exception in WaterMeter prep_schedule: {e}')
            return (None, None)

    def control_schedule(self, command):
        """Toggle WaterMeter schedule valid flag while preserving leakLimit data."""
        logging.info('WaterMeter control_schedule')
        query = command.get("query")
        activated, schedule_selected = self.activate_schedule(query)
        if not isinstance(schedule_selected, int):
            return

        raw = self.yoSchedule.getScheduleInfo(schedule_selected)
        if not isinstance(raw, dict):
            raw = {'index': schedule_selected, 'week': 0}

        raw['index'] = schedule_selected
        raw['isValid'] = bool(activated)

        if 'on' not in raw:
            raw['on'] = '25:0'
        if 'off' not in raw:
            raw['off'] = '25:0'
        if 'week' not in raw:
            raw['week'] = 0

        self.yoSchedule.setSchedule(schedule_selected, raw, schedule_method=self.schedule_type)

    def define_schedule(self, command):
        """Define WaterMeter schedule using valve/leak-specific API method."""
        logging.info('WaterMeter define_schedule')
        query = command.get("query")
        schedule_selected, params = self.prep_schedule(query)
        if schedule_selected is not None and params:
            self.yoSchedule.setSchedule(schedule_selected, params, schedule_method=self.schedule_type)

    commands = {
        'UPDATE': BaseScheduleNode.update,
        'LOOKUPSCH': BaseScheduleNode.lookup_schedule,
        'DEFINESCH': define_schedule,
        'CTRLSCH': control_schedule,
    }


def udiYoSchedule(polyglot, primary, address, name, yoAccess, deviceInfo, schedule_type='valve'):
    """
    Factory function to create appropriate schedule node based on device type.
    
    This function maintains backward compatibility with existing code while
    routing to the appropriate specialized schedule node class.
    
    Args:
        polyglot: Polyglot interface object
        primary: Parent node address
        address: This node's address
        name: Display name
        yoAccess: YoLink access object
        deviceInfo: Device information dictionary
        schedule_type: Optional schedule type (e.g., 'valve' or 'leak' for WaterMeterController)
        
    Returns:
        Appropriate schedule node instance (OnOff, Key, MultiOutlet,
        Sprinkler, or WaterMeter)
    """
    dev_type = deviceInfo.get('type', '')
    
    if dev_type == 'InfraredRemoter':
        return KeyScheduleNode(polyglot, primary, address, name, yoAccess, deviceInfo)
    elif dev_type in ['MultiOutlet']:
        return MultiOutletScheduleNode(polyglot, primary, address, name, yoAccess, deviceInfo)
    elif dev_type in ['SprinklerV2', 'Sprinkler']:
        return SprinklerScheduleNode(polyglot, primary, address, name, yoAccess, deviceInfo)
    elif dev_type in ['WaterMeterController', 'WaterMeterMultiController']:
        return WaterMeterScheduleNode(polyglot, primary, address, name, yoAccess, deviceInfo, schedule_type)
    else:  # Default to OnOff for Switch, Outlet, Dimmer, Manipulator, etc.
        return OnOffScheduleNode(polyglot, primary, address, name, yoAccess, deviceInfo)


class YoLinkSchedule(YoLinkMQTTDevice):
    """
    MQTT device wrapper for YoLink schedule operations.
    
    Handles communication with device schedules via MQTT.
    """
    
    def __init__(yolink, yoAccess, deviceInfo, callback):
        super().__init__(yoAccess, deviceInfo, callback, subscribe_mqtt=True, route_filter='schedule')

        yolink.methodList = ['getSchedules', 'setSchedules']
        yolink.eventList = ['StatusChange', 'Report', 'getState']
        yolink.stateList = ['open', 'closed', 'on', 'off']
        yolink.ManipulatorName = 'OutletEvent'
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
