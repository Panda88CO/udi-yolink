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
from yolinkOutletV2 import YoLinkOutlet
from udiYoSchedule import udiYoSchedule


class udiYoOutlet(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, bool2ISY, checkNameSync
    id = 'yooutlet'
    '''
       drivers = [
            'GV0' = Outlet State
            'GV1' = OnDelay
            'GV2' = OffDelay
            'GV3' = Power
            'GV4' = Energy
            'GV5' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            #{'driver': 'GV3', 'value': 0, 'uom': 73},
            #{'driver': 'GV4', 'value': 0, 'uom': 119},
            {'driver': 'GV5', 'value': 99, 'uom': 25},
            {'driver': 'GV6', 'value': 99, 'uom': 25},
            {'driver': 'GV7', 'value': 99, 'uom': 25},
            {'driver': 'GV8', 'value': 99, 'uom': 25},

            #{'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            #{'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            #{'driver': 'GV15', 'value': 99, 'uom': 25}, #start Hour
            #{'driver': 'GV16', 'value': 99, 'uom': 25}, #start Min
            #{'driver': 'GV21', 'value': 99, 'uom': 25}, #start Sec            
            #{'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            #{'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min                                        
            #{'driver': 'GV22', 'value': 99, 'uom': 25}, #stop Sec                        
            #{'driver': 'GV19', 'value': 0, 'uom': 25}, #days

            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 99, 'uom': 25},            
            {'driver': 'GV20', 'value': 99, 'uom': 25},              
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoOutletPwr INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []
        self.address = address
        self.name = name
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo   
        self.yoOutlet = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.powerSupported = False # assume 
        model = str(deviceInfo['modelName'][:6])        
        if model in ['YS6803','YS6602','YS5716', 'YS6614']:
            self.id = 'yooutletPwr'
            self.powerSupported = True  

        # Use instance-level drivers so power models can expose GV3/GV4 without affecting non-power outlets.
        self.drivers = [dict(d) for d in type(self).drivers]
        if self.powerSupported:
            self.drivers.insert(3, {'driver': 'GV3', 'value': 0, 'uom': 73})
            self.drivers.insert(4, {'driver': 'GV4', 'value': 0, 'uom': 119})

        self.last_state = ''
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.scheduleSupport = True
        #self.schedule_selected = None
        self.poly = polyglot
        self.poly.subscribe(polyglot.START, self.start, self.address)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
               

        # start processing events and create add our controller node
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        #self.my_setDriver('GV30', 1)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True


    def start(self):
        logging.info('start - YoOutlet')
        while not self.node_ready  or not self.configDone:
            time.sleep(0.5)
        #self.my_setDriver('GV30', 0)
        # Create schedule node before device online check

        self.yoOutlet = YoLinkOutlet(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoOutlet.initNode()
        time.sleep(2)        
        self.yoOutlet.delayTimerCallback(self.updateDelayCountdown, self.timer_update)
        # deferred: refreshSchedules() will be invoked after startup to avoid API bursts
        tries = 1
        while not self.yoOutlet.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2*tries))
            #if tries % 10 == 0:
                #self.yoOutlet.refreshDevice()

            tries += 1
        time.sleep(2)
        self.start_done()

    def create_schedule_nodes(self):
        sch_address = self.address[4:14] + '_SCH'
        sch_address = self.poly.getValidAddress(sch_address)
        self.schedule = udiYoSchedule(self.poly, self.address, sch_address, 'Schedules', self.yoAccess, self.devInfo)
        self.adr_list.append(sch_address)
        return [sch_address]

    def stop (self):
        logging.info('Stop udiYoOutlet')
        self.my_setDriver('GV30', 0)
        outlet = self.yoOutlet
        if outlet is not None:
            outlet.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_outlet(self, caller):
        if self.yoOutlet is None:
            logging.warning(f'udiYoOutlet - {caller} skipped; outlet not initialized yet')
            return None
        return self.yoOutlet

    def checkDataUpdate(self):
        # Guard: defer if initialization not complete
        if not self.node_ready or not self.configDone:
            return
        #if self.yoOutlet.data_updated():
        outlet = self._get_outlet('checkDataUpdate')
        if outlet is None:
            return
        self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.my_setDriver('GV1', 0, True, False)
        #    self.my_setDriver('GV2', 0, True, False)     



    def updateData(self):
        logging.info('udiYoOutlet updateData - ')
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)
            outlet = self._get_outlet('updateData')
            if outlet is None:
                return
            message_info = outlet.get_message_type()
            if not isinstance(message_info, tuple) or len(message_info) != 2:
                return
            message_type = message_info[0]
            message_action = message_info[1]
            if message_action in ['getSchedules', 'setSchedules']:
                if self.schedule is not None:
                    self.schedule.update_schedule_data(source_device=outlet)
                if outlet.check_system_online():
                    self.my_setDriver('GV30',1)
            else:
                
                #if 'Schedules' in message_action:  # neED TO THINK THIS THROUGH
                #    logging.debug('Schedule update detected')
                    #sch_info = self.yoOutlet.getScheduleInfo(self.schedule_selected)
                #    self.schedule.refresh_schedules(message_action)
                unix_time = outlet.get_report_time('time')
                logging.debug(f'unix time {unix_time}')
                self.my_setDriver('TIME', unix_time, 151)
                if outlet.check_system_online(): 
                    self.my_setDriver('GV30',1)
                    state = str(outlet.get_data('state'))
                    logging.debug('Outlet Online State : {} '. format(state))
                    logging.debug('Outlet State : {} '. format(state))
                    if state in ['on', 'open']:
                        self.my_setDriver('GV0',1, type=message_type)
                        self.my_setDriver('ST',1, type=message_type)
                        state =  'open'
                    elif state in [ 'off', 'closed']:
                        self.my_setDriver('GV0', 0, type=message_type)
                        self.my_setDriver('ST', 0, type=message_type)
                        state = 'closed'
                    #else:
                    #    self.my_setDriver('GV0', 99)
                    self.last_state = state           
                        

                    if self.powerSupported: 
                        powerW = outlet.get_data('power')
                        if isinstance(powerW, (int, float)):
                            powerW = round(powerW/10,1) # reports 1/10W
                            self.my_setDriver('GV3', powerW, 73, type=message_type)

                        energyWh = outlet.get_data('watt')  
                        if isinstance(energyWh, (int, float)):            
                            energyWh = round(energyWh/10,1) # reports 1/10Wh                    
                        self.my_setDriver('GV4', energyWh, 119, type=message_type)

                        self.my_setDriver('GV5', self.bool2ISY(outlet.get_data('overload', 'alertType')), type=message_type)
                        self.my_setDriver('GV6', self.bool2ISY(outlet.get_data('highLoad', 'alertType')), type=message_type)   
                        self.my_setDriver('GV7', self.bool2ISY(outlet.get_data('lowLoad', 'alertType')), type=message_type)
                        self.my_setDriver('GV8', self.bool2ISY(outlet.get_data('highTemperature', 'alertType')), type=message_type)
                        
                    #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                    if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                        self.my_setDriver('GV1', 0)
                        self.my_setDriver('GV2', 0)
                    if outlet.suspended:
                        self.my_setDriver('GV20', 1)
                    else:
                        self.my_setDriver('GV20', 0)
                else:

                    self.my_setDriver('GV30',0)
                    self.my_setDriver('GV20', 2)


    def updateStatus(self, data):
        logging.info('udiYoOutlet updateStatus')
        if self.yoOutlet is not None:
            with self._update_lock:
                self.yoOutlet.updateStatus(data)
            self.updateData()


    def updateDelayCountdown( self, timeRemaining):
        logging.debug('udiYoOutlet updateDelayCountDown:  delays {}'.format(timeRemaining))
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

    
    def checkOnline(self):
        # Guard: defer if initialization not complete
        if not self.node_ready or not self.configDone:
            return
        outlet = self._get_outlet('checkOnline')
        if outlet is None:
            return
        outlet.refreshDevice()


    def set_outlet_on(self, command = None):
        logging.info('udiYoOutlet set_outlet_on')
        outlet = self._get_outlet('set_outlet_on')
        if outlet is None:
            return
        outlet.setState('open')

    def set_outlet_off(self, command = None):
        logging.info('udiYoOutlet set_outlet_off')
        outlet = self._get_outlet('set_outlet_off')
        if outlet is None:
            return
        outlet.setState('closed')



    def outletControl(self, command):
        
        outlet = self._get_outlet('outletControl')
        if outlet is None:
            return
        ctrl = int(command.get('value'))  
        logging.info('udiYoOutlet outletControl - {}'.format(ctrl))
        ctrl = int(command.get('value'))
        if ctrl == 1:
            outlet.setState('open')
        elif ctrl == 0:
            outlet.setState('closed')
        elif ctrl == 2: #toggle
            state = str(outlet.get_data('state')) 
            if state == 'open':
                outlet.setState('closed')
            elif state == 'closed':
                outlet.setState('open')
        elif ctrl == 5:
            logging.info('outletControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60 )
            outlet.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


            #Unknown remains unknown
        
        
    def prepOnDelay(self, command ):
        self.onDelay =int(command.get('value'))
        logging.info('udiYoOutlet prepOnDelay {}'.format(self.onDelay))
        #self.yoOutlet.setOnDelay(delay)
        #self.my_setDriver('GV1', self.onDelay*60)

    def prepOffDelay(self, command):

        self.offDelay =int(command.get('value'))
        logging.info('udiYoOutlet prefOffDelay Executed {}'.format(self.offDelay ))
        #self.yoOutlet.setOffDelay(delay)
        #self.my_setDriver('GV2', self.offDelay*60)

    def update(self, command = None):
        logging.info('Update Status Executed')
        outlet = self._get_outlet('update')
        if outlet is None:
            return
        outlet.refreshDevice()

    def program_delays(self, command):
        logging.info('udiYoOutlet program_delays {}'.format(command))
        outlet = self._get_outlet('program_delays')
        if outlet is None:
            return
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        outlet.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


    '''
    def lookup_schedule(self, command):
        logging.info('udiYoOutlet lookup_schedule {}'.format(command))
        self.schedule_selected = int(command.get('value'))
        self.yoOutlet.refreshSchedules()

    def define_schedule(self, command):
        logging.info('udiYoSwitch define_schedule {}'.format(command))
        query = command.get("query")
        self.schedule_selected, params = self.prep_schedule(query)
        self.yoOutlet.setSchedule(self.schedule_selected, params)


    def control_schedule(self, command):
        logging.info('udiYoSwitch control_schedule {}'.format(command))       
        query = command.get("query")
        self.activated, self.schedule_selected = self.activate_schedule(query)
        self.yoOutlet.activateSchedule(self.schedule_selected, self.activated)
    '''    


    commands = {
                'UPDATE'        : update,
                'DON'           : set_outlet_on,
                'DOF'           : set_outlet_off,
                'SWCTRL'        : outletControl, 
                #'ONDELAY'       : prepOnDelay,
                #'OFFDELAY'      : prepOffDelay,
                'DELAYCTRL'    : program_delays, 
                #'LOOKUPSCH'    : lookup_schedule,
                #'DEFINESCH'    : define_schedule,
                #'CTRLSCH'      : control_schedule,
                }





