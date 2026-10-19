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
#import sys
import time
from yolinkGarageDoorToggleV2 import YoLinkGarageDoorCtrl




class udiYoGarageDoor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  wait_for_node_done, node_queue, checkNameSync, apply_profile_driver_names
    id = 'yogarage'
    
    '''
       drivers = [
            'ST' = Online
            ]

    ''' 
        
    drivers = [ 
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Node Server Status'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        
        self.yoAccess=yoAccess
        self.devInfo =  deviceInfo   
        self.yoDoorControl  = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        logging.debug('udiYoGarageDoor INIT - {}'.format(deviceInfo['name']))
        self.n_queue = []
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
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True


    def start(self):
        logging.info('start - udiYoGarageDoor')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        self.yoDoorControl = YoLinkGarageDoorCtrl(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        tries = 1
        while not self.yoDoorControl.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoDoorControl.refreshDevice()
            tries += 1

        self.my_setDriver('ST', 1)
        self.my_setDriver('GV30', 1)
        #time.sleep(3)
        self.start_done()

    def initNode(self):
        door_control = self._get_door_control('initNode')
        if door_control is None:
            return
        door_control.online = True
        #self.my_setDriver('ST', 1, True, True)
        
    def checkOnline(self):
        pass
        
    def checkDataUpdate(self):
        pass

    def updateLastTime(self):
        pass
        #self.my_setDriver('TIME', self.yoDoorControl.getTimeSinceUpdateMin(), 44)

    
    def stop (self):
        logging.info('Stop udiYoGarageDoor')
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        door_control = self.yoDoorControl
        if door_control is not None:
            door_control.shut_down()

    def _get_door_control(self, caller):
        if self.yoDoorControl is None:
            logging.warning(f'udiYoGarageDoor - {caller} skipped; garage door control not initialized yet')
            return None
        return self.yoDoorControl

    def updateStatus(self, data):
        logging.debug('updateStatus - udiYoGarageDoor')
        door_control = self._get_door_control('updateStatus')
        if door_control is None:
            return
        with self._update_lock:
            door_control.updateCallbackStatus(data)
            if door_control is not None:

                if door_control.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

                if door_control.check_system_online():
                    self.my_setDriver('ST', 1)
                    self.my_setDriver('GV30', 1)
                else:
                    self.my_setDriver('GV20', 2)
                    #self.my_setDriver('ST', 0, True, True)

        


    def toggleDoor(self, command = None):
        logging.info('GarageDoor Toggle Door')
        door_control = self._get_door_control('toggleDoor')
        if door_control is None:
            return
        door_control.toggleDevice()
        self.node.reportCmd('DON')
        time.sleep(1.5)
        self.node.reportCmd('DOF')

    commands = {
                    'TOGGLE': toggleDoor,
                    'DON'   : toggleDoor,
                    'DOF'   : toggleDoor,
                }




