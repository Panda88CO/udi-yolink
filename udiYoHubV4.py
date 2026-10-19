#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""

import importlib

try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom

from os import truncate
import threading
#import udi_interface
#import sys
import time
from yolinkHubV3 import YoLinkHub

class udiYoBatteryHub(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  wait_for_node_done, node_queue, checkNameSync, apply_profile_driver_names
    '''
       drivers = [
            'ST' =  Powered
            'GV1' = Battery Level
            'GV30' = Online
            ]

    ''' 
    
    
    id = 'yohubbat'
    drivers = [
            {'driver': 'ST', 'value': 99, 'uom': 25, 'name': 'Supply Status'},
            {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Battery Status'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},   
            {'driver': 'TIME', 'value': int(time.time()), 'uom': 151, 'name': 'Last device update'},
            #{'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoBatteryHub INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.yoHub = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.n_queue = [] 
        
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
               
        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = [address]
        self.node_ready = True
    


    def start(self):
        logging.info('start - udiYoBatteryHub')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.yoHub  = YoLinkHub(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoHub.initNode()
        tries = 1
        while not self.yoHub.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoHub.refreshDevice()  
            tries += 1
        time.sleep(1)
        # refreshDevice() is called by initNode(); avoid duplicate call here to reduce API load
        self.start_done()

    def updateDelayCountdown (self, delayRemaining ) :
        logging.debug('updateDelayCountdown {}'.format(delayRemaining))

    def stop (self):
        logging.info('Stop udiYoBatteryHub')
        #self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)

        hub = self._get_hub('stop')
        if hub is not None:
            hub.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_hub(self, caller):
        hub = getattr(self, 'yoHub', None)
        if hub is None:
            logging.warning('udiYoBatteryHub.%s called before device initialization', caller)
        return hub


    def checkOnline(self):
        hub = self._get_hub('checkOnline')
        if hub is None:
            return
        hub.refreshDevice() 

    def checkDataUpdate(self):
        hub = self._get_hub('checkDataUpdate')
        if hub is None:
            return
        if hub.data_updated():
            self.updateData()


    def updateData(self):
        hub = self._get_hub('updateData')
        if hub is None:
            return
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)

            if hub.check_system_online():
                message_info = hub.get_message_type()
                message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
                #pwr_info = self.yoHub.getPowerInfo()
                dc_power = hub.get_data('dc', 'power')
                #battery_exists = self.yoHub.get_data('battery', 'power')
                battery_state = hub.get_data('batteryState', 'power')
                if isinstance(dc_power, bool):
                    if not dc_power:
                        self.my_setDriver('ST', 1, type=message_type)
                    else:
                        self.my_setDriver('ST', 0, type=message_type)
                else:
                    self.my_setDriver('ST', 99, type=message_type)
                if  isinstance(battery_state, int):
                        self.my_setDriver('GV0', battery_state, type=message_type)  
                self.my_setDriver('GV30', 1, type=message_type)
                if hub.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)
                #self.pollDelays()

    def updateStatus(self, data):
        logging.info('updateStatus - Hub')
        if self.yoHub is not None:
            with self._update_lock:
                self.yoHub.updateStatus(data)
            self.updateData()
           

    def update(self, command = None):
        logging.info('udiYoHub Update Status')
        hub = self._get_hub('update')
        if hub is None:
            return
        hub.refreshDevice()
        #self.yoHub.refreshSchedules()     


    commands = {
                'UPDATE': update,
                }



class udiYoHub(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler, wait_for_node_done, node_queue, checkNameSync, apply_profile_driver_names
    id = 'yohub'
    drivers = [
            #{'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Status'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},   
            {'driver': 'TIME', 'value': int(time.time()), 'uom': 151, 'name': 'Last device update'},
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
        self.name = name
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.yoHub = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.n_queue = [] 
        
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
               

        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = [address]
        self.node_ready = True
    


    def start(self):
        logging.info('start - udiYoHub')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.yoHub  = YoLinkHub(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.my_setDriver('ST', 1)
        self.yoHub.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoHub.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(2 * tries, 60))
            tries += 1

        
        #if not self.yoHub.online:
        #    logging.warning('Device {} not on-line'.format(self.devInfo['name']))            
        #else:
        #    self.my_setDriver('ST', 1, True, True)
        self.system_ready=True

    def updateDelayCountdown (self, delayRemaining ) :
        logging.debug('updateDelayCountdown {}'.format(delayRemaining))

    def stop (self):
        logging.info('Stop udiYoHub')
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)

        hub = self._get_hub('stop')
        if hub is not None:
            hub.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_hub(self, caller):
        hub = getattr(self, 'yoHub', None)
        if hub is None:
            logging.warning('udiYoHub.%s called before device initialization', caller)
        return hub


    def checkOnline(self):
        hub = self._get_hub('checkOnline')
        if hub is None:
            return
        hub.refreshDevice() 

    def checkDataUpdate(self):
        hub = self._get_hub('checkDataUpdate')
        if hub is None:
            return
        if hub.data_updated():
            self.updateData()

    def updateData(self):
        hub = self._get_hub('updateData')
        if hub is None:
            return
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)

            message_info = hub.get_message_type()
            message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
            if hub.check_system_online():
                #if state == 'ON':
                #    self.my_setDriver('GV0', 1, True, True)
                #elif  state == 'OFF':
                #    self.my_setDriver('GV0', 0, True, True)
                #else:
                #    self.my_setDriver('GV0', 99, True, True)
                self.my_setDriver('ST', 1, type=message_type)
                self.my_setDriver('GV30', 1, type=message_type)
                if hub.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

            else:
                self.my_setDriver('ST', 0,type=message_type)
                self.my_setDriver('GV30', 0, type=message_type)
                self.my_setDriver('GV20', 2)
                #self.pollDelays()

    def updateStatus(self, data):
        logging.info('updateStatus - Hub')
        if self.yoHub is not None:
            with self._update_lock:
                self.yoHub.updateStatus(data)
            self.updateData()
           

    def update(self, command = None):
        logging.info('udiYoHub Update Status')
        hub = self._get_hub('update')
        if hub is None:
            return
        hub.refreshDevice()
        #self.yoHub.refreshSchedules()     


    commands = {
                'UPDATE': update,
                }


