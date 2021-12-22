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
from yolinkGarageDoorToggle import YoLinkGarageDoorCtrl


polyglot = None
Parameters = None
n_queue = []
count = 0

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''

class udiYoGarageDoor(udi_interface.Node):
    #def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, devInfo):
    id = 'yogaragedoor'
    
    '''
       drivers = [
            'GV8' = Online
            ]

    ''' 
        
    drivers = [
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
        #polyglot.subscribe(polyglot.POLL, self.poll)
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
        self.yoDoorControl = YoLinkGarageDoorCtrl(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
             
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)
    

    def initNode(self):
        logging.debug('Nothing to init')

    
    def stop (self):
        logging.info('Stop ')
        self.node.setDriver('ST', 0, True, True)
        self.yoDoorControl.shut_down()


    def updateStatus(self, data):
        logging.debug('updateStatus - yoTHsensor')
        self.yoDoorControl.updateCallbackStatus(data)
        logging.debug(data)
        if self.node is not None:
            self.node.setDriver('GV8', self.yoDoorControl.bool2Nbr(self.yoDoorControl.online), True, True)


    '''
    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
    '''


    def toggleDoor(self, command = None):
        logging.info('GarageDoor Toggle Door')
        self.yoDoorControl.toggleDevice()

    commands = {
                    'TOGGLE': toggleDoor
                }



