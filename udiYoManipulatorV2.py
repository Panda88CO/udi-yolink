#!/usr/bin/env python3
"""
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
from yolinkManipulatorV2 import YoLinkManipul

polyglot = None
Parameters = None
n_queue = []
count = 0



class udiYoManipulator(udi_interface.Node):
    id = 'yomanipu'
    '''
       drivers = [
            'GV0' = Manipulator State
            'GV1' = OnDelay
            'GV2' = OffDelay
            'GV5' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoManipulator INIT')
   
        self.yoAccess = yoAccess

        self.devInfo =  deviceInfo   
        self.yoManipulator = None


        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)



    def start(self):
        print('start - udiYoManipulator')
        self.yoManipulator = YoLinkManipul(self.yoAccess, self.devInfo, self.updateStatus)
        self.yoManipulator.initNode()
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    def stop (self):
        logging.info('Stop udiYoManipulator')
        self.node.setDriver('ST', 0, True, True)
        self.yoManipulator.shut_down()


    def updateStatus(self, data):
        logging.debug('updateStatus - udiYoManipulator')
        self.yoManipulator.updateCallbackStatus(data)
        
        if self.node is not None:
            state =  self.yoManipulator.getState()
            if self.yoManipulator.online:
                if state.upper() == 'OPEN':
                    self.node.setDriver('GV0', 1, True, True)
                elif state.upper() == 'CLOSED':
                    self.node.setDriver('GV0', 0, True, True)
                else:
                    self.node.setDriver('GV0', 99, True, True)
                
                self.node.setDriver('GV8', 1, True, True)
                self.updateDelays()
            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV1', 0, True, True)     
                self.node.setDriver('GV2', 0, True, True)   
                self.node.setDriver('GV8', 0, True, True)   
                

    def updateDelays(self):
        delays =  self.yoManipulator.getDelays()
        logging.debug('delays: {}'.format(delays))
        #print('on delay: ' + str(delays['on']))
        #print('off delay: '+ str(delays['off']))
        if delays != None:
            if 'on' in delays:
                self.node.setDriver('GV1', delays['on'], True, True)
            if 'off' in delays:
                self.node.setDriver('GV2', delays['off'], True, True)               
        else:
            self.node.setDriver('GV1', 0, True, True)     
            self.node.setDriver('GV2', 0, True, True)     

    '''
    # Need to use shortPoll
    def pollDelays(self):
        delays =  self.yoManipulator.getDelays()
        logging.debug('delays: ' + str(delays))
        #print('on delay: ' + str(delays['on']))
        #print('off delay: '+ str(delays['off']))
        if delays != None:
            delays =  self.yoManipulator.refreshDelays() # should be able to calculate without polling 
            if 'on' in delays:
                self.node.setDriver('GV1', delays['on'], True, True)
            if 'off' in delays:
                self.node.setDriver('GV2', delays['off'], True, True)               
        else:
            self.node.setDriver('GV1', 0, True, True)     
            self.node.setDriver('GV2', 0, True, True)     

    def poll(self, polltype):
        logging.debug('ISY poll - {}'.format(polltype))

        if 'longPoll' in polltype:
            timeNow = time.time()*1000
            if timeNow -self.yoManipulator.lastUpdate > 60*60*1000:
                logging.info('Polling status ')
                self.yoManipulator.refreshState()
            #self.yoManipulator.refreshSchedules()
        #if 'shortPoll' in polltype:
            #self.pollDelays()
            #update Delays calculated
    '''
    def switchControl(self, command):
        logging.info('switchControl')
        state = int(command.get('value'))     
        if state == 1:
            self.yoManipulator.setState('ON')
        else:
            self.yoManipulator.setState('OFF')
        
    def setOnDelay(self, command ):
        logging.info('setOnDelay')
        delay =int(command.get('value'))
        self.yoManipulator.setOnDelay(delay)
        self.node.setDriver('GV1', delay*60, True, True)

    def setOffDelay(self, command):
        logging.info('setOnDelay Executed')
        delay =int(command.get('value'))
        self.yoManipulator.setOffDelay(delay)
        self.node.setDriver('GV2', delay*60, True, True)



    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoManipulator.refreshState()
        #self.yoManipulator.refreshSchedules()     


    commands = {
                'UPDATE': update,
                'MANCTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay 
                }




