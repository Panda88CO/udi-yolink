#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate
import udi_interface
import sys
import time
from yolinkTHsensor import YoLinkTHSen
logging = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None
Parameters = None
n_queue = []
count = 0

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''

class udiYoTHsensor(udi_interface.Node):
    #def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, devInfo):
    id = 'yothsensor'
    
    '''
       drivers = [
            'GV0' = TempC
            'GV1' = Low Temp Alarm
            'GV2' = high Temp Alarm 
            'GV3' = Humidity
            'GV4' = Low Humidity Alarm
            'GV5' = High Humidity Alarm
            'GV6' = BatteryLevel
            'GV7' = BatteryAlarm
            'GV8' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'CLITEMP', 'value': 0, 'uom': 4},
            {'driver': 'GV1', 'value': 0, 'uom': 25}, 
            {'driver': 'GV2', 'value': 0, 'uom': 25}, 
            {'driver': 'CLIHUM', 'value': 0, 'uom': 51},
            {'driver': 'GV4', 'value': 0, 'uom': 25},
            {'driver': 'GV5', 'value': 0, 'uom': 25},
            {'driver': 'BATLVL', 'value': 0, 'uom': 25},
            {'driver': 'GV7', 'value': 0, 'uom': 25},
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
        #self.count = 0
        #self.n_queue = []

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
        self.yoTHsensor  = YoLinkTHSen(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        self.yoTHsensor.initNode()
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)
    
    def heartbeat(self):
        #LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0
    '''
    def parameterHandler(self, params):
        self.Parameters.load(params)
    '''
    def initNode(self):
        self.yoTHsensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop not implemented')
        self.node.setDriver('ST', 0, True, True)
        self.yoTHsensor.shut_down()


    def updateStatus(self, data):
        logging.debug('updateStatus - yoLink')
        self.yoTHsensor.updateCallbackStatus(data)
        print(data)
        if self.node is not None:
            self.node.setDriver('CLITEMP', 20, True, True)
            self.node.setDriver('GV1', 0, True, True)
            self.node.setDriver('GV2', 1, True, True)
            self.node.setDriver('CLIHUM', 75, True, True)
            self.node.setDriver('GV4', 1, True, True)
            self.node.setDriver('GV5', 0, True, True)
            self.node.setDriver('BATLVL', 3, True, True)
            self.node.setDriver('GV7', 0, True, True)
            self.node.setDriver('GV8', 1, True, True)
        
        #while self.yoSwitch.eventPending():
        #    print(self.yoSwitch.getEvent())



    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if 'longPoll' in polltype:
            self.yoTHsensor.refreshSensor()



    def update(self, command = None):
        logging.info('THsensor Update Status Executed')
        self.yoTHsensor.refreshState()
       


    commands = {
                'UPDATE': update,
                }




