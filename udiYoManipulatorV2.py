#!/usr/bin/env python3
"""
MIT License
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

from os import truncate
#import udi_interface
#import sys
import time
from yolinkManipulatorV2 import YoLinkManipul




class udiYoManipulator(udi_interface.Node):
    from  udiYolinkLib import prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key    
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
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'BATLVL', 'value': 99, 'uom': 25}, 
            {'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            {'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            {'driver': 'GV15', 'value': 99, 'uom': 25}, #start Hour
            {'driver': 'GV16', 'value': 99, 'uom': 25}, #start Min
            {'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            {'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min
            {'driver': 'GV19', 'value': 0, 'uom': 25}, #days
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},              
            {'driver': 'TIME', 'value': 0, 'uom': 44},            
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoManipulator INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoManipulator = None
        self.node_ready = False
        self.last_state = ''
        self.timer_cleared = True
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.schedule_selected = 0
        self.valveState = 99 # needed as class c device - keep value until online again 
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
        logging.info('Start - udiYoManipulator')
        self.my_setDriver('ST', 0)
        self.yoManipulator = YoLinkManipul(self.yoAccess, self.devInfo, self.updateStatus)
        
        time.sleep(4)
        self.yoManipulator.initNode()
        time.sleep(2)
        #self.my_setDriver('ST', 1)
        self.yoManipulator.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.yoManipulator.refreshSchedules()
        self.node_ready = True

    def stop (self):
        logging.info('Stop udiYoManipulator')
        self.my_setDriver('ST', 0)
        self.yoManipulator.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    def checkOnline(self):
        #get get info even if battery operated 
        self.yoManipulator.refreshDevice()    

    def checkDataUpdate(self):
        if self.yoManipulator.data_updated():
            self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.my_setDriver('GV1', 0)
        #    self.my_setDriver('GV2', 0)

    def updateLastTime(self):
        self.my_setDriver('TIME', self.yoManipulator.getTimeSinceUpdateMin(), 44)


    def updateData(self):
        if self.node is not None:
            self.my_setDriver('TIME', self.yoManipulator.getTimeSinceUpdateMin(), 44)
            state =  self.yoManipulator.getState()
            if self.yoManipulator.online:
                if state.upper() == 'OPEN':
                    self.valveState = 1
                    self.my_setDriver('GV0', self.valveState )
                    if self.last_state != state:
                        self.node.reportCmd('DON')
                elif state.upper() == 'CLOSED':
                    self.valveState = 0
                    self.my_setDriver('GV0', self.valveState )
                    if self.last_state != state:
                        self.node.reportCmd('DOF')
                else:
                    self.my_setDriver('GV0', 99)
                    
                self.last_state = state
                self.my_setDriver('ST', 1)
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                    self.my_setDriver('GV1', 0)
                    self.my_setDriver('GV2', 0)  
                #logging.debug('udiYoManipulator - getBattery: {}'.format(self.yoManipulator.getBattery()))    
                self.my_setDriver('BATLVL', self.yoManipulator.getBattery())          
                if self.yoManipulator.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

            else:
                #self.my_setDriver('GV0', 99)
                #self.my_setDriver('GV1', 0)     
                #self.my_setDriver('GV2', 0)
                #self.my_setDriver('BATLVL', 99)
                self.my_setDriver('ST', 0)
                self.my_setDriver('GV20', 2)
                #self.my_setDriver('GV13', self.schedule_selected)
                #self.my_setDriver('GV14', 99)
                #self.my_setDriver('GV15', 99, 25)
                #self.my_setDriver('GV16', 99, 25)
                #self.my_setDriver('GV17', 99, 25)
                #self.my_setDriver('GV18', 99, 25)
                #self.my_setDriver('GV19', 0)        

            sch_info = self.yoManipulator.getScheduleInfo(self.schedule_selected)
            self.update_schedule_data(sch_info, self.schedule_selected)            

    def updateStatus(self, data):
        logging.info('updateStatus - udiYoManipulator')
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
        self.timer_expires = time.time()+max_delay
  
    def manipuControl(self, command):
        logging.info('Manipulator manipuControl')
        state = int(command.get('value'))
        if state == 1:
            self.yoManipulator.setState('open')
            self.valveState = 1
            self.my_setDriver('GV0',self.valveState  )
   
            #self.node.reportCmd('DON')
        elif state == 0:
            self.yoManipulator.setState('closed')
            self.valveState  = 0
            self.my_setDriver('GV0',self.valveState )
            #self.node.reportCmd('DOF')
        elif state == 5:
            logging.info('manipuControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60 )
            self.yoManipulator.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


    def set_open(self, command = None):
        logging.info('Manipulator - set_open')
        self.yoManipulator.setState('open')
        self.valveState  = 1
        self.my_setDriver('GV0',self.valveState  )

        #self.node.reportCmd('DON')

    def set_close(self, command = None):
        logging.info('Manipulator - set_close')
        self.yoManipulator.setState('closed')
        self.valveState  = 0
        self.my_setDriver('GV0',self.valveState  )

        #self.node.reportCmd('DOF')


    def prepOnDelay(self, command ):

        self.onDelay =int(command.get('value'))
        logging.info('prepOnDelay {}'.format(self.onDelay))
        #self.yoManipulator.setOnDelay(delay)
        #self.my_setDriver('GV1', delay*60)
        #self.my_setDriver('GV0',self.valveState  )

    def prepOffDelay(self, command):
        logging.info('setOnDelay Executed')
        self.offDelay =int(command.get('value'))
        logging.info('setOnDelay Executed {}'.format(self.offDelay))

        #self.yoManipulator.setOffDelay(delay)
        #self.my_setDriver('GV2', delay*60)
        #self.my_setDriver('GV0',self.valveState  )



    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoManipulator.refreshDevice()

    def program_delays(self, command):
        logging.info('Manipulator program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        self.yoManipulator.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


    def lookup_schedule(self, command):
        logging.info('Manipulator lookup_schedule {}'.format(command))
        self.schedule_selected = int(command.get('value'))
        self.yoManipulator.refreshSchedules()

    def define_schedule(self, command):
        logging.info('udiYoSwitch define_schedule {}'.format(command))
        query = command.get("query")
        self.schedule_selected, params = self.prep_schedule(query)
        self.yoManipulator.setSchedule(self.schedule_selected, params)


    def control_schedule(self, command):
        logging.info('udiYoSwitch control_schedule {}'.format(command))       
        query = command.get("query")
        self.activated, self.schedule_selected = self.activate_schedule(query)
        self.yoSwiyoManipulatortch.activateSchedule(self.schedule_selected, self.activated)
        

    commands = {
                'UPDATE': update,
                'QUERY' : update,
                'DON'   : set_open,
                'DOF'   : set_close,
                'MANCTRL': manipuControl, 
                'ONDELAY' : prepOnDelay,
                'OFFDELAY' : prepOffDelay,
                'DELAY_CTRL'    : program_delays, 
                'LOOKUP_SCH'    : lookup_schedule,
                'DEFINE_SCH'    : define_schedule,
                'CTRL_SCH'      : control_schedule,                
                }




