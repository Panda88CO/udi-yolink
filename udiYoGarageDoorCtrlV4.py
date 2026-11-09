#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
import importlib
import threading
import time

try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom

from yolinkGarageDoorToggleV2 import YoLinkGarageDoorCtrl

STATE_CLOSED = 0
STATE_OPEN = 1
STATE_OPENING = 2
STATE_CLOSING = 3
STATE_HALF_OPEN = 4
STATE_HALF_CLOSED = 5
STATE_UNKNOWN = 99


class udiYoGarageDoor(udi_interface.Node):
    from udiYolinkLib import my_setDriver, start_done, configDoneHandler, wait_for_node_done, node_queue, checkNameSync, apply_profile_driver_names, set_offline_notice, clear_offline_notice, wait_for_device_online
    id = 'YOGARAGE'
    
    '''
       drivers = [
            'ST' = Door State (0: Closed, 1: Open, 2: Opening, 3: Closing, 4: Half-Open, 5: Half-Closed, 99: Unknown)
            'GV30' = Online State
            'GV20' = Connection State
            ]
    ''' 
        
    drivers = [ 
            {'driver': 'ST', 'value': 99, 'uom': 25, 'name': 'Door State'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},
            ]

    def __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__(polyglot, primary, address, name)

        self.yoAccess = yoAccess
        self.devInfo = deviceInfo
        self.yoDoorControl = None
        self.node_ready = False
        self.configDone = False
        self.system_ready = False
        self._update_lock = threading.Lock()
        logging.debug('udiYoGarageDoor INIT - {}'.format(deviceInfo['name']))
        self.n_queue = []

        self.state = STATE_UNKNOWN
        self._state_lock = threading.Lock()
        self._travel_timer = None
        self._travel_timer_lock = threading.Lock()
        self._pulse_lock = threading.Lock()
        self._pulse_thread = None
        self._pulse_abort = threading.Event()
        self.paired_sensor = None
        self.last_sensor_state = None

        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)

        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status=None, rename=True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True

    def _get_param(self, param_name, default=None):
        params = getattr(self, 'Parameters', None)
        if params and param_name in params:
            return params[param_name]
        if hasattr(self.poly, 'getCustomParams') and callable(self.poly.getCustomParams):
            try:
                custom = self.poly.getCustomParams()
                if custom and param_name in custom:
                    return custom[param_name]
            except Exception:
                pass
        if hasattr(self.poly, 'customParams'):
            custom = getattr(self.poly, 'customParams', None)
            if isinstance(custom, dict) and param_name in custom:
                return custom[param_name]
        try:
            primary_node = self.poly.getNode(self.primary)
            if primary_node:
                p_params = getattr(primary_node, 'Parameters', None)
                if p_params and param_name in p_params:
                    return p_params[param_name]
        except Exception:
            pass
        return default

    @property
    def travel_time(self):
        custom_time = self._get_param(f'GARAGE_TRAVEL_TIME_{self.address}')
        if not custom_time:
            custom_time = self._get_param('GARAGE_TRAVEL_TIME')
        if custom_time:
            try:
                val = float(custom_time)
                if val > 0:
                    return val
            except (ValueError, TypeError):
                pass
        return 15.0

    def find_paired_sensor(self):
        """Locates and binds the paired DoorSensor node."""
        if self.paired_sensor is not None:
            return self.paired_sensor

        nodes = {}
        if hasattr(self.poly, 'getNodes') and callable(self.poly.getNodes):
            try:
                nodes = self.poly.getNodes() or {}
            except Exception as e:
                logging.debug(f'{self.name} - getNodes() exception: {e}')
        elif hasattr(self.poly, 'nodes'):
            nodes = getattr(self.poly, 'nodes', {}) or {}

        door_sensors = []
        for addr, node in nodes.items():
            if getattr(node, 'id', None) == 'YODOORSENS' or type(node).__name__ == 'udiYoDoorSensor':
                door_sensors.append(node)

        if not door_sensors:
            logging.debug(f'{self.name} - No door sensors found yet in system')
            return None

        paired = None
        # 1. Custom parameter: GARAGE_SENSOR_<address> or GARAGE_SENSOR
        custom_sensor = self._get_param(f'GARAGE_SENSOR_{self.address}')
        if not custom_sensor:
            custom_sensor = self._get_param('GARAGE_SENSOR')
        if custom_sensor:
            cs_str = str(custom_sensor).strip()
            if ':' in cs_str:
                for mapping in cs_str.split(','):
                    parts = mapping.split(':')
                    if len(parts) == 2 and parts[0].strip() in [self.address, self.name]:
                        cs_str = parts[1].strip()
                        break
            for sensor in door_sensors:
                s_dev = getattr(sensor, 'devInfo', {}) or {}
                if cs_str in [sensor.address, sensor.name, s_dev.get('deviceId'), s_dev.get('name')]:
                    paired = sensor
                    logging.info(f'{self.name} - Matched paired sensor by config: {sensor.name}')
                    break

        # 2. Check parentDeviceId on this controller
        if paired is None:
            ctrl_parent = self.devInfo.get('parentDeviceId')
            if ctrl_parent:
                for sensor in door_sensors:
                    s_dev = getattr(sensor, 'devInfo', {}) or {}
                    if s_dev.get('deviceId') == ctrl_parent:
                        paired = sensor
                        logging.info(f'{self.name} - Matched paired sensor by controller parentDeviceId: {sensor.name}')
                        break

        # 3. Check parentDeviceId on the door sensors
        if paired is None:
            ctrl_id = self.devInfo.get('deviceId')
            if ctrl_id:
                for sensor in door_sensors:
                    s_dev = getattr(sensor, 'devInfo', {}) or {}
                    if s_dev.get('parentDeviceId') == ctrl_id:
                        paired = sensor
                        logging.info(f'{self.name} - Matched paired sensor by sensor parentDeviceId: {sensor.name}')
                        break

        # 4. Check name matching heuristic (e.g. both have "garage" or similar words)
        if paired is None:
            ctrl_name_lower = self.name.lower()
            for sensor in door_sensors:
                s_name_lower = sensor.name.lower()
                if 'garage' in ctrl_name_lower and 'garage' in s_name_lower:
                    paired = sensor
                    logging.info(f'{self.name} - Matched paired sensor by name heuristic: {sensor.name}')
                    break

        # 5. If there is only one door sensor in the entire system, pair with it
        if paired is None and len(door_sensors) == 1:
            paired = door_sensors[0]
            logging.info(f'{self.name} - Exactly one door sensor found, auto-pairing with {paired.name}')

        if paired is not None:
            self.paired_sensor = paired
            if hasattr(paired, 'register_state_callback'):
                paired.register_state_callback(self.on_sensor_state_change)
            # Sync initial state if available
            initial_state = paired.doorState()
            if initial_state == 0:
                with self._state_lock:
                    self.state = STATE_CLOSED
                self.my_setDriver('ST', STATE_CLOSED)
            elif initial_state == 1:
                with self._state_lock:
                    self.state = STATE_OPEN
                self.my_setDriver('ST', STATE_OPEN)
            logging.info(f'{self.name} - Successfully paired with {paired.name}, initial state: {self.state}')

        return self.paired_sensor

    def _delayed_sensor_search(self):
        for _ in range(10):
            time.sleep(2)
            if self.find_paired_sensor() is not None:
                break

    def on_sensor_state_change(self, sensor_state):
        logging.info(f'{self.name} - Paired sensor state change: {sensor_state} (current door state: {self.state})')
        with self._state_lock:
            self.last_sensor_state = sensor_state
            if sensor_state == 0:  # Sensor Closed
                self._cancel_travel_timer()
                self._pulse_abort.set()
                if self.state != STATE_CLOSED:
                    self.state = STATE_CLOSED
                    self.my_setDriver('ST', STATE_CLOSED)
                    if self.node:
                        self.node.reportCmd('DOF')
            elif sensor_state == 1:  # Sensor Open
                if self.state == STATE_CLOSED:
                    # External opening detected! (wall switch, car remote, manual)
                    logging.info(f'{self.name} - External door opening detected via sensor')
                    self.state = STATE_OPENING
                    self.my_setDriver('ST', STATE_OPENING)
                    if self.node:
                        self.node.reportCmd('DON')
                    self._start_travel_timer(STATE_OPEN, self.travel_time)
                elif self.state == STATE_CLOSING:
                    # Safety beam or manual reverse triggered during closing
                    logging.warning(f'{self.name} - Sensor opened while closing; possible safety reverse')
                    self.state = STATE_OPENING
                    self.my_setDriver('ST', STATE_OPENING)
                    if self.node:
                        self.node.reportCmd('DON')
                    self._start_travel_timer(STATE_OPEN, self.travel_time)

    def _start_travel_timer(self, target_state, duration):
        with self._travel_timer_lock:
            if self._travel_timer is not None:
                self._travel_timer.cancel()
                self._travel_timer = None
            self._travel_timer = threading.Timer(duration, self._on_travel_timer_expired, args=[target_state])
            self._travel_timer.daemon = True
            self._travel_timer.start()

    def _cancel_travel_timer(self):
        with self._travel_timer_lock:
            if self._travel_timer is not None:
                self._travel_timer.cancel()
                self._travel_timer = None

    def _on_travel_timer_expired(self, target_state):
        logging.info(f'{self.name} - Travel timer expired, target state: {target_state}')
        with self._state_lock:
            if target_state == STATE_OPEN and self.state == STATE_OPENING:
                self.state = STATE_OPEN
                self.my_setDriver('ST', STATE_OPEN)
            elif target_state == STATE_CLOSED and self.state == STATE_CLOSING:
                if self.paired_sensor is not None:
                    sensor_state = self.paired_sensor.doorState()
                    if sensor_state == 0:
                        self.state = STATE_CLOSED
                        self.my_setDriver('ST', STATE_CLOSED)
                        if self.node:
                            self.node.reportCmd('DOF')
                    else:
                        logging.warning(f'{self.name} - Travel timer expired for closing but sensor is still open')
                        self.state = STATE_HALF_CLOSED
                        self.my_setDriver('ST', STATE_HALF_CLOSED)
                else:
                    self.state = STATE_CLOSED
                    self.my_setDriver('ST', STATE_CLOSED)
                    if self.node:
                        self.node.reportCmd('DOF')

    def _send_pulses(self, num_pulses, target_state, travel_time):
        """Executes 1 or 3 pulses in a daemon thread."""
        def _run():
            logging.info(f'{self.name} - Executing {num_pulses} pulse(s) for target state {target_state}')
            door_control = self._get_door_control('send_pulses')
            if door_control is None:
                return

            for i in range(num_pulses):
                if self._pulse_abort.is_set():
                    logging.info(f'{self.name} - Pulse sequence aborted')
                    return
                if i > 0:
                    time.sleep(1.2)
                    if self._pulse_abort.is_set():
                        return
                door_control.toggleDevice()
                logging.debug(f'{self.name} - Sent pulse {i + 1}/{num_pulses}')

            with self._state_lock:
                self.state = target_state
                self.my_setDriver('ST', target_state)
                if target_state == STATE_OPENING:
                    if self.node:
                        self.node.reportCmd('DON')
                    self._start_travel_timer(STATE_OPEN, travel_time)
                elif target_state == STATE_CLOSING:
                    if self.node:
                        self.node.reportCmd('DOF')
                    self._start_travel_timer(STATE_CLOSED, travel_time)

        with self._pulse_lock:
            self._pulse_abort.clear()
            self._pulse_thread = threading.Thread(target=_run, daemon=True)
            self._pulse_thread.start()

    def start(self):
        logging.info('start - udiYoGarageDoor')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('ST', self.state)
        self.my_setDriver('GV30', 0)
        self.yoDoorControl = YoLinkGarageDoorCtrl(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        tries = 1
        while not self.yoDoorControl.check_system_online() and tries <= 5:
            logging.info(f'Waiting for device {self.name} to come online... ({tries}/5)')
            time.sleep(min(10, 2 * tries))
            tries += 1
        if self.yoDoorControl.check_system_online():
            self.clear_offline_notice()
            self.my_setDriver('GV30', 1)
        else:
            logging.warning(f'Device {self.name} is offline at start')
            self.set_offline_notice()
            self.my_setDriver('GV30', 0)
            self.my_setDriver('GV20', 2)

        # Attempt to pair with door sensor
        if self.find_paired_sensor() is None:
            t = threading.Thread(target=self._delayed_sensor_search, daemon=True)
            t.start()

        self.start_done()

    def initNode(self):
        door_control = self._get_door_control('initNode')
        if door_control is None:
            return
        door_control.online = True

    def checkOnline(self):
        pass

    def checkDataUpdate(self):
        pass

    def updateLastTime(self):
        pass

    def stop(self):
        logging.info('Stop udiYoGarageDoor')
        self._cancel_travel_timer()
        self._pulse_abort.set()
        self.my_setDriver('GV30', 0)
        door_control = self.yoDoorControl
        if door_control is not None:
            door_control.shut_down()

    def _get_door_control(self, caller):
        if self.yoDoorControl is None:
            logging.warning(f'udiYoGarageDoor - {caller} skipped; garage door control not initialized yet')
            return None
        return self.yoDoorControl

    def updateStatus(self, data):
        logging.debug('updateStatus - udiYoGarageDoor')
        door_control = self._get_door_control('updateStatus')
        if door_control is None:
            return
        with self._update_lock:
            door_control.updateCallbackStatus(data)
            if door_control is not None:
                if door_control.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

                if door_control.check_system_online():
                    self.my_setDriver('GV30', 1)
                else:
                    self.my_setDriver('GV20', 2)
                    self.my_setDriver('GV30', 0)

    def openDoor(self, command=None):
        logging.info(f'{self.name} - openDoor called (current state: {self.state})')
        if self.paired_sensor is None:
            self.find_paired_sensor()

        with self._state_lock:
            if self.state in [STATE_OPEN, STATE_OPENING]:
                logging.info(f'{self.name} - Door is already open or opening, ignoring open command')
                return

            if self.state == STATE_HALF_OPEN:
                num_pulses = 3
            else:
                num_pulses = 1

        self._send_pulses(num_pulses, STATE_OPENING, self.travel_time)

    def closeDoor(self, command=None):
        logging.info(f'{self.name} - closeDoor called (current state: {self.state})')
        if self.paired_sensor is None:
            self.find_paired_sensor()

        with self._state_lock:
            if self.state in [STATE_CLOSED, STATE_CLOSING]:
                logging.info(f'{self.name} - Door is already closed or closing, ignoring close command')
                return

            if self.state == STATE_HALF_CLOSED:
                num_pulses = 3
            else:
                num_pulses = 1

        self._send_pulses(num_pulses, STATE_CLOSING, self.travel_time)

    def toggleDoor(self, command=None):
        logging.info(f'{self.name} - toggleDoor called (current state: {self.state})')
        if self.paired_sensor is None:
            self.find_paired_sensor()

        door_control = self._get_door_control('toggleDoor')
        if door_control is None:
            return

        self._pulse_abort.set()
        self._cancel_travel_timer()
        door_control.toggleDevice()

        with self._state_lock:
            if self.state == STATE_CLOSED:
                self.state = STATE_OPENING
                self.my_setDriver('ST', STATE_OPENING)
                if self.node:
                    self.node.reportCmd('DON')
                self._start_travel_timer(STATE_OPEN, self.travel_time)
            elif self.state == STATE_OPENING:
                self.state = STATE_HALF_OPEN
                self.my_setDriver('ST', STATE_HALF_OPEN)
            elif self.state == STATE_HALF_OPEN:
                self.state = STATE_CLOSING
                self.my_setDriver('ST', STATE_CLOSING)
                if self.node:
                    self.node.reportCmd('DOF')
                self._start_travel_timer(STATE_CLOSED, self.travel_time)
            elif self.state == STATE_OPEN:
                self.state = STATE_CLOSING
                self.my_setDriver('ST', STATE_CLOSING)
                if self.node:
                    self.node.reportCmd('DOF')
                self._start_travel_timer(STATE_CLOSED, self.travel_time)
            elif self.state == STATE_CLOSING:
                self.state = STATE_HALF_CLOSED
                self.my_setDriver('ST', STATE_HALF_CLOSED)
            elif self.state == STATE_HALF_CLOSED:
                self.state = STATE_OPENING
                self.my_setDriver('ST', STATE_OPENING)
                if self.node:
                    self.node.reportCmd('DON')
                self._start_travel_timer(STATE_OPEN, self.travel_time)
            else:  # STATE_UNKNOWN
                if self.paired_sensor and self.paired_sensor.doorState() == 0:
                    self.state = STATE_OPENING
                    self.my_setDriver('ST', STATE_OPENING)
                    if self.node:
                        self.node.reportCmd('DON')
                    self._start_travel_timer(STATE_OPEN, self.travel_time)
                elif self.paired_sensor and self.paired_sensor.doorState() == 1:
                    self.state = STATE_CLOSING
                    self.my_setDriver('ST', STATE_CLOSING)
                    if self.node:
                        self.node.reportCmd('DOF')
                    self._start_travel_timer(STATE_CLOSED, self.travel_time)
                else:
                    self.my_setDriver('ST', STATE_UNKNOWN)

    commands = {
        'DON': openDoor,
        'DOF': closeDoor,
        'TOGGLE': toggleDoor,
    }
