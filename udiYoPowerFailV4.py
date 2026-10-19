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
from yolinkPowerFailV3 import YoLinkPowerFailSensor



class udiYoPowerFailSenor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  save_cmd_state, retrieve_cmd_state, bool2ISY, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names

    id = 'yopwralarm'
    
    '''
       drivers = [
            'GV0' = Power Failure Alert
            'GV1' = Battery Level
            'GV2' = AlertState
            'GV3' = Powered
            'GV4' = Muted
                        
            'ST' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Unit State (Legacy)'}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25, 'name': 'Battery Level'}, 
            {'driver': 'GV2', 'value': 99, 'uom': 25, 'name': 'Alert Pending'}, 
            {'driver': 'GV3', 'value': 99, 'uom': 25, 'name': 'Power on Unit'}, 
            {'driver': 'GV4', 'value': 99, 'uom': 25, 'name': 'Muted'}, 
            {'driver': 'GV7', 'value': 0, 'uom': 25, 'name': 'Command Setting'},      
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Unit State'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'}, 
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, bool2ISY
        logging.debug('udiYoPowerFailSenor INIT- {}'.format(deviceInfo['name']))
        self.poly = polyglot
        self.address = address
        self.name = name
        self.adress = address
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoPowerFail = None
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
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        

        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        #self.my_setDriver('GV30', 0)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True


    def start(self):
        logging.info('start - udiYoPowerFailSenor')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0)
        self.yoPowerFail  = YoLinkPowerFailSensor(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoPowerFail.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoPowerFail.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoPowerFail.refreshDevice()
            tries += 1
        #self.my_setDriver('GV30', 1)
        self.start_done()

    def stop (self):
        logging.info('Stop udiYoPowerFailSenor')
        self.my_setDriver('GV30', 0)
        sensor = self._get_sensor('stop')
        if sensor is not None:
            sensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_sensor(self, caller):
        sensor = getattr(self, 'yoPowerFail', None)
        if sensor is None:
            logging.warning('udiYoPowerFailSenor.%s called before device initialization', caller)
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
        alert_state = ['normal', 'alert', 'off']
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
                state = sensor.get_data('state', 'state')
                logging.debug('state GV0 : {}'.format(state))
                if state in alert_state:    
                    state_val = alert_state.index(state) 
                    self.my_setDriver('GV0', state_val, type=message_type)
                    self.my_setDriver('ST', state_val, type=message_type)
                    if state_val != self.last_state:
                        if state_val == 1 and self.cmd_state in [0, 1]:
                            self.node.reportCmd('DON')
                        elif state_val == 0 and self.cmd_state in [0, 2]:
                            self.node.reportCmd('DOF')
                    self.last_state = state_val
                else:
                    self.my_setDriver('GV0', 99, type=message_type)
                    self.my_setDriver('ST', 99, type=message_type)
                    self.last_state = 99
                self.my_setDriver('GV1', sensor.get_data('battery', 'state'))
                alert = sensor.get_data('alertType', 'state')
                logging.debug('AlertState GV2 : {}'.format(alert))
                self.my_setDriver('GV2', alert, type=message_type)
                powered = sensor.get_data('powerSupply', 'state')
                logging.debug('Powered  GV3 : {}'.format(powered))
                self.my_setDriver('GV3', self.bool2ISY(powered), type=message_type)
                muted = sensor.get_data('mute', 'state')
                logging.debug('Muted GV4 : {}'.format(muted))
                self.my_setDriver('GV4', self.bool2ISY(muted), type=message_type)
                self.my_setDriver('GV30', 1)
                if sensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:

                self.my_setDriver('GV30', 1)
                self.my_setDriver('GV20', 2)



    def getPowerSupplyState(self):
        logging.debug('getPowerSupplyState')




    def updateStatus(self, data):
        logging.info('updateStatus - udiYoPowerFailSenor')
        sensor = self._get_sensor('updateStatus')
        if sensor is not None:
            with self._update_lock:
                sensor.updateStatus(data)
            self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoPowerFailSenor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV7', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

        
    def update(self, command = None):
        logging.info('udiYoPowerFailSenor Update  Executed')
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







