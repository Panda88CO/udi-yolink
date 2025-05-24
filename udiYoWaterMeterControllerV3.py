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
from yolinkWaterMeterControllerV2 import YoLinkWaterMeter




class udiYoWaterMeterController(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, bool2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yowatermeterCtrl'
    '''
       drivers = [
            'GV0' = Manipulator State
            'GV1' = Meter count
            'GV2' = OnDelay
            'GV3' = OffDelay
            'BATLVL' = BatteryLevel
            'GV4-9' = alarms
            'GV10' = Supply type
            'ST' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},  # Water flowing
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 69}, #water use
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'GV3', 'value': 0, 'uom': 57}, 
            {'driver': 'GV4', 'value': 99, 'uom': 25}, 
            {'driver': 'GV5', 'value': 99, 'uom': 25}, 
            {'driver': 'GV6', 'value': 99, 'uom': 25}, 
            {'driver': 'GV7', 'value': 99, 'uom': 25}, 
            {'driver': 'GV8', 'value': 99, 'uom': 25},                                              
            {'driver': 'GV9', 'value': 99, 'uom': 25}, 
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
            {'driver': 'GV10', 'value': 99, 'uom': 25}, 
            {'driver': 'GV11', 'value': 99, 'uom' : 25}, # Water flowing
            {'driver': 'GV12', 'value': 99, 'uom' : 6}, # Water flowing
            {'driver': 'GV13', 'value': 99, 'uom' : 25}, # auto shutoffg
            {'driver': 'GV14', 'value': 99, 'uom' : 6}, # Water flowing
            {'driver': 'GV15', 'value': 99, 'uom' : 25}, # auto shutoffg
            {'driver': 'GV16', 'value': 99, 'uom' : 44}, # Water flowing
            {'driver': 'GV17', 'value': 99, 'uom' : 25}, # auto shutoffg
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
            {'driver': 'GV20', 'value': 0, 'uom': 25},
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},                
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoWaterMeterController INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoWaterCtrl= None
        self.node_ready = False
        self.last_state = ''
        self.timer_cleared = True
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
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
        logging.info('Start - udiYoWaterMeterController')
        #self.my_setDriver('ST', 1)
        self.my_setDriver('GV20', 0)
        self.yoWaterCtrl= YoLinkWaterMeter(self.yoAccess, self.devInfo, self.updateStatus)
        
        time.sleep(4)
        self.yoWaterCtrl.initNode()
        time.sleep(2)
        #self.my_setDriver('ST', 1)
        #self.yoWaterCtrl.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.node_ready = True

    def stop (self):
        logging.info('Stop udiYoWaterMeterController')
        #self.my_setDriver('ST', 0)
        self.yoWaterCtrl.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    def checkOnline(self):
        #get get info even if battery operated 
        self.yoWaterCtrl.refreshDevice()    

    def checkDataUpdate(self):
        if self.yoWaterCtrl.data_updated():
            self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.my_setDriver('GV1', 0)
        #    self.my_setDriver('GV2', 0)

    def updateData(self):
        if self.node is not None:
            self.my_setDriver('TIME', self.yoWaterCtrl.getLastUpdateTime(), 151)
            if self.yoWaterCtrl.online:
                #self.my_setDriver('ST', 1)
                state =  self.yoWaterCtrl.getValveState()
                if state != None:
                    if state.upper() == 'OPEN':
                        self.valveState = 1
                        self.my_setDriver('GV0', self.valveState)
                        if self.last_state != state:
                            self.node.reportCmd('DON')
                    elif state.upper() == 'CLOSED':
                        self.valveState = 0
                        self.my_setDriver('GV0', self.valveState)
                        if self.last_state != state:
                            self.node.reportCmd('DOF')
                    elif state.upper() == 'UNKNOWN':
                        self.my_setDriver('GV0', 99)                        
                    self.last_state = state


                meter  = self.yoWaterCtrl.getMeterReading()
                if meter != None:
                    if meter == 'Unknown':
                        self.my_setDriver('GV1', 99,  25)
                    else:
                        self.my_setDriver('GV1', meter,  69)
                #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
                #if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
                #    self.my_setDriver('GV2', 0)
                #    self.my_setDriver('GV3', 0)  

                pwr_mode, bat_lvl =  self.yoWaterCtrl.getBattery()  
                logging.debug('udiYoWaterMeterController - getBattery: {},  {}  '.format(pwr_mode, bat_lvl))
                self.my_setDriver('BATLVL', bat_lvl)          
                if pwr_mode == 'Unknown':
                    self.my_setDriver('GV10', 99)
                elif pwr_mode == 'PowerLine':
                    self.my_setDriver('GV10', 0)
                else:
                    self.my_setDriver('GV10', 1)

                alarms = self.yoWaterCtrl.getAlarms()
                if alarms:
                    if 'openReminder' in alarms:
                        self.my_setDriver('GV4', self.bool2ISY(alarms['openReminder']))
                    
                    if 'leak' in alarms:
                        self.my_setDriver('GV5', self.bool2ISY(alarms['leak']))
    
                    if 'amountOverrun' in alarms:
                        self.my_setDriver('GV6', self.bool2ISY(alarms['amountOverrun']))

                    if 'durationOverrun' in alarms:
                        self.my_setDriver('GV7', self.bool2ISY(alarms['durationOverrun']))
    
                    if 'valveError' in alarms:
                        self.my_setDriver('GV8', self.bool2ISY(alarms['valveError']))

                    if 'reminder' in alarms:
                        self.my_setDriver('GV9', self.bool2ISY(alarms['reminder']))
    
                if self.yoWaterCtrl.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

            else:
                #self.my_setDriver('GV0', 99, 25)
                #self.my_setDriver('GV1', 99, 25)
                
                #self.my_setDriver('GV4', 99, 25)
                #self.my_setDriver('GV5', 99, 25)
                #self.my_setDriver('GV6', 99, 25)
                #self.my_setDriver('GV7', 99, 25)
                #self.my_setDriver('GV8', 99, 25)
                #self.my_setDriver('GV9', 99, 25)
                #self.my_setDriver('GV10', 99, 25)
                #self.my_setDriver('BATLVL', 99, 25)
                self.my_setDriver('ST', 0)
                #self.my_setDriver('BATLVL', 99, 25)
                self.my_setDriver('GV20', 2)
            
    def updateStatus(self, data):
        logging.info('updateStatus - udiYoWaterMeterController')
        self.yoWaterCtrl.updateStatus(data)
        self.updateData()

    '''
    def updateDelayCountdown( self, timeRemaining):

        logging.debug('udiYoWaterMeterController updateDelayCountDown:  delays {}'.format(timeRemaining))
        max_delay = 0
        for delayInfo in range(0, len(timeRemaining)):
            if 'ch' in timeRemaining[delayInfo]:
                if timeRemaining[delayInfo]['ch'] == 1:
                    if 'on' in timeRemaining[delayInfo]:
                        self.my_setDriver('GV2', timeRemaining[delayInfo]['on'])
                        if max_delay < timeRemaining[delayInfo]['on']:
                            max_delay = timeRemaining[delayInfo]['on']
                    if 'off' in timeRemaining[delayInfo]:
                        self.my_setDriver('GV3', timeRemaining[delayInfo]['off'])
                        if max_delay < timeRemaining[delayInfo]['off']:
                            max_delay = timeRemaining[delayInfo]['off']
                    self.my_setDriver('GV0', self.valveState)
        self.timer_expires = time.time()+max_delay
    
    def waterCtrlControl(self, command):
        logging.info('udiYoWaterMeterController manipuControl')
        state = int(command.get('value'))
        if state == 1:
            self.yoWaterCtrl.setState('open')
            self.valveState = 1
            self.my_setDriver('GV0',self.valveState)
   
            #self.node.reportCmd('DON')
        elif state == 0:
            self.yoWaterCtrl.setState('closed')
            self.valveState  = 0
            self.my_setDriver('GV0',self.valveState)
            #self.node.reportCmd('DOF')
        elif state == 5:
            logging.info('udiYoWaterMeterController set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60)
            self.yoWaterCtrl.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 
    '''

    def set_open(self, command = None):
        logging.info('udiYoWaterMeterController - set_open')
        self.yoWaterCtrl.setState('open')
        self.valveState  = 1
        self.my_setDriver('GV0',self.valveState )

        #self.node.reportCmd('DON')

    def set_close(self, command = None):
        logging.info('udiYoWaterMeterController - set_close')
        self.yoWaterCtrl.setState('closed')
        self.valveState  = 0
        self.my_setDriver('GV0',self.valveState )
        #self.node.reportCmd('DOF')


    def prepOnDelay(self, command ):
        self.onDelay =int(command.get('value'))
        logging.info('prepOnDelay {}'.format(self.onDelay))
        #self.yoWaterCtrl.setOnDelay(delay)
        #self.my_setDriver('GV1', delay*60)
        #self.my_setDriver('GV0',self.valveState)

    def prepOffDelay(self, command):
        logging.info('setOnDelay Executed')
        self.offDelay =int(command.get('value'))
        logging.info('setOnDelay Executed {}'.format(self.offDelay))

        #self.yoWaterCtrl.setOffDelay(delay)
        #self.my_setDriver('GV2', delay*60, True, True)
        #self.my_setDriver('GV0',self.valveState  , True, True)

    def set_attributes(yolike, command):
        logging.info(f'set_attributes {command}')
        


    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoWaterCtrl.refreshDevice()



    commands = {
                'UPDATE': update,
                'QUERY' : update,
                'DON'   : set_open,
                'DOF'   : set_close,
                'SETATTRIB' : set_sttributes,
                #'VALVECTRL': waterCtrlControl, 
                #'ONDELAY' : prepOnDelay,
                #'OFFDELAY' : prepOffDelay 
                }




