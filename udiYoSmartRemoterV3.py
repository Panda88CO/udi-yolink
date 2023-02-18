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
            {'driver': 'GV0', 'value': 99, 'uom': 25}, # Command
            {'driver': 'GV1', 'value': 99, 'uom': 25}, # Short Keypress setting
            {'driver': 'GV2', 'value': 99, 'uom': 25}, # Long Keypress setting

            ]
    from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, convert_temp_unit, send_rel_temp_to_isy


    def __init__(self, polyglot, primary, address, name, key):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('__init__ smremotekey : {} {} {}'.format(address,name, key))
        self.key = key
        self.poly = polyglot
        self.address = address
        self.name = name
        self.primary = primary
        #self.presstype = 99
        self.long_press_state = 99
        self.short_press_state = 99
        self.short_cmd_type = 99
        self.long_cmd_type = 99

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
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)


    def start(self):
         logging.debug('start smremotekey : {}'.format(self.key))

    def stop(self):
         logging.debug('stopsmremotekey : {}'.format(self.key))
    
    def checkDataUpdate(self):
        pass

    def noop(self, command = None):
        pass
    
    def send_command (self, press_type):
        logging.debug('send_command - press type : {}'.format(press_type))
        if press_type == 0: #short press
            self.short_press_state, isy_val = self. get_new_state(self.short_cmd_type, self.short_press_state)
            self.node.reportCmd(self.short_press_state )
            self.node.setDriver('GV0', isy_val)
        else:
            self.short_press_state, isy_val = self. get_new_state(self.short_cmd_type, self.short_press_state)
            self.node.reportCmd(self.long_press_state )
            self.node.setDriver('GV0', isy_val)


    def get_new_state(self, cmd_type, state):
        logging.debug('key_pressed = key {} - cmd_type = {}'.format(self.key , cmd_type ))
        if 0 == cmd_type:
            new_state = 'DOF'
            isy_val = 0
        elif 1 == cmd_type:
            new_state = 'DON'
            isy_val = 1
        elif 2 == cmd_type:
            new_state = 'DFOF'
            isy_val = 2
        elif 3 == cmd_type:
            new_state = 'DFON'
            isy_val = 3
        elif 4 == cmd_type:
            if 'DON' == state:
                new_state = 'DOF'
                isy_val = 0
            elif 'DOF' == state:
                new_state = 'DON'
                isy_val = 1
            elif 'UNKNOWN' == state: # Force
                new_state = 'DOF'
                isy_val = 0
            else:
                logging.error('Wrong state exists: {}'.format(self.state))
                new_state = "UNKNOWN"
                isy_val = 99

        elif 5 == cmd_type :
            if 'DFON' == state:
                new_state = 'DFOF'
                isy_val = 2

            elif 'DFON' == state:
                new_state = 'DFON'
                isy_val = 3

            elif 'UNKNOWN' == state: #force a start value of off
                new_state = 'DFOF'
                isy_val = 2
            else:
                logging.error('Wrong state exists: {}'.format(self.state)) 
                new_state = "UNKNOWN"
                isy_val = 99  
        else:
            logging.info('No scene state defined for key {}'.format(self.key))
            new_state = "UNKNOWN"
            isy_val = 99
        return(new_state, isy_val)

    def short_cmdtype(self, command):
        val = int(command.get('value'))   
        logging.debug('short_cmdtype {}'.format(val))
        self.short_cmd_type = val
        self.node.setDriver('GV1', val, True, True)


  
    def long_cmdype(self, command):
        val = int(command.get('value'))   
        logging.debug('long_cmdype {}'.format(val))
        self.long_cmd_type = val
        self.node.setDriver('GV2', val, True, True)

    commands = {
                'KEYPRESS'  : short_cmdtype, 
                'KEYLPRESS' : long_cmdype,
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
        #self.primary = primary
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
        self.poly.ready()
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
        for key in range(0, 4):
            k_address =  self.address[3:12]+'key' + str(key)
            k_address = self.getValidAddress(str(k_address))

            k_name =  str(self.name) + ' key' + str(key)
            k_name = self.getValidName(str(k_name))

            self.keys[key] = udiRemoteKey(self.poly, self.address, k_address, k_name, key)

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
                    logging.debug('updateData - event data {}'.format(event_data))
                    if event_data:
                        key_mask = event_data['keyMask']
                        press_type = event_data['type']
                        remote_key = self.mask2key(key_mask)
                        if press_type == 'LongPress':
                            press = self.max_remote_keys
                        else:
                            press = 0
                        logging.debug('remote key {} press{}'.format(remote_key, press))
                        self.keys[remote_key].send_command(press)
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





