#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
import importlib
from os import truncate
import threading
try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom

import time
from yolinkVibrationSensorV3 import YoLinkVibrationSensor


class udiYoVibrationSensor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  save_cmd_state, retrieve_cmd_state, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names

    id = 'yovibrasens'
    
    '''
       drivers = [
            'GV0' = Vibration Alert
            'GV1' = Battery Level
            'ST' = Online
            ]

    ''' 
        
    drivers = [

            {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Vibration State (Legacy)'}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25, 'name': 'Sensor Battery Level'},
            {'driver': 'GV2', 'value': 0, 'uom': 25, 'name': 'Command Setting'},            
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25, 'name': 'Sensor Temperature'},
            {'driver': 'ST', 'value': 99, 'uom': 25, 'name': 'Vibration State'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},    
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},                   
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoVibrationSensor INIT- {}'.format(deviceInfo['name']))
        self.poly = polyglot
        self.address = address
        self.name = name
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.temp_unit = self.yoAccess.get_temp_unit()
        if self.temp_unit == 1:
            self.id = 'yovibrasensF'
        self.yoVibrationSensor  = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.last_state = 99
        self.cmd_state = self.retrieve_cmd_state()
        self.n_queue = []
        
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(self.poly.START, self.start, self.address)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        

        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True
        logging.debug(f'udiYoVibrationSensor INIT- DONE {self.id}n  {self.name} {self.address} {self.temp_unit}')


    def start(self):
        logging.info('start - udiYoVibrationSensor')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        #self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        self.yoVibrationSensor  = YoLinkVibrationSensor(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoVibrationSensor.initNode()
        #self.my_setDriver('ST', 1)
        time.sleep(1)
        tries = 1
        while not self.yoVibrationSensor.check_system_online():
            logging.info('Waiting for vibration sensor to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoVibrationSensor.refreshDevice()  
            tries += 1
        self.start_done()

    def stop (self):
        logging.info('Stop udiYoVibrationSensor')
        #self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        sensor = self._get_sensor('stop')
        if sensor is not None:            
            sensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_sensor(self, caller):
        sensor = getattr(self, 'yoVibrationSensor', None)
        if sensor is None:
            logging.warning('udiYoVibrationSensor.%s called before device initialization', caller)
        return sensor

    def checkOnline(self):
        sensor = self._get_sensor('checkOnline')
        if sensor is None:
            return
        sensor.refreshDevice()   
    
    def checkDataUpdate(self):
        sensor = self._get_sensor('checkDataUpdate')
        if sensor is None:
            return
        if sensor.data_updated():
            self.updateData()


    def updateData(self):
            sensor = self._get_sensor('updateData')
            if sensor is None:
                return
            if self.node is not None:
                while not self.node_ready or not self.system_ready or not self.configDone:
                    time.sleep(0.5)
            message_info = sensor.get_message_type()
            message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
            unix_time = sensor.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)
            if sensor.check_system_online():               
                vib_state = sensor.get_data('state', 'state')
                if vib_state in ['normal']:
                    self.my_setDriver('GV0', 0, type=message_type)
                    self.my_setDriver('ST', 0, type=message_type)
                    if self.last_state != 0 and self.cmd_state in [0, 2]:
                        self.node.reportCmd('DOF')
                        self.last_state = 0
                elif vib_state in ['alert']:
                    self.my_setDriver('GV0', 1, type=message_type)
                    self.my_setDriver('ST', 1, type=message_type)
                    if self.last_state != 1 and self.cmd_state in [0, 1]:
                        self.node.reportCmd('DON')
                        self.last_state = 1
                else:
                    self.my_setDriver('GV0', 99) 
                    self.my_setDriver('ST', 99)
                    self.last_state = 99
                self.my_setDriver('GV1', sensor.get_data( 'battery', 'state'), type=message_type)

                self.my_setDriver('GV30', 1)
                devTemp =  sensor.get_data('devTemperature', 'state')
                if devTemp != 'NA':
                    if self.temp_unit == 0:
                        self.my_setDriver('CLITEMP', round(devTemp,0), 4, type=message_type)
                    elif self.temp_unit == 1:
                        self.my_setDriver('CLITEMP', round(devTemp*9/5+32,0), 17, type=message_type)
                else:
                    self.my_setDriver('CLITEMP', 99,  25)
                if sensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                #self.my_setDriver('GV0', 99)
                #self.my_setDriver('GV1', 99)
                #self.my_setDriver('CLITEMP', 99, 25)
                #self.my_setDriver('ST', 0)
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)



    def updateStatus(self, data):
        logging.info('updateStatus - udiYoLinkVibrationSensor')
        if self.yoVibrationSensor is not None:
            with self._update_lock:
                self.yoVibrationSensor.updateStatus(data)
            self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoVibrationSensor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV2', self.cmd_state)
        self.save_cmd_state(self.cmd_state)


    def update(self, command = None):
        logging.info('udiYoVibrationSensor Update  Executed')
        sensor = self._get_sensor('update')
        if sensor is None:
            return
        sensor.refreshSensor()
       

    def noop(self, command = None):
        pass

    commands = {
                'SETCMD': set_cmd,        
                'UPDATE': update,
                }







