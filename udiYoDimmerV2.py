#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    #logging = getlogger('udiDimmerV2')
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

from os import truncate
#import udi_interface
#import sys
import time
from yolinkDimmerV3 import YoLinkDim

class udiYoDimmer(udi_interface.Node):
    from  udiYolinkLib import  my_setDriver, save_cmd_struct, retrieve_cmd_struct, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key
    id = 'yodimmer'
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'GV3', 'value': 0, 'uom': 51},
            {'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            {'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            {'driver': 'GV15', 'value': 99, 'uom': 25}, #start Hour
            {'driver': 'GV16', 'value': 99, 'uom': 25}, #start Min
            {'driver': 'GV21', 'value': 99, 'uom': 25}, #start Min              
            {'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            {'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min
            {'driver': 'GV22', 'value': 99, 'uom': 25}, #start Min              
            {'driver': 'GV19', 'value': 0, 'uom': 25}, #days
                 
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},            
            {'driver': 'TIME', 'value': int(time.time()), 'uom': 151},
            ]
    '''
       drivers = [
            'GV0' =  Dinner State
            'GV1' = OnDelay
            'GV2' = OffDelay
            'GV3' = Dimmer Brightness
            #'GV4' = Energy
            'ST' = Online/Connected
            'GV20' = Suspended state
            ]

    ''' 

    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoDimmer INIT- {}'.format(deviceInfo['name']))
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.yoDimmer = None
        self.node_ready = False
        self.timer_cleared = True
        self.n_queue = [] # one queue for all
        self.last_state = ''
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.schedule_selected = 0
        self.dim_setting = self.retrieve_cmd_struct()
        if self.dim_setting == {}:
            self.dim_setting['dim'] = 50
            self.dim_setting['dim_up'] =  80
            self.dim_setting['dim_down'] = 20
            self.dim_setting['previous'] = self.dim_setting['dim']
            self.save_cmd_struct(self.dim_setting)
        self.dim_setting['previous'] = self.dim_setting['dim']
        self.dimmer_step = 5
        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
               

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)


    def start(self):
        logging.info('start - udiYoDimmer')
        self.my_setDriver('ST', 0)
        self.yoDimmer  = YoLinkDim(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoDimmer.initNode()
        time.sleep(2)
        self.yoDimmer.setBrightness(self.dim_setting['dim'])
        self.dim_setting['previous'] = self.yoDimmer.brightness
        #self.my_setDriver('ST', 1)
        self.yoDimmer.delayTimerCallback (self.updateDelayCountdown, self.timer_update )
        self.yoDimmer.refreshSchedules()
        self.node_ready = True


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
        self.my_setDriver('ST', 0)
        self.yoDimmer.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    def checkOnline(self):
        self.yoDimmer.refreshDevice()
    
    
    def checkDataUpdate(self):
        if self.yoDimmer.data_updated():
            self.updateData()



    def updateData(self):
        if self.node is not None:
            self.my_setDriver('TIME', self.yoDimmer.getLastUpdateTime(), 151)
            state =  self.yoDimmer.getState().upper()
            self.dim_setting['dim'] = self.yoDimmer.brightness
            if self.yoDimmer.online:
                self.my_setDriver('ST', 1)
                if state == 'ON':
                    self.my_setDriver('GV0', 1)
                    #if self.last_state != state:
                    #    self.node.reportCmd('DON')  
                elif  state == 'OFF':
                    self.my_setDriver('GV0', 0)
                    #if self.last_state != state:
                    #    self.node.reportCmd('DOF')  
                else:
                    self.my_setDriver('GV0', 99)
                self.last_state = state

                if self.yoDimmer.brightness >= self.dim_setting['previous'] + self.dimmer_step:
                    self.node.reportCmd('FDUP')
                    dim_change = abs(self.yoDimmer.brightness - self.dim_setting['previous'])
                    dim_time = self.yoDimmer.ramp_up_time*(dim_change/(self.yoDimmer.max_level-self.yoDimmer.min_level))
                    time.sleep(dim_time)
                    self.node.reportCmd('FDSTOP')
                if self.yoDimmer.brightness <= self.dim_setting['previous'] - self.dimmer_step:
                    self.node.reportCmd('FDDOWN')
                    dim_change = abs(self.yoDimmer.brightness - self.dim_setting['previous'])
                    dim_time = self.yoDimmer.ramp_down_time*(dim_change/(self.yoDimmer.max_level-self.yoDimmer.min_level))
                    time.sleep(dim_time)
                    self.node.reportCmd('FDSTOP')
                if self.dim_setting['previous'] != self.dim_setting['dim']:
                    self.dim_setting['previous'] = self.dim_setting['dim']
                    self.save_cmd_struct(self.dim_setting)
                self.my_setDriver('GV3', self.dim_setting['dim'])
                self.my_setDriver('GV4', self.dim_setting['dim_down'])
                self.my_setDriver('GV3', self.dim_setting['dim_up'])
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                    self.my_setDriver('GV1', 0)
                    self.my_setDriver('GV2', 0) 
                if self.yoDimmer.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                self.my_setDriver('ST', 0)
                self.my_setDriver('GV20', 2)

            sch_info = self.yoDimmer.getScheduleInfo(self.schedule_selected)
            self.update_schedule_data(sch_info, self.schedule_selected)

    def updateStatus(self, data):
        logging.info('updateStatus - Switch')
        self.yoDimmer.updateStatus(data)
        self.updateData()
 
    def set_switch_on(self, command = None):
        logging.info('udiyoDimmer set_switch_on')  
        self.yoDimmer.setState('ON')
        self.my_setDriver('GV0',1 )
        self.node.reportCmd('DON')

    def set_switch_off(self, command = None):
        logging.info('udiYoDimmer set_switch_off')  
        self.yoDimmer.setState('OFF')
        self.my_setDriver('GV0',0 )
        self.node.reportCmd('DOF')

    def set_switch_fon(self, command = None):
        logging.info('udiyoDimmer set_switch_on')  
        self.yoDimmer.setState('ON')
        self.my_setDriver('GV0',1 )
        self.node.reportCmd('DFON')

    def set_switch_foff(self, command = None):
        logging.info('udiYoDimmer set_switch_off')  
        self.yoDimmer.setState('OFF')
        self.my_setDriver('GV0',0 )
        self.node.reportCmd('DFOF')


    def increase_level(self, command = None):
        logging.info(f'udiYoDimmer increase_level - {command}') 
        self.yoDimmer.brightness += self.dimmer_step
        self.yoDimmer.setBrightness(self.yoDimmer.brightness)
        self.my_setDriver('GV3', self.yoDimmer.brightness)
        #self.my_setDriver('GV0',0 )
        #self.node.reportCmd('DFOF')

    def decrease_level(self, command = None):
        logging.info(f'udiYoDimmer decrease_level - {command}')
        self.yoDimmer.brightness -= self.dimmer_step
        self.yoDimmer.setBrightness(self.yoDimmer.brightness) 
        self.my_setDriver('GV3', self.yoDimmer.brightness)
        #self.my_setDriver('GV0',0 )
        #self.node.reportCmd('DFOF')

    def scene_dim(self, command = None):
        logging.info(f'udiYoDimmer scene_dim - {command}')
        ctrl = str(command.get('cmd')  )
        if ctrl == 'FDUP':
            logging.debug('FDUP detected')
            self.yoDimmer.setBrightness(self.dim_setting['dim_up'], True)
            self.dim_setting['dim'] = self.dim_setting['dim_up']
            #self.my_setDriver('GV3', self.dim_setting['dim'])
            
            self.save_cmd_struct(self.dim_setting)
        elif ctrl == 'FDDOWN':
            logging.debug('FDDOWN detected')
            self.yoDimmer.setBrightness(self.dim_setting['dim_down'], True)
            self.dim_setting['dim'] = self.dim_setting['dim_up']
            #self.my_setDriver('GV3', self.dim_setting['dim'])            
            self.save_cmd_struct(self.dim_setting)
        elif ctrl == 'FDSTOP':
            logging.debug('FDSTOP detected')

    def set_dimmer_level(self, command = None):
        brightness = int(command.get('value'))
        #self.brightness = brightness
        logging.info('udiYoDimmer set_dimmer_level:{}'.format(brightness) )
        if 0 >= brightness :
            #self.yoDimmer.setState('OFF')
            brightness = 0            
        elif 100 <=  brightness:
            brightness = 100
        self.yoDimmer.setBrightness(brightness) #????
        self.my_setDriver('GV3',brightness )
        self.dim_setting['dim'] = brightness
        self.save_cmd_struct(self.dim_setting)

    def setDimUp(self, command = None):
        logging.debug(f'setDimUp {command}')
        dimlvl = int(command.get('value'))
        self.dim_setting['dim_up'] = dimlvl
        self.my_setDriver('GV5', self.dim_setting['dim_up'])
        self.save_cmd_struct(self.dim_setting)

    def setDimDown(self, command = None):
        logging.debug(f'setDimDown {command}')
        dimlvl = int(command.get('value'))
        self.dim_setting['dim_down'] = dimlvl
        self.my_setDriver('GV5', self.dim_setting['dim_down'])
        self.save_cmd_struct(self.dim_setting)

    def switchControl(self, command):
        logging.info('udiYoDimmer switchControl')
        ctrl = command.get('value')   
        logging.debug('switchControl : {}'.format(ctrl))
        if ctrl == 1:
            self.yoDimmer.setState('ON')
            self.my_setDriver('GV0',1 )
            self.node.reportCmd('DON')
        elif ctrl == 0:
            self.yoDimmer.setState('OFF')
            self.my_setDriver('GV0',0 )
            self.node.reportCmd('DOF')
        elif ctrl == 2: #toggle
            state = str(self.yoDimmer.getState()).upper() 
            logging.debug('switchControl : {}, {}'.format(ctrl, state))
            if state == 'ON':
                self.yoDimmer.setState('OFF')
                self.my_setDriver('GV0',0 )
                self.node.reportCmd('DOF')
            elif state == 'OFF':
                self.yoDimmer.setState('ON')
                self.my_setDriver('GV0',1 )
                self.node.reportCmd('DON')
            #Unknown remains unknown
        elif ctrl == 5:
            logging.info('switchControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60 )
            self.yoDimmer.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    def setOnDelay(self, command ):
        logging.info('udiYoDimmer setOnDelay')
        self.onDelay =int(command.get('value'))
        self.yoDimmer.setOnDelay(self.onDelay )
        self.my_setDriver('GV1', self.onDelay *60)

    def setOffDelay(self, command):
        logging.info('udiYoDimmer setOffDelay')
        self.offDelay  =int(command.get('value'))
        self.yoDimmer.setOffDelay(self.offDelay)
        self.my_setDriver('GV2', self.offDelay*60)

    def program_delays(self, command):
        logging.info('udiYoDimmer program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        self.yoDimmer.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


    def lookup_schedule(self, command):
        logging.info('udiYoDimmer lookup_schedule {}'.format(command))
        self.schedule_selected = int(command.get('value'))
        self.yoDimmer.refreshSchedules()

    def define_schedule(self, command):
        logging.info('udiYoSwitch define_schedule {}'.format(command))
        query = command.get("query")
        self.schedule_selected, params = self.prep_schedule(query)
        self.yoDimmer.setSchedule(self.schedule_selected, params)


    def control_schedule(self, command):
        logging.info('udiYoSwitch control_schedule {}'.format(command))       
        query = command.get("query")
        self.activated, self.schedule_selected = self.activate_schedule(query)
        self.yoDimmer.activateSchedule(self.schedule_selected, self.activated)

    def update(self, command = None):
        logging.info('udiYoDimmer Update Status')
        self.yoDimmer.refreshDevice()
        #self.yoDimmer.refreshSchedules()     


    commands = {
                'UPDATE': update,
                'QUERY' : update,
                'DON'   : set_switch_on,
                'DOF'   : set_switch_off,
                'DFON'   : set_switch_fon,
                'DFOF'   : set_switch_foff,                
                'SWCTRL': switchControl, 
                'DIMLVL' : set_dimmer_level,
                'DIMUP' : setDimUp,
                'DIMDOWN' : setDimDown,
                'DELAY_CTRL'    : program_delays, 
                'LOOKUP_SCH'    : lookup_schedule,
                'DEFINE_SCH'    : define_schedule,
                'CTRL_SCH'      : control_schedule,
                'FDUP'          : scene_dim,
                'FDDOWN'        : scene_dim,
                #'BMAN'          : scene_dim,
                #'SMAN'          : scene_dim,
                'FDSTOP'        : scene_dim
                }




