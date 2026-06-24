#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
import importlib
from os import truncate
import threading
try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom

import time
import math
from yolinkSmartRemoterV3 import YoLinkSmartRemoter


SINGLE_PRESS_REMOTE_MODELS = {
    'YS3605', 'YS3615', 'YS3606', 'YS3607',
}
TWO_KEY_REMOTE_MODELS = {'YS3614', 'YS3615'}
REMOTE_TYPE_SINGLE_PRESS = 0
REMOTE_TYPE_DUAL_PRESS = 1

class udiRemoteKey(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_struct, retrieve_cmd_struct, node_queue, wait_for_node_done, mask2key, set_node_custom, get_node_custom, checkNameSync

    id = 'smremotekey'
    drivers = [
            {'driver': 'ST', 'value': 99, 'uom': 25}, # Command
            {'driver': 'GV1', 'value': 0, 'uom': 25}, # Short Keypress setting
            {'driver': 'GV2', 'value': 1, 'uom': 25}, # Long Keypress setting
            {'driver': 'TIME', 'value': 0, 'uom': 151}, # Last successful key press (unix time)
            ]
    single_press_drivers = [
            {'driver': 'ST', 'value': 99, 'uom': 25}, # Command
            {'driver': 'GV1', 'value': 0, 'uom': 25}, # Press setting
            {'driver': 'TIME', 'value': 0, 'uom': 151}, # Last successful key press (unix time)
            ]

    def __init__(self, polyglot, primary, address, name, key, single_press_only=False, single_press_event_type='Press'):
        super().__init__( polyglot, primary, address, name)

        logging.debug('__init__ smremotekey : {} {} {}'.format(address,name, key))
        self.key = key
        self.single_press_only = single_press_only
        self.single_press_event_type = single_press_event_type
        self.poly = polyglot
        self.address = address
        self.node_ready = False
        self.LONG_CMD = self.address+'_L_CMD'
        self.SHORT_CMD = self.address+'_S_CMD'
        self.name = name
        self.primary = primary
        self.id = 'smremotekeysingle' if self.single_press_only else 'smremotekeydual'
        if self.single_press_only:
            self.drivers = [dict(d) for d in type(self).single_press_drivers]
        else:
            self.drivers = [dict(d) for d in type(self).drivers]
        #self.presstype = 99
        self.long_press_state = 'UNKNOWN'
        self.short_press_state = 'UNKNOWN'
        self.cmd_struct = {}
        self.cmd_struct = self.retrieve_cmd_struct()
        if self.cmd_struct == {}:
            self.cmd_struct['short_press'] = 1
            self.cmd_struct['long_press']  = 0
            self.cmd_struct['last_press_time'] = 0
            if self.single_press_only:
                self.cmd_struct['press_command'] = self._resolve_single_press_command({})
            self.save_cmd_struct(self.cmd_struct)
        else:
            if 'last_press_time' not in self.cmd_struct:
                self.cmd_struct['last_press_time'] = 0
            if self.single_press_only and 'press_command' not in self.cmd_struct:
                self.cmd_struct['press_command'] = self._resolve_single_press_command(self.cmd_struct)
            self.save_cmd_struct(self.cmd_struct)
        self.configDone = False
        self.n_queue = []

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        #self.KeyOperations = Custom(self.poly, 'customdata')
        self.poly.subscribe(self.poly.START, self.start, self.address)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        #self.poly.subscribe(self.poly.CUSTOMDATA, self.handleData)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configHandler)
        # start processing events and create add our controller node
        
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        # persist or restore saved name for key node
        try:
            saved = self.get_node_custom('saved_name')
            if saved:
                saved = self.poly.getValidName(saved)
                self._name_sync_saved = saved
                self.set_node_custom('saved_name', saved)
                if self.node.name != saved:
                    try:
                        self.node.rename(saved)
                        logging.info(f'Restored key node name for {self.address} to saved name {saved}')
                    except Exception as e:
                        logging.debug(f'Failed to restore key node name for {self.address}: {e}')
            else:
                self.set_node_custom('saved_name', self.node.name)
                self._name_sync_saved = self.node.name
        except Exception as e:
            logging.debug(f'Error handling key custom name for {self.address}: {e}')
        self.node_ready = True
        
    def start(self):
        logging.debug('start / initialize smremotekey : {}'.format(self.key))
        while not self.configDone or not self.node_ready:
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

        self.my_setDriver('ST', 99)
        if self.single_press_only:
            self.my_setDriver('GV1', self.cmd_struct['press_command'], 25)
        else:
            self.my_setDriver('GV1', self.cmd_struct['short_press'], 25)
            self.my_setDriver('GV2', self.cmd_struct['long_press'], 25)
        self.my_setDriver('TIME', self.cmd_struct.get('last_press_time', 0), 151)
        self.system_ready=True

    def stop(self):
        logging.debug('stop smremotekey : {}'.format(self.key))
       
    def checkOnline(self):
        pass #this is a sub node - main node reflects on line

    def checkDataUpdate(self):
        pass

    def updateLastTime(self):
        unix_time = int(time.time())
        self.cmd_struct['last_press_time'] = unix_time
        self.my_setDriver('TIME', unix_time, 151)
        self.save_cmd_struct(self.cmd_struct)

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

    def _resolve_single_press_command(self, cmd_struct):
        expected_press = str(self.single_press_event_type or 'Press')
        primary_key = 'long_press' if expected_press == 'LongPress' else 'short_press'
        fallback_key = 'short_press' if primary_key == 'long_press' else 'long_press'

        if primary_key in cmd_struct:
            return cmd_struct[primary_key]
        if fallback_key in cmd_struct:
            return cmd_struct[fallback_key]
        return 1
    
    def send_command (self, press_type):
        logging.info('send_command - press type : {}'.format(press_type))
        if self.single_press_only:
            command_state, isy_val = self.get_new_state(self.cmd_struct['press_command'], self.short_press_state)
            if command_state != 'UNKNOWN':
                logging.info('SmartRemoter key%d (%s) reportCmd sending %s for %s press', self.key + 1, self.address, command_state, press_type)
                self.node.reportCmd(command_state)
                logging.debug('SmartRemoter key%d (%s) reportCmd queued command %s', self.key + 1, self.address, command_state)
                self.short_press_state = command_state
                self.updateLastTime()
            self.my_setDriver('ST', isy_val, UOM=25, force=True)
            logging.debug('send single press command cmd:{} driver {}'.format(command_state, isy_val))
            return

        if press_type == 0 or press_type == 'Press' : #short press
            self.short_press_state, isy_val = self.get_new_state(self.cmd_struct['short_press'], self.short_press_state)
            if self.short_press_state  != 'UNKNOWN':
                logging.info('SmartRemoter key%d (%s) reportCmd sending %s for %s press', self.key + 1, self.address, self.short_press_state, press_type)
                self.node.reportCmd(self.short_press_state )
                logging.debug('SmartRemoter key%d (%s) reportCmd queued command %s', self.key + 1, self.address, self.short_press_state)
                self.updateLastTime()
            self.my_setDriver('ST', isy_val, UOM=25, force=True)

            logging.debug('send short press command cmd:{} driver{}'.format(self.short_press_state, isy_val))
        else:
            self.long_press_state, isy_val = self.get_new_state(self.cmd_struct['long_press'], self.long_press_state)
            if self.long_press_state  != 'UNKNOWN':
                logging.info('SmartRemoter key%d (%s) reportCmd sending %s for %s press', self.key + 1, self.address, self.long_press_state, press_type)
                self.node.reportCmd(self.long_press_state )
                logging.debug('SmartRemoter key%d (%s) reportCmd queued command %s', self.key + 1, self.address, self.long_press_state)
                self.updateLastTime()
            self.my_setDriver('ST', isy_val)
   
            logging.debug('send long press command cmd:{} driver {}'.format(self.long_press_state, isy_val))
            

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

            elif 'DFOF' == state:
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
        self.my_setDriver('GV1', val, UOM=25, force=True)
        self.save_cmd_struct(self.cmd_struct)

    def press_cmdtype(self, command):
        val = int(command.get('value'))
        logging.debug('press_cmdtype {}'.format(val))
        self.cmd_struct['press_command'] = val
        self.my_setDriver('GV1', val, UOM=25, force=True)
        self.save_cmd_struct(self.cmd_struct)

    def long_cmdtype(self, command):
        val = int(command.get('value'))   
        logging.debug('long_cmdype {}'.format(val))
        self.cmd_struct['long_press'] = val
        #self.KeyOperations[self.LONG_CMD] = val
        self.my_setDriver('GV2', val, UOM=25, force=True)
        self.save_cmd_struct(self.cmd_struct)

        
    commands = {
                'PRESSCMD'  : press_cmdtype,
                'KEYPRESS'  : short_cmdtype, 
                'KEYLPRESS' : long_cmdtype,
    }


class udiYoSmartRemoter(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  node_queue, wait_for_node_done, set_node_custom, get_node_custom, checkNameSync as sharedCheckNameSync, saveCurrentNodeNames

    id = 'yosmremote'


        
    drivers = [
            {'driver': 'ST', 'value': 99, 'uom': 25},
            {'driver': 'GV3', 'value': 99, 'uom': 25},
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},
            {'driver': 'GV30', 'value': 99, 'uom': 25},
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        
        logging.debug('udiYoSmartRemoter INIT- {}'.format(deviceInfo['name']))
        self.address = address
        self.poly = polyglot
        #self.primary = primary
        self.name = name
        self.yoAccess = yoAccess
        self.temp_unit = self.yoAccess.get_temp_unit()           
        if self.temp_unit == 1:
            self.id = 'yosmremoteF'

        
        self.devInfo =  deviceInfo   
        self.yoSmartRemote  = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self.main_node_ready = False
        self.sub_nodes_ready = False
        self._update_lock = threading.Lock()
        self.last_state = 99
        self.n_queue = []
        self._last_processed_press_signature = None
        self._last_status_packet = None
        self.max_remote_keys = 8
        self.model = str(self.devInfo.get('modelName', '')[:6])
        self.single_press_only = self.model in SINGLE_PRESS_REMOTE_MODELS
        self.remote_type = REMOTE_TYPE_SINGLE_PRESS if self.single_press_only else REMOTE_TYPE_DUAL_PRESS
        if self.model in TWO_KEY_REMOTE_MODELS:
             self.nbr_keys = 2
        else:
            self.nbr_keys = 4
        self.keys = {}
        logging.debug(f'Model {self.model} identified as remote type {self.remote_type} with {self.nbr_keys} keys and single_press_only={self.single_press_only}')
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(self.poly.START, self.start, self.address)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        

        # start processing events and create add our controller node
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)

        # persist or restore saved name for parent SmartRemoter
        try:
            saved = self.get_node_custom('saved_name')
            if saved:
                saved = self.poly.getValidName(saved)
                self._name_sync_saved = saved
                self.set_node_custom('saved_name', saved)
                if self.node.name != saved:
                    try:
                        self.node.rename(saved)
                        logging.info(f'Restored SmartRemoter node name for {self.address} to saved name {saved}')
                    except Exception as e:
                        logging.debug(f'Failed to restore SmartRemoter node name for {self.address}: {e}')
            else:
                self.set_node_custom('saved_name', self.node.name)
                self._name_sync_saved = self.node.name
        except Exception as e:
            logging.debug(f'Error handling SmartRemoter custom name for {self.address}: {e}')

        # Track the initial child-key build, but do not block parent readiness on it.
        self.main_node_ready = True
        self.node_ready = True

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
        while not self.main_node_ready  or not self.configDone:
            time.sleep(0.5)
        logging.debug(f'SmartRemoter {self.name} starting with model {self.model}, remote_type {self.remote_type}, single_press_only {self.single_press_only}')
        self.my_setDriver('ST', self.remote_type, UOM=25, force=True)
        self.my_setDriver('GV30', 0, UOM=25, force=True)
        self.yoSmartRemote  = YoLinkSmartRemoter(self.yoAccess, self.devInfo, self.updateStatus)
        self._ensure_key_nodes_created()
        time.sleep(2)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.yoSmartRemote.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoSmartRemote.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoSmartRemote.refreshDevice()
            tries += 1
        time.sleep(2)
        #self.my_setDriver('GV30', 1, UOM=25, force=True)
        self._capture_press_baseline(self.yoSmartRemote)
        self.sub_nodes_ready = True
        self.start_done()

    def _ensure_key_nodes_created(self):
        for key in range(0, self.nbr_keys):
            if key in self.keys:
                continue
            k_address =  self.address[4:14]+'key' + str(key)
            k_address = self.poly.getValidAddress(str(k_address))

            k_name =  str(self.name) + ' key' + str(key+1)
            k_name = self.poly.getValidName(str(k_name))

            self.keys[key] = udiRemoteKey(
                self.poly,
                self.address,
                k_address,
                k_name,
                key,
                single_press_only=self.single_press_only,
                single_press_event_type=self._get_single_press_event_type_for_key(key),
            )
            self.adr_list.append(k_address)

    def stop (self):
        logging.info('Stop udiYoSmartRemoter')
        self.my_setDriver('GV30', 0, UOM=25, force=True)
        remote = self._get_remote('stop')
        if remote is not None:
            remote.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_remote(self, caller):
        remote = getattr(self, 'yoSmartRemote', None)
        if remote is None:
            logging.warning('udiYoSmartRemoter.%s called before device initialization', caller)
        return remote

    def checkOnline(self):
        remote = self._get_remote('checkOnline')
        if remote is None:
            return
        remote.refreshDevice()
    
    def checkDataUpdate(self):
        remote = self._get_remote('checkDataUpdate')
        if remote is None:
            return
        if remote.data_updated():
            self.updateData()

    def checkNameSync(self):
        self.sharedCheckNameSync()
        for key_node in self.keys.values():
            if hasattr(key_node, 'checkNameSync'):
                key_node.checkNameSync()

    def mask2key (self, mask):
        logging.debug('mask2key : {}'.format(mask))
        if mask == 0:
            return(0)
        else:
            return(int(round(math.log2(mask),0)))

    def updateLastTime(self):
        pass

    def _get_single_press_event_type_for_key(self, key):
        if key % 2 == 0:
            return 'Press'
        return 'LongPress'

    def _extract_press_event(self, packet):
        if not isinstance(packet, dict):
            return None

        data = packet.get('data')
        if not isinstance(data, dict):
            return None

        event_data = data.get('event')
        if isinstance(event_data, dict):
            return event_data, packet.get('time'), packet.get('msgid')

        state_data = data.get('state')
        if isinstance(state_data, dict):
            event_data = state_data.get('event')
            if isinstance(event_data, dict):
                return event_data, packet.get('time'), packet.get('msgid')

        return None

    def _get_press_info(self, remote):
        signature_time = remote.lastUpdate() if remote is not None else None
        signature_msgid = None

        extracted = self._extract_press_event(self._last_status_packet)
        if extracted is not None:
            event_data, signature_time, signature_msgid = extracted
        else:
            event_data = remote.get_data('event', 'state')
            if not isinstance(event_data, dict):
                return None

        key_mask = event_data.get('keyMask')
        press_type = event_data.get('type')

        # Some Smart Remoter payloads include stale event snapshots with type=report.
        # Treat those as non-press updates and ignore keyMask/type for command dispatch.
        if isinstance(press_type, str) and press_type.lower() == 'report':
            logging.debug('SmartRemoter (%s) ignoring stale report event payload: %s', self.address, event_data)
            return None

        if not isinstance(key_mask, int) or not isinstance(press_type, str):
            return None

        remote_key = self.mask2key(key_mask)
        if not isinstance(remote_key, int) or remote_key not in self.keys:
            return None

        press = self.max_remote_keys if press_type == 'LongPress' else 0
        signature = (signature_time, signature_msgid, key_mask, press_type)
        return {
            'remote_key': remote_key,
            'press_type': press_type,
            'press': press,
            'signature': signature,
        }

    def _capture_press_baseline(self, remote):
        if remote is None:
            return
        press_info = self._get_press_info(remote)
        if press_info is not None:
            self._last_processed_press_signature = press_info['signature']
    
    def updateData(self):
        remote = self._get_remote('updateData')
        if remote is None:
            return
        try:
            if self.node is not None:
                while not self.node_ready or not self.system_ready or not self.configDone:
                    time.sleep(0.5)
                message_info = remote.get_message_type()
                if remote.check_system_online():      


                    #event_data = self.yoSmartRemote.getEventData()
                    #logging.debug('updateData - event data {}'.format(event_data))
                    press_info = self._get_press_info(remote)
                    if press_info is not None:
                        remote_key = press_info['remote_key']

                        # Only send command for actual event messages, not status responses (getState)
                        if message_info[0] == 'event' and press_info['signature'] != self._last_processed_press_signature:
                            self.keys[remote_key].send_command(press_info['press_type'])
                            self._last_processed_press_signature = press_info['signature']
                    if isinstance(self.remote_type, int):
                        self.my_setDriver('ST', self.remote_type, UOM=25)
                    battery = remote.get_data('battery', 'state')
                    if isinstance(battery, int) or battery is None  :                
                        self.my_setDriver('GV3', battery, UOM=25)
                    tempC = remote.get_data('devTemperature', 'state')
                    logging.debug("udiYoSmartRemoter temp: {}".format(tempC))
                    if isinstance(tempC, (int, float)):
                        if self.temp_unit == 0:
                            self.my_setDriver('CLITEMP', round(tempC), UOM=4)
                        elif self.temp_unit == 1:
                            self.my_setDriver('CLITEMP', round(tempC*9/5+32,1), UOM=17)
                    elif    tempC is None:
                        self.my_setDriver('CLITEMP', tempC, UOM=25)   

                    self.my_setDriver('GV30', 1,UOM=25)
                    if remote.suspended:
                        self.my_setDriver('GV20', 1, UOM=25)
                    else:
                        self.my_setDriver('GV20', 0, UOM=25)
                else:
                    self.my_setDriver('GV30', 0, UOM=25)
                    self.my_setDriver('GV20', 2, UOM=25)
        except Exception as e:
            logging.error('Smart Remote updateData exeption: {}'.format(e))
            logging.exception('SmartRemoter updateData traceback')



    def updateStatus(self, data):
        logging.info('updateStatus - udiYoSmartRemoter')
        remote = self._get_remote('updateStatus')
        if remote is not None:
            with self._update_lock:
                self._last_status_packet = data
                remote.updateStatus(data)
            self.updateData()

    def update(self, command = None):
        logging.info('udiYoSmartRemoter Update  Executed')
        self.saveCurrentNodeNames()
        remote = self._get_remote('update')
        if remote is None:
            return
        remote.refreshDevice()
    

    def noop(self, command = None):
        pass

    commands = {
                'UPDATE'    : update,
  
                }






