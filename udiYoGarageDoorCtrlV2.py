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
from yolinkGarageDoorToggleV2 import YoLinkGarageDoorCtrl




class udiYoGarageDoor(udi_interface.Node):
    id = 'yogarage'
    
    '''
       drivers = [
            'ST' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},   
            #{'driver': 'ST', 'value': 1, 'uom': 25},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        
        self.yoAccess=yoAccess
        self.devInfo =  deviceInfo   
        self.yoDoorControl  = None
        self.node_ready = False
        logging.debug('udiYoGarageDoor INIT - {}'.format(deviceInfo['name']))
        self.n_queue = []
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
        logging.info('start - udiYoGarageDoor')
        self.node.setDriver('ST', 0, True, True)
        self.yoDoorControl = YoLinkGarageDoorCtrl(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)
        self.node_ready = True

    def initNode(self):
        self.yoDoorControl.online = True
        #self.node.setDriver('ST', 1, True, True)
        
    def checkOnline(self):
        pass
        
    def checkDataUpdate(self):
        pass
    
    def stop (self):
        logging.info('Stop udiYoGarageDoor')
        self.node.setDriver('ST', 0, True, True)
        self.yoDoorControl.shut_down()

    
    def updateStatus(self, data):
        logging.debug('updateStatus - udiYoGarageDoor')
        self.yoDoorControl.updateCallbackStatus(data)
        if self.yoDoorControl.suspended:
            self.node.setDriver('GV20', 1, True, True)
        else:
            self.node.setDriver('GV20', 0)

        if self.yoDoorControl.online:
            self.node.setDriver('ST', 1)
        else:
            self.node.setDriver('GV20', 2, True, True)
            #self.node.setDriver('ST', 0, True, True)

        

        #logging.debug(data)
        #if self.node is not None:
        #    self.node.setDriver('ST',1, True, True)


    def toggleDoor(self, command = None):
        logging.info('GarageDoor Toggle Door')
        self.yoDoorControl.toggleDevice()
        self.node.reportCmd('DON')
        time.sleep(1.5)
        self.node.reportCmd('DOF')

    commands = {
                    'TOGGLE': toggleDoor,
                    'DON'   : toggleDoor,
                    'DOF'   : toggleDoor,
                }




