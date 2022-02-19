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
from yolinkMotionSensor import YoLinkMotionSen

polyglot = None
Parameters = None
n_queue = []
count = 0



class udiYoMotionSensor(udi_interface.Node):
    #def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, devInfo):
    id = 'yomotionsens'
    
    '''
       drivers = [
            'GV0' = Motin Alert
            'GV1' = Battery Level
            'GV8' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25}, 
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
        print('start - YoLinkMotionSensor')
        self.yoMotionsSensor  = YoLinkMotionSen(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        #self.yoMotionsSensor.initNode()
        time.sleep(2)
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    '''
    def initNode(self):
        self.yoMotionsSensor.refreshSensor()
    '''
    
    def stop (self):
        logging.info('Stop not implemented')
        self.node.setDriver('ST', 0, True, True)
        self.yoMotionsSensor.shut_down()

    '''
    def yoTHsensor.bool2Nbr(self, bool):
        if bool:
            return(1)
        else:
            return(0)
    '''
    
    def MotionState(self):
        if self.yoMotionsSensor.online:
            if  self.yoMotionsSensor.motionState() == 'normal':
                return(0)
            else:
                return(1)
        else:
            return(-1)

    def updateStatus(self, data):
        logging.debug('updateStatus - yoTHsensor')
        self.yoMotionsSensor.updateCallbackStatus(data)
        #motionState = self.yoMotonsSensor.getMotion()

        logging.debug(data)
        if self.node is not None:
            if self.yoMotionsSensor.online:
                self.node.setDriver('GV0', self.MotionState(), True, True)
                self.node.setDriver('GV1', self.yoMotionsSensor.getBattery(), True, True)
                self.node.setDriver('GV8', 1, True, True)
            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV1', 99, True, True)
                self.node.setDriver('GV8', 1, True, True)

    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if 'longPoll' in polltype:
            self.yoMotionsSensor.refreshSensor()

    def update(self, command = None):
        logging.info('THsensor Update Status Executed')
        self.yoMotionsSensor.refreshState()
       

    commands = {
                'UPDATE': update,
                }



