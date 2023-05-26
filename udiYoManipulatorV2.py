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
            'BATLVL' = BatteryLevel
            
            'ST' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'BATLVL', 'value': 99, 'uom': 25}, 
            {'driver': 'ST', 'value': 0, 'uom': 25},
            #{'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoManipulator INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoManipulator = None
        self.node_ready = False
        self.last_state = ''
        self.timer_cleared = True
        self.timer_update = 5
        self.timer_expires = 0

        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)



    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
        logging.info('Start - udiYoManipulator')
        self.yoManipulator = YoLinkManipul(self.yoAccess, self.devInfo, self.updateStatus)
        
        time.sleep(4)
        self.yoManipulator.initNode()
        time.sleep(2)
        #self.node.setDriver('ST', 1, True, True)
        self.yoManipulator.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.node_ready = True

    def stop (self):
        logging.info('Stop udiYoManipulator')
        self.node.setDriver('ST', 0, True, True)
        self.yoManipulator.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    def checkOnline(self):
        #get get info even if battery operated 
        self.yoManipulator.refreshDevice()    

    def checkDataUpdate(self):
        if self.yoManipulator.data_updated():
            self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.node.setDriver('GV1', 0, True, False)
        #    self.node.setDriver('GV2', 0, True, False)

    def updateData(self):
        if self.node is not None:
            state =  self.yoManipulator.getState()
            if self.yoManipulator.online:
                if state.upper() == 'OPEN':
                    self.node.setDriver('GV0', 1, True, True)
                    if self.last_state != state:
                        self.node.reportCmd('DON')
                elif state.upper() == 'CLOSED':
                    self.node.setDriver('GV0', 0, True, True)
                    if self.last_state != state:
                        self.node.reportCmd('DOF')
                else:
                    self.node.setDriver('GV0', 99, True, True)
                self.last_state = state
                self.node.setDriver('ST', 1)
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                    self.node.setDriver('GV1', 0, True, False)
                    self.node.setDriver('GV2', 0, True, False)  
                logging.debug('udiYoManipulator - getBattery: () '.format(self.yoManipulator.getBattery()))    
                self.node.setDriver('BATLVL', self.yoManipulator.getBattery(), True, True)          
            else:
                self.node.setDriver('GV0', 99)
                self.node.setDriver('GV1', 0)     
                self.node.setDriver('GV2', 0)
                self.node.setDriver('BATLVL', 99)
                self.node.setDriver('ST', 0)   
                

    def updateStatus(self, data):
        logging.info('updateStatus - udiYoManipulator')
        self.yoManipulator.updateStatus(data)
        self.updateData()
      


    def updateDelayCountdown( self, timeRemaining):

        logging.debug('Manipulator updateDelayCountDown:  delays {}'.format(timeRemaining))
        max_delay = 0
        for delayInfo in range(0, len(timeRemaining)):
            if 'ch' in timeRemaining[delayInfo]:
                if timeRemaining[delayInfo]['ch'] == 1:
                    if 'on' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV1', timeRemaining[delayInfo]['on'], True, False)
                        if max_delay < timeRemaining[delayInfo]['on']:
                            max_delay = timeRemaining[delayInfo]['on']
                    if 'off' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV2', timeRemaining[delayInfo]['off'], True, False)
                        if max_delay < timeRemaining[delayInfo]['off']:
                            max_delay = timeRemaining[delayInfo]['off']
        self.timer_expires = time.time()+max_delay
  
    def switchControl(self, command):
        logging.info('Manipulator switchControl')
        state = int(command.get('value'))     
        if state == 1:
            self.yoManipulator.setState('open')
            self.node.reportCmd('DON')
        else:
            self.yoManipulator.setState('closed')
            self.node.reportCmd('DOF')

    def set_open(self, command = None):
        logging.info('Manipulator - set_open')
        self.yoManipulator.setState('open')
        #self.node.reportCmd('DON')

    def set_close(self, command = None):
        logging.info('Manipulator - set_close')
        self.yoManipulator.setState('closed')
        #self.node.reportCmd('DOF')

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
        self.yoManipulator.refreshDevice()



    commands = {
                'UPDATE': update,
                'QUERY' : update,
                'DON'   : set_open,
                'DOF'   : set_close,
                'MANCTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay 
                }




