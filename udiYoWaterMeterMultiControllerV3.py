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


class udiYoWaterMeterMulti(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, w_unit2ISY, save_cmd_state,water_meter_unit2uom, retrieve_cmd_state, state2ISY, bool2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

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
            {'driver': 'ST', 'value': 0, 'uom': 25}, # On line
            {'driver': 'GV5', 'value': 99, 'uom': 25}, #Leak
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
            {'driver': 'GV4', 'value': 99, 'uom' : 25}, # Unit
            {'driver': 'GV20', 'value': 0, 'uom': 25},
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},                
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name, )   
        logging.debug('udiYoWaterMeterMultiController INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []
        
        self.poly = polyglot
        self.yoAccess = yoAccess
        self.temp_unit = self.yoAccess.get_temp_unit()     # Curent multi unit does not report temp
        if self.temp_unit == 1:
            self.id = 'yowatermeterMultiF'    
        self.devInfo =  deviceInfo
        self.name = name
        self.address = address
        self.yoWaterCtrl= None
        self.node_ready = False
        self.last_state = ''
        self.meter_uom = None
        known_meters = ['']
        self.onDelay = 0
        self.offDelay = 0
        self.valveState = 99 # needed as class c device - keep value until online again 
        #polyglot.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(polyglot.START, self.start, self.address)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        # start processing events and create add our controller node
        self.poly.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.wm_nodes= {}


    def start(self):
        logging.info('Start - udiYoWaterMeterMultiController')
        self.my_setDriver('GV30', 1)
        self.my_setDriver('GV20', 0)
        self.yoWaterCtrl= YoLinkWaterMeter(self.yoAccess, self.devInfo, self.updateStatus)
        self.water_meter_list = []
        if self.yoWaterCtrl is None:
            logging.error('YoLinkWaterMultiMeter not created')
            return
        else:
            self.yoWaterCtrl.initNode()
            while not self.yoWaterCtrl.online:
                logging.info('waiting for watermeter to be online')
                time.sleep(1)
            self.yoWaterCtrl.getMeterCount()
            self.yoWaterCtrl.getMeterUnit()
            logging.debug(f'Water_meter_count {self.yoWaterCtrl.water_meter_count} unit {self.yoWaterCtrl.meter_unit}')
            self.my_setDriver('GV4', self.yoWaterCtrl.meter_unit, 25)          
            self.meter_uom = self.water_meter_unit2uom(self.yoWaterCtrl.meter_unit)
            if self.yoWaterCtrl.water_meter_count > 1:
                self.wm_nodes= {}
                for wm_index in range(0, self.yoWaterCtrl.water_meter_count):
                    address = f'{self.address[-12:]}_{wm_index}'
                    wm_address = self.poly.getValidAddress(address)
                    wm_name = self.poly.getValidName(f'{self.name} CH{wm_index+1}')

                    self.wm_nodes[wm_index] = udiYoSubWaterMeter(self.poly, self.address, wm_address, wm_name, wm_index, self.yoAccess, self.yoWaterCtrl)
                    self.adr_list.append(wm_address)
                    logging.info(f'Added Water Meter Node: {wm_name} at {wm_address}')

            
        time.sleep(4)
        self.yoWaterCtrl.initNode()
        time.sleep(2)
        #self.my_setDriver('GV30', 1)
        #self.yoWaterCtrl.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.node_ready = True
        self.updateData()


    def stop (self):
        logging.info('Stop udiYoWaterMeterMultiController')
        #self.my_setDriver('GV30', 0)
        self.yoWaterCtrl.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkDataUpdate(self):
        if self.yoWaterCtrl.data_updated():
            #self.yoWaterCtrl.refreshDevice() 
            self.updateData()

    def checkOnline(self):
        #get get info even if battery operated 
        self.yoWaterCtrl.refreshDevice()    


    def updateData(self):
        try:
            if self.node is not None:
                self.my_setDriver('TIME', self.yoWaterCtrl.getLastUpdateTime(), 151)
                if self.yoWaterCtrl.online:
                    self.my_setDriver('ST', 1)   
                    if self.yoWaterCtrl.emptyData():
                        logging.debug('Empty data received - skip updateData')
                        self.my_setDriver('GV20', 6)
                        return
                    if self.meter_uom is None:
                        logging.debug(f'meter unit : {self.yoWaterCtrl.meter_unit}')
                        self.my_setDriver('GV4', self.yoWaterCtrl.meter_unit, 25)          
                        self.meter_uom = self.water_meter_unit2uom(self.yoWaterCtrl.meter_unit)            
                    pwr_mode, bat_lvl =  self.yoWaterCtrl.getBattery()  
                    logging.debug('udiYoWaterMeterMultiController - getBattery: {},  {}  '.format(pwr_mode, bat_lvl))
                    if pwr_mode == 'PowerLine':
                        self.my_setDriver('BATLVL', 98, 25)
                    else:
                        self.my_setDriver('BATLVL', bat_lvl, 25)
                    leak = self.yoWaterCtrl.getData('alarm', 'leak')
                    logging.debug(f'leak : {leak}')
                    self.my_setDriver('GV5', self.state2ISY(leak))                 
               
                    if self.yoWaterCtrl.suspended:
                        self.my_setDriver('GV20', 1)
                    else:
                        self.my_setDriver('GV20', 0)

                    for wm_index in range(0, self.yoWaterCtrl.water_meter_count):
                        if wm_index in self.wm_nodes:
                            self.wm_nodes[wm_index].updateData()
                
                else:
                    self.my_setDriver('ST', 0)
                    self.my_setDriver('GV20', 2)
                
        except KeyError as e:
            logging.error(f'EXCEPTION - {e}')

    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoWaterCtrl.refreshDevice()
                    
    def updateStatus(self, data):
        logging.info('updateStatus - udiYoWaterMeterController')
        self.yoWaterCtrl.updateStatus(data)
        self.updateData()

    commands = {
                'UPDATE': update,

                }



class udiYoSubWaterMeter(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, w_unit2ISY, save_cmd_state,water_meter_unit2uom, retrieve_cmd_state, bool2ISY, state2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yowatermeterSub'
    '''
       drivers = [
            'GV0' = Manipulator State

            ]
    ''' 
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25}, # Water flowing
            {'driver': 'GV0', 'value': 99, 'uom': 25},#Valve state
            {'driver': 'GV1', 'value': 0, 'uom': 69}, #water use total
            {'driver': 'GV10', 'value': 99, 'uom': 25}, #water use daily             
            {'driver': 'GV2', 'value': 0, 'uom': 69},  #wateruse recent
            {'driver': 'GV3', 'value': 0, 'uom': 44},  #Wateruse duration
            {'driver': 'GV4', 'value': 99, 'uom': 25}, #WATER uNITS
            {'driver': 'GV6', 'value': 99, 'uom': 25}, #alarm
            {'driver': 'GV7', 'value': 99, 'uom': 25}, 
            {'driver': 'GV8', 'value': 99, 'uom': 25},                                              
            {'driver': 'GV9', 'value': 99, 'uom': 25}, 
            #{'driver': 'GV11', 'value': 99, 'uom' : 25}, # alarm
            {'driver': 'GV12', 'value': 99, 'uom' : 25}, #  alarm
            #{'driver': 'GV13', 'value': 99, 'uom' : 25}, # alarm
            #{'driver': 'GV14', 'value': 99, 'uom' : 25}, # Water flowing
             
            ]



    def  __init__(self, polyglot, primary, address, name, WMindex, yoAccess, wmAccess):
        super().__init__( polyglot, primary, address, name)   
        logging.debug(f'udiYoWaterMeterSub- {name}')
        self.n_queue = []
        self.yoAccess = yoAccess
        self.temp_unit = self.yoAccess.get_temp_unit()     
        #if self.temp_unit == 1:
        #    self.id = 'yowatermeterSubF'    

        self.WM_index = WMindex
        
        self.yoWaterCtrl= wmAccess
        self.node_ready = False
        self.last_state = ''
        self.meter_uom = None
        self.valveState = 99 # needed as class c device - keep value until online again 
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        #known_meters = ['YS5007','YS5018', 'YS5008', 'YS5009', 'YS5029']
        #if self.yoWaterCtrl.devInfo['model'] in known_meters:
        #    logging.debug(f'Known water meter model {self.yoWaterCtrl.devInfo["model"]}')   
        #    if self.yoWaterCtrl.devInfo['model'] in ['YS5029']: # dual channel model  -  no temps and not 

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)



    def start(self):
        logging.info('Start - udiYoWaterMeterMultiController')

        #self.yoWaterCtrl= YoLinkWaterMultiMeter(self.yoAccess, self.yoWaterCtrl.devInfo, self.updateStatus)
        
        #time.sleep(4)
        #self.yoWaterCtrl.initNode()
        time.sleep(2)
        self.yoWaterCtrl.getMeterUnit()
        #self.yoWaterCtrl.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.node_ready = True
        self.updateData()

    def stop (self):
        logging.info('Stop udiYoWaterMeterMultiController')

        self.yoWaterCtrl.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    def checkOnline(self):
        #get get info even if battery operated 
        pass

    def checkDataUpdate(self):
        if self.yoWaterCtrl.data_updated():
            self.updateData()


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
                if self.yoWaterCtrl.online:
                    #self.my_setDriver('GV30', 1)
                    if self.yoWaterCtrl.emptyData():
                        logging.debug('Empty data received - skip updateData')
                        self.my_setDriver('GV20', 6)
                        return
                    if self.meter_uom is None:
                        logging.debug(f'meter unit : {self.yoWaterCtrl.meter_unit}')
                        self.my_setDriver('GV4', self.yoWaterCtrl.meter_unit, 25)          
                        self.meter_uom = self.water_meter_unit2uom(self.yoWaterCtrl.meter_unit)
                    state =  self.yoWaterCtrl.getData('state', 'valve', self.WM_index)
                    #Needs to update 
                    
                    if state != None:
                        if state.lower() == 'open':
                            self.valveState = 1
                            self.my_setDriver('GV0', self.valveState)
                            if self.last_state != state:
                                self.node.reportCmd('DON')
                        elif state.lower() == 'closed':
                            self.valveState = 0
                            self.my_setDriver('GV0', self.valveState)
                            if self.last_state != state:
                                self.node.reportCmd('DOF')                 
                        self.last_state = state

                    water_flowing = self.yoWaterCtrl.getData('state','waterFlowing', self.WM_index)
                    logging.debug(f'water flowing : {water_flowing}')       
                    self.my_setDriver('ST', self.state2ISY(water_flowing ))
                    total_meter = self.yoWaterCtrl.getData('state','meter', self.WM_index)
                    logging.debug(f'total meter : {total_meter}')
                    self.my_setDriver('GV10', total_meter,  self.unit2uom())

                    daily_use = self.yoWaterCtrl.getData('dailyUsage', 'amount', self.WM_index)
                    logging.debug(f'daily use : {daily_use}')   
                    self.my_setDriver('GV0', daily_use,  self.unit2uom())
                    recent_amount = self.yoWaterCtrl.getData('recentUsage','amount', self.WM_index)
                    logging.debug(f'recent amount : {recent_amount}')
                    self.my_setDriver('GV2', recent_amount,  self.unit2uom())
                    recent_duration = self.yoWaterCtrl.getData('recentUsage','duration', self.WM_index)
                    logging.debug(f'recent duration : {recent_duration}')
                    self.my_setDriver('GV3', recent_duration,  44)  
                    meter_unit = self.yoWaterCtrl.getData('attributes', 'meterUnit')
                    logging.debug(f'meter unit : {meter_unit}')  
                    self.my_setDriver('GV4', meter_unit, 25)        
                    #pwr_mode, bat_lvl =  self.yoWaterCtrl.getBattery()  
                    #logging.debug('udiYoWaterMeterMultiController - getBattery: {},  {}  '.format(pwr_mode, bat_lvl))
                    #if pwr_mode == 'PowerLine':
                    #    self.my_setDriver('BATLVL', 98, 25)
                    #else:
                    #    self.my_setDriver('BATLVL', bat_lvl, 25)

                    #leak = self.yoWaterCtrl.getData('alarm', 'leak')
                    #logging.debug(f'leak : {leak}')
                    #self.my_setDriver('GV5', self.state2ISY(leak))
                    amount_overrun = self.yoWaterCtrl.getData('alarm', 'overrunAmount24H', self.WM_index ) #amountOverrun24H,amountOverrun 
                    if amount_overrun is None: # try alternate key
                        amount_overrun = self.yoWaterCtrl.getData('alarm', 'amountOverrun')
                    logging.debug(f'overrunAmount24H : {amount_overrun}')     
                    self.my_setDriver('GV6', self.state2ISY(amount_overrun))


                    duration_overrun = self.yoWaterCtrl.getData('alarm', 'overrunDurationOnce', self.WM_index) #durationOverrun overrunDurationOnce
                    if duration_overrun is None: # try alternate key
                        duration_overrun = self.yoWaterCtrl.getData('alarm', 'durationOverrun', self.WM_index)
                    logging.debug(f'duration overrun : {duration_overrun}')     
                    self.my_setDriver('GV7', self.state2ISY( duration_overrun))

                    times_overrun_24h = self.yoWaterCtrl.getData('alarm', 'overrunTimes24H', self.WM_index) #overrunTimes24H
                    logging.debug(f'times overrun 24h : {times_overrun_24h}')   
                    self.my_setDriver('GV8', self.state2ISY(times_overrun_24h))

                    #reminder = self.yoWaterCtrl.getData('alarm', 'reminder', self.WM_index) #reminder
                    #logging.debug(f'reminder : {reminder}')     
                    #self.my_setDriver('GV9', self.state2ISY(reminder))

                    open_reminder = self.yoWaterCtrl.getData('alarm', 'openReminder', self.WM_index) #openReminder
                    logging.debug(f'open reminder : {open_reminder}')
                    self.my_setDriver('GV11', self.state2ISY(open_reminder))

                    valve_error = self.yoWaterCtrl.getData('alarm', 'valveError', self.WM_index)   #valveError
                    logging.debug(f'valve error : {valve_error}')   
                    self.my_setDriver('GV12', self.state2ISY(valve_error))   


                    #high_T_error = self.yoWaterCtrl.getData('alarm', 'highTemp', self.WM_index)   #valveError
                    #logging.debug(f'high temp error : {high_T_error}')
                    #self.my_setDriver('GV12', self.state2ISY(high_T_error))    

                    #low_T_error = self.yoWaterCtrl.getData('alarm', 'lowTemp',self.WM_index)   #valveError
                    #logging.debug(f'low temp error : {low_T_error}')
                    #self.my_setDriver('GV13', self.state2ISY(low_T_error))
                    

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
        self.yoWaterCtrl.setValveState('open', self.WM_index)
        self.valveState  = 1
        self.my_setDriver('GV0',self.valveState )

        #self.node.reportCmd('DON')

    def set_close(self, command = None):
        logging.info('udiYoWaterMeterMultiController - set_close')
        self.yoWaterCtrl.setValveState('closed', self.WM_index)
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
        self.yoWaterCtrl.setDelayList([{'ch':str(self.WM_index), 'on':self.onDelay, 'off':self.offDelay}]) 

    def updateStatus(self, data):
        logging.info('updateStatus - udiYoWaterMeterController')
        self.yoWaterCtrl.updateStatus(data)
        self.updateData()

    commands = {
                'UPDATE': update,
                'QUERY' : update,
                'DON'   : set_open,
                'DOF'   : set_close,
                'SETATTRIB' : set_attributes,
                #'VALVECTRL': waterCtrlControl, 
                #'DELAYCTRL' : program_delays,
                #'OFFDELAY' : prepOffDelay 
                }




