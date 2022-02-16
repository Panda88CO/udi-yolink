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
from yolinkTHsensorV2 import YoLinkTHSen

polyglot = None
Parameters = None
n_queue = []
count = 0


class udiYoTHsensor(udi_interface.Node):
    id = 'yothsens'
    
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
            {'driver': 'GV1', 'value': 2, 'uom': 25}, 
            {'driver': 'GV2', 'value': 2, 'uom': 25}, 
            {'driver': 'CLIHUM', 'value': 0, 'uom': 51},
            {'driver': 'GV4', 'value': 2, 'uom': 25},
            {'driver': 'GV5', 'value': 2, 'uom': 25},
            {'driver': 'BATLVL', 'value': 5, 'uom': 25},
            {'driver': 'GV7', 'value': 2, 'uom': 25},
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoTHsensor INIT')

        self.yoAccess = yoAccess
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
        print('start - YoLinkTHsensor')
        self.yoTHsensor  = YoLinkTHSen(self.yoAccess, self.devInfo, self.updateStatus)
        self.yoTHsensor.initNode()
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    def initNode(self):
        self.yoTHsensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoTHsensor')
        self.node.setDriver('ST', 0, True, True)
        self.yoTHsensor.shut_down()

    '''
    def yoTHsensor.bool2Nbr(self, bool):
        if bool:
            return(1)
        else:
            return(0)
    '''

    def updateStatus(self, data):
        logging.debug('updateStatus - yoTHsensor')
        self.yoTHsensor.updateCallbackStatus(data)
        logging.debug(data)
        alarms = self.yoTHsensor.getAlarms()
        if self.node is not None:
            if self.yoTHsensor.online:
                self.node.setDriver('CLITEMP', self.yoTHsensor.getTempValueC(), True, True)
                self.node.setDriver('GV1', self.yoTHsensor.bool2Nbr(alarms['lowTemp']), True, True)
                self.node.setDriver('GV2', self.yoTHsensor.bool2Nbr(alarms['highTemp']), True, True)
                self.node.setDriver('CLIHUM', self.yoTHsensor.getHumidityValue(), True, True)
                self.node.setDriver('GV4', self.yoTHsensor.bool2Nbr(alarms['lowHumidity']), True, True)
                self.node.setDriver('GV5', self.yoTHsensor.bool2Nbr(alarms['highHumidity']), True, True)
                self.node.setDriver('BATLVL', self.yoTHsensor.getBattery(), True, True)
                self.node.setDriver('GV7', self.yoTHsensor.bool2Nbr(alarms['lowBattery']), True, True)
                self.node.setDriver('GV8', self.yoTHsensor.bool2Nbr(self.yoTHsensor.getOnlineStatus()), True, True)
            else:
                self.node.setDriver('CLITEMP', 0, True, True)
                self.node.setDriver('GV1',99, True, True)
                self.node.setDriver('GV2', 99, True, True)
                self.node.setDriver('CLIHUM', 0, True, True)
                self.node.setDriver('GV4',99, True, True)
                self.node.setDriver('GV5',99, True, True)
                self.node.setDriver('BATLVL', 99, True, True)
                self.node.setDriver('GV7',99, True, True)
                self.node.setDriver('GV8', 0, True, True)

    def poll(self, polltype):
        logging.debug('ISY poll - {} '.format(polltype))

        if 'longPoll' in polltype:
            self.yoTHsensor.refreshSensor()
                

    def update(self, command = None):
        logging.info('THsensor Update Status Executed')
        self.yoTHsensor.refreshState()
       

    commands = {
                'UPDATE': update,
                }




