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
            {'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            {'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min
            {'driver': 'GV19', 'value': 0, 'uom': 25}, #days
                 
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},            

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
        self.brightness = 50
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

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()


    def start(self):
        logging.info('start - udiYoDimmer')
        self.node.setDriver('ST', 0, True, True)
        self.yoDimmer  = YoLinkDim(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoDimmer.initNode()
        time.sleep(2)
        #self.node.setDriver('ST', 1, True, True)
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
                        self.node.setDriver('GV1', timeRemaining[delayInfo]['on'], True, False)
                        if max_delay < timeRemaining[delayInfo]['on']:
                            max_delay = timeRemaining[delayInfo]['on']
                    if 'off' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV2', timeRemaining[delayInfo]['off'], True, False)
                        if max_delay < timeRemaining[delayInfo]['off']:
                            max_delay = timeRemaining[delayInfo]['off']
        self.timer_expires = time.time()+max_delay
      

    def stop (self):
        logging.info('Stop udiyoDimmer')
        self.node.setDriver('ST', 0, True, True)
        self.yoDimmer.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    #def checkOnline(self):
    #    self.yoDimmer.refreshDevice()
    
    
    def checkDataUpdate(self):
        if self.yoDimmer.data_updated():
            self.updateData()


    def updateData(self):
        if self.node is not None:
            state =  self.yoDimmer.getState().upper()
            if self.yoDimmer.online:
                self.node.setDriver('ST', 1, True, True)
                if state == 'ON':
                    self.node.setDriver('GV0', 1, True, True)
                    #if self.last_state != state:
                    #    self.node.reportCmd('DON')  
                elif  state == 'OFF':
                    self.node.setDriver('GV0', 0, True, True)
                    #if self.last_state != state:
                    #    self.node.reportCmd('DOF')  
                else:
                    self.node.setDriver('GV0', 99, True, True)
                self.last_state = state
                self.node.setDriver('GV3', self.yoDimmer.brightness, True, True)
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                    self.node.setDriver('GV1', 0, True, False)
                    self.node.setDriver('GV2', 0, True, False) 
                if self.yoDimmer.suspended:
                    self.node.setDriver('GV20', 1, True, True)
                else:
                     self.node.setDriver('GV20', 0)
            else:
                self.node.setDriver('ST', 0, True, True)
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV1', 0, True, False)
                self.node.setDriver('GV2', 0, True, False)
                self.node.setDriver('GV20', 2, True, True)
                self.node.setDriver('GV13', self.schedule_selected)
                self.node.setDriver('GV14', 99)
                self.node.setDriver('GV15', 99,True, True, 25)
                self.node.setDriver('GV16', 99,True, True, 25)
                self.node.setDriver('GV17', 99,True, True, 25)
                self.node.setDriver('GV18', 99,True, True, 25)            
                self.node.setDriver('GV19', 0)       

        sch_info = self.yoDimmer.getScheduleInfo(self.schedule_selected)
        logging.debug('sch_info {}'.format(sch_info))
        if sch_info:
            #if 'ch' in sch_info:
            #    self.node.setDriver('GV12', sch_info['ch'])
            self.node.setDriver('GV13', self.schedule_selected)
            if self.yoDimmer.isScheduleActive(self.schedule_selected):
                self.node.setDriver('GV14', 1)
            else:
                self.node.setDriver('GV14', 0)
            timestr = sch_info['on']
            logging.debug('timestr : {}'.format(timestr))
            if '25:0' in timestr:
                self.node.setDriver('GV15', 98,True, True, 25)
                self.node.setDriver('GV16', 98,True, True, 25)
            else:
                timelist =  timestr.split(':')
                hour = int(timelist[0])
                minute = int(timelist[1])
                self.node.setDriver('GV15', int(hour),True, True, 19)
                self.node.setDriver('GV16', int(minute),True, True, 44)
            timestr = sch_info['off']
            logging.debug('timestr : {}'.format(timestr))
            if '25:0' in timestr:
                self.node.setDriver('GV17', 98,True, True, 25)
                self.node.setDriver('GV18', 98,True, True, 25)
            else:
                timelist =  timestr.split(':')
                hour = timelist[0]
                minute = timelist[1]               
                self.node.setDriver('GV17', int(hour),True, True, 19)
                self.node.setDriver('GV18', int(minute),True, True, 44)
            self.node.setDriver('GV19',  int(sch_info['week']))
        else:
            self.node.setDriver('GV13', self.schedule_selected)
            self.node.setDriver('GV14', 99)
            self.node.setDriver('GV15', 99,True, True, 25)
            self.node.setDriver('GV16', 99,True, True, 25)
            self.node.setDriver('GV17', 99,True, True, 25)
            self.node.setDriver('GV18', 99,True, True, 25)
            self.node.setDriver('GV19', 0)                

    def updateStatus(self, data):
        logging.info('updateStatus - Switch')
        self.yoDimmer.updateStatus(data)
        self.updateData()
 
    def set_switch_on(self, command = None):
        logging.info('udiyoDimmer set_switch_on')  
        self.yoDimmer.setState('ON')
        self.node.setDriver('GV0',1 , True, True)
        self.node.reportCmd('DON')

    def set_switch_off(self, command = None):
        logging.info('udiYoDimmer set_switch_off')  
        self.yoDimmer.setState('OFF')
        self.node.setDriver('GV0',0 , True, True)
        self.node.reportCmd('DOF')

    def set_switch_fon(self, command = None):
        logging.info('udiyoDimmer set_switch_on')  
        self.yoDimmer.setState('ON')
        self.node.setDriver('GV0',1 , True, True)
        self.node.reportCmd('DFON')

    def set_switch_foff(self, command = None):
        logging.info('udiYoDimmer set_switch_off')  
        self.yoDimmer.setState('OFF')
        self.node.setDriver('GV0',0 , True, True)
        self.node.reportCmd('DFOF')



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
        self.node.setDriver('GV3',brightness , True, True)

    def switchControl(self, command):
        logging.info('udiYoDimmer switchControl') 
        ctrl = command.get('value')   
        logging.debug('switchControl : {}'.format(ctrl))
        if ctrl == 1:
            self.yoDimmer.setState('ON')
            self.node.setDriver('GV0',1 , True, True)
            self.node.reportCmd('DON')
        elif ctrl == 0:
            self.yoDimmer.setState('OFF')
            self.node.setDriver('GV0',0 , True, True)
            self.node.reportCmd('DOF')
        elif ctrl == 2: #toggle
            state = str(self.yoDimmer.getState()).upper() 
            logging.debug('switchControl : {}, {}'.format(ctrl, state))
            if state == 'ON':
                self.yoDimmer.setState('OFF')
                self.node.setDriver('GV0',0 , True, True)
                self.node.reportCmd('DOF')
            elif state == 'OFF':
                self.yoDimmer.setState('ON')
                self.node.setDriver('GV0',1 , True, True)
                self.node.reportCmd('DON')
            #Unknown remains unknown
        elif ctrl == 5:
            logging.info('switchControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.node.setDriver('GV1', self.onDelay * 60, True, True)
            self.node.setDriver('GV2', self.offDelay * 60 , True, True)
            self.yoDimmer.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    def setOnDelay(self, command ):
        logging.info('udiYoDimmer setOnDelay')
        self.onDelay =int(command.get('value'))
        self.yoDimmer.setOnDelay(self.onDelay )
        self.node.setDriver('GV1', self.onDelay *60, True, True)

    def setOffDelay(self, command):
        logging.info('udiYoDimmer setOffDelay')
        self.offDelay  =int(command.get('value'))
        self.yoDimmer.setOffDelay(self.offDelay)
        self.node.setDriver('GV2', self.offDelay*60, True, True)

    def program_delays(self, command):
        logging.info('udiYoDimmer program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("Dondelay.uom44"))
        self.offDelay = int(query.get("Doffdelay.uom44"))
        self.node.setDriver('GV1', self.onDelay * 60, True, True)
        self.node.setDriver('GV2', self.offDelay * 60 , True, True)
        self.yoDimmer.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


    def lookup_schedule(self, command):
        logging.info('udiYoDimmer lookup_schedule {}'.format(command))
        self.schedule_selected = int(command.get('value'))
        self.yoDimmer.refreshSchedules()

    def define_schedule(self, command):
        logging.info('udiYoDimmer define_schedule {}'.format(command))
        query = command.get("query")
        self.schedule_selected = int(query.get('DDindex.uom25'))
        tmp = int(query.get('DDactive.uom25'))
        self.activated = (tmp == 1)
        if 'DDstartH.uom19' in query:
            StartH = int(query.get('DDstartH.uom19'))
            StartM = int(query.get('DDstartM.uom44'))
        else:
            startH = 25
            StartM = 0
        if 'DDstopH.uom19' in query:
            StopH = int(query.get('DDstopH.uom19'))
            StopM = int(query.get('DDstopM.uom44'))
        else:
            startH = 25
            StartM = 0      

        binDays = int(query.get('DDbindays.uom25'))

        params = {}
        params['index'] = str(self.schedule_selected )
        params['isValid'] = self.activated 
        params['on'] = str(StartH)+':'+str(StartM)
        params['off'] = str(StopH)+':'+str(StopM)
        params['week'] = binDays
        self.yoDimmer.setSchedule(self.schedule_selected, params)

    def control_schedule(self, command):
        logging.info('udiYoDimmer control_schedule {}'.format(command))       
        query = command.get("query")
        self.schedule_selected = int(query.get('DCindex.uom25'))
        tmp = int(query.get('DCactive.uom25'))
        self.activated = (tmp == 1)
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
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay,
                'DELAY_CTRL'    : program_delays, 
                'LOOKUP_SCH'    : lookup_schedule,
                'DEFINE_SCH'    : define_schedule,
                'CTRL_SCH'      : control_schedule,
                }




