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
from sre_parse import State
import time

from yolinkDimmerV3 import YoLinkDim
from udiYoSchedule import udiYoSchedule

class udiYoDimmer(udi_interface.Node):
    from  udiYolinkLib import  my_setDriver, start_done, configDoneHandler,  save_cmd_struct, retrieve_cmd_struct, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, checkNameSync
    id = 'yodimmer'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 51},
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'GV3', 'value': 0, 'uom': 51},
            {'driver': 'GV4', 'value': 0, 'uom': 51},
            {'driver': 'GV5', 'value': 0, 'uom': 51},
            {'driver': 'GV9', 'value': 99, 'uom': 25},
            {'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            {'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            {'driver': 'GV15', 'value': 99, 'uom': 25}, #start Hour
            {'driver': 'GV16', 'value': 99, 'uom': 25}, #start Min
            {'driver': 'GV21', 'value': 99, 'uom': 25}, #start sec             
            {'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            {'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min
            {'driver': 'GV22', 'value': 99, 'uom': 25}, #start sec             
            {'driver': 'GV19', 'value': 0, 'uom': 25}, #days
                 
            {'driver': 'GV30', 'value': 99, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},            
            {'driver': 'TIME', 'value': int(time.time()), 'uom': 151},
            ]
    '''
       drivers = [
            'GV0' =  Dinner State
            'GV1' = OnDelay
            'GV2' = OffDelay
            'GV3' = Dimmer Brightness
            'GV4' = Dim down target
            'GV5' = Dim up target
            'ST' = Online/Connected
            'GV20' = Suspended state
            ]

    ''' 

    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoDimmer INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.yoDimmer = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.timer_cleared = True
        self.n_queue = [] # one queue for all
        self.last_state = ''
        self._last_reported_state = None
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.scheduleSupport = True
        self.schedule_selected = 0
        self.dim_setting = self.retrieve_cmd_struct()
        if self.dim_setting == {} or self.dim_setting is None:
            self.dim_setting = {}   
            self.dim_setting['dim'] = 50
            self.dim_setting['dim_up'] =  80
            self.dim_setting['dim_down'] = 20
            self.dim_setting['previous'] = self.dim_setting['dim']
            self.save_cmd_struct(self.dim_setting)
        self.dim_setting['previous'] = self.dim_setting['dim']
        logging.debug(f'Initial dim_setting {self.dim_setting}')
        self.dimmer_step = 3
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
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
        logging.info('start - udiYoDimmer')
        while not self.node_ready  or not self.configDone:
            time.sleep(0.5)
        #self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        # Create schedule node before device online check
        self.yoDimmer = YoLinkDim(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoDimmer.initNode()
        time.sleep(1)

        tries = 1
        while not self.yoDimmer.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoDimmer.refreshDevice()
            tries += 1
        time.sleep(2)
        self.yoDimmer.get_attributes()
        self.dim_setting['dim'] = self.yoDimmer.get_data('brightness')
        self.yoDimmer.setBrightness(self.dim_setting['dim'])
        self.dim_setting['previous'] = self.dim_setting['dim']
        #self.my_setDriver('ST', 1)
        self.yoDimmer.delayTimerCallback(self.updateDelayCountdown, self.timer_update)
        time.sleep(1)
        self.start_done()

    def create_schedule_nodes(self):
        sch_address = self.address[4:14] + '_SCH'
        sch_address = self.poly.getValidAddress(sch_address)
        self.schedule = udiYoSchedule(self.poly, self.address, sch_address, 'Schedules', self.yoAccess, self.devInfo)
        self.adr_list.append(sch_address)
        return [sch_address]

    def updateDelayCountdown (self, timeRemaining ) :
        logging.debug('updateDelayCountdown {}'.format(timeRemaining))
        max_delay = 0
        for delayInfo in range(0, len(timeRemaining)):
            if 'ch' in timeRemaining[delayInfo]:
                if timeRemaining[delayInfo]['ch'] == 1:
                    if 'on' in timeRemaining[delayInfo]:
                        self.my_setDriver('GV1', timeRemaining[delayInfo]['on'])
                        if max_delay < timeRemaining[delayInfo]['on']:
                            max_delay = timeRemaining[delayInfo]['on']
                    if 'off' in timeRemaining[delayInfo]:
                        self.my_setDriver('GV2', timeRemaining[delayInfo]['off'])
                        if max_delay < timeRemaining[delayInfo]['off']:
                            max_delay = timeRemaining[delayInfo]['off']
        self.timer_expires = time.time()+max_delay
      

    def stop (self):
        logging.info('Stop udiyoDimmer')
        #self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        dimmer = self._get_dimmer('stop')
        if dimmer is not None:
            dimmer.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_dimmer(self, caller):
        dimmer = getattr(self, 'yoDimmer', None)
        if dimmer is None:
            logging.warning('udiYoDimmer.%s called before device initialization', caller)
        return dimmer

    def _normalize_binary_state(self, state):
        if not isinstance(state, str):
            return None
        state_l = state.lower()
        if state_l in ['on', 'open']:
            return 'on'
        if state_l in ['off', 'closed', 'close']:
            return 'off'
        return None

    def _report_binary_state_change(self, state):
        normalized_state = self._normalize_binary_state(state)
        if normalized_state is None:
            return
        if self._last_reported_state is None:
            self._last_reported_state = normalized_state
            return
        if self._last_reported_state == normalized_state:
            return
        if normalized_state == 'on':
            self.node.reportCmd('DON')
        else:
            self.node.reportCmd('DOF')
        self._last_reported_state = normalized_state
            
    def checkOnline(self):
        dimmer = self._get_dimmer('checkOnline')
        if dimmer is None:
            return
        dimmer.refreshDevice()
    
    
    def checkDataUpdate(self):
        dimmer = self._get_dimmer('checkDataUpdate')
        if dimmer is None:
            return
        if dimmer.data_updated():
            self.updateData()



    def updateData(self):
        logging.info('udiYoDimmer -  updateData{}'.format(self.schedule_selected))
        dimmer = self._get_dimmer('updateData')
        if dimmer is None:
            return

        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)
            message_info = dimmer.get_message_type()
            message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
            self.my_setDriver('TIME', dimmer.getLastUpdateTime(), 151)
            state = dimmer.get_data('state')
            if message_type in ['setAttributes', 'setDeviceAttributes']:
                logging.debug('Attributes updated')
                dimmer.ramp_up_time = dimmer.get_data('on', 'gradient')
                dimmer.ramp_down_time = dimmer.get_data('off', 'gradient')
                dimmer.min_level = dimmer.get_data('calibration', 'deviceAttributes')
                dimmer.max_level = dimmer.get_data('calibrationHigh', 'deviceAttributes')

            current_dim = dimmer.get_data('brightness')
            if isinstance(current_dim, (int, float)):
                self.dim_setting['dim'] = current_dim
            if dimmer.check_system_online():
                #self.my_setDriver('ST', 1)
                self.my_setDriver('GV30', 1)               
                if state in[ 'ON', 'open', 'on', 'OPEN']:
                    self.my_setDriver('GV0', 1)
                elif  state in ['OFF', 'closed', 'off', 'CLOSED']:
                    self.my_setDriver('GV0', 0)
                else:
                    self.my_setDriver('GV0', 99)
                self._report_binary_state_change(state)
                self.last_state = state
                if self.dim_setting['previous'] is None:
                    self.dim_setting['previous'] = self.dim_setting['dim']
                tmp = self.dim_setting['previous']
                logging.debug(f"dim {self.dim_setting['dim']} {tmp}")
                if self.dim_setting['dim'] >= self.dim_setting['previous'] + self.dimmer_step:
                    #logging.debug('dim UP detected')
                    self.node.reportCmd('FDUP')
                    dim_change = abs(self.dim_setting['dim'] - self.dim_setting['previous'])
                    dim_time = dimmer.ramp_up_time*(dim_change/(dimmer.max_level-dimmer.min_level))
                    time.sleep(dim_time)
                    self.node.reportCmd('FDSTOP')
                if self.dim_setting['dim'] <= self.dim_setting['previous'] - self.dimmer_step:
                    #logging.debug('dim DOWN detected')
                    self.node.reportCmd('FDDOWN')
                    dim_change = abs(self.dim_setting['dim'] - self.dim_setting['previous'])
                    dim_time = dimmer.ramp_down_time*(dim_change/(dimmer.max_level-dimmer.min_level))
                    time.sleep(dim_time)
                    self.node.reportCmd('FDSTOP')
                if self.dim_setting['previous'] != self.dim_setting['dim']:
                    self.dim_setting['previous'] = self.dim_setting['dim']
                    self.save_cmd_struct(self.dim_setting)
                led_state = dimmer.get_data('status', 'led')
                if isinstance(led_state, str):
                    if led_state.lower() == 'on':
                        self.my_setDriver('GV9', 1)
                    else:
                        self.my_setDriver('GV9', 0)
                else:
                    self.my_setDriver('GV9', None)
                if state in ['ON', 'open', 'on', 'OPEN']:
                    self.my_setDriver('GV3', self.dim_setting['dim'])
                else:
                    self.my_setDriver('GV3', 0)

                self.my_setDriver('ST', self.dim_setting['dim'], 51)
                self.my_setDriver('GV4', self.dim_setting['dim_down'], 51)
                self.my_setDriver('GV5', self.dim_setting['dim_up'], 51)
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                    self.my_setDriver('GV1', 0)
                    self.my_setDriver('GV2', 0) 
                if dimmer.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                #self.my_setDriver('ST', 0)
                self.my_setDriver('GV30', 0)    
                self.my_setDriver('GV20', 2)

            sch_info = dimmer.getScheduleInfo(self.schedule_selected)
            self.update_schedule_data(sch_info, self.schedule_selected)

    def updateStatus(self, data):
        logging.info('updateStatus - Switch')
        if self.yoDimmer is not None:   
            with self._update_lock:
                self.yoDimmer.updateStatus(data)
            self.updateData()
 
    def set_switch_on(self, command = None):
        logging.info('udiyoDimmer set_switch_on')  
        dimmer = self._get_dimmer('set_switch_on')
        if dimmer is None:
            return
        dimmer.setState('ON')

    def set_switch_off(self, command = None):
        logging.info('udiYoDimmer set_switch_off')  
        dimmer = self._get_dimmer('set_switch_off')
        if dimmer is None:
            return
        dimmer.setState('OFF')

    def set_switch_fon(self, command = None):
        logging.info('udiyoDimmer set_switch_on')  
        dimmer = self._get_dimmer('set_switch_fon')
        if dimmer is None:
            return
        dimmer.setState('ON')

    def set_switch_foff(self, command = None):
        logging.info('udiYoDimmer set_switch_off')  
        dimmer = self._get_dimmer('set_switch_foff')
        if dimmer is None:
            return
        dimmer.setState('OFF')


    def increase_level(self, command = None):
        logging.info(f'udiYoDimmer increase_level - {command}') 
        dimmer = self._get_dimmer('increase_level')
        if dimmer is None:
            return
        next_dim = int(self.dim_setting.get('dim', 0)) + self.dimmer_step
        next_dim = max(0, min(100, next_dim))
        self.dim_setting['dim'] = next_dim
        dimmer.setBrightness(next_dim)


    def decrease_level(self, command = None):
        logging.info(f'udiYoDimmer decrease_level - {command}')
        dimmer = self._get_dimmer('decrease_level')
        if dimmer is None:
            return
        next_dim = int(self.dim_setting.get('dim', 0)) - self.dimmer_step
        next_dim = max(0, min(100, next_dim))
        self.dim_setting['dim'] = next_dim
        dimmer.setBrightness(next_dim)

    def scene_dim(self, command = None):
        logging.info(f'udiYoDimmer scene_dim - {command}')
        dimmer = self._get_dimmer('scene_dim')
        if dimmer is None or command is None:
            return
        ctrl = str(command.get('cmd')  )
        if ctrl == 'FDUP':
            logging.debug('FDUP detected')
            self.dim_setting['dim'] = self.dim_setting['dim_up']
            dimmer.setBrightness(self.dim_setting['dim'], True)
            

            
            self.save_cmd_struct(self.dim_setting)
        elif ctrl == 'FDDOWN':
            logging.debug('FDDOWN detected')
            self.dim_setting['dim'] = self.dim_setting['dim_down']
            dimmer.setBrightness(self.dim_setting['dim'], True)
        
            self.save_cmd_struct(self.dim_setting)
        elif ctrl == 'FDSTOP':
            logging.debug('FDSTOP detected')

    def set_dimmer_level(self, command = None):
        if command is None:
            return
        brightness = int(command.get('value'))
        #self.brightness = brightness
        logging.info('udiYoDimmer set_dimmer_level:{}'.format(brightness) )
        if 0 >= brightness :
            #self.yoDimmer.setState('OFF')
            brightness = 0            
        elif 100 <=  brightness:
            brightness = 100
        dimmer = self._get_dimmer('set_dimmer_level')
        if dimmer is None:
            return
        dimmer.setBrightness(brightness) #????
        self.dim_setting['dim'] = brightness
        self.save_cmd_struct(self.dim_setting)

    def setDimUp(self, command = None):
        logging.debug(f'setDimUp {command}')
        if command is None:
            return
        dimlvl = int(command.get('value'))
        self.dim_setting['dim_up'] = dimlvl
        self.my_setDriver('GV5', self.dim_setting['dim_up'])
        self.save_cmd_struct(self.dim_setting)

    def setDimDown(self, command = None):
        logging.debug(f'setDimDown {command}')
        if command is None:
            return
        dimlvl = int(command.get('value'))
        self.dim_setting['dim_down'] = dimlvl
        self.my_setDriver('GV4', self.dim_setting['dim_down'])
        self.save_cmd_struct(self.dim_setting)

    def switchControl(self, command):
        logging.info('udiYoDimmer switchControl')
        dimmer = self._get_dimmer('switchControl')
        if dimmer is None:
            return
        ctrl = command.get('value')   
        logging.debug('switchControl : {}'.format(ctrl))
        if ctrl == 1:
            dimmer.setState('ON')
        elif ctrl == 0:
            dimmer.setState('OFF')
        elif ctrl == 2: #toggle
            state = str(dimmer.get_data('State'))
            logging.debug('switchControl : {}, {}'.format(ctrl, state))
            if state == 'on' or state == 'open' or state == 'ON' or state == 'OPEN':
                dimmer.setState('OFF')
            elif state == 'off' or state == 'closed' or state == 'OFF' or state == 'CLOSED' :
                dimmer.setState('ON')
            #Unknown remains unknown
        elif ctrl == 5:
            logging.info('switchControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            dimmer.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    def setOnDelay(self, command ):
        logging.info('udiYoDimmer setOnDelay')
        self.onDelay =int(command.get('value'))
        dimmer = self._get_dimmer('setOnDelay')
        if dimmer is None:
            return
        dimmer.setOnDelay(self.onDelay )
        self.my_setDriver('GV1', self.onDelay *60)

    def setOffDelay(self, command):
        logging.info('udiYoDimmer setOffDelay')
        self.offDelay  =int(command.get('value'))
        dimmer = self._get_dimmer('setOffDelay')
        if dimmer is None:
            return
        dimmer.setOffDelay(self.offDelay)
        self.my_setDriver('GV2', self.offDelay*60)

    def program_delays(self, command):
        logging.info('udiYoDimmer program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        dimmer = self._get_dimmer('program_delays')
        if dimmer is None:
            return
        dimmer.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    def set_attributes(self, command):
        logging.debug(f'set_attributes {command}')
        dimmer = self._get_dimmer('set_attributes')
        if dimmer is None:
            return
        led_state = int(command.get('value'))
        if isinstance(led_state, int) and led_state in [0, 1]:
            logging.info('Set LED attribute to {}'.format(led_state))
            params = {}
            params['led'] = {}
            if led_state == 1:
                params['led']['status'] = 'on'
            else:
                params['led']['status'] = 'off'
            dimmer.set_attributes(params)


    def lookup_schedule(self, command):
        logging.info('udiYoDimmer lookup_schedule {}'.format(command))
        self.schedule_selected = int(command.get('value'))
        dimmer = self._get_dimmer('lookup_schedule')
        if dimmer is None:
            return
        dimmer.refreshSchedules()

    def define_schedule(self, command):
        logging.info('udiYoSwitch define_schedule {}'.format(command))
        query = command.get("query")
        self.schedule_selected, params = self.prep_schedule(query)
        dimmer = self._get_dimmer('define_schedule')
        if dimmer is None:
            return
        dimmer.setSchedule(self.schedule_selected, params)


    def control_schedule(self, command):
        logging.info('udiYoSwitch control_schedule {}'.format(command))       
        query = command.get("query")
        self.activated, self.schedule_selected = self.activate_schedule(query)
        dimmer = self._get_dimmer('control_schedule')
        if dimmer is None:
            return
        dimmer.activateSchedule(self.schedule_selected, self.activated)

    def update(self, command = None):
        logging.info('udiYoDimmer Update Status')
        dimmer = self._get_dimmer('update')
        if dimmer is None:
            return
        dimmer.refreshDevice()
        dimmer.get_attributes()
        #self.yoDimmer.refreshSchedules()     


    commands = {
                'UPDATE': update,
                'DON'   : set_switch_on,
                'DOF'   : set_switch_off,
                'DFON'   : set_switch_fon,
                'DFOF'   : set_switch_foff,                
                'SWCTRL': switchControl, 
                'DIMLVL' : set_dimmer_level,
                'DIMUP' : setDimUp,
                'DIMDOWN' : setDimDown,
                'DELAYCTRL'    : program_delays, 
                'SETATTRIB'    : set_attributes,
                #'LOOKUPSCH'    : lookup_schedule,
                #'DEFINESCH'    : define_schedule,
                #'CTRLSCH'      : control_schedule,
                'FDUP'          : scene_dim,
                'FDDOWN'        : scene_dim,
                'FDSTOP'        : scene_dim
                }





