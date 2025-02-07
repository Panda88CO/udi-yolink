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
    from  udiYolinkLib import my_setDriver, save_cmd_struct, retrieve_cmd_struct, bool2ISY, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'smremotekey'
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25}, # Command
            {'driver': 'GV1', 'value': 0, 'uom': 25}, # Short Keypress setting
            {'driver': 'GV2', 'value': 1, 'uom': 25}, # Long Keypress setting
            ]

    def __init__(self, polyglot, primary, address, name, key):
        super().__init__( polyglot, primary, address, name)

        logging.debug('__init__ smremotekey : {} {} {}'.format(address,name, key))
        self.key = key
        self.poly = polyglot
        self.address = address
        self.LONG_CMD = self.address+'_L_CMD'
        self.SHORT_CMD = self.address+'_S_CMD'
        self.name = name
        self.primary = primary
        #self.presstype = 99
        self.long_press_state = 'UNKNOWN'
        self.short_press_state = 'UNKNOWN'
        self.cmd_struct = {}
        self.cmd_struct = self.retrieve_cmd_struct()
        if self.cmd_struct == {}:
            self.cmd_struct['short_press'] = 1
            self.cmd_struct['long_press']  = 0
            self.save_cmd_struct(self.cmd_struct)
        self.configDone = False
        self.n_queue = []

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        #self.KeyOperations = Custom(self.poly, 'customdata')
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        #self.poly.subscribe(self.poly.CUSTOMDATA, self.handleData)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configHandler)
        # start processing events and create add our controller node
        
        polyglot.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
     
        
    def start(self):
        logging.debug('start / initialize smremotekey : {}'.format(self.key))
        while not self.configDone:
            time.sleep(1)
        '''
        if self.SHORT_CMD in self.KeyOperations:
            self.cmd_struct['short_press'] = self.KeyOperations[self.SHORT_CMD]
        else:
            self.KeyOperations[self.SHORT_CMD] = 1
            self.cmd_struct['short_press'] = 1

        if self.LONG_CMD in self.KeyOperations:
            self.cmd_struct['long_press'] = self.KeyOperations[self.LONG_CMD]
        else:
            self.KeyOperations[self.LONG_CMD] = 1
            self.cmd_struct['long_press'] = 1
        '''

        self.node.setDriver('GV0', 99)
        self.node.setDriver('GV1', self.cmd_struct['short_press'])
        self.node.setDriver('GV2', self.cmd_struct['long_press'])


    def stop(self):
        logging.debug('stop smremotekey : {}'.format(self.key))
       
    def checkOnline(self):
        pass #this is a sub node - main node reflects on line

    def checkDataUpdate(self):
        pass

    def updateLastTime(self):
        pass

    '''
    def handleData(self, data):
        self.KeyOperations.load(data)
        logging.debug('handleData {}'.format(data))
        try:
            if data is None: #Initialize
                self.cmd_struct['long_press'] = 0
                self.cmd_struct['short_press'] = 1
            else:
                if self.LONG_CMD in data:
                    self.cmd_struct['long_press'] = data[self.LONG_CMD]
                else:
                    self.cmd_struct['long_press'] = 0
                if self.SHORT_CMD in data:
                    self.cmd_struct['short_press'] = data[self.SHORT_CMD]
                else:
                    self.cmd_struct['short_press'] = 1            
        except Exception as e:
            logging.info('No Key definitions exist yet : {}'.format(e))
    '''

    def configHandler(self):
        self.configDone = True

    def noop(self, command = None):
        pass
    
    def send_command (self, press_type):
        logging.debug('send_command - press type : {}'.format(press_type))
        if press_type == 0 or press_type == 'Press' : #short press
            self.short_press_state, isy_val = self. get_new_state(self.cmd_struct['short_press'], self.short_press_state)
            if self.short_press_state  != 'UNKNOWN':
                self.node.reportCmd(self.short_press_state )
            self.node.setDriver('GV0', isy_val)
            logging.debug('send short press command cmd:{} driver{}'.format(self.short_press_state, isy_val))
        else:
            self.long_press_state, isy_val = self. get_new_state(self.cmd_struct['long_press'], self.long_press_state)
            if self.long_press_state  != 'UNKNOWN':
                self.node.reportCmd(self.long_press_state )
            self.node.setDriver('GV0', isy_val)
            logging.debug('send long press command cmd:{} driver{}'.format(self.long_press_state, isy_val))
            

    def get_new_state(self, cmd_type, state):
        logging.debug('key_pressed = key {} - cmd_type = {} state {}'.format(self.key , cmd_type, state ))
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
            logging.info('No state defined for key {}'.format(self.key))
            new_state = "UNKNOWN"
            isy_val = 99
        return(new_state, isy_val)

    def short_cmdtype(self, command):
        val = int(command.get('value'))   
        logging.debug('short_cmdtype {}'.format(val))
        self.cmd_struct['short_press'] = val
        #self.KeyOperations[self.SHORT_CMD] = val  
        self.node.setDriver('GV1', val, True, True)
        self.save_cmd_struct(self.cmd_struct)

    def long_cmdtype(self, command):
        val = int(command.get('value'))   
        logging.debug('long_cmdype {}'.format(val))
        self.cmd_struct['long_press'] = val
        #self.KeyOperations[self.LONG_CMD] = val
        self.node.setDriver('GV2', val, True, True)
        self.save_cmd_struct(self.cmd_struct)

        
    commands = {
                'KEYPRESS'  : short_cmdtype, 
                'KEYLPRESS' : long_cmdtype,
                'DON'       : noop,
                'DOF'       : noop,    
    }


class udiYoSmartRemoter(udi_interface.Node):
    from  udiYolinkLib import node_queue, wait_for_node_done

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
            {'driver': 'GV20', 'value': 99, 'uom': 25},
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
        self.node_ready = False
        self.last_state = 99
        self.n_queue = []
        self.max_remote_keys = 8
        model = str(self.devInfo['modelName'][:6])
        if model in ['YS3614', 'YS3615']:
             self.nbr_keys = 2
        else:
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
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        
        self.nodesOK = False

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
        self.node.setDriver('ST', 0, True, True)
        self.yoSmartRemote  = YoLinkSmartRemote(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.yoSmartRemote.initNode()
        time.sleep(2)
        #self.node.setDriver('ST', 1, True, True)
        for key in range(0, self.nbr_keys):
            k_address =  self.address[4:14]+'key' + str(key)
            k_address = self.poly.getValidAddress(str(k_address))

            k_name =  str(self.name) + ' key' + str(key+1)
            k_name = self.poly.getValidName(str(k_name))

            self.keys[key] = udiRemoteKey(self.poly, self.address, k_address, k_name, key)
            self.adr_list.append(k_address)
            self.wait_for_node_done()
        self.nodesOK = True
        self.node_ready = True

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
        if mask == 0:
            return(0)
        else:
            return(int(round(math.log2(mask),0)))

    def updateLastTime(self):
        pass
    
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
                        logging.debug('remote key {} press {}'.format(remote_key, press))
                        
                        while not self.nodesOK:
                            time.sleep(1)
                        if self.yoSmartRemote.isControlEvent():
                            self.keys[remote_key].send_command(press)
                            self.yoSmartRemote.clearEventData()
                            logging.debug('clearEventData')
                        self.node.setDriver('GV0', remote_key + press)
                        self.node.setDriver('GV1', remote_key)
                        self.node.setDriver('GV2', press)                        
                    self.node.setDriver('GV3', self.yoSmartRemote.getBattery())
                    logging.debug("udiYoSmartRemoter temp: {}".format(self.yoSmartRemote.getDevTemperature()))
                    if self.temp_unit == 0:
                        self.node.setDriver('CLITEMP', round(self.yoSmartRemote.getDevTemperature(),1), True, True, 4)
                    elif self.temp_unit == 1:
                        self.node.setDriver('CLITEMP', round(self.yoSmartRemote.getDevTemperature()*9/5+32,1), True, True, 17)
                    elif self.temp_unit == 2:
                        self.node.setDriver('CLITEMP', round(self.yoSmartRemote.getDevTemperature()+273.15,1), True, True, 26)
                    else:
                        self.node.setDriver('CLITEMP', 99, True, True, 25)
                    self.node.setDriver('ST', 1)
                    if self.yoSmartRemote.suspended:
                        self.node.setDriver('GV20', 1)
                    else:
                        self.node.setDriver('GV20', 0)
                else:

                    self.node.setDriver('ST', 0, True, True)
                    self.node.setDriver('GV20', 2)
        except Exception as e:
            logging.error('Smart Remote  updateData exeption: {}'.format(e))



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





