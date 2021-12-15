#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate

import sys
import time
from yolinkDoorSensor import YoLinkDoorSens

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

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''

class udiYoDoorSensor(udi_interface.Node):
    #def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, devInfo):
    id = 'yodoorsens'
    
    '''
       drivers = [
            'GV0' = DoorState
            'GV1' = Batery
            'GV8' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 2, 'uom': 25}, 
            {'driver': 'GV1', 'value': 5, 'uom': 25}, 
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('TestYoLinkNode INIT')
        self.csid = csid
        self.csseckey = csseckey
        self.csName = csName
        self.mqtt_URL= mqtt_URL
        self.mqtt_port = mqtt_port
        self.yolink_URL = yolink_URL

        self.devInfo =  deviceInfo   
        self.yoTHsensor  = None
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
        self.yoDoorSensor  = YoLinkDoorSens(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
       
        self.yoDoorSensor.initNode()
       
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)
    '''
    def heartbeat(self):
        #LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

    def parameterHandler(self, params):
        self.Parameters.load(params)
    '''
    def initNode(self):
        self.yoDoorSensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop ')
        self.node.setDriver('ST', 0, True, True)
        self.yoDoorSensor.shut_down()
       


    def updateStatus(self, data):
        logging.debug('updateStatus - yoTHsensor')
        self.yoDoorSensor.updateCallbackStatus(data)
        logging.debug(data)
        alarms = self.yoDoorSensor.getAlarms()
        if self.node is not None:
            self.node.setDriver('GV0', self.yoDoorSensor.getState(), True, True)
            self.node.setDriver('GV1', self.yoDoorSensor.getBattery(), True, True)
            self.node.setDriver('GV8', self.yoDoorSensor.bool2Nbr(self.yoDoorSensor.getOnlineStatus()), True, True)

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




