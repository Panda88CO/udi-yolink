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

import time
import math
from yolinkSmartRemoterV2 import YoLinkSmartRemote



class udiYoSmartRemoter(udi_interface.Node):
    id = 'yosmremote'
    
    '''
       drivers = [
            'GV0' = RemoteKey 
            'GV1' = Battery Level

            'ST' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25}, 
            {'driver': 'GV2', 'value': 99, 'uom': 25}, 
            {'driver': 'GV3', 'value': 99, 'uom': 25},     
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25},            
            {'driver': 'ST', 'value': 0, 'uom': 25},

            #{'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoSmartRemoter INIT- {}'.format(deviceInfo['name']))
        self.adress = address
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo   
        self.yoSmartRemote  = None
        self.last_state = 99
        self.n_queue = []
        self.max_remore_keys = 8
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
        logging.info('start - udiYoSmartRemoter')
        self.yoSmartRemote  = YoLinkSmartRemote(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.yoSmartRemote.initNode()
        time.sleep(2)
        #self.node.setDriver('ST', 1, True, True)

    def stop (self):
        logging.info('Stop udiYoSmartRemoter')
        self.node.setDriver('ST', 0, True, True)
        self.yoSmartRemote.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkOnline(self):
        self.yoSmartRemote.refreshDevice()   
    
    def checkDataUpdate(self):
        if self.yoSmartRemote.data_updated():
            self.updateData()

    def mask2key (self, mask):
        logging.debug('mask2key : {}'.format(mask))
        return(int(round(math.log2(mask),0)))


    def updateData(self):
        try:
            if self.node is not None:
                if self.yoSmartRemote.online:               
                    event_data = self.yoSmartRemote.getEventData()
                    if event_data:
                        key_mask = event_data['keyMask']
                        press_type = event_data['type']
                        remote_key = self.mask2key(key_mask)
                        if press_type == 'LongPress':
                            press = self.max_remore_keys
                        else:
                            press = 0
                    self.node.setDriver('GV0', remote_key + press, True, True)
                    self.node.setDriver('GV1', remote_key, True, True)
                    self.node.setDriver('GV2', press, True, True)
                    self.node.setDriver('GV3', self.yoSmartRemote.getBattery(), True, True)
                    logging.debug("udiYoSmartRemoter temp: {}".format(self.yoSmartRemote.getDevTemperature()))
                    if self.temp_unit == 0:
                        self.node.setDriver('CLITEMP', round(self.yoSmartRemote.getDevTemperature(),1), True, True, 4)
                    elif self.temp_unit == 1:
                        self.node.setDriver('CLITEMP', round(self.yoSmartRemote.getDevTemperature()*9/5+32,1), True, True, 17)
                    elif self.temp_unit == 2:
                        self.node.setDriver('CLITEMP', round(self.yoSmartRemote.getDevTemperature()+273.15,1), True, True, 26)
                    else:
                        self.node.setDriver('CLITEMP', 99, True, True, 25)
                    self.node.setDriver('ST', 1, True, True)
                else:
                    self.node.setDriver('GV0', 99, True, True)
                    self.node.setDriver('GV1', 99, True, True)
                    self.node.setDriver('GV2', 99, True, True)
                    self.node.setDriver('GV3', 99, True, True)
                    self.node.setDriver('CLITEMP', 99, True, True, 25)
                    self.node.setDriver('ST', 1, True, True)
        except Exception as E:
            logging.error('Smart Remote get updateData exeption: {}'.format(E))



    def updateStatus(self, data):
        logging.info('updateStatus - udiYoSmartRemoter')
        self.yoSmartRemote.updateStatus(data)
        self.updateData()



    def update(self, command = None):
        logging.info('udiYoSmartRemoter Update  Executed')
        self.yoSmartRemote.refreshSensor()
       

    def noop(self, command = None):
        pass

    commands = {
                'UPDATE': update,
                'QUERY' : update, 
                'DON'   : noop,
                'DOF'   : noop
                }





