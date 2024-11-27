#!/usr/bin/env python3
"""
MIT License
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

from ctypes import set_errno
from os import truncate
#import udi_interface
#import sys
import time
from yolinkLockV2 import YoLink_lock



class udiYoLock(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, bool2ISY, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

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
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 25}, 
            {'driver': 'GV2', 'value': 0, 'uom': 25}, 
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},
            {'driver': 'TIME', 'value': 0, 'uom': 44},            
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoOutlet INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []   
        
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoLock = None
        self.node_ready = False
        self.last_state = ''
        self.powerSupported = True # assume

        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
             

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)        



    def start(self):
        logging.info('start - YoLinkOutlet')
        self.yoLock  = YoLink_lock(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoLock.initNode()
        self.node_ready = True
        #self.my_setDriver('ST', 1)


    def stop (self):
        logging.info('Stop udiYoOutlet')
        self.my_setDriver('ST', 0)
        self.yoLock.shut_down()


    def checkDataUpdate(self):
        if self.yoLock.data_updated():
            self.updateData()

    def updateLastTime(self):
        self.my_setDriver('TIME', self.yoLock.getTimeSinceUpdateMin(), 44)

    def updateData(self):
        if self.node is not None:
            self.my_setDriver('TIME', self.yoLock.getTimeSinceUpdateMin(), 44)

            if  self.yoLock.online:
                state = str(self.yoLock.getState()).upper()
                logging.debug('Lock state: {}'.format(state))
                if state == 'LOCK':
                    self.my_setDriver('GV0', 1)
                    if self.last_state != state:
                        self.node.reportCmd('DON')
                elif state == 'UNLOCK' :
                    self.my_setDriver('GV0', 0)
                    if self.last_state != state:
                        self.node.reportCmd('DOF')
                else:
                    self.my_setDriver('GV0', 99)
                self.last_state = state
                battery = self.yoLock.getBattery()
                self.my_setDriver('GV1', battery)
                if None == self.yoLock.getDoorBellRing():
                    self.my_setDriver('GV2', 0)
                else:
                    self.my_setDriver('GV2', 1)
                self.my_setDriver('ST', 1)
                if self.yoLock.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

            else:
                #self.my_setDriver('GV0', 99)
                #self.my_setDriver('GV1', -1)
                #self.my_setDriver('GV2', 0)
                self.my_setDriver('ST', 0)
                self.my_setDriver('GV20', 2)
            



    def updateStatus(self, data):
        logging.info('udiYoOutlet updateStatus')
        self.yoLock.updateStatus(data)
        self.updateData()



    
    def checkOnline(self):
        self.yoLock.refreshDevice()


    def set_lock(self, command = None):
        logging.info('udiYoOutlet set_lock')
        self.yoLock.setState('LOCK')
        self.my_setDriver('GV0',1 )
        self.node.reportCmd('DON')

    def set_unlock(self, command = None):
        logging.info('udiYoOutlet set_outlet_off')
        self.yoLock.setState('UNLOCK')
        self.my_setDriver('GV0',0 )
        self.node.reportCmd('DOF')



    def lockControl(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoOutlet switchControl - {}'.format(ctrl))
        ctrl = int(command.get('value'))     
        if ctrl == 1:
            self.yoLock.setState('LOCK')
            self.my_setDriver('GV0',1 )
            self.node.reportCmd('DON')
        elif ctrl == 0:
            self.yoLock.setState('UNLOCK')
            self.my_setDriver('GV0',0 )
            self.node.reportCmd('DOF')
      
        
        
    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoLock.refreshDevice()
        
 


    commands = {
                'UPDATE' : update,
                'LOCK'   : set_lock,
                'UNLOCK' : set_unlock,
                'LOCKCTRL' : lockControl, 

                }




