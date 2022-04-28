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
    logging.basicConfig(level=logging.INFO)

from os import truncate
#import udi_interface
#import sys
import time
from yolinkManipulatorV2 import YoLinkManipul




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
        logging.debug('udiYoManipulator INIT- {}'.format(deviceInfo['name']))
   
        self.yoAccess = yoAccess

        self.devInfo =  deviceInfo   
        self.yoManipulator = None


        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)



    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
        logging.info('Start - udiYoManipulator')
        self.yoManipulator = YoLinkManipul(self.yoAccess, self.devInfo, self.updateStatus)
        self.yoManipulator.delayTimerCallback (self.updateDelayCountdown, 5)
        time.sleep(2)
        self.yoManipulator.initNode()
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    def stop (self):
        logging.info('Stop udiYoManipulator')
        self.node.setDriver('ST', 0, True, True)
        self.yoManipulator.shut_down()

    def checkOnline(self):
        #get get info even if battery operated 
        self.yoManipulator.refreshDevice()    

    def updateStatus(self, data):
        logging.info('updateStatus - udiYoManipulator')
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
            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV1', 0, True, True)     
                self.node.setDriver('GV2', 0, True, True)   
                self.node.setDriver('GV8', 0, True, True)   
                


    def updateDelayCountdown( self, timeRemaining):
        logging.debug('Manipulator updateDelayCountDown:  delays {}'.format(timeRemaining))
        for delayInfo in range(0, len(timeRemaining)):
            if 'ch' in timeRemaining[delayInfo]:
                if timeRemaining[delayInfo]['ch'] == 1:
                    if 'on' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV1', timeRemaining[delayInfo]['on'], True, False)
                    if 'off' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV2', timeRemaining[delayInfo]['off'], True, False)

  
    def switchControl(self, command):
        logging.info('Manipulator switchControl')
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



    commands = {
                'UPDATE': update,
                'MANCTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay 
                }




