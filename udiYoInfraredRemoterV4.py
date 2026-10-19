#!/usr/bin/env python3
"""
MIT License
"""

import importlib

try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom

from ctypes import set_errno
from os import truncate
import threading
#import udi_interface
#import sys
import time
from yolinkInfraredRemoterV3 import YoLinkInfraredRemoter
from udiYoSchedule import udiYoSchedule

class udiYoInfraredCode(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, node_queue, wait_for_node_done, set_node_custom, get_node_custom, checkNameSync, apply_profile_driver_names

    '''
       drivers = [

            'GV2' = Command status
            'GV5' = Online
            ]
    ''' 
    
    id = 'yoircode'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'TX success'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},       
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},                 
            ] 
    def  __init__(self, polyglot, primary, address, name, code_indx, yoIRrem, yoAccess):
        logging.debug('udiIRcode'.format(code_indx))
        super().__init__( polyglot, primary, address, name)   
        self.yoIRrem = yoIRrem
        self.yoAccess = yoAccess    
        self.code = code_indx
        self.n_queue = []   
       
        #self.poly.subscribe(polyglot.START, self.start, self.address)
        #self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        # persist current node name if not set, or restore saved name
        try:
            saved = self.get_node_custom('saved_name')
            if saved:
                saved = self.poly.getValidName(saved)
                self._name_sync_saved = saved
                self.set_node_custom('saved_name', saved)
                if self.node.name != saved:
                    try:
                        self.node.rename(saved)
                        logging.info(f'Restored node name for {self.address} to saved name {saved}')
                    except Exception as e:
                        logging.debug(f'Failed to restore node name for {self.address}: {e}')
            else:
                self.set_node_custom('saved_name', self.node.name)
                self._name_sync_saved = self.node.name
        except Exception as e:
            logging.debug(f'Error handling custom name for {self.address}: {e}')
        time.sleep(2)
        #self.updateData()


    def checkDataUpdate(self):
        remote = self._get_remote('checkDataUpdate')
        if remote is None:
            return
        if remote.data_updated():
            self.updateData()

    def _get_remote(self, caller):
        remote = getattr(self, 'yoIRrem', None)
        if remote is None:
            logging.warning('udiYoInfraredCode.%s called before infrared-remote initialization', caller)
        return remote
            
    def checkOnline(self):
        pass  #is it a sub node - do nothing

    def updateData(self):
        remote = self._get_remote('updateData')
        if remote is None:
            return
        if self.node is not None:
            #while not self.node_ready or not self.system_ready:
            #    time.sleep(0.5)
            #logging.debug('updateData - {}'.format(self.yoIRrem.check_system_online()))
            self.my_setDriver('TIME', remote.getLastUpdateTime(), 151)
            #self.my_setDriver('ST', 0)
            if remote.suspended:
                self.my_setDriver('GV20', 1)
            else:
                self.my_setDriver('GV20', 0)
        else:
            self.my_setDriver('GV20', 2)

    def clear_delay(self, delay=5):
        time.sleep(delay)
        self.my_setDriver('ST', 0)

    def send_IRcode(self, command=None):
        try:
            logging.info('udiIRremote send_IRcode')
            remote = self._get_remote('send_IRcode')
            if remote is None:
                return
            if remote.send_code( self.code):
                #time.sleep(0.5)
                #res = self.yoIRrem.get_send_status()
                #while res is {} and self.yoIRrem.check_system_online():
                time.sleep(1)
                #res = self.yoIRrem.get_send_status()
                #logging.debug(f'Send code {self.code} {res}')
                if remote.get_data('success') and remote.get_data('key') == self.code:
                    logging.info('Code {} sent successfully'.format(self.code))
                    self.node.reportCmd('DON')  
                    self.my_setDriver('ST', 1)
                    self.clear_delay(5)
                    return
                else:
                    logging.info('Failed to send code {}'.format(self.code))
                    self.my_setDriver('ST', 2)
                    self.clear_delay(5)
                    return
            else:
                logging.info('Failed to send code {}'.format(self.code))
                self.my_setDriver('ST', 2)
                self.clear_delay(5)
                return
        except Exception as E:
            logging.error('udiIRcode send_IRcode - Exception: {}'.format(E))        
        '''   
            if 'success' in res:
                if  res['success'] == True:
                    logging.info('Code {} sent successfully'.format(self.code))
                    self.node.reportCmd('DON')  
                    self.my_setDriver('ST', 1)
                else:
                    self.my_setDriver('ST', 0)
            else:
                self.my_setDriver('ST', 0)              
        else:
            self.my_setDriver('ST', 0)
        
        if self.yoIRrem.suspended:
            self.my_setDriver('GV20', 1)
        else:
            self.my_setDriver('GV20', 0)  
        '''
    commands = {
            'TXCODE': send_IRcode,
            }


class udiYoInfraredRemoter(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  update_schedule_data, node_queue, wait_for_node_done, set_node_custom, get_node_custom, checkNameSync as sharedCheckNameSync, saveCurrentNodeNames, apply_profile_driver_names


    '''
       drivers = [
            'GV0' = Nbr codes
            'GV1' = Battery Level
            'GV2' = Command status
            ]
    ''' 
    id = 'yoirremote'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Last Command Status'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV0', 'value': 0, 'uom': 56, 'name': 'Number of Learned codes'},
            {'driver': 'GV1', 'value': 0, 'uom': 25, 'name': 'Battery Level (legacy)'},
            {'driver': 'GV2', 'value': 0, 'uom': 25, 'name': 'Last Command Status (legacy)'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},       
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},                 
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiIRremote INIT- {}'.format(deviceInfo['name']))
        self.name = name

        self.yoAccess = yoAccess
        self.poly = polyglot
        self.devInfo =  deviceInfo
        self.address = address
        self.primary = primary
        self.yoIRrem = None
        self.schedule = None
        self.scheduleSupport = True
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self.main_node_ready = False
        self.sub_nodes_ready = False
        self._update_lock = threading.Lock()
        self.powerSupported = True # assume 
        self.n_queue = []     

        self.poly.subscribe(polyglot.START, self.start, self.address)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
          

        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        # persist or restore parent node name
        try:
            saved = self.get_node_custom('saved_name')
            if saved:
                saved = self.poly.getValidName(saved)
                self._name_sync_saved = saved
                self.set_node_custom('saved_name', saved)
                if self.node.name != saved:
                    try:
                        self.node.rename(saved)
                        logging.info(f'Restored parent node name for {self.address} to saved name {saved}')
                    except Exception as e:
                        logging.debug(f'Failed to restore parent node name for {self.address}: {e}')
            else:
                self.set_node_custom('saved_name', self.node.name)
                self._name_sync_saved = self.node.name
        except Exception as e:
            logging.debug(f'Error handling parent custom name for {self.address}: {e}')
        self.adr_list = []
        self.adr_list.append(address)   
        self.codes_used = []
        self.code_nodes = {}
        # Track the initial learned-code scan, but allow later child-node additions.
        self.main_node_ready = True
        self.node_ready = True

    def add_code_node(self, code):
        nde_address = self.address[-11:] + 'x' + str(code)
        logging.debug(f'ircode {self.primary} {code} {nde_address}')
        if code < 9:
            name = 'Code 0' + str(code+1)
        else:
            name = 'Code ' + str(code+1)
        name = self.poly.getValidName(name)
        self.code_nodes[code] = udiYoInfraredCode(self.poly, self.primary, nde_address, name, code, self.yoIRrem, self.yoAccess)



    def start(self):
        logging.info('start - udiIRremote')
        while not self.main_node_ready  or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('ST', 0)
        # Create schedule node before device online check

        self.yoIRrem = YoLinkInfraredRemoter(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoIRrem.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoIRrem.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online.. Must be online to get learned codes')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoIRrem.refreshDevice()    
            tries += 1
        #self.my_setDriver('ST', 1)
        self.my_setDriver('GV30', 1)
        code_dict_temp = self.yoIRrem.get_code_dict()
        logging.debug(f'Code dict temp: {code_dict_temp}')
        time.sleep(2)
        for code in range(0, len(code_dict_temp)):
            if code_dict_temp[code]:
                logging.info(f'Adding code {code} to node list')
                self.codes_used.append(code)
                self.add_code_node(code)
        self.sub_nodes_ready = True
        logging.info('YoLink Infrared Remoter Node Ready')
        self.start_done()

    def create_schedule_nodes(self):
        sch_address = self.address[4:14] + '_SCH'
        sch_address = self.poly.getValidAddress(sch_address)
        self.schedule = udiYoSchedule(self.poly, self.address, sch_address, 'Schedules', self.yoAccess, self.devInfo)
        self.adr_list.append(sch_address)
        return [sch_address]

    def stop (self):
        logging.info('Stop udiIRremote')
        self.my_setDriver('ST', 0)
        remote = self._get_remote('stop')
        if remote is not None:
            remote.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_remote(self, caller):
        remote = getattr(self, 'yoIRrem', None)
        if remote is None:
            logging.warning('udiYoInfraredRemoter.%s called before device initialization', caller)
        return remote

    def checkDataUpdate(self):
        remote = self._get_remote('checkDataUpdate')
        if remote is None:
            return
        if remote.data_updated():
            self.updateData()

    def checkNameSync(self):
        self.sharedCheckNameSync()
        for code_node in self.code_nodes.values():
            if hasattr(code_node, 'checkNameSync'):
                code_node.checkNameSync()

    def err_code2nbr(self, status_code):
        #if status_code == 'notLearn':
        #    return(0)
        if isinstance(status_code, bool):
            if status_code == True: 
                return(1)
            else: 
                return(2)
        else:
            return(None)


    def updateData(self):
        remote = self._get_remote('updateData')
        if remote is None:
            return
        message_type = None
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)
            logging.debug('updateData - {}'.format(remote.check_system_online()))
            message_info = remote.get_message_type()
            message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
            message_action = message_info[1] if isinstance(message_info, (list, tuple)) and len(message_info) >= 2 else None
            unix_time = remote.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)

            if isinstance(message_action, str) and 'Schedules' in message_action:
                if self.schedule is not None:
                    self.schedule.update_schedule_data(source_device=remote)
                return

        if  remote.check_system_online():
            res = remote.get_status_code()
            logging.debug(f'IR remote status code: {res}')
            self.my_setDriver('ST', self.err_code2nbr(res), type=message_type)
            self.my_setDriver('GV0',len(self.codes_used) )                 
            self.my_setDriver('GV1',remote.get_data('battery'), type=message_type)
            self.my_setDriver('GV2',self.err_code2nbr(res), type=message_type)

            self.my_setDriver('GV30', 1)
            if remote.suspended:
                self.my_setDriver('GV20', 1)
            else:
                self.my_setDriver('GV20', 0)
        else:
            self.my_setDriver('ST', 0)
            self.my_setDriver('GV20', 2)
            self.my_setDriver('GV30', 0)




    def updateStatus(self, data):
        logging.info('udiIRremote updateStatus')
        remote = self._get_remote('updateStatus')
        if remote is not None:
            with self._update_lock:
                remote.updateStatus(data)
            self.updateData()
            #res = self.yoIRrem.getIRstatus_info()
            #logging.debug(f'IR status info: {res}')
            logging.debug(f'Code nodes: {self.code_nodes}')
            update_type = remote.get_info('type')
            action = remote.get_info('action')
            if action in ['send', 'report'] or update_type == 'event':
                res_code = remote.get_data('key')
                if isinstance(res_code, int) and res_code in self.code_nodes:
                    logging.debug(f'Updating code node {res_code}')
                    self.code_nodes[res_code].updateData()
                    
    def checkOnline(self):
        remote = self._get_remote('checkOnline')
        if remote is None:
            return
        remote.refreshDevice()


    def update(self, command = None):
        logging.info('Update Status Executed')
        self.saveCurrentNodeNames()
        remote = self._get_remote('update')
        if remote is None:
            return
        remote.refreshDevice()
        # Keep schedule child node in sync when UPDATE is requested.
        remote.refreshSchedules()
    
    
    def find_next_code(self):  
        for code in range(1, 65):
            if code not in self.codes_used:
                return(code)
        return(None)


    
    def learn_IRcode(self, command=None):
        logging.info('udiIRremote learn_IRcode')
        remote = self._get_remote('learn_IRcode')
        if remote is None:
            return
        if remote.nbr_codes < 64:
            code = self.find_next_code()
            if  not isinstance(code, int):
                logging.info('Maximum number of codes already learned')
                return() 
            self.codes_used.append(code)
            logging.info(f'Learning code {code}')

            remote.learn(code)
            time.sleep(1)
            res = remote.check_learn_completed(code)
            logging.debug(f'Initial learn res: {res}')  
            attempts = 1
            while res in ['learning', 'ignore'] and attempts < 10:
                time.sleep(1)
                res = remote.check_learn_completed(code)
                attempts += 1   
                logging.debug(f'Learn res: {res}')  

            if res == 'success':
                logging.info(f'Learned code {code} successfully')
                logging.info(f'Code {code} learned - creating new node')
                self.add_code_node(code)
                                                                   
                remote.refreshDevice()
                #self.updateData()
            else:
                logging.info('Unsuccessful learn of code {}'.format(code))
    


    commands = {
                'UPDATE': update,
                'LEARNCODE' : learn_IRcode,
                #'TXCODE': send_IRcode,                'LEARNCODE' : learn_IRcode,
                }





