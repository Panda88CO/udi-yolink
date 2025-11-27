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

from ctypes import set_errno
from os import truncate
#import udi_interface
#import sys
import time
from yolinkOutletV2 import YoLinkOutl



class udiYoOutlet(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, prep_schedule, convert_timestr_to_epoch, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, bool2ISY, mask2key
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
            {'driver': 'GV3', 'value': -1, 'uom': 30},
            {'driver': 'GV4', 'value': -1, 'uom': 33},
            {'driver': 'GV5', 'value': 99, 'uom': 25},
            {'driver': 'GV6', 'value': 99, 'uom': 25},
            {'driver': 'GV7', 'value': 99, 'uom': 25},
            {'driver': 'GV8', 'value': 99, 'uom': 25},

            {'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            {'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            {'driver': 'GV15', 'value': 99, 'uom': 25}, #start Hour
            {'driver': 'GV16', 'value': 99, 'uom': 25}, #start Min
            {'driver': 'GV21', 'value': 99, 'uom': 25}, #start Sec            
            {'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            {'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min                                        
            {'driver': 'GV22', 'value': 99, 'uom': 25}, #stop Sec
                        
            {'driver': 'GV19', 'value': 0, 'uom': 25}, #days
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 0, 'uom': 25},            
            {'driver': 'GV20', 'value': 99, 'uom': 25},              
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiYoOutletPwr INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []
     
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo   
        self.yoOutlet = None
        self.node_ready = False
        self.powerSupported = False # assume 
        model = str(deviceInfo['modelName'][:6])        
        if model in ['YS6803','YS6602','YS5716', 'YS6614']:
            self.id = 'yooutletPwr'
            self.powerSupported = True  

        self.last_state = ''
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.schedule_selected = None
  
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
               

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        #self.my_setDriver('GV30', 1)
        self.adr_list = []
        self.adr_list.append(address)


    def start(self):
        logging.info('start - YoOutlet')
        self.my_setDriver('GV30', 0)
        self.yoOutlet  = YoLinkOutl(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoOutlet.initNode()
        time.sleep(2)

        self.yoOutlet.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.yoOutlet.refreshSchedules()
        self.node_ready = True
        
    
    def stop (self):
        logging.info('Stop udiYoOutlet')
        self.my_setDriver('GV30', 0)
        self.yoOutlet.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkDataUpdate(self):
        #if self.yoOutlet.data_updated():
        self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.my_setDriver('GV1', 0, True, False)
        #    self.my_setDriver('GV2', 0, True, False)     



    def updateData(self):
        logging.info('udiYoOutlet updateData -  {}'.format(self.schedule_selected))
        if self.node is not None:
            unix_time = self.yoOutlet.get_report_time('time')
            self.my_setDriver('TIME', unix_time, 151)
            if self.yoOutlet.online: 
                #if  self.yoOutlet.online:
                self.my_setDriver('GV30',1)
                #state = str(self.yoOutlet.getState()).upper()
                state = str(self.yoOutlet.get_data('state'))
                logging.debug('Outlet State : {} '. format(state))
                if state in ['on', 'open']:
                    self.my_setDriver('GV0',1 )
                    self.my_setDriver('ST',1 )
                    state =  'open'
                    #if self.last_state != state:
                    #    self.node.reportCmd('DON')  
                elif state in [ 'off', 'closed']:
                    self.my_setDriver('GV0', 0)
                    self.my_setDriver('ST', 0)
                    state = 'closed'
                    #if self.last_state != state:
                    #    self.node.reportCmd('DOF')  
                #else:
                #    self.my_setDriver('GV0', 99)
                self.last_state = state           
                      

                #tmp =  self.yoOutlet.getEnergy()
                #logging.debug('Power/Energy info : {} '. format(tmp))
                
                if self.powerSupported: 
                    power = self.yoOutlet.get_data(None, 'power')
                    if isinstance(power, int, float):
                        powerkW = round(power/10000,3) # reports 1/10W
                    self.my_setDriver('GV3', powerkW, 30)

                    energykWh = self.yoOutlet.get_data(None, 'watt')  
                    if isinstance(energykWh, int, float):            
                        energykWh = round(energykWh/10000,3) # reports 1/10Wh                    
                    self.my_setDriver('GV4', energykWh, 33)

                    self.my_setDriver('GV5', self.bool2ISY(self.yoOutlet.get_data('alertType', 'overload')))
                    self.my_setDriver('GV6', self.bool2ISY(self.yoOutlet.get_data('alertType', 'highLoad')))   
                    self.my_setDriver('GV7', self.bool2ISY(self.yoOutlet.get_data('alertType', 'lowLoad')))
                    self.my_setDriver('GV8', self.bool2ISY(self.yoOutlet.get_data('alertType', 'highTemperature'))) 
                    
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                    self.my_setDriver('GV1', 0)
                    self.my_setDriver('GV2', 0)
                if self.yoOutlet.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:

                self.my_setDriver('GV30',0)
                self.my_setDriver('GV20', 2)
  

        sch_info = self.yoOutlet.getScheduleInfo(self.schedule_selected)
        self.update_schedule_data(sch_info, self.schedule_selected)

    def updateStatus(self, data):
        logging.info('udiYoOutlet updateStatus')
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
        self.yoOutlet.refreshDevice()


    def set_outlet_on(self, command = None):
        logging.info('udiYoOutlet set_outlet_on')
        self.yoOutlet.setState('open')
        self.my_setDriver('GV0',1 )
        self.my_setDriver('ST',1 )
        #self.node.reportCmd('DON')

    def set_outlet_off(self, command = None):
        logging.info('udiYoOutlet set_outlet_off')
        self.yoOutlet.setState('closed')
        self.my_setDriver('GV0',0 )
        self.my_setDriver('ST',0 )
        #self.node.reportCmd('DOF')



    def outletControl(self, command):
        
        ctrl = int(command.get('value'))  
        logging.info('udiYoOutlet outletControl - {}'.format(ctrl))
        ctrl = int(command.get('value'))
        if ctrl == 1:
            self.yoOutlet.setState('open')
            self.my_setDriver('GV0',1 ) 
            self.my_setDriver('ST',1 )

            self.node.reportCmd('DON')
        elif ctrl == 0:
            self.yoOutlet.setState('closed')
            self.my_setDriver('GV0',0 )
            self.my_setDriver('ST',0 )
            self.node.reportCmd('DOF')
        elif ctrl == 2: #toggle
            state = str(self.yoOutlet.getState()).upper() 
            if state == 'open':
                self.yoOutlet.setState('closed')
                self.my_setDriver('GV0',0 )
                self.my_setDriver('ST',0 )
                self.node.reportCmd('DOF')
            elif state == 'closed':
                self.yoOutlet.setState('open')
                self.my_setDriver('GV0',1 )
                self.my_setDriver('ST',1 )
                self.node.reportCmd('DON')                
        elif ctrl == 5:
            logging.info('outletControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60 )
            self.yoOutlet.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


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
        self.yoOutlet.refreshDevice()

    def program_delays(self, command):
        logging.info('udiYoOutlet program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        self.yoOutlet.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 


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
        


    commands = {
                'UPDATE'        : update,
                'DON'           : set_outlet_on,
                'DOF'           : set_outlet_off,
                'SWCTRL'        : outletControl, 
                #'ONDELAY'       : prepOnDelay,
                #'OFFDELAY'      : prepOffDelay,
                'DELAYCTRL'    : program_delays, 
                'LOOKUPSCH'    : lookup_schedule,
                'DEFINESCH'    : define_schedule,
                'CTRLSCH'      : control_schedule,
                }




