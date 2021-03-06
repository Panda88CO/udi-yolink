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
from yolinkTHsensorV2 import YoLinkTHSen



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


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo, temp_unit):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoTHsensor INIT- {}'.format(deviceInfo['name']))

        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo   
        self.yoTHsensor  = None
        
        self.temp_unit = temp_unit
        #self.address = address
        #self.poly = polyglot

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []               
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()

        self.node = self.poly.getNode(address)



    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
        logging.info('Start udiYoTHsensor')
        self.yoTHsensor  = YoLinkTHSen(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoTHsensor.initNode()
        if not self.yoTHsensor.online:
            logging.warning('Device {} not on-line'.format(self.devInfo['name']))            
            #self.yoTHsensor.shut_down()
            #if self.node:
            #    self.poly.delNode(self.node.address)
        else:
            self.node.setDriver('ST', 1, True, True)

    def initNode(self):
        self.yoTHsensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoTHsensor')
        self.node.setDriver('ST', 0, True, True)
        self.yoTHsensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkOnline(self):
        self.yoTHsensor.refreshDevice()


    def updateStatus(self, data):
        logging.debug('udiYoTHsensor - updateStatus')
        self.yoTHsensor.updateCallbackStatus(data)

        alarms = self.yoTHsensor.getAlarms()
        if self.node is not None:
            if self.yoTHsensor.online:
                logging.debug("yoTHsensor temp: {}".format(self.yoTHsensor.getTempValueC()))
                if self.temp_unit == 0:
                    self.node.setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC(),1), True, True, 4)
                elif self.temp_unit == 1:
                    self.node.setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC()*9/5+32,1), True, True, 17)
                elif self.temp_unit == 2:
                    self.node.setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC()+273.15,1), True, True, 26)
                else:
                    self.node.setDriver('CLITEMP', 99, True, True, 25)
                self.node.setDriver('GV1', self.yoTHsensor.bool2Nbr(alarms['lowTemp']), True, True)
                self.node.setDriver('GV2', self.yoTHsensor.bool2Nbr(alarms['highTemp']), True, True)
                self.node.setDriver('CLIHUM', self.yoTHsensor.getHumidityValue(), True, True)
                self.node.setDriver('GV4', self.yoTHsensor.bool2Nbr(alarms['lowHumidity']), True, True)
                self.node.setDriver('GV5', self.yoTHsensor.bool2Nbr(alarms['highHumidity']), True, True)
                self.node.setDriver('BATLVL', self.yoTHsensor.getBattery(), True, True)
                self.node.setDriver('GV7', self.yoTHsensor.bool2Nbr(alarms['lowBattery']), True, True)
                self.node.setDriver('GV8', self.yoTHsensor.bool2Nbr(self.yoTHsensor.online), True, True)
            else:
                self.node.setDriver('CLITEMP', 99, True, True, 25)
                self.node.setDriver('GV1',99, True, True)
                self.node.setDriver('GV2', 99, True, True)
                self.node.setDriver('CLIHUM', 0, True, True)
                self.node.setDriver('GV4',99, True, True)
                self.node.setDriver('GV5',99, True, True)
                self.node.setDriver('BATLVL', 99, True, True)
                self.node.setDriver('GV7',99, True, True)
                self.node.setDriver('GV8', 0, True, True)


    def update(self, command = None):
        logging.info('THsensor Update')
        self.yoTHsensor.refreshState()
       

    commands = {
                'UPDATE': update,
                }




