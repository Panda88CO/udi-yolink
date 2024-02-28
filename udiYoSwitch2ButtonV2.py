#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


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
from yolinkSwitchV2 import YoLinkSW
from udiYoSmartRemoterV3 import udiRemoteKey

class udiYoSwitch2Button(udi_interface.Node):
    #from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, convert_temp_unit, send_rel_temp_to_isy

    id = 'yoswitch2b'
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'GV3', 'value': 99, 'uom': 25}, #button Left
            {'driver': 'GV4', 'value': 99, 'uom': 25}, #button Right            

            {'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            {'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            {'driver': 'GV15', 'value': 99, 'uom': 25}, #start Hour
            {'driver': 'GV16', 'value': 99, 'uom': 25}, #start Min
            {'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            {'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min
            {'driver': 'GV19', 'value': 0, 'uom': 25}, #days
            {'driver': 'GV20', 'value': 99, 'uom': 25},                          
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]
    '''
       drivers = [
            'GV0' =  switch State
            'GV1' = OnDelay
            'GV2' = OffDelay

            ]

    ''' 

    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoSwitch INIT- {}'.format(deviceInfo['name']))
        self.poly = polyglot
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.address = address
        self.name = name
        self.yoSwitch = None
        self.node_ready = False
        self.timer_cleared = True
        self.n_queue = [] 
        self.last_state = ''
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.schedule_selected = 0
        self.keys = {}
        self.max_remote_keys = 4
        self.nbr_keys = 2
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
        logging.info('start - udiYoSwitch')
        self.node.setDriver('ST', 0, True, True)
        self.yoSwitch  = YoLinkSW(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(10.1)
        self.yoSwitch.initNode()
        time.sleep(10)
        #self.node.setDriver('ST', 1, True, True)
        self.yoSwitch.delayTimerCallback (self.updateDelayCountdown, self.timer_update )
        self.yoSwitch.refreshSchedules()
        self.node_ready = True
        for key in range (0,self.nbr_keys):
            logging.debug('Adding keys to 2 button switch: {}'.format(key) )
            k_address =  self.address[4:14]+'key' + str(key)
            k_address = self.poly.getValidAddress(str(k_address))
            k_name =  str(self.name) + ' key' + str(key+1)
            k_name = self.poly.getValidName(str(k_name))
            self.keys[key] = udiRemoteKey(self.poly, self.address, k_address, k_name, key)
            self.adr_list.append(k_address)
            logging.debug('Waiting for node to complete{}'.format(self.adr_list))
            self.wait_for_node_done()



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
        logging.info('Stop udiYoSwitch')
        self.node.setDriver('ST', 0, True, True)
        self.yoSwitch.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    def checkOnline(self):
        self.yoSwitch.refreshDevice() 
    
    
    def checkDataUpdate(self):
        if self.yoSwitch.data_updated():
            self.updateData()


    def updateData(self):
        if self.node is not None:
            state =  self.yoSwitch.getState().upper()
            if self.yoSwitch.online:
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
                
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                    self.node.setDriver('GV1', 0, True, False)
                    self.node.setDriver('GV2', 0, True, False)
                if self.yoSwitch.suspended:
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
           
            sch_info = self.yoSwitch.getScheduleInfo(self.schedule_selected)
            logging.debug('sch_info {}'.format(sch_info))
            if sch_info:
                #if 'ch' in sch_info:
                #    self.node.setDriver('GV12', sch_info['ch'])
                self.node.setDriver('GV13', self.schedule_selected)
                if self.yoSwitch.isScheduleActive(self.schedule_selected):
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
        self.yoSwitch.updateStatus(data)
        self.updateData()
 
    def set_switch_on(self, command = None):
        logging.info('udiYoSwitch set_switch_on')  
        self.yoSwitch.setState('ON')
        self.node.setDriver('GV0',1 , True, True)
        #self.node.reportCmd('DON')

    def set_switch_off(self, command = None):
        logging.info('udiYoSwitch set_switch_off')  
        self.yoSwitch.setState('OFF')
        self.node.setDriver('GV0',0 , True, True)
        #self.node.reportCmd('DOF')

    def set_switch_fon(self, command = None):
        logging.info('udiYoSwitch set_switch_on')  
        self.yoSwitch.setState('ON')
        self.node.setDriver('GV0',1 , True, True)
        #self.node.reportCmd('DFON')

    def set_switch_foff(self, command = None):
        logging.info('udiYoSwitch set_switch_off')  
        self.yoSwitch.setState('OFF')
        self.node.setDriver('GV0',0 , True, True)
        #self.node.reportCmd('DFOF')


    def switchControl(self, command):
        logging.info('udiYoSwitch switchControl') 
        ctrl = int(command.get('value'))     
        if ctrl == 1:
            self.yoSwitch.setState('ON')
            self.node.setDriver('GV0',1 , True, True)
            self.node.reportCmd('DON')
        elif ctrl == 0:
            self.yoSwitch.setState('OFF')
            self.node.setDriver('GV0',0 , True, True)
            self.node.reportCmd('DOF')
        elif ctrl == 2: #toggle
            state = str(self.yoSwitch.getState()).upper() 
            if state == 'ON':
                self.yoSwitch.setState('OFF')
                self.node.setDriver('GV0',0 , True, True)
                self.node.reportCmd('DOF')
            elif state == 'OFF':
                self.yoSwitch.setState('ON')
                self.node.setDriver('GV0',1 , True, True)
                self.node.reportCmd('DON')
        elif ctrl == 5:
            logging.info('switchControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.node.setDriver('GV1', self.onDelay * 60, True, True)
            self.node.setDriver('GV2', self.offDelay * 60 , True, True)
            self.yoSwitch.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

            #Unknown remains unknown
    

    def prepOnDelay(self, command ):
        
        self.onDelay =int(command.get('value'))
        logging.info('udiYoSwitch prepOnDelay {}'.format(self.onDelay))
        #self.yoSwitch.setOnDelay(delay)
        #self.node.setDriver('GV1', delay*60, True, True)

    def prepOffDelay(self, command):

        self.offDelay =int(command.get('value'))
        logging.info('udiYoSwitch prepOffDelay {}'.format(self.offDelay))
        #self.yoSwitch.setOffDelay(delay)
        #self.node.setDriver('GV2', delay*60, True, True)

    def program_delays(self, command):
        logging.info('udiYoOutlet program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.node.setDriver('GV1', self.onDelay * 60, True, True)
        self.node.setDriver('GV2', self.offDelay * 60 , True, True)
        self.yoSwitch.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    def update(self, command = None):
        logging.info('udiYoSwitch Update Status')
        self.yoSwitch.refreshDevice()
        #self.yoSwitch.refreshSchedules()
        
        
    def lookup_schedule(self, command):
        logging.info('udiYoSwitch lookup_schedule {}'.format(command))
        self.schedule_selected = int(command.get('value'))
        self.yoSwitch.refreshSchedules()

    def define_schedule(self, command):
        logging.info('udiYoSwitch define_schedule {}'.format(command))
        query = command.get("query")
        self.schedule_selected = int(query.get('index.uom25'))
        tmp = int(query.get('active.uom25'))
        self.activated = (tmp == 1)
        if 'startH.uom19' in query:
            StartH = int(query.get('startH.uom19'))
            StartM = int(query.get('startM.uom44'))
        else:
            startH = 25
            StartM = 0
        if 'stopH.uom19' in query:
            StopH = int(query.get('stopH.uom19'))
            StopM = int(query.get('stopM.uom44'))
        else:
            startH = 25
            StartM = 0      

        binDays = int(query.get('bindays.uom25'))

        params = {}
        params['index'] = str(self.schedule_selected )
        params['isValid'] = self.activated 
        params['on'] = str(StartH)+':'+str(StartM)
        params['off'] = str(StopH)+':'+str(StopM)
        params['week'] = binDays
        self.yoSwitch.setSchedule(self.schedule_selected, params)

    def control_schedule(self, command):
        logging.info('udiYoSwitch control_schedule {}'.format(command))       
        query = command.get("query")
        self.schedule_selected = int(query.get('index.uom25'))
        tmp = int(query.get('active.uom25'))
        self.activated = (tmp == 1)
        self.yoSwitch.activateSchedule(self.schedule_selected, self.activated)
        

    commands = {
                'UPDATE'        : update,
                'QUERY'         : update,
                'DON'           : set_switch_on,
                'DOF'           : set_switch_off,    
                'DFON'          : set_switch_fon,
                'DFOF'          : set_switch_foff,                         
                'SWCTRL'        : switchControl, 
                'ONDELAY'       : prepOnDelay,
                'OFFDELAY'      : prepOffDelay,
                'DELAY_CTRL'    : program_delays, 
                'LOOKUP_SCH'    : lookup_schedule,
                'DEFINE_SCH'    : define_schedule,
                'CTRL_SCH'      : control_schedule,                
                }




