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
from yolinkOutlet import YoLinkOutl

polyglot = None
Parameters = None
n_queue = []
count = 0



class udiYoManipulator(udi_interface.Node):
    #def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, devInfo):
    id = 'yomanipulator'
    '''
       drivers = [
            'GV0' = Manipulator State
            'GV1' = OnDelay
            'GV2' = OffDelay
            'GV5' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 2, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 44}, 
            {'driver': 'GV2', 'value': 0, 'uom': 44}, 
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoManipulator INIT')
   
        self.mqtt_URL= mqtt_URL
        self.mqtt_port = mqtt_port
        self.yolink_URL = yolink_URL
        self.csid = csid
        self.csseckey = csseckey
        self.csName = csName

        self.devInfo =  deviceInfo   
        self.yoOutlet = None


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
        print('start - udiYoManipulator')
        self.yoOutlet  = YoLinkOutl(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        self.yoOutlet.initNode()
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    def stop (self):
        logging.info('Stop ')
        self.node.setDriver('ST', 0, True, True)
        self.yoOutlet.shut_down()


    def updateStatus(self, data):
        logging.debug('updateStatus - udiYoManipulator')
        self.yoOutlet.updateCallbackStatus(data)
        print(data)
        if self.node is not None:
            state =  self.yoOutlet.getState()
            print(state)
            if state.upper() == 'ON':
                self.node.setDriver('GV0', 1, True, True)
            else:
                self.node.setDriver('GV0', 0, True, True)
       
            self.node.setDriver('GV8', self.yoOutlet.bool2Nbr(self.yoOutlet.getOnlineStatus()), True, True)
        
        #while self.yoOutlet.eventPending():
        #    print(self.yoOutlet.getEvent())


    # Need to use shortPoll
    def pollDelays(self):
        delays =  self.yoOutlet.getDelays()
        logging.debug('delays: ' + str(delays))
        #print('on delay: ' + str(delays['on']))
        #print('off delay: '+ str(delays['off']))
        if delays != None:
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
        if 'longPoll' in polltype:
            self.yoOutlet.refreshState()
            self.yoOutlet.refreshSchedules()
        #if 'shortPoll' in polltype:
            #self.pollDelays()
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
                'MACTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay 
                }




