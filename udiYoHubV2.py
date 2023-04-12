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
    logging.basicConfig(level=logging.INFO)

from os import truncate
#import udi_interface
#import sys
import time
from yolinkHubV2 import YoLinkHu

class udiYoHub(udi_interface.Node):
  
    id = 'yohub'
    drivers = [
            #{'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            #{'driver': 'ST', 'value': 0, 'uom': 25},
            ]
    '''
       drivers = [
            'GV0' =  switch State
            'GV1' = OnDelay
            'GV2' = OffDelay

            'ST' = Online
            ]

    ''' 

    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoHub INIT- {}'.format(deviceInfo['name']))
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.yoHub = None
        self.node_ready = False
        self.n_queue = [] 
        
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
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
        logging.info('start - udiYoHub')
        self.yoHub  = YoLinkHu(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoHub.initNode()
        #self.node.setDriver('ST', 1, True, True)
        
        #if not self.yoHub.online:
        #    logging.warning('Device {} not on-line'.format(self.devInfo['name']))            
        #else:
        #    self.node.setDriver('ST', 1, True, True)
        self.node_ready = True

    def updateDelayCountdown (self, delayRemaining ) :
        logging.debug('updateDelayCountdown {}'.format(delayRemaining))

    def stop (self):
        logging.info('Stop udiYoHub')
        self.node.setDriver('ST', 0, True, True)
        self.yoHub.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)


    def checkOnline(self):
        self.yoHub.refreshDevice() 

    def checkDataUpdate(self):
        if self.yoHub.data_updated():
            self.updateData()

    def updateData(self):
        if self.node is not None:
            state =  self.yoHub.getState().upper()
            if self.yoHub.online:
                #if state == 'ON':
                #    self.node.setDriver('GV0', 1, True, True)
                #elif  state == 'OFF':
                #    self.node.setDriver('GV0', 0, True, True)
                #else:
                #    self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('ST', 1)
            else:
                self.node.setDriver('ST', 0)
                #self.pollDelays()

    def updateStatus(self, data):
        logging.info('updateStatus - Hub')
        self.yoHub.updateStatus(data)
        self.updateData()
           
    def setWiFi (self, command):
        logging ('setWiFi')
        
    def setSSID (self, command):
        logging ('setSSID')
        ssidStr = command.get('value')

    def setPassword (self, command ):

        logging ('setPassword')
        passwordStr = command.get('value')
        
    '''
    def switchControl(self, command):
        logging.info('udiYoHub switchControl')
        state = int(command.get('value'))     
        if state == 1:
            self.yoHub.setState('ON')
        else:
            self.yoHub.setState('OFF')
        
    def setOnDelay(self, command ):
        logging.info('udiYoHub setOnDelay')
        delay =int(command.get('value'))
        self.yoHub.setOnDelay(delay)
        self.node.setDriver('GV1', delay*60, True, True)

    def setOffDelay(self, command):
        logging.info('udiYoHub setOffDelay')
        delay =int(command.get('value'))
        self.yoHub.setOffDelay(delay)
        self.node.setDriver('GV2', delay*60, True, True)
    '''

    def update(self, command = None):
        logging.info('udiYoHub Update Status')
        self.yoHub.refreshDevice()
        #self.yoHub.refreshSchedules()     


    commands = {
                'UPDATE': update,
                'QUERY' :update
                }




