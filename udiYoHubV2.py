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

class udiYoBatteryHub(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, wait_for_node_done, node_queue
    id = 'yohubbat'
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'ST', 'value': 99, 'uom': 25},
            {'driver': 'GV30', 'value': 99, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},   
            {'driver': 'TIME', 'value': int(time.time()), 'uom': 151},
            #{'driver': 'ST', 'value': 0, 'uom': 25},
            ]
    '''
       drivers = [
            'ST' =  Powered
            'GV1' = Battery Level
            'GV30' = Online
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
    
 

    def start(self):
        logging.info('start - udiYoHub')
        self.yoHub  = YoLinkHu(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoHub.initNode()
        self.node_ready = True
        time.sleep(1)
        self.yoHub.refreshDevice()


    def updateDelayCountdown (self, delayRemaining ) :
        logging.debug('updateDelayCountdown {}'.format(delayRemaining))

    def stop (self):
        logging.info('Stop udiYoHub')
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)

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

            if self.yoHub.online:
                pwr_info = self.yoHub.getPowerInfo()
                if 'powered' in pwr_info and pwr_info['powered'] != True: 
                    self.my_setDriver('ST', 1)
                else:
                    self.my_setDriver('ST', 0)
                if  'batteryState' in pwr_info:
                    self.my_setDriver('GV0', pwr_info['batteryState'])  
                self.my_setDriver('GV30', 1)
                if self.yoHub.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)
                #self.pollDelays()

    def updateStatus(self, data):
        logging.info('updateStatus - Hub')
        self.yoHub.updateStatus(data)
        self.updateData()
           

    def update(self, command = None):
        logging.info('udiYoHub Update Status')
        self.yoHub.refreshDevice()
        #self.yoHub.refreshSchedules()     


    commands = {
                'UPDATE': update,
                }



class udiYoHub(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, wait_for_node_done, node_queue
    id = 'yohub'
    drivers = [
            #{'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},   
            {'driver': 'TIME', 'value': int(time.time()), 'uom': 151},
            #{'driver': 'ST', 'value': 0, 'uom': 25},
            ]
    '''
       drivers = [
            'ST' =  Online
            'GV1' = Battery Level
            'GV30' = Online
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
    
 

    def start(self):
        logging.info('start - udiYoHub')
        self.yoHub  = YoLinkHu(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.my_setDriver('ST', 1)
        self.yoHub.initNode()

        
        #if not self.yoHub.online:
        #    logging.warning('Device {} not on-line'.format(self.devInfo['name']))            
        #else:
        #    self.node.setDriver('ST', 1, True, True)
        self.node_ready = True

    def updateDelayCountdown (self, delayRemaining ) :
        logging.debug('updateDelayCountdown {}'.format(delayRemaining))

    def stop (self):
        logging.info('Stop udiYoHub')
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)

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

            if self.yoHub.online:
                #if state == 'ON':
                #    self.node.setDriver('GV0', 1, True, True)
                #elif  state == 'OFF':
                #    self.node.setDriver('GV0', 0, True, True)
                #else:
                #    self.node.setDriver('GV0', 99, True, True)
                self.my_setDriver('ST', 1)
                self.my_setDriver('GV30', 1)
                if self.yoHub.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

            else:
                self.my_setDriver('ST', 0)
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)
                #self.pollDelays()

    def updateStatus(self, data):
        logging.info('updateStatus - Hub')
        self.yoHub.updateStatus(data)
        self.updateData()
           

    def update(self, command = None):
        logging.info('udiYoHub Update Status')
        self.yoHub.refreshDevice()
        #self.yoHub.refreshSchedules()     


    commands = {
                'UPDATE': update,
                }
