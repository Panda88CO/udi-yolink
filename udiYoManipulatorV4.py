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
from yolinkManipulatorV3 import YoLinkManipulator
from udiYoSchedule import udiYoSchedule




class udiYoManipulator(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,   prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names
    id = 'yomanipu'
    '''
       drivers = [
            'GV0' = Manipulator State
            'GV1' = OnDelay
            'GV2' = OffDelay
            'BATLVL' = BatteryLevel
            
            'ST' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Manipulator State (Legacy)'},
            {'driver': 'GV1', 'value': 0, 'uom': 57, 'name': 'On Delay Remaining'}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57, 'name': 'Off Delay Remaining'}, 
            {'driver': 'BATLVL', 'value': 99, 'uom': 25, 'name': 'Battery Level'}, 
            #{'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            #{'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            #{'driver': 'GV15', 'value': 99, 'uom': 25}, #start Hour
            #{'driver': 'GV16', 'value': 99, 'uom': 25}, #start Min
            #{'driver': 'GV21', 'value': 99, 'uom': 25}, #start Min              
            #{'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            #{'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min
            #{'driver': 'GV22', 'value': 99, 'uom': 25}, #start Min              
            #{'driver': 'GV19', 'value': 0, 'uom': 25}, #days
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Manipulator State'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},              
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},            
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoManipulator INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.n_queue = []
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoManipulator = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.last_state = ''
        self._last_reported_state = None
        self.timer_cleared = True
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.scheduleSupport = True
        self.schedule_selected = 0
        self.valveState = 99 # needed as class c device - keep value until online again 
        #polyglot.subscribe(polyglot.POLL, self.poll)
        self.poly = polyglot
        self.poly.subscribe(polyglot.START, self.start, self.address)
        self.poly.subscribe(polyglot.STOP, self.stop)
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
        logging.info('Start - udiYoManipulator')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0)
        # Create schedule node before device online check

        self.yoManipulator = YoLinkManipulator(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(4)
        self.yoManipulator.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoManipulator.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoManipulator.refreshDevice()  
            tries += 1
        #self.my_setDriver('GV30', 1)
        time.sleep(2)
        self.yoManipulator.delayTimerCallback(self.updateDelayCountdown, self.timer_update)
        self.start_done()

    def create_schedule_nodes(self):
        sch_address = self.address[4:14] + '_SCH'
        sch_address = self.poly.getValidAddress(sch_address)
        self.schedule = udiYoSchedule(self.poly, self.address, sch_address, 'Schedules', self.yoAccess, self.devInfo)
        self.adr_list.append(sch_address)
        return [sch_address]

    def stop (self):
        logging.info('Stop udiYoManipulator')
        self.my_setDriver('GV30', 0)
        manipulator = self.yoManipulator
        if manipulator is not None:
            manipulator.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_manipulator(self, caller):
        if self.yoManipulator is None:
            logging.warning(f'udiYoManipulator - {caller} skipped; manipulator not initialized yet')
            return None
        return self.yoManipulator

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
        #get get info even if battery operated 
        manipulator = self._get_manipulator('checkOnline')
        if manipulator is None:
            return
        manipulator.refreshDevice()    

    def checkDataUpdate(self):
        manipulator = self._get_manipulator('checkDataUpdate')
        if manipulator is None:
            return
        if manipulator.data_updated():
            self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.my_setDriver('GV1', 0)
        #    self.my_setDriver('GV2', 0)


    def updateData(self):
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)
            manipulator = self._get_manipulator('updateData')
            if manipulator is None:
                return
            message_info = manipulator.get_message_type()
            if not isinstance(message_info, tuple) or len(message_info) != 2:
                return
            message_type = message_info[0]
            message_action = message_info[1]
            if message_action in ['getSchedules', 'setSchedules']:
                if self.schedule is not None:
                    self.schedule.update_schedule_data(source_device=manipulator)
            else:                

                unix_time = manipulator.get_report_time('reportAt')
                self.my_setDriver('TIME', unix_time, 151)
                if manipulator.check_system_online():
                    state =  manipulator.get_data('state')

                    if isinstance(state, str) and state.upper() == 'OPEN':
                        self.valveState = 1
                        self.my_setDriver('GV0', self.valveState, type = message_type )
                        self.my_setDriver('ST', self.valveState, type = message_type )
                    elif isinstance(state, str) and state.upper() == 'CLOSED':
                        self.valveState = 0
                        self.my_setDriver('GV0', self.valveState, type=message_type )
                        self.my_setDriver('ST', self.valveState, type=message_type )
                    else:
                        self.my_setDriver('GV0', 99)
                        self.my_setDriver('ST',99)
                    self._report_binary_state_change(state)
                    self.last_state = state
                    self.my_setDriver('GV30', 1)
                    #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                    if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                        self.my_setDriver('GV1', 0)
                        self.my_setDriver('GV2', 0)  
                    #logging.debug('udiYoManipulator - getBattery: {}'.format(self.yoManipulator.getBattery()))    
                    self.my_setDriver('BATLVL', manipulator.get_data('battery'), type=message_type)      
                    if manipulator.suspended:
                        self.my_setDriver('GV20', 1)
                    else:
                        self.my_setDriver('GV20', 0)

                else:
                    #self.my_setDriver('GV0', 99)
                    #self.my_setDriver('GV1', 0)     
                    #self.my_setDriver('GV2', 0)
                    #self.my_setDriver('BATLVL', 99)
                    self.my_setDriver('GV30', 0)
                    self.my_setDriver('GV20', 2)
                    #self.my_setDriver('GV13', self.schedule_selected)
                    #self.my_setDriver('GV14', 99)
                    #self.my_setDriver('GV15', 99, 25)
                    #self.my_setDriver('GV16', 99, 25)
                    #self.my_setDriver('GV17', 99, 25)
                    #self.my_setDriver('GV18', 99, 25)
                    #self.my_setDriver('GV19', 0)        


    def updateStatus(self, data):
        logging.info('updateStatus - udiYoManipulator')
        if self.yoManipulator is not None:
            with self._update_lock:
                self.yoManipulator.updateStatus(data)
            self.updateData()

      


    def updateDelayCountdown( self, timeRemaining):

        logging.debug('Manipulator updateDelayCountDown:  delays {}'.format(timeRemaining))
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
                    self.my_setDriver('GV0', self.valveState )
                    self.my_setDriver('ST', self.valveState )
        self.timer_expires = time.time()+max_delay
  
    def manipuControl(self, command):
        logging.info('Manipulator manipuControl')
        manipulator = self._get_manipulator('manipuControl')
        if manipulator is None:
            return
        state = int(command.get('value'))
        if state == 1:
            manipulator.setState('open')
        elif state == 0:
            manipulator.setState('closed')
        elif state == 5:
            logging.info('manipuControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            manipulator.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


    def set_open(self, command = None):
        logging.info('Manipulator - set_open')
        manipulator = self._get_manipulator('set_open')
        if manipulator is None:
            return
        manipulator.setState('open')

    def set_close(self, command = None):
        logging.info('Manipulator - set_close')
        manipulator = self._get_manipulator('set_close')
        if manipulator is None:
            return
        manipulator.setState('closed')


    def prepOnDelay(self, command ):

        self.onDelay =int(command.get('value'))
        logging.info('prepOnDelay {}'.format(self.onDelay))
        #self.yoManipulator.setOnDelay(delay)
        #self.my_setDriver('GV1', delay*60)
        #self.my_setDriver('GV0',self.valveState  )
        #self.my_setDriver('ST',self.valveState  )

    def prepOffDelay(self, command):
        logging.info('setOnDelay Executed')
        self.offDelay =int(command.get('value'))
        logging.info('setOnDelay Executed {}'.format(self.offDelay))

        #self.yoManipulator.setOffDelay(delay)
        #self.my_setDriver('GV2', delay*60)
        #self.my_setDriver('GV0',self.valveState  )
        #$self.my_setDriver('ST',self.valveState  )


    def update(self, command = None):
        logging.info('Update Status Executed')
        manipulator = self._get_manipulator('update')
        if manipulator is None:
            return
        manipulator.refreshDevice()

    def program_delays(self, command):
        logging.info('Manipulator program_delays {}'.format(command))
        manipulator = self._get_manipulator('program_delays')
        if manipulator is None:
            return
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        manipulator.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    commands = {
                'UPDATE': update,
                'MOPEN'   : set_open,
                'MCLOSE'   : set_close,
                'MANCTRL': manipuControl, 
                #'ONDELAY' : prepOnDelay,
                #'OFFDELAY' : prepOffDelay,
                'DELAYCTRL'    : program_delays, 
                #'LOOKUPSCH'    : lookup_schedule,
                #'DEFINESCH'    : define_schedule,
                #'CTRLSCH'      : control_schedule,                
                }





