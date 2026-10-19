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

from yolinkMotionSensorV3 import YoLinkMotionSensor



class udiYoMotionSensor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  save_cmd_state, retrieve_cmd_state, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names

    id = 'yomotionsens'
    
    '''
       drivers = [
            'GV0' = Motion Alert
            'GV1' = Battery Level
            'GV2' = Command Setting

            'ST' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Motion State (Legacy)'}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25, 'name': 'Sensor Battery Level'}, 
            {'driver': 'GV2', 'value': 0, 'uom': 25, 'name': 'Command Setting'},      
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25, 'name': 'Sensor Temperature'},
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Motion State'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},
            ]
    



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('YoLinkMotionSensor INIT- {}'.format(deviceInfo['name']))
        self.address = address
        self.name = name
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo

        self.temp_unit = self.yoAccess.get_temp_unit()           

        self.yoMotionsSensor  = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.cmd_state = self.retrieve_cmd_state()
        self.last_state = 99        
        self.n_queue = []
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        

        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True


    def start(self):
        logging.info('start - udiYoLinkMotionSensor')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0)
        self.yoMotionsSensor  = YoLinkMotionSensor(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoMotionsSensor.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoMotionsSensor.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoMotionsSensor.refreshDevice()    
            tries += 1
        #self.my_setDriver('GV30', 1)
        self.start_done()

    def stop (self):
        logging.info('Stop udiYoMotionSensor')
        self.my_setDriver('GV30', 0)
        sensor = self._get_sensor('stop')
        if sensor is not None:
            sensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_sensor(self, caller):
        sensor = getattr(self, 'yoMotionsSensor', None)
        if sensor is None:
            logging.warning('udiYoMotionSensor.%s called before device initialization', caller)
        return sensor
                
    def checkOnline(self):
        sensor = self._get_sensor('checkOnline')
        if sensor is None:
            return
        sensor.refreshDevice()

    

    def getMotionState(self):
        sensor = self._get_sensor('getMotionState')
        if sensor is None:
            return None
        if sensor.check_system_online():
            if  sensor.get_data('state', 'state') in ['normal']:
                return(0)
            else:
                return(1)
        else:
            return(None)

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
                logging.debug('Motion sensor CMD setting: {}'.format(self.cmd_state))
                motion_state = sensor.get_data('state', 'state')
                if motion_state in ['normal']:
                    self.my_setDriver('GV0', 0, type=message_type)
                    self.my_setDriver('ST', 0, type=message_type)
                    if self.last_state != 0 and self.cmd_state in [0, 2]:
                        self.node.reportCmd('DOF')
                        self.last_state = 0
                elif motion_state in ['alert']:
                    self.my_setDriver('GV0', 1, type=message_type)
                    self.my_setDriver('ST', 1, type=message_type)
                    if self.last_state != 1 and self.cmd_state in [0, 1]:
                        self.node.reportCmd('DON')
                        self.last_state = 1
                else:
                    self.my_setDriver('GV0', 99)
                    self.my_setDriver('ST', 99)
                    self.last_state = 99

                self.my_setDriver('GV1', sensor.get_data('battery', 'state'), type=message_type)
                self.my_setDriver('GV2', self.cmd_state)
                self.my_setDriver('GV30', 1)
                devTemp =  sensor.get_data('devTemperature', 'state')
                if devTemp != None:
                    if self.temp_unit == 0:
                        self.my_setDriver('CLITEMP', round(devTemp,0), 4, type=message_type)
                    elif self.temp_unit == 1:
                        self.my_setDriver('CLITEMP', round(devTemp*9/5+32,0), 17, type=message_type)
                    #elif self.temp_unit == 2:
                    #    self.my_setDriver('CLITEMP', round(devTemp+273.15,0), 26)
                else:
                    self.my_setDriver('CLITEMP', 99, 25)
                if sensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)         
            else:

                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)       




    def updateStatus(self, data):
        logging.info('updateStatus - udiYoLinkMotionSensor')
        if self.yoMotionsSensor is not None:
            with self._update_lock:
                self.yoMotionsSensor.updateStatus(data)
            self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoMotionSensor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV2', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('udiYoMotionSensor Update  Executed')
        sensor = self._get_sensor('update')
        if sensor is None:
            return
        sensor.refreshDevice()
       

    def noop(self, command = None):
        pass

    commands = {
                'SETCMD': set_cmd,
                'UPDATE': update,
    
                #'DON'   : noop,
                #'DOF'   : noop
                }






