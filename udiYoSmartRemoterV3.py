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

class udiRemoteKey(udi_interface.Node):
    id = 'smremotekey'
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 99, 'uom': 25},
            ]
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, convert_temp_unit, send_rel_temp_to_isy


    def __init__(self, polyglot, primary, address, name, key):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('__init__ smremotekey : {}'.format(key))
        self.key = key
        self.presstype = 99
        self.n_queue = []
        self.max_remote_keys = 8
        self.nbr_keys = 4
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


    def start(self):
         logging.debug('start smremotekey : {}'.format(self.key))

    def stop(self):
         logging.debug('stopsmremotekey : {}'.format(self.key))
    
    
    def noop(self, command = None):
        pass
    
    def get_new_state(self, presstype, state):
        logging.debug('key_pressed = key {} - presstype = {}'.format(self.key , self.presstype ))
        if 0 == presstype:
            new_state = 'DOF'
        elif 1 == presstype:
            new_state = 'DON'
        elif 2 == presstype:
            new_state = 'DFOF'
        elif 3 == presstype:
            new_state = 'DFON'
        elif 4 == presstype:
            if 'DON' == state:
                new_state = 'DOF'
                #self.node.reportCmd(self.state)
            elif 'DON' == state:
                new_state = 'DON'
                #self.node.reportCmd(self.state)
            else:
                logging.error('Wrong state exists: {}'.format(self.state))
        elif 5 == presstype :
            if 'DFON' == state:
                new_state = 'DFOF'
                #self.node.reportCmd(state)
            elif 'DFON' == state:
                new_state = 'DFON'
                #self.node.reportCmd(state)
            else:
                logging.error('Wrong state exists: {}'.format(self.state))                
        else:
            logging.info('No scene state defined for key {}'.format(self.key))
            new_state = "UNKNOWN"
        return(new_state)

    def key_presstype(self, command):
        val = int(command.get('value'))   
        logging.debug('key_presstype {}'.format(val))
        self.presstype = val
        if 4 == self.presstype:
            self.state = 'DOF'
        elif 5 == self.presstype:
            self.state = 'DFOF'

  
    def long_key_presstype(self, command):
        val = int(command.get('value'))   
        logging.debug('keyL_presstype {}'.format(val))
        #self.set_key_press_type(1, 'normal', val)
        self.long_presstype = val
        if 4 == self.long_presstype:
            self.long_press_state = 'DOF'
        elif 5 == self.long_presstype:
            self.long_press_state = 'DFOF'
    
    commands = {
                'KEYPRESS'  : key_presstype, 
                'KEYLPRESS' : long_key_presstype,
                'DON'       : noop,
                'DOF'       : noop,    
    }
class udiYoSmartRemoter(udi_interface.Node):
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, convert_temp_unit, send_rel_temp_to_isy

    id = 'yosmremote'

    '''
       drivers = [
            'GV0' = Keypress
            'GV1' = Keynumber
            'GV2' = press type
            'GV3' = batlevel
            'CLITEMP' = temperature   
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

            ]




    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoSmartRemoter INIT- {}'.format(deviceInfo['name']))
        self.address = address
        self.poly = polyglot
        self.primary = primary
        self.name = name
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo   
        self.yoSmartRemote  = None
        self.last_state = 99
        self.n_queue = []
        self.max_remote_keys = 8
        self.nbr_keys = 4
        self.keys = {}
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

    '''
    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()
    '''


    def start(self):
        logging.info('start - udiYoSmartRemoter')
        self.yoSmartRemote  = YoLinkSmartRemote(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.yoSmartRemote.initNode()
        time.sleep(2)
        #self.node.setDriver('ST', 1, True, True)
        for key in range(1, 4):
            address = 'key'+str(key)
            name = self.address
            self.keys[address] = udiRemoteKey(self.poly, self.primary, address, name, key)

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
                            press = self.max_remote_keys
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
        self.yoSmartRemote.refreshDevice()
    

    def noop(self, command = None):
        pass

    commands = {
                'UPDATE'    : update,
                'QUERY'     : update, 
                }





