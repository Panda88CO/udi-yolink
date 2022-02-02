#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate

import sys
import time
from yolinkDoorSensorV2 import YoLinkDoorSens

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)
polyglot = None
Parameters = None
n_queue = []
count = 0



class udiYoDoorSensor(udi_interface.Node):
    id = 'yodoorsens'
    
    '''
       drivers = [
            'GV0' = DoorState
            'GV1' = Batery
            'GV8' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25}, 
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('TestYoLinkNode INIT')

        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        #self.address = address
        #self.poly = polyglot

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        

        #self.switchState = self.yoSwitch.getState()
        #self.switchPower = self.yoSwitch.getEnergy()
        #udi_interface.__init__(self, polyglot, primary, address, name)

    def start(self):
        print('start - YoLinkThsensor')
        self.yoDoorSensor  = YoLinkDoorSens(self.yoAccess, self.devInfo, self.updateStatus)     
        self.yoDoorSensor.initNode()
        time.sleep(2)
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    def initNode(self):
        self.yoDoorSensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop ')
        self.node.setDriver('ST', 0, True, True)
        self.yoDoorSensor.shut_down()
       
    def doorState(self):
        state = self.yoDoorSensor.getState()
        if state.lower() == 'closed':
            return(0)
        elif state.lower() == 'open':
            return(1)
        else:
            return(99)

    def updateStatus(self, data):
        logging.debug('updateStatus - yoTHsensor')
        self.yoDoorSensor.updateCallbackStatus(data)
        logging.debug(data)
        alarms = self.yoDoorSensor.getAlarms()
        if self.node is not None:
            if self.yoDoorSensor.online:
                self.node.setDriver('GV0', self.doorState() , True, True)
                self.node.setDriver('GV1', self.yoDoorSensor.getBattery(), True, True)
                self.node.setDriver('GV8', self.yoDoorSensor.bool2Nbr(self.yoDoorSensor.getOnlineStatus()), True, True)
            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV1', 99, True, True)
                self.node.setDriver('GV8', 0, True, True)


    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if 'longPoll' in polltype:
            self.yoDoorSensor.refreshSensor()

    def update(self, command = None):
        logging.info('GarageDoor Update Status Executed')
        self.yoDoorSensor.refreshState()
       


    commands = {
                'UPDATE': update,

                }



