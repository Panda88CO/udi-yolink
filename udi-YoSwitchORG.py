#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate
import udi_interface
import sys
import time
from yolinkSwitch import YoLinkSW
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

class udiYoSwitch(YoLinkSW):
    def __init__(self, polyglot, nodeAddress, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(csName, csid, csseckey,  deviceInfo, self.updateStatus, yolink_URL, mqtt_URL, mqtt_port )   
        #self.yoSwitch  = YoLinkSW(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        self.initNode()
        self.node = polyglot.getNode(nodeAddress)

    
    def heartbeat(self):
        #LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

    def updateStatus(self, data):
        logging.debug('updateStatus - TestYoLinkNode')
        self.updateCallbackStatus(data)
        print(data)
        self.node = polyglot.getNode('yoswitch')
        if self.node is not None:
            state =  self.getState()
            print(state)
            if state.upper() == 'ON':
                self.node.setDriver('GV0', 1, True, True)
            else:
                self.node.setDriver('GV0', 0, True, True)
            tmp =  self.yoSwitch.getEnergy()
            power = tmp['power']
            watt = tmp['watt']
            self.node.setDriver('GV3', power, True, True)
            self.node.setDriver('GV4', watt, True, True)
        
        #while self.yoSwitch.eventPending():
        #    print(self.yoSwitch.getEvent())


    # Need to use shortPoll
    def pollDelays(self):
        delays =  self.yoSwitch.getDelays()
        logging.debug('delays: ' + str(delays))
        #print('on delay: ' + str(delays['on']))
        #print('off delay: '+ str(delays['off']))
        if delays != None:
            if delays['on'] != 0 or delays['off'] !=0:
                delays =  self.yoSwitch.refreshDelays() # should be able to calculate without polling 
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
            self.yoSwitch.refreshState()
            self.yoSwitch.refreshSchedules()
        if 'shortPoll' in polltype:
            self.pollDelays()
            #update Delays calculated

    def switchControl(self, command):
        logging.info('switchControl')
        state = int(command.get('value'))     
        if state == 1:
            self.yoSwitch.setState('ON')
        else:
            self.yoSwitch.setState('OFF')
        
    def setOnDelay(self, command ):
        logging.info('setOnDelay')
        delay =int(command.get('value'))
        self.yoSwitch.setDelay([{'delayOn':delay}])
        self.node.setDriver('GV1', delay, True, True)

    def setOffDelay(self, command):
        logging.info('setOnDelay Executed')
        delay =int(command.get('value'))
        self.yoSwitch.setDelay([{'delayOff':delay}])
        self.node.setDriver('GV2', delay, True, True)


    def parameterHandler(self, params):
        self.Parameters.load(params)

    def stop (self):
        logging.info('Stop not implemented')
        self.yoSwitch.shut_down()

    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoSwitch.refreshState()
        self.yoSwitch.refreshSchedules()     



