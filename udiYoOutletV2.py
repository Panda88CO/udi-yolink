#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from os import truncate
#import udi_interface
import sys
import time
from yolinkOutletV2 import YoLinkOutl

polyglot = None
Parameters = None
n_queue = []
count = 0



class udiYoOutlet(udi_interface.Node):
    id = 'yooutlet'
    '''
       drivers = [
            'GV0' = Outlet State
            'GV1' = OnDelay
            'GV2' = OffDelay
            'GV3' = Power
            'GV4' = Energy
            'GV5' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 44}, 
            {'driver': 'GV2', 'value': 0, 'uom': 44}, 
            {'driver': 'GV3', 'value': -1, 'uom': 30},
            {'driver': 'GV4', 'value': -1, 'uom': 33},
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('TestYoLinkNode INIT')

        
        self.yoAccess = yoAccess

        self.devInfo =  deviceInfo   
        self.yoOutlet = None
        #self.outletStates = {'ON':1, 'OFF':0, 'UNKNOWN':2}
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
        self.node.setDriver('ST', 1, True, True)

        #self.switchState = self.yoOutlet.getState()
        #self.switchPower = self.yoOutlet.getEnergy()
        #udi_interface.__init__(self, polyglot, primary, address, name)

    def start(self):
        print('start - YoLinkSw')
        self.yoOutlet  = YoLinkOutl(self.yoAccess, self.devInfo, self.updateStatus)
        self.yoOutlet.initNode()
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    def stop (self):
        logging.info('Stop not implemented')
        self.node.setDriver('ST', 0, True, True)
        self.yoOutlet.shut_down()


    def updateStatus(self, data):
        logging.debug('updateStatus - TestYoLinkNode')
        self.yoOutlet.updateCallbackStatus(data)

        if self.node is not None:
            if  self.yoOutlet.online:
                state = str(self.yoOutlet.getState()).upper()
                if state == 'ON':
                    self.node.setDriver('GV0',1 , True, True)
                elif state == 'OFF' :
                    self.node.setDriver('GV0', 0, True, True)
                else:
                    self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV8',1, True, True)
            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV3', -1, True, True)
                self.node.setDriver('GV4', -1, True, True)
                self.node.setDriver('GV8',0, True, True)
            
            self.pollDelays
            tmp =  self.yoOutlet.getEnergy()
            power = tmp['power']
            watt = tmp['watt']
            self.node.setDriver('GV3', power, True, True)
            self.node.setDriver('GV4', watt, True, True)
            
    # Need to use shortPoll
    def pollDelays(self):
        delays =  self.yoOutlet.getDelays()
        logging.debug('delays: ' + str(delays))
        #print('on delay: ' + str(delays['on']))
        #print('off delay: '+ str(delays['off']))
        if delays != None and  self.yoOutlet.online:
            if delays['on'] != 0 or delays['off'] !=0:
                delays =  self.yoOutlet.refreshDelays() # should be able to calculate without polling 
                if 'on' in delays:
                    self.node.setDriver('GV1', delays['on'], True, True)
                if 'off' in delays:
                    self.node.setDriver('GV2', delays['off'], True, True)               
        else:
            self.node.setDriver('GV1', 0, True, True)     
            self.node.setDriver('GV2', 0, True, True)     

    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if self.yoOutlet.getOnlineStatus():
            if 'longPoll' in polltype:
                self.yoOutlet.refreshState()
                #self.yoOutlet.refreshSchedules()
            if 'shortPoll' in polltype:
                self.pollDelays()
                #update Delays calculated

    def switchControl(self, command):
        logging.info('switchControl')
        state = int(command.get('value'))     
        if state == 1:
            self.yoOutlet.setState('ON')
        else:
            self.yoOutlet.setState('OFF')
        
    def setOnDelay(self, command ):
        logging.info('setOnDelay')
        delay =int(command.get('value'))
        self.yoOutlet.setDelay([{'delayOn':delay}])
        self.node.setDriver('GV1', delay, True, True)

    def setOffDelay(self, command):
        logging.info('setOnDelay Executed')
        delay =int(command.get('value'))
        self.yoOutlet.setDelay([{'delayOff':delay}])
        self.node.setDriver('GV2', delay, True, True)



    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoOutlet.refreshState()
        self.yoOutlet.refreshSchedules()     


    commands = {
                'UPDATE': update,
                'SWCTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay 
                }




