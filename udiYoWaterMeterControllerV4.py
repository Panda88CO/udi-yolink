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

from os import truncate
import threading
#import udi_interface
#import sys
import time
from yolinkWaterMeterControllerV3 import YoLinkWaterMeter
from udiYoSchedule import udiYoSchedule




class udiYoWaterMeterController(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler, w_unit2ISY, water_meter_unit2uom, calculate_water_volume, get_meter_correction_factor, apply_meter_correction, state2ISY, bool2ISY, update_schedule_data, node_queue, wait_for_node_done, checkNameSync

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
            'ST' = GV0 
            ]
    ''' 
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25}, # Water flowing
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 99, 'uom': 25}, #water use total
            {'driver': 'GV10', 'value': 99, 'uom': 25}, #water use daily             
            {'driver': 'GV2', 'value': 99, 'uom': 25},  #wateruse recent
            {'driver': 'GV3', 'value': 99, 'uom': 44},  #Wateruse duration
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25},            
            #{'driver': 'GV4', 'value': 99, 'uom': 25}, #Measure Unit
            {'driver': 'GV5', 'value': 99, 'uom': 25}, #alarm
            {'driver': 'GV6', 'value': 99, 'uom': 25}, 
            {'driver': 'GV7', 'value': 99, 'uom': 25}, 
            {'driver': 'GV8', 'value': 99, 'uom': 25},                                              
            {'driver': 'GV9', 'value': 99, 'uom': 25}, 

            {'driver': 'GV11', 'value': 99, 'uom' : 25}, # 
            {'driver': 'GV12', 'value': 99, 'uom' : 25}, #  leak limit
            {'driver': 'GV13', 'value': 99, 'uom' : 25}, # auto shutoffg
            {'driver': 'GV14', 'value': 99, 'uom' : 25}, # Water flowing
            #{'driver': 'GV15', 'value': 99, 'uom' : 25}, # auto shutoffg
            #{'driver': 'GV16', 'value': 99, 'uom' : 44}, # Water flowing
            #{'driver': 'GV17', 'value': 99, 'uom' : 25}, # auto shutoffg
            {'driver': 'GV22', 'value': 99, 'uom': 25}, #LeakLimit
            {'driver': 'GV23', 'value': 99, 'uom': 25}, #Overrtun limit
            {'driver': 'GV24', 'value': 99, 'uom': 25}, #Overrun Time
    
            {'driver': 'GV25', 'value': 99, 'uom': 25}, #Leak AC
            {'driver': 'GV26', 'value': 99, 'uom': 25}, #LEakAC
            {'driver': 'GV27', 'value': 99, 'uom': 25}, #Overrun AC
            {'driver': 'GV28', 'value': 99, 'uom': 25}, #OverrunTIme AC        
            {'driver': 'GV20', 'value': 99, 'uom': 25},
            {'driver': 'GV30', 'value': 99, 'uom': 25},
            {'driver': 'TIME', 'value' :0, 'uom': 151},                
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoWaterMeterController INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.n_queue = []
        self.yoAccess = yoAccess
        self.ValveSupported = True
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.water_unit = self.yoAccess.get_water_unit()  
        model = str(deviceInfo['modelName'][:6])  
        if model in ['YS5007']:
            if self.temp_unit == 1 and self.water_unit == 0:
                self.id = 'yowatermeterCtrlF'
            else:
                self.id = 'yowatermeterCtrl'
            self.ValveSupported = False
            if self.commands.get('DON') is not None:
                del self.commands['DON']
            if self.commands.get('DOF') is not None:
                del self.commands['DOF']
        else: #YS5018 or YS5008 YS5009
            if self.temp_unit == 1 and self.water_unit == 0:
                self.id = 'yowatermeterCtrlF'
            else:   
                self.id = 'yowatermeterCtrl'

        if model in ['YS5029','YS5009']:
            self.scheduleSupport = False
        else:
            self.scheduleSupport = True

        if self.water_unit not in [0,3]:
            logging.error('Only Liters and Gallons supported for now')

        self.devInfo =  deviceInfo
        self.yoWaterCtrl= None

        self.schedule_valve = None
        self.schedule_leak = None
        self.node_ready = False
        self.system_ready = False
        self.configDone = False
        self._update_lock = threading.Lock()
        self.meter_count = 1
        self.last_state = ''
        self._last_reported_state = None
        self.timer_cleared = True
        self.timer_update = 5
        self.timer_expires = 0
        self.onDelay = 0
        self.offDelay = 0
        self.valveState = 99 # needed as class c device - keep value until online again 
        self.ISYmeter_uom = None
        self.ISYwater_unit = None
        self.meter_correction_factor = 1.0
        #polyglot.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(self.poly.START, self.start, self.address)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        #self.poly.subscribe(self.poly.STARTDONE, self.start_done)


        #known_meters = ['YS5007','YS5018', 'YS5008', 'YS5009', ]
        #if self.yoWaterCtrl.devInfo['model'] in known_meters:
        #    logging.debug(f'Known water meter model {self.yoWaterCtrl.devInfo["model"]}')   
        #    if self.yoWaterCtrl.devInfo['model'] in ['YS5029']: # dual channel model  -  no temps and not 

        # start processing events and create add our controller node
      
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        #self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        
        logging.debug('udiYoWaterMeterController INIT done- {}'.format(self.commands))
        self.node = self.poly.getNode(address)
        self.node_ready = True



    def start(self):
        logging.info('Start - udiYoWaterMeterController')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 1)
        self.my_setDriver('GV20', 0)
       
        self.yoWaterCtrl = YoLinkWaterMeter(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoWaterCtrl.initDevice()
        time.sleep(1)
        tries = 1
        while not self.yoWaterCtrl.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            self.poly.Notices['offline'] = f'Waiting for device {self.name} to come online...'
            time.sleep(min(60, tries*2))  # Exponential backoff, max 5 minutes
            #if tries % 10 == 0:
                #self.yoWaterCtrl.refreshDevice()    
            tries += 1
        self.poly.Notices.delete('offline')
        self.meter_unit = self.yoWaterCtrl.getMeterUnit()
        self.ISYwater_unit = self.yoAccess.get_water_unit()
        self.ISYmeter_uom = self.water_meter_unit2uom(self.ISYwater_unit)
        self.meter_correction_factor = self.get_meter_correction_factor(self.yoWaterCtrl)
        logging.debug(f'meter unit : {self.meter_unit} ISY unit: {self.ISYwater_unit} uom: {self.ISYmeter_uom}')
        
        self.start_done()

    def create_schedule_nodes(self):
        new_addresses = []
        if self.scheduleSupport:
            sch_address_valve = self.address[4:14] + '_VSC'
            sch_address_valve = self.poly.getValidAddress(sch_address_valve)
            self.schedule_valve = udiYoSchedule(self.poly, self.address, sch_address_valve, 'Valve Schedules', self.yoAccess, self.devInfo, schedule_type='valve')
            self.adr_list.append(sch_address_valve)
            new_addresses.append(sch_address_valve)
            sch_address_leak = self.address[4:14] + '_LSC'
            sch_address_leak = self.poly.getValidAddress(sch_address_leak)
            self.schedule_leak = udiYoSchedule(self.poly, self.address, sch_address_leak, 'Leak Schedules', self.yoAccess, self.devInfo, schedule_type='leak')
            self.adr_list.append(sch_address_leak)
            new_addresses.append(sch_address_leak)
        return new_addresses

    def stop (self):
        logging.info('Stop udiYoWaterMeterController')
        self.my_setDriver('GV30', 0)
        water_ctrl = self.yoWaterCtrl
        if water_ctrl is not None:
            water_ctrl.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_water_ctrl(self, caller):
        if self.yoWaterCtrl is None:
            logging.warning(f'udiYoWaterMeterController - {caller} skipped; water controller not initialized yet')
            return None
        return self.yoWaterCtrl

    def _normalize_binary_state(self, state):
        if not isinstance(state, str):
            return None
        state_l = state.lower()
        if state_l in ['on', 'open']:
            return 'on'
        if state_l in ['off', 'closed', 'close']:
            return 'off'
        return None

    def _report_binary_state_change(self, state):
        normalized_state = self._normalize_binary_state(state)
        if normalized_state is None:
            return
        if self._last_reported_state is None:
            self._last_reported_state = normalized_state
            return
        if self._last_reported_state == normalized_state:
            return
        if normalized_state == 'on':
            self.node.reportCmd('DON')
        else:
            self.node.reportCmd('DOF')
        self._last_reported_state = normalized_state
            
    def checkOnline(self):
        #get get info even if battery operated 
        water_ctrl = self._get_water_ctrl('checkOnline')
        if water_ctrl is None:
            return
        water_ctrl.refreshDevice()    

    def checkDataUpdate(self):
        water_ctrl = self._get_water_ctrl('checkDataUpdate')
        if water_ctrl is None:
            return
        if water_ctrl.data_updated():
            #self.yoWaterCtrl.refreshDevice() 
            self.updateData()
        #if time.time() >= self.timer_expires - self.timer_update:
        #    self.my_setDriver('GV1', 0)
        #    self.my_setDriver('GV2', 0)

    
    def unit2uom(self):
        isy_uom = None
        if self.water_unit == 0:
            isy_uom = 69 # gallon
        if self.water_unit== 1:
            isy_uom = 6 #ft^3
        if self.water_unit == 2:
            isy_uom = 8 #m^3
        if self.water_unit == 3:
            isy_uom = 35 # liter          
        logging.debug(f'unit2uom {isy_uom}')             
        return(isy_uom)
    
    def updateData(self):
        try:
            water_ctrl = self._get_water_ctrl('updateData')
            if water_ctrl is not None:
                while not self.node_ready or not self.system_ready or not self.configDone:
                    time.sleep(0.5)
                message_info = water_ctrl.get_message_type()
                if not isinstance(message_info, tuple) or len(message_info) != 2:
                    return
                message_type = message_info[0]
                message_action = message_info[1]
                unix_time = water_ctrl.get_report_time('time')
                self.my_setDriver('TIME', unix_time, 151)
                if self.meter_unit is None:
                    self.meter_unit = water_ctrl.getMeterUnit()
                    self.ISYwater_unit = self.yoAccess.get_water_unit()
                    self.ISYmeter_uom = self.water_meter_unit2uom(self.ISYwater_unit)
                    self.meter_correction_factor = self.get_meter_correction_factor(water_ctrl)

                if message_type and 'Schedules' in str(message_type):
                    # Route valve schedules to valve node
                    if 'Valve' in str(message_type) and self.schedule_valve is not None:
                        self.schedule_valve.update_schedule_data(source_device=water_ctrl)
                    # Route leak schedules to leak node
                    elif 'Leak' in str(message_type) and self.schedule_leak is not None:
                        self.schedule_leak.update_schedule_data(source_device=water_ctrl)
                    return

                if water_ctrl.check_system_online():
                    self.my_setDriver('GV30', 1)
                    if water_ctrl.emptyData():
                        logging.debug('Empty data received - skip updateData')
                        self.my_setDriver('GV20', 6)
                        return
                    if self.ISYmeter_uom is None:
                        logging.debug(f'meter unit : { self.meter_unit}')
                        #self.my_setDriver('GV4',  self.meter_unit, 25)          
                        self.ISYmeter_uom = self.water_meter_unit2uom( self.meter_unit)
                    if self.ValveSupported:
                        state = water_ctrl.get_data( 'valve', 'state')
                        logging.debug(f'valve state: {state}')                    
                        self.my_setDriver('GV0', self.state2ISY(state))
                        if state is not None:
                            if isinstance(state, str) and state.upper() == 'OPEN':
                                self.valveState = 1
                                #self.my_setDriver('GV0', self.valveState)
                            elif isinstance(state, str) and state.upper() == 'CLOSED':
                                self.valveState = 0
                                #self.my_setDriver('GV0', self.valveState)
                            self._report_binary_state_change(state)
                            #elif state.upper() == 'UNKNOWN':
                            #self.my_setDriver('GV0', 99)                        
                            self.last_state = state
                    

                    #meter  = self.yoWaterCtrl.getMeterReading()
                    #logging.debug(f'meter: {meter}')
                    #if meter != None:
                        #if 'water_runing' in meter:
                        #    self.my_setDriver('ST', meter['water_runing'])
                    water_flowing = water_ctrl.get_data('waterFlowing', 'state')
                    logging.debug(f'water flowing : {water_flowing}')       
                    self.my_setDriver('ST', self.state2ISY(water_flowing ), type=message_type)

                    total_meter = self.apply_meter_correction(water_ctrl.get_data('meter', 'state'), self.meter_correction_factor)
                    
                    if isinstance(total_meter, (int,float)):
                        total_meter =round(float(self.calculate_water_volume(total_meter,  self.meter_unit,  self.ISYwater_unit)), 1)
                    logging.debug(f'total meter : {total_meter}')
                    self.my_setDriver('GV1', total_meter,  self.ISYmeter_uom, type=message_type)
    
                    daily_use = self.apply_meter_correction(water_ctrl.get_data('amount', 'dailyUsage'), self.meter_correction_factor)
                    if isinstance(daily_use, (int,float)):   
                        daily_use =round(float(self.calculate_water_volume(daily_use,  self.meter_unit,  self.ISYwater_unit)), 1)
                    logging.debug(f'daily use : {daily_use}')
                    self.my_setDriver('GV10', daily_use,  self.ISYmeter_uom, type=message_type   )
                    recent_amount = self.apply_meter_correction(water_ctrl.get_data('amount','recentUsage'), self.meter_correction_factor)
                    if isinstance(recent_amount, (int,float)):
                        recent_amount = round(float(self.calculate_water_volume(recent_amount,  self.meter_unit,  self.ISYwater_unit)), 1)
                    logging.debug(f'recent amount : {recent_amount}')
                    self.my_setDriver('GV2', recent_amount,  self.ISYmeter_uom, type=message_type)

                    recent_duration = water_ctrl.get_data('duration','recentUsage')
                    logging.debug(f'recent duration : {recent_duration}')
                    self.my_setDriver('GV3', recent_duration,  44, type=message_type)   

                    pwr_mode = water_ctrl.get_data('powerMode')
                    if pwr_mode is None:
                        pwr_mode = water_ctrl.get_data('powerSupply')
                    bat_lvl =  water_ctrl.get_data('battery')

                    logging.debug('udiYoWaterMeterController - getBattery: {},  {}  '.format(pwr_mode, bat_lvl))
                    if pwr_mode in ['PowerLine']:
                        self.my_setDriver('BATLVL', 98, 25)  # AC powered
                    else:
                        self.my_setDriver('BATLVL', bat_lvl, 25, type=message_type)
                        
                    water_temp =  water_ctrl.get_data('waterTemperature', 'state')
                    logging.debug(f'water temperature : {water_temp}')
                    #NEEDS TO BE FIXED 
                    self.my_setDriver('CLITEMP', water_temp,  4, type=message_type)  
                    
                    #meter_unit = self.yoWaterCtrl.get_data('attributes', 'meterUnit')
                    #logging.debug(f'meter unit : {meter_unit}')
                    #self.my_setDriver('GV4', meter_unit, 25)        
                    #alarms = self.yoWaterCtrl.getAlarms()
                    #if alarms:

                    #   , , highTemp, , lowTemp, , o
    
                    leak = water_ctrl.get_data('leak', 'alarm')
                    logging.debug(f'leak : {leak}')
                    self.my_setDriver('GV5', self.state2ISY(leak), type=message_type)
                    amount_overrun = water_ctrl.get_data('overrunAmount24H', 'alarm') #amountOverrun24H,amountOverrun 
                    if amount_overrun is None: # try alternate key
                        amount_overrun = water_ctrl.get_data('amountOverrun', 'alarm')
                    logging.debug(f'overrunAmount24H : {amount_overrun}')     
                    self.my_setDriver('GV6', self.state2ISY(amount_overrun), type=message_type)

                    duration_overrun = water_ctrl.get_data('overrunDurationOnce', 'alarm') #durationOverrun overrunDurationOnce
                    if duration_overrun is None: # try alternate key
                        duration_overrun = water_ctrl.get_data('durationOverrun', 'alarm')
                    logging.debug(f'duration overrun : {duration_overrun}')     
                    self.my_setDriver('GV7', self.state2ISY( duration_overrun), type=message_type)

                    times_overrun_24h = water_ctrl.get_data('overrunTimes24H', 'alarm') #overrunTimes24H
                    logging.debug(f'times overrun 24h : {times_overrun_24h}')   
                    self.my_setDriver('GV8', self.state2ISY(times_overrun_24h), type=message_type)
                    reminder = water_ctrl.get_data('reminder', 'alarm') #reminder
                    logging.debug(f'reminder : {reminder}')     
                    self.my_setDriver('GV9', self.state2ISY(reminder), type=message_type)
                    if self.ValveSupported:
                        supply_type = water_ctrl.get_data('supplyType')   #supplyType
                        logging.debug(f'supply type : {supply_type}')     
                        self.my_setDriver('GV10', self.w_unit2ISY(supply_type), type=message_type)
                        open_reminder = water_ctrl.get_data('openReminder', 'alarm') #openReminder
                        logging.debug(f'open reminder : {open_reminder}')
                        self.my_setDriver('GV11', self.state2ISY(open_reminder), type=message_type)

                        valve_error = water_ctrl.get_data('valveError', 'alarm')   #valveError
                        logging.debug(f'valve error : {valve_error}')   
                        self.my_setDriver('GV12', self.state2ISY(valve_error), type=message_type)   

                    high_T_error = water_ctrl.get_data('highTemp', 'alarm')   #valveError
                    logging.debug(f'high temp error : {high_T_error}')
                    self.my_setDriver('GV13', self.state2ISY(high_T_error), type=message_type)    
                    low_T_error = water_ctrl.get_data('lowTemp', 'alarm')   #valveError
                    logging.debug(f'low temp error : {low_T_error}')
                    self.my_setDriver('GV14', self.state2ISY(low_T_error), type=message_type)

                    overrun24 = water_ctrl.get_data('overrunAmount24H', 'attributes')
                    if overrun24 is not None:
                        overrun24= round(float(self.calculate_water_volume(overrun24,  self.meter_unit,  self.ISYwater_unit)), 1)
                    logging.debug(f'Overrun24  limit : {overrun24}')
                    self.my_setDriver('GV22', overrun24, self.ISYmeter_uom, type=message_type)
                    nbroverrun = water_ctrl.get_data('overrunTimes24H', 'attributes')
                    #if nbroverrun is not None:
                    #    overrun_amount = round(float(self.calculate_water_volume(overrun_amount,  self.meter_unit,  self.ISYwater_unit)), 1)                          
                    logging.debug(f'overrun times limit : {nbroverrun}')                    
                    self.my_setDriver('GV23', nbroverrun, 70, type=message_type)
                    overrun_duration = water_ctrl.get_data('overrunDuration', 'attributes')
                    if overrun_duration is None:
                        overrun_duration = water_ctrl.get_data('overrunDurationOnce', 'attributes')
                    logging.debug(f'overrun duration limit : {overrun_duration}')
                    self.my_setDriver('GV24', overrun_duration, 44, type=message_type)
                    if self.ValveSupported:
                        leak_ac = water_ctrl.get_data('leakDetection', 'autoCloseValve')
                        logging.debug(f'leak ACV : {leak_ac}')
                        self.my_setDriver('GV25', self.bool2ISY(leak_ac), type=message_type)
                        overrun_ac = water_ctrl.get_data('overrunAmount24H', 'autoCloseValve')
                        logging.debug(f'overrun amount24 ACV : {overrun_ac}')
                        self.my_setDriver('GV26', self.bool2ISY(overrun_ac), type=message_type)
                        overrun_time_ac = water_ctrl.get_data('overrunDurationOnce', 'autoCloseValve')
                        logging.debug(f'overrun duration ACV : {overrun_time_ac}')
                        self.my_setDriver('GV27', self.bool2ISY(overrun_time_ac), type=message_type)
                        overrun_time_ac = water_ctrl.get_data('overrunTimes24H', 'autoCloseValve')
                        logging.debug(f'overrun times ACV : {overrun_time_ac}')
                        self.my_setDriver('GV28', self.bool2ISY(overrun_time_ac), type=message_type)

                    if water_ctrl.suspended:
                        self.my_setDriver('GV20', 1)
                    else:
                        self.my_setDriver('GV20', 0)
                else:
                    self.my_setDriver('GV30', 0)
                    self.my_setDriver('GV20', 2)
                
        except KeyError as e:
            logging.error(f'EXCEPTION - {e}')
            
    def updateStatus(self, data):
        logging.info('updateStatus - udiYoWaterMeterController')
        if self.yoWaterCtrl is not None:        
            with self._update_lock:
                self.yoWaterCtrl.updateStatus(data)
            self.updateData()


    def set_open(self, command = None):
        logging.info('udiYoWaterMeterController - set_open')
        water_ctrl = self._get_water_ctrl('set_open')
        if water_ctrl is None:
            return
        water_ctrl.setValveState('open')

    def set_close(self, command = None):
        logging.info('udiYoWaterMeterController - set_close')
        water_ctrl = self._get_water_ctrl('set_close')
        if water_ctrl is None:
            return
        water_ctrl.setValveState('closed')


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
        water_ctrl = self._get_water_ctrl('set_attributes')
        if water_ctrl is None:
            return
        query = command.get("query")
        data={}
        data['attributes'] = {}
        leak_lim = None
        or_lim = None
        if 'LLIMIT.uom69' in query:
            leak_lim = float(query.get('LLIMIT.uom69'))
            or_lim = float(self.calculate_water_volume(or_lim, 0, self.water_unit))
        elif 'LLIMIT.uom6' in query:
            leak_lim = float(query.get('LLIMIT.uom6'))
            leak_lim = float(self.calculate_water_volume(leak_lim, 1, self.water_unit))
        elif 'LLIMIT.uom8' in query:
            leak_lim = float(query.get('LLIMIT.uom8'))
            leak_lim = float(self.calculate_water_volume(leak_lim, 2, self.water_unit))
        elif 'LLIMIT.uom35' in query:
            leak_lim = float(query.get('LLIMIT.uom35'))
            leak_lim = float(self.calculate_water_volume(leak_lim, 3, self.water_unit))
        if leak_lim:
            data['attributes'] ['leakLimit'] = leak_lim

        if 'LOFF.uom25' in query:
            data['attributes'] ['autoCloseValve'] = bool(query.get('LOFF.uom25'))

        if 'ORLIMIT.uom69' in query:
            or_lim = float(query.get('ORLIMIT.uom69'))
            or_lim = float(self.calculate_water_volume(or_lim, 0, self.water_unit))
        elif 'ORLIMIT.uom6' in query:
            or_lim = float(query.get('ORLIMIT.uom6'))
            or_lim = float(self.calculate_water_volume(or_lim, 1, self.water_unit))
        elif 'ORLIMIT.uom8' in query:
            or_lim = float(query.get('ORLIMIT.uom8'))
            or_lim = float(self.calculate_water_volume(or_lim, 2, self.water_unit))
        elif 'ORLIMIT.uom35' in query:
            or_lim = float(query.get('ORLIMIT.uom35'))   
            or_lim = float(self.calculate_water_volume(or_lim, 3, self.water_unit))
        if self.ValveSupported:    
            if or_lim:
                data['attributes'] ['overrunAmount'] = or_lim     
            if 'OROFF.uom25' in query:
                data['attributes'] ['overrunAmountACV'] = bool(query.get('OROFF.uom25')) 
            if 'ORTLIMIT.uom44' in query:
                data['attributes'] ['overrunDuration']  = int(query.get('ORTLIMIT.uom44'))
            if 'ORTOFF' in query:
                data['attributes'] ['overrunDurationACV']  = bool(query.get('ORTOFF.uom25'))

        water_ctrl.setAttributes(data)


    def update(self, command = None):
        logging.info('Update Status Executed')
        water_ctrl = self._get_water_ctrl('update')
        if water_ctrl is None:
            return
        water_ctrl.refreshDevice()
        time.sleep(2)
        # Keep both schedule nodes synchronized on explicit UPDATE.
        if self.scheduleSupport:
            water_ctrl.refreshSchedules()
        
    def program_delays(self, command):
        logging.info('udiYoOutlet program_delays {}'.format(command))
        water_ctrl = self._get_water_ctrl('program_delays')
        if water_ctrl is None:
            return
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        water_ctrl.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 

    commands = {
                'UPDATE': update,
                'VOPEN'   : set_open,
                'VCLOSE'   : set_close,
                'SETATTRIB' : set_attributes,
                #'VALVECTRL': waterCtrlControl, 
                #'DELAYCTRL' : program_delays,
                #'OFFDELAY' : prepOffDelay 
                }





