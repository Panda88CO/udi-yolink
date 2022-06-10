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
from yolinkOutletV2 import YoLinkOutl



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
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'GV3', 'value': -1, 'uom': 30},
            {'driver': 'GV4', 'value': -1, 'uom': 33},
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoOutlet INIT- {}'.format(deviceInfo['name']))

        
        self.yoAccess = yoAccess

        self.devInfo =  deviceInfo   
        self.yoOutlet = None
        self.powerSupported = True # assume 

        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []        

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.node.setDriver('ST', 1, True, True)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
        logging.info('start - YoLinkOutlet')
        self.yoOutlet  = YoLinkOutl(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoOutlet.initNode()
        if not self.yoOutlet.online:
            logging.error('Device {} not on-line - remove node'.format(self.devInfo['name']))       
            self.node.setDriver('ST', 0, True, True)
            self.yoOutlet.shut_down()
            if self.node:
                self.poly.delNode(self.node)
        else:
            self.yoOutlet.delayTimerCallback (self.updateDelayCountdown, 5)
            self.node.setDriver('ST', 1, True, True)
    
    def stop (self):
        logging.info('Stop udiYoOutlet')
        self.node.setDriver('ST', 0, True, True)
        if self.yoOutlet.online:
            self.yoOutlet.shut_down()


    def updateStatus(self, data):
        logging.info('udiYoOutlet updateStatus')
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
                tmp =  self.yoOutlet.getEnergy()
                if tmp != None:
                    power = tmp['power']
                    watt = tmp['watt']
                    self.node.setDriver('GV3', power, True, True)
                    self.node.setDriver('GV4', watt, True, True)

            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV3', -1, True, True)
                self.node.setDriver('GV4', -1, True, True)
                self.node.setDriver('GV8',0, True, True)
            


    def updateDelayCountdown( self, timeRemaining):
        logging.debug('udiYoOutlet updateDelayCountDown:  delays {}'.format(timeRemaining))
        for delayInfo in range(0, len(timeRemaining)):
            if 'ch' in timeRemaining[delayInfo]:
                if timeRemaining[delayInfo]['ch'] == 1:
                    if 'on' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV1', timeRemaining[delayInfo]['on'], True, False)
                    if 'off' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV2', timeRemaining[delayInfo]['off'], True, False)

    
    def checkOnline(self):
        self.yoOutlet.refreshDevice()

    def switchControl(self, command):
        logging.info('udiYoOutlet switchControl')
        state = int(command.get('value'))     
        if state == 1:
            self.yoOutlet.setState('ON')
        else:
            self.yoOutlet.setState('OFF')
        
    def setOnDelay(self, command ):
        logging.info('udiYoOutlet setOnDelay')
        delay =int(command.get('value'))
        self.yoOutlet.setOnDelay(delay)
        self.node.setDriver('GV1', delay*60, True, True)

    def setOffDelay(self, command):
        logging.info('udiYoOutlet setOnDelay Executed')
        delay =int(command.get('value'))
        self.yoOutlet.setOffDelay(delay)
        self.node.setDriver('GV2', delay*60, True, True)

    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoOutlet.refreshState()
 


    commands = {
                'UPDATE': update,
                'SWCTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay 
                }




