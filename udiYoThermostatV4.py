#!/usr/bin/env python3
"""
Polyglot v3 node server for YoLink Thermostat

Supports Thermostat.getState, setState, setECO, setProperties, setCorrection
MIT License
"""

import importlib

try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom

import time
import threading
from yolinkThermostatV2 import YoLinkThermostat


class udiYoThermostat(udi_interface.Node):
    from udiYolinkLib import my_setDriver, start_done, configDoneHandler,  node_queue, wait_for_node_done, checkNameSync

    id = 'yothermostat'

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 4},           # Current temperature (UoM 4=Celsius, 17=Fahrenheit)
        {'driver': 'CLIHCS', 'value': 99, 'uom': 66},     # Running state (UoM 66: 0=Idle, 1=Heating, 2=Cooling)
        {'driver': 'CLIHUM', 'value': 0, 'uom': 51},      # Current humidity (UoM 51=percent)
        {'driver': 'CLISPH', 'value': 0, 'uom': 4},       # Heat setpoint (UoM 4=Celsius, 17=Fahrenheit)
        {'driver': 'CLISPC', 'value': 0, 'uom': 4},       # Cool setpoint (UoM 4=Celsius, 17=Fahrenheit)
        {'driver': 'CLIMD', 'value': 99, 'uom': 67},      # Thermostat mode (UoM 67: 0=Off, 1=Heat, 2=Cool, 3=Auto)
        {'driver': 'CLIFS', 'value': 99, 'uom': 68},      # Fan setting (UoM 68: 0=Auto, 1=On)
        {'driver': 'CLISMD', 'value': 99, 'uom': 25},     # Schedule mode (UoM 25: 0=run, 1=hold)
        {'driver': 'GV0', 'value': 99, 'uom': 4},         # Sensor 1 temp (optional, UoM 4=C)
        {'driver': 'GV1', 'value': 99, 'uom': 4},         # Sensor 2 temp (optional, UoM 4=C)
        {'driver': 'GV2', 'value': 99, 'uom': 25},        # Aux heat running (UoM 25: 0=no, 1=yes)
        {'driver': 'GV3', 'value': 99, 'uom': 25},        # Second stage running (UoM 25: 0=no, 1=yes)
        {'driver': 'CLIEMD', 'value': 99, 'uom': 25},     # ECO mode (UoM 25: 0=off, 1=on)
        {'driver': 'GV18', 'value': 99, 'uom': 4},        # ECO low temp offset (Celsius)
        {'driver': 'GV19', 'value': 99, 'uom': 4},        # ECO high temp offset (Celsius)        
        {'driver': 'GV5', 'value': 99, 'uom': 25},        # DR running (UoM 25: 0=no, 1=yes)

        {'driver': 'GV20', 'value': 99, 'uom': 25},       # Suspended state (UoM 25: 0=not suspended, 1=suspended, 2=error)
        {'driver': 'GV30', 'value': 99, 'uom': 25},       # Online status (UoM 25: 0=offline, 1=online)
        {'driver': 'TIME', 'value': int(time.time()), 'uom': 151},  # Last update time (UoM 151=Unix Timestamp)
    ]

    def __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__(polyglot, primary, address, name)
        logging.debug(f'udiYoThermostat INIT - {deviceInfo["name"]}')
        
        self.poly = polyglot
        self.address = address
        self.name = name
        self.yoAccess = yoAccess
        self.devInfo = deviceInfo
        self.yoThermostat = None
        self.node_ready = False
        self.configDone = False
        self.system_ready = False
        self._update_lock = threading.Lock()
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.properties_node = None
        self.n_queue = []
        self.main_node_ready = False
        self.sub_nodes_ready = False
        
        # Set node ID based on temperature unit
        if self.temp_unit == 1:
            self.id = 'yothermostatf'  # Fahrenheit variant
        else:
            self.id = 'yothermostat'   # Celsius variant (default)

        # Subscribe to events
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)

        # Add node and wait
        self.poly.addNode(self, conn_status=None, rename=True)
        self.wait_for_node_done()

        self.node = self.poly.getNode(address)
        self.adr_list = [address]
        # Thermostat has one fixed child node created during startup.

        while not self.sub_nodes_ready:
            time.sleep(0.5)
        self.node_ready = True
        self.main_node_ready = True


    def start(self):
        """Initialize and start the thermostat device"""
        logging.info('Start udiYoThermostat')
        while not self.main_node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0)
        self.yoThermostat = YoLinkThermostat(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoThermostat.initDevice()
        time.sleep(1)
        tries = 1
        while not self.yoThermostat.check_system_online():
            logging.info('Waiting for thermostat to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoThermostat.refreshDevice()
            tries += 1

        # Create child node that owns thermostat properties and related controls.
        prop_address = self.poly.getValidAddress(f'{self.address[4:14]}_TPR'[:14])
        self.properties_node = udiYoThermostatProperties(
            self.poly,
            self.address,
            prop_address,
            f'{self.name} Properties',
            self,
        )
        self.adr_list.append(prop_address)
        self.sub_nodes_ready = True

        logging.info('Thermostat online and ready')
        self.start_done()

    def stop(self):
        """Stop the thermostat device"""
        logging.info('Stop udiYoThermostat')
        self.my_setDriver('GV30', 0)
        thermostat = self._get_thermostat('stop')
        if thermostat is not None:
            thermostat.shut_down()

    def _get_thermostat(self, caller):
        thermostat = getattr(self, 'yoThermostat', None)
        if thermostat is None:
            logging.warning('udiYoThermostat.%s called before device initialization', caller)
        return thermostat

    def updateStatus(self, data):
        """Handle MQTT status updates from the device"""
        logging.debug('udiYoThermostat - updateStatus')
        thermostat = self._get_thermostat('updateStatus')
        if thermostat is not None:
            with self._update_lock:
                thermostat.updateStatus(data)
            self.updateData()

    def updateData(self):
        """Parse device state and update drivers"""
        logging.info('udiYoThermostat - updateData')
        thermostat = self._get_thermostat('updateData')
        if thermostat is None:
            return
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)            
            message_info = thermostat.get_message_type()
            message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
            # Update timestamp
            unix_time = thermostat.get_report_time('time')
            self.my_setDriver('TIME', unix_time, 151)
            
            if thermostat.check_system_online():
                self.my_setDriver('GV30', 1)
                
                # Current readings from state
                currentTemp = thermostat.get_data('temperature', 'state')
                humidity = thermostat.get_data('humidity', 'state')
                
                # Setpoints
                lowTemp = thermostat.get_data('lowTemp', 'state')
                highTemp = thermostat.get_data('highTemp', 'state')
                
                # Operating mode
                mode = thermostat.get_data('mode', 'state')
                fan = thermostat.get_data('fan', 'state')
                sche = thermostat.get_data('sche', 'state')
                running = thermostat.get_data('running', 'state')

                # Sensors (optional)
                sensor1 = thermostat.get_data('temperature', 'sensor1')
                sensor2 = thermostat.get_data('temperature', 'sensor2')

                # Optional states in 'other'
                auxHeat = thermostat.get_data('auxiliaryHeat',  'other')
                stage2 = thermostat.get_data('secondStage', 'other')
                drRunning = thermostat.get_data('drRunning', 'other')

                # Eco mode
                eco_mode = thermostat.get_data('mode','eco')
                eco_highTemp = thermostat.get_data('highTemp','eco')
                eco_lowTemp = thermostat.get_data('lowTemp','eco')

                # Current temperature
                if isinstance(currentTemp, (int, float)):
                    if self.temp_unit == 1:  # Fahrenheit
                        self.my_setDriver('ST', round(currentTemp * 9/5 + 32, 1), 17, type=message_type)
                    else:
                        self.my_setDriver('ST', round(currentTemp, 1), 4, type=message_type)

                # Humidity
                if isinstance(humidity, (int, float)):
                    self.my_setDriver('CLIHUM', round(humidity, 1), 51, type=message_type)

                # Heat setpoint (low temp = heat setpoint)
                if isinstance(lowTemp, (int, float)):
                    if self.temp_unit == 1:
                        self.my_setDriver('CLISPH', round(lowTemp * 9/5 + 32, 1), 17, type=message_type)
                    else:
                        self.my_setDriver('CLISPH', round(lowTemp, 1), 4, type=message_type)

                # Cool setpoint (high temp = cool setpoint)
                if isinstance(highTemp, (int, float)):
                    if self.temp_unit == 1:
                        self.my_setDriver('CLISPC', round(highTemp * 9/5 + 32, 1), 17, type=message_type)
                    else:
                        self.my_setDriver('CLISPC', round(highTemp, 1), 4, type=message_type)

                # Mode: UoM 67: 0=Off, 1=Heat, 2=Cool, 3=Auto
                if mode:
                    mode_map = {'off': 0, 'heat': 1, 'cool': 2, 'auto': 3}
                    self.my_setDriver('CLIMD', mode_map.get(mode.lower(), 99), 67, type=message_type)

                # Fan setting: UoM 68: 0=Auto, 1=On
                if fan:
                    fan_map = {'auto': 0, 'on': 1}
                    self.my_setDriver('CLIFS', fan_map.get(fan.lower(), 99), 68, type=message_type)

                # Schedule mode: 0=run, 1=hold
                if sche:
                    sche_map = {'run': 0, 'hold': 1}
                    self.my_setDriver('CLISMD', sche_map.get(sche.lower(), 99), 25, type=message_type)

                # Running state: UoM 66: 0=Idle, 1=Heating, 2=Cooling
                if running:
                    running_map = {'idle': 0, 'heat': 1, 'cool': 2}
                    self.my_setDriver('CLIHCS', running_map.get(running.lower(), 99), 66, type=message_type)

                # Optional sensors
                if isinstance(sensor1, (int, float)):
                    if sensor1<=-100 or sensor1>=200:  # Invalid reading, set to error value
                        self.my_setDriver('GV0', 99, 25, type=message_type)
                    else:
                        if self.temp_unit == 1:
                            self.my_setDriver('GV0', round(sensor1 * 9/5 + 32, 1), 17, type=message_type)
                        else:
                            self.my_setDriver('GV0', round(sensor1, 1), 4, type=message_type)

                if isinstance(sensor2, (int, float)):
                    if sensor2<=-100 or sensor2>=200:  # Invalid reading, set to error value
                        self.my_setDriver('GV1', 99, 25, type=message_type)
                    else:
                        if self.temp_unit == 1:
                            self.my_setDriver('GV1', round(sensor2 * 9/5 + 32, 1), 17, type=message_type)
                        else:
                            self.my_setDriver('GV1', round(sensor2, 1), 4, type=message_type)

                # Optional other states (UoM 25 = index)
                if auxHeat is not None:
                    self.my_setDriver('GV2', 1 if auxHeat else 0, 25, type=message_type)
                if stage2 is not None:
                    self.my_setDriver('GV3', 1 if stage2 else 0, 25, type=message_type)

                # ECO mode (UoM 25 = index)
                logging.debug(f'Parsing ECO data: mode={eco_mode}, low={eco_lowTemp}, high={eco_highTemp}')
                if eco_mode and isinstance(eco_mode, str):
                    self.my_setDriver('CLIEMD', 1 if eco_mode.lower() == 'on' else 0, 25, type=message_type)

                if eco_lowTemp is not None and isinstance(eco_lowTemp, (int, float)):
                    if self.temp_unit == 1:
                        self.my_setDriver('GV18', round(eco_lowTemp * 9/5, 1), 17, type=message_type)
                    else:
                        self.my_setDriver('GV18', round(eco_lowTemp, 1), 4, type=message_type)

                if eco_highTemp is not None and isinstance(eco_highTemp, (int, float)):
                    if self.temp_unit == 1:
                        self.my_setDriver('GV19', round(eco_highTemp * 9/5, 1), 17, type=message_type)
                    else:
                        self.my_setDriver('GV19', round(eco_highTemp, 1), 4, type=message_type)

                # DR running state (UoM 25: 0=no, 1=yes)
                if drRunning is not None:
                    self.my_setDriver('GV5', 1 if drRunning else 0, 25, type=message_type)

                # Properties
                properties = thermostat.get_data('properties')
                if not isinstance(properties, dict):
                    properties = thermostat.get_data('properties', 'state')
                logging.debug(f'Parsing properties data: {properties}')
                if properties and isinstance(properties, dict) and self.properties_node is not None:
                    self.properties_node.updateProperties(properties, message_type)

                # Suspended state check
                if thermostat.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)

    def update(self, command=None):
        """Refresh device state"""
        logging.info('udiYoThermostat update')
        thermostat = self._get_thermostat('update')
        if thermostat is not None:
            thermostat.refreshDevice()

    def setLowTemp(self, command):
        """Set low temperature setpoint"""
        try:
            temp = float(command.get('value'))
            # Convert from Fahrenheit to Celsius if needed (API expects Celsius)
            if self.temp_unit == 1:
                temp_celsius = round((temp - 32) * 5/9, 1)
                logging.info(f'udiYoThermostat setLowTemp - {temp}°F ({temp_celsius}°C)')
                thermostat = self._get_thermostat('setLowTemp')
                if thermostat is not None:
                    thermostat.setLowTemp(temp_celsius)
            else:
                logging.info(f'udiYoThermostat setLowTemp - {temp}°C')
                thermostat = self._get_thermostat('setLowTemp')
                if thermostat is not None:
                    thermostat.setLowTemp(temp)
        except (ValueError, TypeError) as e:
            logging.error(f'setLowTemp invalid value: {e}')

    def setHighTemp(self, command):
        """Set high temperature setpoint"""
        try:
            temp = float(command.get('value'))
            # Convert from Fahrenheit to Celsius if needed (API expects Celsius)
            if self.temp_unit == 1:
                temp_celsius = round((temp - 32) * 5/9, 1)
                logging.info(f'udiYoThermostat setHighTemp - {temp}°F ({temp_celsius}°C)')
                thermostat = self._get_thermostat('setHighTemp')
                if thermostat is not None:
                    thermostat.setHighTemp(temp_celsius)
            else:
                logging.info(f'udiYoThermostat setHighTemp - {temp}°C')
                thermostat = self._get_thermostat('setHighTemp')
                if thermostat is not None:
                    thermostat.setHighTemp(temp)
        except (ValueError, TypeError) as e:
            logging.error(f'setHighTemp invalid value: {e}')

    def setMode(self, command):
        """Set operating mode (UoM 67: 0=Off, 1=Heat, 2=Cool, 3=Auto)"""
        try:
            mode_val = int(command.get('value'))
            mode_map = {0: 'off', 1: 'heat', 2: 'cool', 3: 'auto'}
            mode = mode_map.get(mode_val, 'off')
            logging.info(f'udiYoThermostat setMode - {mode}')
            thermostat = self._get_thermostat('setMode')
            if thermostat is not None:
                thermostat.setMode(mode)
        except (ValueError, TypeError) as e:
            logging.error(f'setMode invalid value: {e}')

    def setFan(self, command):
        """Set fan mode (UoM 68: 0=Auto, 1=On)"""
        try:
            fan_val = int(command.get('value'))
            fan_map = {0: 'auto', 1: 'on'}
            fan = fan_map.get(fan_val, 'auto')
            logging.info(f'udiYoThermostat setFan - {fan}')
            thermostat = self._get_thermostat('setFan')
            if thermostat is not None:
                thermostat.setFan(fan)
        except (ValueError, TypeError) as e:
            logging.error(f'setFan invalid value: {e}')

    def setScheduleMode(self, command):
        """Set schedule mode (run/hold)"""
        try:
            sche_val = int(command.get('value'))
            sche_map = {0: 'run', 1: 'hold'}
            sche = sche_map.get(sche_val, 'run')
            logging.info(f'udiYoThermostat setScheduleMode - {sche}')
            thermostat = self._get_thermostat('setScheduleMode')
            if thermostat is not None:
                thermostat.setScheduleMode(sche)
        except (ValueError, TypeError) as e:
            logging.error(f'setScheduleMode invalid value: {e}')

    def setEco(self, command):
        """Set ECO mode and optional low/high ECO offsets."""
        try:
            query = command.get('query') or {}

            # Parse ECO mode from query first (3-parameter nodedef), fallback to value.
            eco_raw = None
            for key in query:
                if key.lower().startswith('ecomode'):
                    eco_raw = query.get(key)
                    break
            if eco_raw is None:
                eco_raw = command.get('value')

            eco_mode = None
            if eco_raw is not None:
                eco_str = str(eco_raw).strip().lower()
                if eco_str in ['on', 'off']:
                    eco_mode = eco_str
                else:
                    eco_mode = 'on' if int(float(eco_raw)) == 1 else 'off'

            # Parse optional low/high ECO adjustments from query payload.
            eco_low = None
            eco_high = None
            for key, raw in query.items():
                key_l = key.lower()
                if key_l.startswith('ecolow'):
                    eco_low = float(raw)
                elif key_l.startswith('ecohigh'):
                    eco_high = float(raw)

            # API expects Celsius values; these are relative offsets, not absolute temps.
            if self.temp_unit == 1:
                if eco_low is not None:
                    eco_low = round(eco_low * 5 / 9, 1)
                if eco_high is not None:
                    eco_high = round(eco_high * 5 / 9, 1)

            logging.info(f'udiYoThermostat setEco - mode={eco_mode}, low={eco_low}, high={eco_high}')
            thermostat = self._get_thermostat('setEco')
            if thermostat is not None:
                thermostat.setECO(mode=eco_mode, lowTemp=eco_low, highTemp=eco_high)
        except (ValueError, TypeError) as e:
            logging.error(f'setEco invalid value: {e} | command={command}')

    commands = {
        'UPDATE': update,
        'SETHEATTEMP': setLowTemp,
        'SETCOOLTEMP': setHighTemp,
        'SETMODE': setMode,
        'SETFAN': setFan,
        'SETSCHE': setScheduleMode,
        'SETECO': setEco,
    }


class udiYoThermostatProperties(udi_interface.Node):
    from udiYolinkLib import my_setDriver, node_queue, wait_for_node_done, checkNameSync

    id = 'yothermprop'

    drivers = [
        {'driver': 'GV6', 'value': 99, 'uom': 44},        # minRuntime (minutes)
        {'driver': 'GV7', 'value': 99, 'uom': 4},         # coolLimit (Celsius)
        {'driver': 'GV8', 'value': 99, 'uom': 4},         # heatLimit (Celsius)
        {'driver': 'GV9', 'value': 99, 'uom': 25},        # mute (0=no, 1=yes)
        {'driver': 'GV10', 'value': 99, 'uom': 25},       # menuLock (0=no, 1=yes)
        {'driver': 'GV11', 'value': 99, 'uom': 44},       # auxStandby (minutes)
        {'driver': 'GV12', 'value': 99, 'uom': 20},       # auxMaxSpan (hours)
        {'driver': 'GV13', 'value': 99, 'uom': 4},        # auxThreshold (Celsius)
        {'driver': 'GV14', 'value': 99, 'uom': 44},       # stage2Standby (minutes)
        {'driver': 'GV15', 'value': 99, 'uom': 20},       # stage2MaxSpan (hours)
        {'driver': 'GV16', 'value': 99, 'uom': 4},        # stage2Threshold (Celsius)
        {'driver': 'GV17', 'value': 99, 'uom': 25},       # master temp source (0=local, 1=sensor1, 2=sensor2)
    ]

    def __init__(self, polyglot, primary, address, name, thermostat_node):
        super().__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.parent_node = thermostat_node
        self.temp_unit = thermostat_node.temp_unit
        self.node_ready = False
        self.n_queue = []

        if self.temp_unit == 1:
            self.id = 'yothermpropf'

        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.addNode(self, conn_status=None, rename=True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.node_ready = True

    def _yo(self):
        yo = self.parent_node.yoThermostat if self.parent_node else None
        if yo is None:
            logging.warning('udiYoThermostatProperties called before thermostat initialization')
        return yo

    def updateProperties(self, properties, message_type=None):
        if not isinstance(properties, dict):
            return

        minRuntime = properties.get('minRuntime')
        if isinstance(minRuntime, (int, float)):
            self.my_setDriver('GV6', int(minRuntime), 44, type=message_type)

        coolLimit = properties.get('coolLimit')
        if isinstance(coolLimit, (int, float)):
            if self.temp_unit == 1:
                self.my_setDriver('GV7', round(coolLimit * 9/5 + 32, 1), 17, type=message_type)
            else:
                self.my_setDriver('GV7', round(coolLimit, 1), 4, type=message_type)

        heatLimit = properties.get('heatLimit')
        if isinstance(heatLimit, (int, float)):
            if self.temp_unit == 1:
                self.my_setDriver('GV8', round(heatLimit * 9/5 + 32, 1), 17, type=message_type)
            else:
                self.my_setDriver('GV8', round(heatLimit, 1), 4, type=message_type)

        mute = properties.get('mute')
        if mute is not None:
            self.my_setDriver('GV9', 1 if mute else 0, 25, type=message_type)

        menuLock = properties.get('menuLock')
        if menuLock is not None:
            self.my_setDriver('GV10', 1 if menuLock else 0, 25, type=message_type)

        auxStandby = properties.get('auxStandby')
        if isinstance(auxStandby, (int, float)):
            self.my_setDriver('GV11', int(auxStandby), 44, type=message_type)

        auxMaxSpan = properties.get('auxMaxSpan')
        if isinstance(auxMaxSpan, (int, float)):
            self.my_setDriver('GV12', int(auxMaxSpan), 20, type=message_type)

        auxThreshold = properties.get('auxThreshold')
        if isinstance(auxThreshold, (int, float)):
            if self.temp_unit == 1:
                self.my_setDriver('GV13', round(auxThreshold * 9/5 + 32, 1), 17, type=message_type)
            else:
                self.my_setDriver('GV13', round(auxThreshold, 1), 4, type=message_type)

        stage2Standby = properties.get('stage2Standby')
        if isinstance(stage2Standby, (int, float)):
            self.my_setDriver('GV14', int(stage2Standby), 44, type=message_type)

        stage2MaxSpan = properties.get('stage2MaxSpan')
        if isinstance(stage2MaxSpan, (int, float)):
            self.my_setDriver('GV15', int(stage2MaxSpan), 20, type=message_type)

        stage2Threshold = properties.get('stage2Threshold')
        if isinstance(stage2Threshold, (int, float)):
            if self.temp_unit == 1:
                self.my_setDriver('GV16', round(stage2Threshold * 9/5 + 32, 1), 17, type=message_type)
            else:
                self.my_setDriver('GV16', round(stage2Threshold, 1), 4, type=message_type)

        master = properties.get('master')
        if master:
            master_map = {'local': 0, 'sensor1': 1, 'sensor2': 2}
            self.my_setDriver('GV17', master_map.get(str(master).lower(), 99), 25, type=message_type)

    def update(self, command=None):
        yo = self._yo()
        if yo:
            yo.refreshDevice()

    def setMinRuntime(self, command):
        try:
            minutes = int(command.get('value'))
            yo = self._yo()
            if yo:
                yo.setProperties(minRuntime=minutes)
        except (ValueError, TypeError) as e:
            logging.error(f'setMinRuntime invalid value: {e}')

    def setCoolLimit(self, command):
        try:
            temp = float(command.get('value'))
            yo = self._yo()
            if yo:
                if self.temp_unit == 1:
                    temp = round((temp - 32) * 5/9, 1)
                yo.setProperties(coolLimit=temp)
        except (ValueError, TypeError) as e:
            logging.error(f'setCoolLimit invalid value: {e}')

    def setHeatLimit(self, command):
        try:
            temp = float(command.get('value'))
            yo = self._yo()
            if yo:
                if self.temp_unit == 1:
                    temp = round((temp - 32) * 5/9, 1)
                yo.setProperties(heatLimit=temp)
        except (ValueError, TypeError) as e:
            logging.error(f'setHeatLimit invalid value: {e}')

    def setMute(self, command):
        try:
            mute_val = int(command.get('value'))
            yo = self._yo()
            if yo:
                yo.setProperties(mute=(mute_val == 1))
        except (ValueError, TypeError) as e:
            logging.error(f'setMute invalid value: {e}')

    def setMenuLock(self, command):
        try:
            lock_val = int(command.get('value'))
            yo = self._yo()
            if yo:
                yo.setProperties(menuLock=(lock_val == 1))
        except (ValueError, TypeError) as e:
            logging.error(f'setMenuLock invalid value: {e}')

    def setMaster(self, command):
        try:
            master_val = int(command.get('value'))
            master_map = {0: 'local', 1: 'sensor1', 2: 'sensor2'}
            yo = self._yo()
            if yo:
                yo.setProperties(master=master_map.get(master_val, 'local'))
        except (ValueError, TypeError) as e:
            logging.error(f'setMaster invalid value: {e}')

    commands = {
        'UPDATE': update,
        'SETMINRUNTIME': setMinRuntime,
        'SETCOOLLIMIT': setCoolLimit,
        'SETHEATLIMIT': setHeatLimit,
        'SETMUTE': setMute,
        'SETMENULOCK': setMenuLock,
        'SETMASTER': setMaster,
    }





