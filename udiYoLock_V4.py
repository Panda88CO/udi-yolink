#!/usr/bin/env python3
"""
MIT License
"""

import importlib

try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom

from ctypes import set_errno
from os import truncate
import threading
#import udi_interface
#import sys
import time
from yolinkLockV3 import YoLinkLock



class udiYoLockV2(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  save_cmd_state, retrieve_cmd_state, bool2ISY, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key, checkNameSync, apply_profile_driver_names

    id = 'yolockv2'
    '''
       drivers = [
            'GV0' = LockState
            'GV1' = Battery
            'GV2' = DoorBell
            'ST' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Lock State (legacy)'},
            {'driver': 'GV1', 'value': 0, 'uom': 25, 'name': 'Battery Level'}, 
            {'driver': 'GV2', 'value': 0, 'uom': 25, 'name': 'Doorbell Active'}, 
            {'driver': 'GV3', 'value': 98, 'uom': 25, 'name': 'Door State'},
            {'driver': 'GV4', 'value': 0, 'uom': 25, 'name': 'Lock Action'}, 
            {'driver': 'GV5', 'value': 98, 'uom': 25, 'name': 'Source'},            
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Lock State'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},            
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoLock INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.n_queue = []   
        
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoLock = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.last_state = ''
        self._last_reported_lock_state = None
        self.powerSupported = True # assume
        if deviceInfo.get('type') in ['LockV2']:
            self.isLockV2 = True
        
        self.poly = polyglot


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




    def start(self):
        logging.info('start - YoLinkLock')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.yoLock  = YoLinkLock(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoLock.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoLock.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoLock.refreshDevice()
            tries += 1
        self.my_setDriver('GV30', 1)
        self.start_done()

    def stop (self):
        logging.info('Stop udiYoLock')
        self.my_setDriver('GV30', 0)
        lock = self.yoLock
        if lock is not None:
            lock.shut_down()

    def _get_lock(self, caller):
        if self.yoLock is None:
            logging.warning(f'udiYoLockV2 - {caller} skipped; lock not initialized yet')
            return None
        return self.yoLock

    def checkDataUpdate(self):
        lock = self._get_lock('checkDataUpdate')
        if lock is None:
            return
        if lock.data_updated():
            self.updateData()

    def get_alerts(self):
        lock = self._get_lock('get_alerts')
        if lock is None:
            return None, {}
        type = None
        info = {}
        #alert_info = self.yoLockget_data('alert')
        #if isinstance(alert_info, dict):
        type = lock.get_data('type','alert')
        info = lock.get_data('source','alert')

        return type, info

    def source2ISY(self, source) -> int:
        if source in ['Password']:
            return 0
        elif source in ['Manual']:
            return 1
        elif source in ['Key']:
            return 2
        elif source in['AutoLock', 'Automatic']:
            return 3
        elif source in ['Fingerprint']:
            return 4
        else:
            return 99            

    def _normalize_lock_state(self, state):
        state_str = str(state).lower()
        if state_str in ['lock', 'locked']:
            return 'locked'
        if state_str in ['unlock', 'unlocked']:
            return 'unlocked'
        return None

    def _report_lock_state_change(self, state):
        normalized_state = self._normalize_lock_state(state)
        if normalized_state is None:
            return
        # Prime baseline on first status read; only emit on subsequent transitions.
        if self._last_reported_lock_state is None:
            self._last_reported_lock_state = normalized_state
            return
        if self._last_reported_lock_state == normalized_state:
            return
        if normalized_state == 'locked':
            self.node.reportCmd('DON')
        elif normalized_state == 'unlocked':
            self.node.reportCmd('DOF')
        self._last_reported_lock_state = normalized_state

    def updateData(self):
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)
            lock = self._get_lock('updateData')
            if lock is None:
                return
            message_info = lock.get_message_type()
            if not isinstance(message_info, tuple) or len(message_info) != 2:
                return
            message_type = message_info[0]
            message_action = message_info[1] # if event some data may not be updated 
            unix_time = lock.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)

            if  lock.check_system_online():
                state = str(lock.get_data('lock','state'))
                logging.debug('LockV2 state: {}'.format(state))
                if state in ['lock','locked'] :
                    self.my_setDriver('GV0', 1, type=message_type)
                    self.my_setDriver('ST', 1, type=message_type)
                elif state in ['unlock', 'unlocked']: 
                    self.my_setDriver('GV0', 0, type=message_type)
                    self.my_setDriver('ST', 0, type=message_type    )
                else:
                    self.my_setDriver('GV0', 99)
                    self.my_setDriver('ST', 99)

                self.last_state = state
                self._report_lock_state_change(state)
                battery = lock.get_data('battery')
                self.my_setDriver('GV1', battery, type=message_type)
                #bell = self.yoLock.getDoorBellRing()
                door_state = lock.get_data('door', 'state')
                if door_state in ['closed']:
                    self.my_setDriver('GV3', 0)
                elif  door_state in ['open']:
                    self.my_setDriver('GV3', 1)
                else:
                    self.my_setDriver('GV3', 99, type=message_type)
                self.my_setDriver('GV30', 1)                
  

                alert_type, source = self.get_alerts()   
                lock_list = ['Lock','Unlock','LockFailed','UnLockFailed']             
                if alert_type is None:
                    logging.debug('No alert')
                elif alert_type in ['doorbell', 'bell', 'DoorBell']:
                    logging.debug('Doorbell rung')
                    self.my_setDriver('GV2', 1, type=message_type)
                elif alert_type in lock_list:
                    logging.debug('Lock/Unlock event')          
                    self.my_setDriver('GV4', lock_list.index(alert_type), type=message_type)
                    if isinstance(source, str):
                        self.my_setDriver('GV5', self.source2ISY(source), type=message_type) 
                else:
                    logging.debug('Unknown alert type: {}'.format(alert_type))
                #self.my_setDriver('GV2', self.bool2ISY(self.yoLock.getDoorBellRing()), type=message_type)

                #doorstate = self.yoLock.getDoorState()

                if lock.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)
            



    def updateStatus(self, data):
        logging.info('udiYoLock updateStatus')
        if self.yoLock is not None:
            with self._update_lock:
                self.yoLock.updateStatus(data)
            self.updateData()



    
    def checkOnline(self):
        lock = self._get_lock('checkOnline')
        if lock is None:
            return
        lock.refreshDevice()


    def set_lock(self, command = None):
        logging.info('udiYoLock set_lock')
        lock = self._get_lock('set_lock')
        if lock is None:
            return
        lock.setState('LOCK')

    def set_unlock(self, command = None):
        logging.info('udiYoLock set_unlock')
        lock = self._get_lock('set_unlock')
        if lock is None:
            return
        lock.setState('UNLOCK')

    def lockControl(self, command):
        lock = self._get_lock('lockControl')
        if lock is None:
            return
        ctrl = int(command.get('value'))
        logging.info('udiYoLock lockControl - {}'.format(ctrl))
        if ctrl == 1:
            lock.setState('LOCK')
        elif ctrl == 0:
            lock.setState('UNLOCK')


        
    def update(self, command = None):
        logging.info('Update Status Executed')
        lock = self._get_lock('update')
        if lock is None:
            return
        lock.refreshDevice()
        
 


    commands = {
                'UPDATE' : update,
                'LOCK'   : set_lock,
                'UNLOCK' : set_unlock,
                'LOCKCTRL' : lockControl, 

                }


class udiYoLock(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler, save_cmd_state, retrieve_cmd_state, bool2ISY, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key, checkNameSync, apply_profile_driver_names

    id = 'yolock'
    '''
       drivers = [
            'GV0' = LockState
            'GV1' = Battery
            'GV2' = DoorBell
            'ST' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Lock State (legacy)'},
            {'driver': 'GV1', 'value': 0, 'uom': 25, 'name': 'Battery Level'}, 
            #{'driver': 'GV2', 'value': 0, 'uom': 25}, 
            {'driver': 'GV3', 'value': 98, 'uom': 25, 'name': 'Door State'},
            #{'driver': 'GV4', 'value': 0, 'uom': 25}, 
            #{'driver': 'GV5', 'value': 98, 'uom': 25},            
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Lock State'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},            
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoLock INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.n_queue = []   
        
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoLock = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.last_state = ''
        self._last_reported_lock_state = None
        self.powerSupported = True # assume
        if deviceInfo.get('type') in ['LockV2']:
            self.isLockV2 = True
        
        self.poly = polyglot


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



    def start(self):
        logging.info('start - YoLinkLock')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.yoLock  = YoLinkLock(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoLock.initNode()
        tries = 1
        while not self.yoLock.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(2 * tries, 60))
            tries += 1
        self.my_setDriver('GV30', 1)
        self.system_ready=True

    def stop (self):
        logging.info('Stop udiYoLock')
        self.my_setDriver('GV30', 0)
        lock = self.yoLock
        if lock is not None:
            lock.shut_down()

    def _get_lock(self, caller):
        if self.yoLock is None:
            logging.warning(f'udiYoLock - {caller} skipped; lock not initialized yet')
            return None
        return self.yoLock

    def checkDataUpdate(self):
        lock = self._get_lock('checkDataUpdate')
        if lock is None:
            return
        if lock.data_updated():
            self.updateData()

    def _normalize_lock_state(self, state):
        state_str = str(state).lower()
        if state_str in ['lock', 'locked']:
            return 'locked'
        if state_str in ['unlock', 'unlocked']:
            return 'unlocked'
        return None

    def _report_lock_state_change(self, state):
        normalized_state = self._normalize_lock_state(state)
        if normalized_state is None:
            return
        # Prime baseline on first status read; only emit on subsequent transitions.
        if self._last_reported_lock_state is None:
            self._last_reported_lock_state = normalized_state
            return
        if self._last_reported_lock_state == normalized_state:
            return
        if normalized_state == 'locked':
            self.node.reportCmd('DON')
        elif normalized_state == 'unlocked':
            self.node.reportCmd('DOF')
        self._last_reported_lock_state = normalized_state

 

    def updateData(self):
        if self.node is not None:
            while not self.node_ready or not self.system_ready:
                time.sleep(0.5)
            lock = self._get_lock('updateData')
            if lock is None:
                return
            message_info = lock.get_message_type()
            if not isinstance(message_info, tuple) or len(message_info) != 2:
                return
            message_type = message_info[0]
            message_action = message_info[1] # if event some data may not be updated 
            unix_time = lock.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)

            if  lock.check_system_online():
                state = str(lock.get_data('state', 'state'))
                logging.debug('Lock state: {}'.format(state))
                if state in ['lock','locked'] :
                    self.my_setDriver('GV0', 1, type=message_type)
                    self.my_setDriver('ST', 1, type=message_type)
                elif state in ['unlock', 'unlocked']: 
                    self.my_setDriver('GV0', 0, type=message_type)
                    self.my_setDriver('ST', 0, type=message_type    )
                else:
                    self.my_setDriver('GV0', 99)
                    self.my_setDriver('ST', 99)

                self.last_state = state
                self._report_lock_state_change(state)
                battery = lock.get_data('battery', 'state')
                self.my_setDriver('GV1', battery, type=message_type)
                #bell = self.yoLock.getDoorBellRing()
                door_state = lock.get_data('door', 'state')
                if door_state in ['closed']:
                    self.my_setDriver('GV3', 0)
                elif  door_state in ['open']:
                    self.my_setDriver('GV3', 1)
                else:
                    self.my_setDriver('GV3', 99, type=message_type)
                self.my_setDriver('GV30', 1)                
  


                if lock.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)
            



    def updateStatus(self, data):
        logging.info('udiYoLock updateStatus')
        lock = self._get_lock('updateStatus')
        if lock is None:
            return
        with self._update_lock:
            lock.updateStatus(data)
        self.updateData()



    
    def checkOnline(self):
        lock = self._get_lock('checkOnline')
        if lock is None:
            return
        lock.refreshDevice()


    def set_lock(self, command = None):
        logging.info('udiYoLock set_lock')
        lock = self._get_lock('set_lock')
        if lock is None:
            return
        lock.setState('LOCK')

    def set_unlock(self, command = None):
        logging.info('udiYoLock set_outlet_off')
        lock = self._get_lock('set_unlock')
        if lock is None:
            return
        lock.setState('UNLOCK')



    def lockControl(self, command):
        lock = self._get_lock('lockControl')
        if lock is None:
            return
        ctrl = int(command.get('value'))   
        logging.info('udiYoLock switchControl - {}'.format(ctrl))
        ctrl = int(command.get('value'))     
        if ctrl == 1:
            lock.setState('LOCK')
        elif ctrl == 0:
            lock.setState('UNLOCK')
      
        
        
        
    def update(self, command = None):
        logging.info('Update Status Executed')
        lock = self._get_lock('update')
        if lock is None:
            return
        lock.refreshDevice()
        
 


    commands = {
                'UPDATE' : update,
                'LOCK'   : set_lock,
                'UNLOCK' : set_unlock,
                'LOCKCTRL' : lockControl,

                }




