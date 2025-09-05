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

#import udi_interface
#import sys
import time
import math
from yolinkSwitchV2 import YoLinkSW
from udiYoSmartRemoterV3 import udiRemoteKey

class udiYoSwitch(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yoswitch'
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            
            {'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            {'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            {'driver': 'GV15', 'value': 99, 'uom': 25}, #On Hour
            {'driver': 'GV16', 'value': 99, 'uom': 25}, #On Min
            {'driver': 'GV21', 'value': 99, 'uom': 25}, #onSec
            {'driver': 'GV17', 'value': 99, 'uom': 25}, #off Hour                                              
            {'driver': 'GV18', 'value': 99, 'uom': 25}, #off Min
            {'driver': 'GV22', 'value': 99, 'uom': 25}, #offSec            
            {'driver': 'GV19', 'value': 0, 'uom': 25}, #days

            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},      
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},        
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoSwitch2Button INIT- {}'.format(deviceInfo['name']))
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
        if  'YS5708' in deviceInfo['modelName'] or 'YS5709' in deviceInfo['modelName']:
            self.max_remote_keys = 8
            self.nbr_keys = 2
        else:
            self.max_remote_keys = 0
            self.nbr_keys = 0

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
               

        # start processing events and create add our controller node
        self.poly.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        
            

    def start(self):
        logging.info('start - udiYoSwitch')
        self.my_setDriver('ST', 0)
        self.yoSwitch  = YoLinkSW(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(3)
        self.yoSwitch.initNode()
        time.sleep(2)
        #self.my_setDriver('ST', 1)
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
                        self.my_setDriver('GV1', timeRemaining[delayInfo]['on'])
                        if max_delay < timeRemaining[delayInfo]['on']:
                            max_delay = timeRemaining[delayInfo]['on']
                    if 'off' in timeRemaining[delayInfo]:
                        self.my_setDriver('GV2', timeRemaining[delayInfo]['off'])
                        if max_delay < timeRemaining[delayInfo]['off']:
                            max_delay = timeRemaining[delayInfo]['off']
        self.timer_expires = time.time()+max_delay
      

    def stop (self):
        logging.info('Stop udiYoSwitch')
        self.my_setDriver('ST', 0)
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
            self.my_setDriver('TIME', self.yoSwitch.getLastUpdateTime(), 151)

            if self.yoSwitch.online:
                self.my_setDriver('ST', 1)
                if state == 'ON':
                    self.my_setDriver('GV0', 1)
                    self.node.reportCmd('DON')  
                elif  state == 'OFF':
                    self.my_setDriver('GV0', 0)
                    self.node.reportCmd('DOF')  
                else:
                    self.my_setDriver('GV0', 99)
                self.last_state = state
                
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                    self.my_setDriver('GV1', 0)
                    self.my_setDriver('GV2', 0)
                if self.yoSwitch.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

            else:
                self.my_setDriver('ST', 0)
                self.my_setDriver('GV20', 2)


            if self.nbr_keys > 0:
                event_data = self.yoSwitch.getEventData()
                logging.debug('updateData - event data {}'.format(event_data))
                if event_data:
                    key_mask = event_data['keyMask']
                    press_type = event_data['type']
                    remote_key = self.mask2key(key_mask)
                    if press_type == 'LongPress':
                        press = self.max_remote_keys
                    else:
                        press = 0
                    logging.debug('remote key {} press {}'.format(remote_key, press))
                    
                    if self.yoSwitch.isControlEvent():
                        self.keys[remote_key].send_command(press)
                        self.yoSwitch.clearEventData()
                        logging.debug('clearEventData')           

            sch_info = self.yoSwitch.getScheduleInfo(self.schedule_selected)
            self.update_schedule_data(sch_info, self.schedule_selected)


    def updateStatus(self, data):
        logging.info('updateStatus - Switch')
        self.yoSwitch.updateStatus(data)
        self.updateData()
 
    def set_switch_on(self, command = None):
        logging.info('udiYoSwitch set_switch_on')  
        self.yoSwitch.setState('ON')
        self.my_setDriver('GV0',1 )
        #self.node.reportCmd('DON')

    def set_switch_off(self, command = None):
        logging.info('udiYoSwitch set_switch_off')  
        self.yoSwitch.setState('OFF')
        self.my_setDriver('GV0',0 )
        #self.node.reportCmd('DOF')

    def set_switch_fon(self, command = None):
        logging.info('udiYoSwitch set_switch_on')  
        self.yoSwitch.setState('ON')
        self.my_setDriver('GV0',1 )
        #self.node.reportCmd('DFON')

    def set_switch_foff(self, command = None):
        logging.info('udiYoSwitch set_switch_off')  
        self.yoSwitch.setState('OFF')
        self.my_setDriver('GV0',0 )
        #self.node.reportCmd('DFOF')


    def switchControl(self, command):
        logging.info('udiYoSwitch switchControl') 
        ctrl = int(command.get('value'))     
        if ctrl == 1:
            self.yoSwitch.setState('ON')
            self.my_setDriver('GV0',1 )
            #self.node.reportCmd('DON')
        elif ctrl == 0:
            self.yoSwitch.setState('OFF')
            self.my_setDriver('GV0',0 )
            #self.node.reportCmd('DOF')
        elif ctrl == 2: #toggle
            state = str(self.yoSwitch.getState()).upper() 
            if state == 'ON':
                self.yoSwitch.setState('OFF')
                self.my_setDriver('GV0',0 )
                #self.node.reportCmd('DOF')
            elif state == 'OFF':
                self.yoSwitch.setState('ON')
                self.my_setDriver('GV0',1 )
                #self.node.reportCmd('DON')
        elif ctrl == 5:
            logging.info('switchControl set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60 )
            self.yoSwitch.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

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
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
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
        self.schedule_selected, params = self.prep_schedule(query)
        self.yoSwitch.setSchedule(self.schedule_selected, params)


    def control_schedule(self, command):
        logging.info('udiYoSwitch control_schedule {}'.format(command))       
        query = command.get("query")
        self.activated, self.schedule_selected = self.activate_schedule(query)
        self.yoSwitch.activateSchedule(self.schedule_selected, self.activated)

    commands = {
                'UPDATE'        : update,
                'QUERY'         : update,
                'DON'           : set_switch_on,
                'DOF'           : set_switch_off,    
                'DFON'          : set_switch_fon,
                'DFOF'          : set_switch_foff,                         
                'SWCTRL'        : switchControl, 
                #'ONDELAY'       : prepOnDelay,
                #'OFFDELAY'      : prepOffDelay,
                'DELAY_CTRL'    : program_delays, 
                'LOOKUP_SCH'    : lookup_schedule,
                'DEFINE_SCH'    : define_schedule,
                'CTRL_SCH'      : control_schedule,                
                }




