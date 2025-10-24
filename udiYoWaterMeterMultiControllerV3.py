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
from yolinkWaterMeterControllerV3 import YoLinkWaterMeter
from yolinkLeakSensorV2 import YoLinkLeakSensor



class udiYoWaterMeterMultiController(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, w_unit2ISY, save_cmd_state, retrieve_cmd_state, bool2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yowatermeterMulti'
    '''
       drivers = [
            'GV0' = Manipulator State
            'GV1' = Meter count
            'GV2' = OnDelay
            'GV3' = OffDelay
            'BATLVL' = BatteryLevel
            'GV4-9' = alarms
            'GV10' = Supply type
            'ST' = GV0 
            ]
    ''' 
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25}, # Water flowing
            {'driver': 'GV30', 'value': 0, 'uom': 25},  #online
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 69}, #water use total
            {'driver': 'GV10', 'value': 99, 'uom': 25}, #water use daily             
            {'driver': 'GV2', 'value': 0, 'uom': 69},  #wateruse recent
            {'driver': 'GV3', 'value': 0, 'uom': 44},  #Wateruse duration
            {'driver': 'GV4', 'value': 99, 'uom': 25}, #alarm
            {'driver': 'GV5', 'value': 99, 'uom': 25}, 
            {'driver': 'GV6', 'value': 99, 'uom': 25}, 
            {'driver': 'GV7', 'value': 99, 'uom': 25}, 
            {'driver': 'GV8', 'value': 99, 'uom': 25},                                              
            {'driver': 'GV9', 'value': 99, 'uom': 25}, 
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
            {'driver': 'GV11', 'value': 99, 'uom' : 25}, # Unit
            {'driver': 'GV12', 'value': 99, 'uom' : 6}, #  leak limit
            {'driver': 'GV13', 'value': 99, 'uom' : 25}, # auto shutoffg
            {'driver': 'GV14', 'value': 99, 'uom' : 6}, # Water flowing
            {'driver': 'GV15', 'value': 99, 'uom' : 25}, # auto shutoffg
            {'driver': 'GV16', 'value': 99, 'uom' : 44}, # Water flowing
            {'driver': 'GV17', 'value': 99, 'uom' : 25}, # auto shutoffg

            {'driver': 'GV20', 'value': 0, 'uom': 25},
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},                
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoWaterMeterMultiController INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []
        self.yoAccess = yoAccess

        self.temp_unit = self.yoAccess.get_temp_unit()        
        if self.temp_unit == 1:
            self.id = 'yowatermeterMultiF'        
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
        logging.info('Start - udiYoWaterMeterMultiController')
        self.my_setDriver('GV30', 1)
        self.my_setDriver('GV20', 0)
        self.yoWaterCtrl= YoLinkWaterMeter(self.yoAccess, self.devInfo, self.updateStatus)
        
        time.sleep(4)
        self.yoWaterCtrl.initNode()
        time.sleep(2)
        #self.my_setDriver('GV30', 1)
        #self.yoWaterCtrl.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.node_ready = True
        self.updateData()

    def stop (self):
        logging.info('Stop udiYoWaterMeterMultiController')
        self.my_setDriver('GV30', 0)
        self.yoWaterCtrl.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    def checkOnline(self):
        #get get info even if battery operated 
        self.yoWaterCtrl.refreshDevice()    

    def checkDataUpdate(self):
        if self.yoWaterCtrl.data_updated():
            #self.yoWaterCtrl.refreshDevice() 
            self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.my_setDriver('GV1', 0)
        #    self.my_setDriver('GV2', 0)

    def unit2uom(self) -> int:
        logging.debug('unit2uom')
        isy_uom = None
        if self.yoWaterCtrl.uom == 0:
            isy_uom = 69 # gallon
        if self.yoWaterCtrl.uom == 1:
            isy_uom = 6 #ft^3
        if self.yoWaterCtrl.uom == 2:
            isy_uom = 8 #m^3
        if self.yoWaterCtrl.uom == 3:
            isy_uom = 35 # liter                       
        return(isy_uom)

    def updateData(self):
        try:
            if self.node is not None:
                self.my_setDriver('TIME', self.yoWaterCtrl.getLastUpdateTime(), 151)
                if self.yoWaterCtrl.online:
                    self.my_setDriver('GV30', 1)
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
                    logging.debug(f'meter: {meter}')
                    if meter != None:
                        if 'water_runing' in meter:
                            self.my_setDriver('ST', meter['water_runing'])
                        else:
                            self.my_setDriver('ST', None)
                        if 'total' in meter:
                            self.my_setDriver('GV1', meter['total'],  self.unit2uom())
                        else:
                            self.my_setDriver('GV1', None)
                        if 'daily_usage' in meter:
                            self.my_setDriver('GV10', meter['daily_usage'],  self.unit2uom())
                        else:
                            self.my_setDriver('GV10', None)
                        if 'recent_amount' in meter:
                            self.my_setDriver('GV2', meter['recent_amount'],  self.unit2uom())
                        else:
                            self.my_setDriver('GV2', None)
                        if 'recent_duration' in meter:
                            self.my_setDriver('GV3', meter['recent_duration'],  44)
                        else:
                            self.my_setDriver('GV3', None)

                    pwr_mode, bat_lvl =  self.yoWaterCtrl.getBattery()  
                    logging.debug('udiYoWaterMeterMultiController - getBattery: {},  {}  '.format(pwr_mode, bat_lvl))
                    if pwr_mode == 'PowerLine':
                        self.my_setDriver('BATLVL', 98, 25)
                    else:
                        self.my_setDriver('BATLVL', bat_lvl, 25)

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

                    attributes = self.yoWaterCtrl.getAttributes()
                    if attributes:
                        if 'meterUnit' in attributes:
                            self.my_setDriver('GV11', attributes['meterUnit'], 25)                    
                        if 'leakLimit' in attributes:
                            self.my_setDriver('GV12', attributes['leakLimit'], self.unit2uom())
                        if 'autoCloseValve' in attributes:
                            self.my_setDriver('GV13', self.bool2ISY(attributes['autoCloseValve']), 25)
                        if 'overrunAmountACV' in attributes:
                            self.my_setDriver('GV15', self.bool2ISY(attributes['overrunAmountACV']), 25)
                        if 'overrunDurationACV' in attributes:
                            self.my_setDriver('GV17', self.bool2ISY(attributes['overrunDurationACV']), 25)
                        if 'overrunAmount' in attributes:
                            self.my_setDriver('GV14', attributes['overrunAmount'],self.unit2uom())
                        if 'overrunDuration' in attributes:
                            self.my_setDriver('GV16', attributes['overrunDuration'], 44)


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
                    self.my_setDriver('GV30', 0)
                    #self.my_setDriver('BATLVL', 99, 25)
                    self.my_setDriver('GV20', 2)
                
        except KeyError as e:
            logging.error(f'EXCEPTION - {e}')
    def updateStatus(self, data):
        logging.info('updateStatus - udiYoWaterMeterMultiController')
        self.yoWaterCtrl.updateStatus(data)
        self.updateData()

    '''
    def updateDelayCountdown( self, timeRemaining):

        logging.debug('udiYoWaterMeterMultiController updateDelayCountDown:  delays {}'.format(timeRemaining))
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
        logging.info('udiYoWaterMeterMultiController manipuControl')
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
            logging.info('udiYoWaterMeterMultiController set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60)
            self.yoWaterCtrl.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 
    '''

    def set_open(self, command = None):
        logging.info('udiYoWaterMeterMultiController - set_open')
        self.yoWaterCtrl.setState('open')
        self.valveState  = 1
        self.my_setDriver('GV0',self.valveState )

        #self.node.reportCmd('DON')

    def set_close(self, command = None):
        logging.info('udiYoWaterMeterMultiController - set_close')
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

    def set_attributes(self, command):
        logging.info(f'set_attributes {command}')
        query = command.get("query")
        data={}
        data['attributes'] = {}
        leak_lim = None
        or_lim = None
        if 'L_LIMIT.uom69' in query:
            leak_lim = float(query.get('L_LIMIT.uom69'))
        elif 'L_LIMIT.uom6' in query:
            leak_lim = float(query.get('L_LIMIT.uom6'))
        elif 'L_LIMIT.uom8' in query:
            leak_lim = float(query.get('L_LIMIT.uom8'))
        elif 'L_LIMIT.uom35' in query:
            leak_lim = float(query.get('L_LIMIT.uom35'))
        if leak_lim:
            data['attributes'] ['leakLimit'] = leak_lim

        if 'L_OFF.uom25' in query:
            data['attributes'] ['autoCloseValve'] = bool(query.get('L_OFF.uom25'))

        if 'OR_LIMIT.uom69' in query:
            or_lim = float(query.get('OR_LIMIT.uom69'))
        elif 'OR_LIMIT.uom6' in query:
            or_lim = float(query.get('OR_LIMIT.uom6'))
        elif 'OR_LIMIT.uom8' in query:
            or_lim = float(query.get('OR_LIMIT.uom8'))
        elif 'OR_LIMIT.uom35' in query:
            or_lim = float(query.get('OR_LIMIT.uom35'))   
        if or_lim:
            data['attributes'] ['overrunAmount'] = or_lim     
        if 'OR_OFF.uom25' in query:
            data['attributes'] ['overrunAmountACV'] = bool(query.get('OR_OFF.uom25')) 
        if 'ORT_LIMIT.uom44' in query:
            data['attributes'] ['overrunDuration']  = int(query.get('ORT_LIMIT.uom44'))
        if 'ORT_OFF' in query:
            data['attributes'] ['overrunDurationACV']  = bool(query.get('ORT_OFF.uom25'))

        self.yoWaterCtrl.setAttributes(data)


    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoWaterCtrl.refreshDevice()
        
    def program_delays(self, command):
        logging.info('udiYoOutlet program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        self.yoWaterCtrl.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    commands = {
                'UPDATE': update,
                'QUERY' : update,
                'DON'   : set_open,
                'DOF'   : set_close,
                'SETATTRIB' : set_attributes,
                #'VALVECTRL': waterCtrlControl, 
                'DELAYCTRL' : program_delays,
                #'OFFDELAY' : prepOffDelay 
                }




