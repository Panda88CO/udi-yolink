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

#import udi_interface
#import sys
import time
import threading
from yolinkSwitchV3 import YoLinkSwitch
from udiYoSmartRemoterV4 import udiRemoteKey
from udiYoSchedule import udiYoSchedule

class udiYoSwitch(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  prep_schedule, state2ISY, bool2ISY, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key, checkNameSync
    id = 'yoswitch'

    drivers = [
            {'driver': 'ST', 'value': 99, 'uom': 25},        
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
            {'driver': 'GV5', 'value': 99, 'uom': 25},
            {'driver': 'GV6', 'value': 99, 'uom': 25},
            {'driver': 'GV7', 'value': 99, 'uom': 25},
            {'driver': 'GV8', 'value': 99, 'uom': 25},
            {'driver': 'GV9', 'value': 99, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},                          
            {'driver': 'GV30', 'value': 99, 'uom': 25},
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},        
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoSwitchSec INIT- {}'.format(deviceInfo['name']))
        self.poly = polyglot    
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.address = address
        self.name = name
        self.yoSwitch = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.timer_cleared = True
        self.n_queue = [] 
        self.last_state = ''
        self._last_reported_state = None
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.scheduleSupport = True
        self.schedule_selected = 0
        self.keys = {}
        self.support_power = False
        self.support_battery = False
        self.nbr_keys = 0
        self.max_remote_keys = 0
        model = str(self.devInfo['modelName'][:6])
        if model in ['YS5716']:
            self.meas_support = ['pwr']
            self.support_power = True
            self.id = 'yoswitchPwr'
        elif model in ['YS5709']:
            self.id = 'yoswitchBat'
            self.support_battery = True
        else:
            self.meas_support = []
        if  model in ['YS5708', 'YS5709']:
            self.max_remote_keys = 8
            self.nbr_keys = 2

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
        self.node_ready = True
        
            


    def start(self):
        logging.info('start - udiYoSwitch')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        # Create schedule node before device online check

        self.yoSwitch  = YoLinkSwitch(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(3)
        self.yoSwitch.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoSwitch.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoSwitch.refreshDevice()
            tries += 1
        time.sleep(2)
        self.yoSwitch.get_attributes()
        # deferred: refreshSchedules() will be invoked after startup to avoid API bursts
        time.sleep(1)
        #self.my_setDriver('GV30', 1)
        self.yoSwitch.delayTimerCallback(self.updateDelayCountdown, self.timer_update)
        for key in range(0, self.nbr_keys):
            logging.debug(' {}'.format(key))
            k_address = self.address[4:14] + 'key' + str(key)
            k_address = self.poly.getValidAddress(str(k_address))
            k_name = str(self.name) + ' key' + str(key + 1)
            k_name = self.poly.getValidName(str(k_name))
            self.keys[key] = udiRemoteKey(self.poly, self.address, k_address, k_name, key)
            self.adr_list.append(k_address)
            logging.debug('Waiting for node to complete{}'.format(self.adr_list))
            #self.wait_for_node_done()
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
                        self.my_setDriver('GV1', timeRemaining[delayInfo]['on'] )
                        if max_delay < timeRemaining[delayInfo]['on']:
                            max_delay = timeRemaining[delayInfo]['on']
                    if 'off' in timeRemaining[delayInfo]:
                        self.my_setDriver('GV2', timeRemaining[delayInfo]['off'] )
                        if max_delay < timeRemaining[delayInfo]['off']:
                            max_delay = timeRemaining[delayInfo]['off']
        self.timer_expires = time.time()+max_delay
      

    def stop (self):
        logging.info('Stop udiYoSwitch')
        self.my_setDriver('GV30', 0)
        switch = self.yoSwitch
        if switch is not None:
            switch.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_switch(self, caller):
        if self.yoSwitch is None:
            logging.warning(f'udiYoSwitch - {caller} skipped; switch not initialized yet')
            return None
        return self.yoSwitch

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
        # Guard: defer if initialization not complete
        if not self.node_ready or not self.configDone:
            return
        switch = self._get_switch('checkOnline')
        if switch is None:
            return
        switch.refreshDevice() 
    
    
    def checkDataUpdate(self):
        # Guard: defer if initialization not complete
        if not self.node_ready or not self.configDone:
            return
        switch = self._get_switch('checkDataUpdate')
        if switch is None:
            return
        if switch.data_updated():
                self.updateData()

 
    def updateData(self):
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)
            switch = self._get_switch('updateData')
            if switch is None:
                return
            message_info = switch.get_message_type()
            if not isinstance(message_info, tuple) or len(message_info) != 2:
                return
            message_type = message_info[0]
            message_action = message_info[1]
            if message_action in ['getSchedules', 'setSchedules']:
                if self.schedule is not None:
                    self.schedule.update_schedule_data(source_device=switch)
            else:            
                
                logging.debug('updateData - message type: {}'.format(message_type))
                unix_time = switch.get_report_time('reportAt')
                self.my_setDriver('TIME', unix_time, 151)

                if switch.check_system_online():
                    self.my_setDriver('GV30', 1)                    
                    state = switch.get_data('state')
                    if not isinstance(state, str) and isinstance(self.last_state, str):
                        # Battery devices sometimes publish partial state payloads; keep last valid state.
                        state = self.last_state
                    if isinstance(state, str):
                        if state in ['on', 'ON', 'open', 'OPEN']:
                            self.my_setDriver('GV0', 1, type=message_type)
                            self.my_setDriver('ST', 1, type=message_type)
                        elif  state in ['off', 'OFF', 'closed', 'CLOSED', 'close', 'CLOSE' ]:
                            self.my_setDriver('GV0', 0, type=message_type)
                            self.my_setDriver('ST', 0, type=message_type)
                        self._report_binary_state_change(state)
                    else:
                         self.my_setDriver('GV0', None, type=message_type)
                         self.my_setDriver('ST', None, type=message_type)
                    self.last_state = state 

                    if self.support_battery:
                        battery = switch.get_data('battery')
                        if not isinstance(battery, (int, float)):
                            battery = switch.get_data('state', 'battery')
                        if isinstance(battery, (int, float)):
                            self.my_setDriver('BATLVL', int(round(battery)), type=message_type)

                    led_state = switch.get_data('status', 'led')
                    if isinstance(led_state, str):
                        if led_state.lower() == 'on':   
                            self.my_setDriver('GV9', 1, type=message_type)
                        else:
                            self.my_setDriver('GV9', 0, type=message_type)
                    else:
                        self.my_setDriver('GV9', None, type=message_type)

                    if self.support_power:      
                        powerW = switch.get_data('power')                      
                        if isinstance(powerW, (int, float)):
                            powerW = round(powerW/10,1) # reports 1/10W
                            self.my_setDriver('GV3', powerW, 73, type=message_type)

                        energyWh = switch.get_data('watt')  
                        if isinstance(energyWh, (int, float)):            
                            energyWh = round(energyWh/10,1) # reports 1/10Wh                    
                        self.my_setDriver('GV4', energyWh, 119, type=message_type)

                        self.my_setDriver('GV5', self.bool2ISY(switch.get_data('overload', 'alertType')), type=message_type)
                        self.my_setDriver('GV6', self.bool2ISY(switch.get_data('highload', 'alertType')), type=message_type)
                        self.my_setDriver('GV7', self.bool2ISY(switch.get_data('lowload', 'alertType')), type=message_type)
                        self.my_setDriver('GV8', self.bool2ISY(switch.get_data('highTemperature', 'alertType')), type=message_type)

                        #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                    if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                        self.my_setDriver('GV1', 0)
                        self.my_setDriver('GV2', 0)
                    if switch.suspended:
                        self.my_setDriver('GV20', 1)
                    else:
                        self.my_setDriver('GV20', 0)

                else:
                    self.my_setDriver('GV30', 0)

                    self.my_setDriver('GV20', 2)

                if self.nbr_keys > 0:
                    #logging.debug('updateData - event data {}'.format(event_data))
                    if message_type in ['event']: 
                        key_mask = switch.get_data('keyMask', 'event')
                        press_type = switch.get_data('type', 'event')
                        logging.debug('key_mask {} press_type {}'.format(key_mask, press_type))
                        if isinstance(key_mask, int):
                            remote_key = self.mask2key(key_mask)
                            if isinstance(press_type, str):
                                if  remote_key in self.keys:
                                    self.keys[remote_key].send_command(press_type)
                                    # Send command updates ISY variables and reports to ISY as needed.



                


    def updateStatus(self, data):
        logging.info('updateStatus - Switch')
        if self.yoSwitch is not None:
            with self._update_lock:
                self.yoSwitch.updateStatus(data)
            self.updateData()
 
    def set_switch_on(self, command = None):
        logging.info('udiYoSwitch set_switch_on')  
        switch = self._get_switch('set_switch_on')
        if switch is None:
            return
        switch.setState('ON')
        #self.my_setDriver('GV0',1 )
        #self.my_setDriver('ST',1 )
        #self.node.reportCmd('DON')

    def set_switch_off(self, command = None):
        logging.info('udiYoSwitch set_switch_off')  
        switch = self._get_switch('set_switch_off')
        if switch is None:
            return
        switch.setState('OFF')
        #self.my_setDriver('GV0',0 )
        #self.my_setDriver('ST',0 )
        #self.node.reportCmd('DOF')

    def set_switch_fon(self, command = None):
        logging.info('udiYoSwitch set_switch_on')  
        switch = self._get_switch('set_switch_fon')
        if switch is None:
            return
        switch.setState('ON')
        #self.my_setDriver('GV0',1 )
        #self.my_setDriver('ST',1 )
        #self.node.reportCmd('DFON')

    def set_switch_foff(self, command = None):
        logging.info('udiYoSwitch set_switch_off')  
        switch = self._get_switch('set_switch_foff')
        if switch is None:
            return
        switch.setState('OFF')
        #self.my_setDriver('GV0',0 ) 
        #self.my_setDriver('ST',0 )
        #self.node.reportCmd('DFOF')


    def switchControl(self, command):
        logging.info('udiYoSwitch switchControl') 
        switch = self._get_switch('switchControl')
        if switch is None:
            return
        ctrl = int(command.get('value'))     
        if ctrl == 1:
            switch.setState('ON')
            #self.my_setDriver('GV0',1 )
            #self.my_setDriver('ST',1 )
            #self.node.reportCmd('DON')
        elif ctrl == 0:
            switch.setState('OFF')
            #self.my_setDriver('GV0',0 )
            #self.my_setDriver('ST',0 )
            #self.node.reportCmd('DOF')
        elif ctrl == 2: #toggle
            state = switch.get_data('state')
            if state == 'on' or state == 'open':
                switch.setState('OFF')
                #self.my_setDriver('GV0',0 )
                #self.my_setDriver('ST',0 )
                #self.node.reportCmd('DOF')
            elif state == 'off' or state == 'closed':
                switch.setState('ON')
                #self.my_setDriver('GV0',1 )
                #self.my_setDriver('ST',1 )
                #self.node.reportCmd('DON')
        elif ctrl == 5:
            logging.info('switchControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60 )
            switch.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

            #Unknown remains unknown
    

    def prepOnDelay(self, command ):
        
        self.onDelay =int(command.get('value'))
        logging.info('udiYoSwitch prepOnDelay {}'.format(self.onDelay))
        #self.yoSwitch.setOnDelay(delay)
        #self.my_setDriver('GV1', delay*60)

    def prepOffDelay(self, command):

        self.offDelay =int(command.get('value'))
        logging.info('udiYoSwitch prepOffDelay {}'.format(self.offDelay))
        #self.yoSwitch.setOffDelay(delay)
        #self.my_setDriver('GV2', delay*60)

    def program_delays(self, command):
        logging.info('udiYoOutlet program_delays {}'.format(command))
        switch = self._get_switch('program_delays')
        if switch is None:
            return
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        switch.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    def set_attributes(self, command):
        logging.debug(f'set_attributes {command}')
        switch = self._get_switch('set_attributes')
        if switch is None:
            return
        #add led control
        led_state = int(command.get('value'))

        if isinstance(led_state, int) and led_state in [0,1]:
            logging.info('Set LED attribute to {}'.format(led_state))
            params = {}
            params['led'] ={}
            if led_state == 1:
                params['led']['status'] = 'on'
            else:
                params['led']['status'] = 'off'
            switch.set_attributes(params)

    def update(self, command = None):
        logging.info('udiYoSwitch Update Status')
        switch = self._get_switch('update')
        if switch is None:
            return
        switch.refreshDevice()
        switch.get_attributes()
        #self.yoSwitch.refreshSchedules()
        
    '''    
    def lookup_schedule(self, command):
        logging.info('udiYoSwitch lookup_schedule {}'.format(command))
        self.schedule_selected = int(command.get('value'))
        self.yoSwitch.refreshSchedules()

    
    def define_schedule(self, command):
        logging.info('udiYoSwitch define_schedule {}'.format(command))
        StartH = 25
        StartM = 0        
        StopH = 25
        StopM = 0      

        query = command.get("query")
        self.schedule_selected = int(query.get('index.uom25'))
        tmp = int(query.get('active.uom25'))
        self.activated = (tmp == 1)
        if 'startH.uom19' in query:
            StartH = int(query.get('startH.uom19'))
            StartM = int(query.get('startM.uom44'))

        if 'stopH.uom19' in query:
            StopH = int(query.get('stopH.uom19'))
            StopM = int(query.get('stopM.uom44'))
            
        binDays = int(query.get('bindays.uom25'))

        params = {}
        params['index'] = str(self.schedule_selected )
        params['isValid'] = self.activated 
        params['on'] = str(StartH)+':'+str(StartM)
        params['off'] = str(StopH)+':'+str(StopM)
        params['week'] = binDays
        self.yoSwitch.setSchedule(self.schedule_selected, params)
        
    def define_schedule(self, command):
        logging.info('udiYoSwitch define_schedule {}'.format(command))
        query = command.get("query")
        self.schedule_selected, params = self.prep_schedule(query)
        self.yoSwitch.setSchedule(self.schedule_selected, params)


    def control_schedule(self, command):
        logging.info('udiYoSwitch control_schedule {}'.format(command))       
        query = command.get("query")
        self.activated, self.schedule_selected = self.activate_schedule(query)
        self.yoSwitch.activateSchedule(self.schedule_selected, self.activated)
    '''  

    commands = {
                'UPDATE'        : update,
                'DON'           : set_switch_on,
                'DOF'           : set_switch_off,    
                'DFON'          : set_switch_fon,
                'DFOF'          : set_switch_foff,                         
                'SWCTRL'        : switchControl, 
                'DELAYCTRL'     : program_delays, 
                'SETATTRIB'     : set_attributes,
                #'LOOKUPSCH'    : lookup_schedule,
                #'DEFINESCH'    : define_schedule,
                #'CTRLSCH'      : control_schedule,                
                }





