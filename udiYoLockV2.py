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
            #{'driver': 'ST', 'value': 0, 'uom': 25},
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

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
        logging.info('start - YoLinkOutlet')
        self.yoLock  = YoLink_lock(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoLock.initNode()
        self.node_ready = True
        #self.node.setDriver('ST', 1, True, True)


    def stop (self):
        logging.info('Stop udiYoOutlet')
        self.node.setDriver('ST', 0, True, True)
        self.yoLock.shut_down()


    def checkDataUpdate(self):
        if self.yoLock.data_updated():
            self.updateData()


    def updateData(self):
        if self.node is not None:
            if  self.yoLock.online:
                state = str(self.yoLock.getState()).upper()
                logging.debug('Lock state: {}'.format(state))
                if state == 'LOCK':
                    self.node.setDriver('GV0', 1, True, True)
                    if self.last_state != state:
                        self.node.reportCmd('DON')
                elif state == 'UNLOCK' :
                    self.node.setDriver('GV0', 0, True, True)
                    if self.last_state != state:
                        self.node.reportCmd('DOF')
                else:
                    self.node.setDriver('GV0', 99, True, True)
                self.last_state = state
                battery = self.yoLock.getBattery()
                self.node.setDriver('GV1', battery)
                if None == self.yoLock.getDoorBellRing():
                    self.node.setDriver('GV2', 0, True, True)
                else:
                    self.node.setDriver('GV2', 1, True, True)
                self.node.setDriver('ST', 1)

            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV1', -1)
                self.node.setDriver('GV2', 0, True, True)
                self.node.setDriver('ST', 0)
            



    def updateStatus(self, data):
        logging.info('udiYoOutlet updateStatus')
        self.yoLock.updateStatus(data)
        self.updateData()



    
    def checkOnline(self):
        self.yoLock.refreshDevice()


    def set_lock(self, command = None):
        logging.info('udiYoOutlet set_lock')
        self.yoLock.setState('LOCK')
        self.node.setDriver('GV0',1 , True, True)
        self.node.reportCmd('DON')

    def set_unlock(self, command = None):
        logging.info('udiYoOutlet set_outlet_off')
        self.yoLock.setState('UNLOCK')
        self.node.setDriver('GV0',0 , True, True)
        self.node.reportCmd('DOF')



    def lockControl(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoOutlet switchControl - {}'.format(ctrl))
        ctrl = int(command.get('value'))     
        if ctrl == 1:
            self.yoLock.setState('LOCK')
            self.node.setDriver('GV0',1 , True, True)
            self.node.reportCmd('DON')
        elif ctrl == 0:
            self.yoLock.setState('UNLOCK')
            self.node.setDriver('GV0',0 , True, True)
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




