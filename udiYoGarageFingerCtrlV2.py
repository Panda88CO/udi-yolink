#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
#import sys
import time
from yolinkGarageFingerToggleV2 import YoLinkGarageFingerCtrl




class udiYoGarageFinger(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, wait_for_node_done, node_queue
    id = 'yogarage'
    
    '''
       drivers = [
            'ST' = Online
            ]

    '''
        
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},
            #{'driver': 'ST', 'value': 1, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        
        self.yoAccess=yoAccess
        self.devInfo =  deviceInfo
        self.node_ready = False
        self.yoDoorControl  = None
        logging.debug('udiYoGarageFinger INIT - {}'.format(deviceInfo['name']))
        self.n_queue = []
        #polyglot.subscribe(polyglot.POLL, self.poll)
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
        logging.info('start - udiYoGarageFinger')
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        self.yoDoorControl = YoLinkGarageFingerCtrl(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.my_setDriver('ST', 1)
        self.my_setDriver('GV30', 1)
        #time.sleep(3)
        self.node_ready = True

    def initNode(self):
        self.yoDoorControl.online = True
        #self.my_setDriver('ST',1)
        
    def checkOnline(self):
        pass
        
    def checkDataUpdate(self):
        pass
    
    def stop (self):
        logging.info('Stop udiYoGarageFinger')
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        self.yoDoorControl.shut_down()

    
    def updateStatus(self, data):
        logging.debug('updateStatus - udiYoGarageFinger')
        self.yoDoorControl.updateCallbackStatus(data)
        logging.debug(data)
        if self.node is not None:
            self.my_setDriver('ST',1)
            self.my_setDriver('GV30',1)
        if self.yoDoorControl.suspended:
            self.my_setDriver('GV20', 1)
        else:
            self.my_setDriver('GV20', 0)
            
        if self.yoDoorControl.online:
            self.my_setDriver('ST', 1)
            self.my_setDriver('GV30', 1)
        else:
            self.my_setDriver('GV20', 2)
            self.my_setDriver('ST', 0)
            self.my_setDriver('GV30', 0)


    def toggleDoor(self, command = None):
        logging.info('GarageFinger Toggle Door')
        self.yoDoorControl.toggleDevice()

    commands = {
                    'TOGGLE': toggleDoor,
                    'DON'   : toggleDoor,
                    'DOF'   : toggleDoor,
                }




