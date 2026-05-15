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

from os import truncate
import threading
#import udi_interface
#import sys
import time
from yolinkSirenV3 import YoLinkSiren


class udiYoSiren(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  node_queue, wait_for_node_done, checkNameSync

    id = 'yosiren'
    '''
       drivers = [
            'GV0' = Siren State
            'GV1' = Alarm Duration
            'GV2' = BatteryLevel
            'ST' = Online
            ]
    '''  #Needs update 
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 58}, # seconds
            {'driver': 'GV2', 'value': 99, 'uom': 25},
            {'driver': 'GV3', 'value': 99, 'uom': 25},

            {'driver': 'GV20', 'value': 99, 'uom': 25},
            {'driver': 'GV30', 'value': 99, 'uom': 25},

             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoSiren INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.n_queue = []
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoSiren = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.last_state = ''
        self.timer_cleared = True
        self.timer_update = 5
        self.timer_expires = 0
        self.sirenState = 99 # needed as class c device - keep value until online again 
        model = str(deviceInfo['modelName'][:6])        
        self.soundLevelSupport = model in ['YS7103']      
        #
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)

        # start processing events and create add our controller node
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True



    def start(self):
        logging.info('Start - udiYoSiren')
        while not self.node_ready  or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0, True, True)

        self.yoSiren = YoLinkSiren(self.yoAccess, self.devInfo, self.updateStatus)
        
        time.sleep(2)
        self.yoSiren.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoSiren.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoSiren.refreshDevice()    
            tries += 1
        time.sleep(2)
        self.start_done()

        
    def stop (self):
        logging.info('Stop udiYoSiren')
        self.my_setDriver('GV30', 0, True, True)
        siren = self.yoSiren
        if siren is not None:
            siren.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_siren(self, caller):
        if self.yoSiren is None:
            logging.warning(f'udiYoSiren - {caller} skipped; siren not initialized yet')
            return None
        return self.yoSiren
            
    def checkOnline(self):
        #get get info even if battery operated 
        siren = self._get_siren('checkOnline')
        if siren is None:
            return
        siren.refreshDevice()    


 

    def checkDataUpdate(self):
        siren = self._get_siren('checkDataUpdate')
        if siren is None:
            return
        if siren.data_updated():
            self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.my_setDriver('GV1', 0, True, False)
        #    self.my_setDriver('GV2', 0, True, False)


    def updateData(self):
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)
            siren = self._get_siren('updateData')
            if siren is None:
                return
            message_info = siren.get_message_type()
            if not isinstance(message_info, tuple) or len(message_info) != 2:
                return
            message_type = message_info[0]
            message_action = message_info[1] # if event some data may not be updated 
            unix_time = siren.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)
            state_list = ['normal', 'alert', 'off']
            if siren.check_system_online():
                state =  siren.get_data('state')
                logging.debug('Siren state {}'.format(state))
                if state in state_list:
  
                    self.my_setDriver('GV0', state_list.index(state), type=message_type)
                    self.my_setDriver('ST', state_list.index(state), type=message_type)
                else:
                    self.my_setDriver('GV0', 99)
                    self.my_setDriver('ST', 99)
                supply = siren.get_data('powerSupply')
                if supply in ['battery']:
                    logging.debug(f'udiYoSiren - getBattery: {supply} ')    
                    self.node.my_setDriver('GV2', siren.get_data('battery'), type=message_type)
                elif supply in ['ext_supply', 'usb']:
                    logging.debug('udiYoSiren - external Supply')    
                    self.my_setDriver('GV2', 98, type=message_type)
                else:
                    self.my_setDriver('GV2', 99, type=message_type)
                duration = siren.get_data('alarmDuration')
                logging.debug('AlarmDuration : {}'.format(duration))
                self.my_setDriver('GV1', duration, type=message_type)
                if self.soundLevelSupport:
                    sound_level = siren.get_data('soundLevel')
                    if sound_level in [1,100]:
                        sound_level = 1
                    elif sound_level in [2,104]:
                        sound_level = 2
                    elif sound_level in [3,110]:
                        sound_level = 3
                    elif sound_level in [0]:
                        sound_level = 0
                    else:
                        sound_level = 99
                else:   
                    sound_level = 98
                logging.debug('Sound Level : {}'.format(sound_level))                    
                self.my_setDriver('GV3', sound_level,  type=message_type)

                self.my_setDriver('GV30', 1)


                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if siren.suspended:
                    self.my_setDriver('GV20', 1, True, True)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                
                self.node.my_setDriver('GV30', 0)
                self.node.my_setDriver('GV20', 2)
                

    def updateStatus(self, data):
        logging.info('updateStatus - udiYoSiren')
        if self.yoSiren is not None:
            with self._update_lock:
                self.yoSiren.updateStatus(data)
            self.updateData()
    

    def sirenControl(self, command):
        logging.info('Siren Control')
        siren = self._get_siren('sirenControl')
        if siren is None:
            return
        state = int(command.get('value'))
        if state == 1:
            siren.setState('on')
            self.sirenState = 1

        else:
            siren.setState('off')
            self.sirenState  = 0




    def update(self, command = None):
        logging.info('Update Status Executed')
        siren = self._get_siren('update')
        if siren is None:
            return
        siren.refreshDevice()



    commands = {
                'UPDATE': update,
                'SIRENCTRL': sirenControl, 
                }






