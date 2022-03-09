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
    logging.basicConfig(level=logging.DEBUG)
import sys
import time
from yolinkGarageDoorToggleV2 import YoLinkGarageDoorCtrl


polyglot = None
Parameters = None
n_queue = []
count = 0



class udiYoGarageDoor(udi_interface.Node):
    id = 'yogarage'
    
    '''
       drivers = [
            'GV8' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV8', 'value': 1, 'uom': 25},
            {'driver': 'ST', 'value': 1, 'uom': 25},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        
        self.yoAccess=yoAccess
        self.devInfo =  deviceInfo   
        self.yoTHsensor  = None
        logging.debug('udiYoGarageDoor INIT - {}'.format(deviceInfo['name']))

        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)

    def start(self):
        logging.info('start - YoLinkThsensor')
        self.yoDoorControl = YoLinkGarageDoorCtrl(self.yoAccess, self.devInfo, self.updateStatus)

        time.sleep(2)
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)
    

    def initNode(self):
        self.yoDoorControl.online = True
        self.node.setDriver('GV8', self.yoDoorControl.bool2Nbr(self.yoDoorControl.online), True, True)
        
    def checkOnline(self):
        pass
        
    
    def stop (self):
        logging.info('Stop udiYoGarageDoor')
        self.node.setDriver('ST', 0, True, True)
        self.yoDoorControl.shut_down()

    
    def updateStatus(self, data):
        logging.debug('updateStatus - udiYoGarageDoor')
        self.yoDoorControl.updateCallbackStatus(data)
        logging.debug(data)
        if self.node is not None:
            self.node.setDriver('GV8', self.yoDoorControl.bool2Nbr(self.yoDoorControl.online), True, True)


    def toggleDoor(self, command = None):
        logging.info('GarageDoor Toggle Door')
        self.yoDoorControl.toggleDevice()

    commands = {
                    'TOGGLE': toggleDoor
                }




