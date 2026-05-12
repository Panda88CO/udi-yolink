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


class udiYoWaterMeterMulti(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler, w_unit2ISY, save_cmd_state, water_meter_unit2uom, calculate_water_volume, retrieve_cmd_state, state2ISY, bool2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key, checkNameSync

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
            {'driver': 'GV1', 'value': 0, 'uom': 25}, # Meter count
            {'driver': 'GV5', 'value': 99, 'uom': 25}, #Leak
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
            #{'driver': 'GV4', 'value': 99, 'uom' : 25}, # Unit
            {'driver': 'GV20', 'value': 0, 'uom': 25},
            {'driver': 'TIME', 'value' :0, 'uom': 151},                
            ]



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name, )   
        logging.debug('udiYoWaterMeterMultiController INIT- {}'.format(deviceInfo['name']))
        
        self.poly = polyglot
        self.yoAccess = yoAccess
        self.temp_unit = self.yoAccess.get_temp_unit()     # Curent multi unit does not report temp
        if self.temp_unit == 1:
            self.id = 'yowatermeterMultiF'    
        model = str(deviceInfo['modelName'][:6])  
        if model in ['YS5029','YS5009']:
            self.scheduleSupport = False
        else:
            self.scheduleSupport = True     

        self.meter_count = 2 # must be 2 or more - mostly if device is offline at startup - will be updated when device is online and data is retrieved
        if model in ['YS5029']:
            self.meter_count = 2
    
        self.devInfo =  deviceInfo
        self.name = name
        self.address = address
        self.yoWaterCtrl= None
        self.schedule_valve = None
        self.schedule_leak = None
        self.node_ready = False
        self.main_node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.last_state = ''
        self.ISYmeter_uom= None
        known_meters = ['']
        self.onDelay = 0
        self.offDelay = 0
        self.n_queue = []
        self.valveState = 99 # needed as class c device - keep value until online again 
        #polyglot.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(self.poly.START, self.start, self.address)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        #self.poly.subscribe(self.poly.STARTDONE, self.start_done)
        # start processing events and create add our controller node
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.wm_nodes= {}
        self.main_node_ready = True
        self.sub_nodes_ready = False
        while not self.sub_nodes_ready:
            time.sleep(0.5)
        self.node_ready = True



    def start(self):
        logging.info('Start - udiYoWaterMeterMultiController')
        while not self.main_node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV20', 0)
        self.yoWaterCtrl= YoLinkWaterMeter(self.yoAccess, self.devInfo, self.updateStatus)
        self.water_meter_list = []
        if self.yoWaterCtrl is None:
            logging.error('YoLinkWaterMultiMeter not created')
            return
        else:
            time.sleep(2)
            self.yoWaterCtrl.initDevice()
            time.sleep(1)
            tries = 1
            while not self.yoWaterCtrl.check_system_online():
                
                logging.info(f'Waiting for device {self.name} to come online... Attempt {tries}')
                self.poly.Notices['offline'] = f'Waiting for device {self.name} to come online...'  
                time.sleep(min(60, tries*2))
                #if tries % 10 == 0:
                    #self.yoWaterCtrl.refreshDevice()    
                tries += 1
            self.meter_count = self.yoWaterCtrl.getMeterCount()
            logging.debug(f'Meter count: {self.meter_count}')
            self.meter_unit =  self.yoWaterCtrl.getMeterUnit()
            self.ISYwater_unit = self.yoAccess.get_water_unit()     
            self.ISYmeter_uom= self.water_meter_unit2uom( self.ISYwater_unit)
            logging.debug(f'meter unit : { self.meter_unit} ISY unit: { self.ISYwater_unit} uom: {self.ISYmeter_uom}')
            if self.meter_count is None:
                self.meter_count = 2 # default value if device is online but meter count not retrieved - should be updated when data is retrieved
                self.poly.Notices['offline'] = 'Number of meters not retrieved (device likely offline) -  defaulting to 2.  If wrong make sure device is online and restart'
            self.poly.Notices.delete('offline')
            self.my_setDriver('GV1', self.yoWaterCtrl.water_meter_count)
            logging.debug(f'Setting water meter count driver to: {self.yoWaterCtrl.water_meter_count}')
            if isinstance(self.meter_count, int) and self.meter_count > 1:
                self.wm_nodes= {}
                for wm_index in range(0, self.meter_count):
                    address = f'{self.address[-12:]}_{wm_index}'
                    wm_address = self.poly.getValidAddress(address)
                    wm_name = self.poly.getValidName(f'{self.name} CH{wm_index+1}')
                    self.wm_nodes[wm_index] = udiYoSubWaterMeter(self.poly, self.address, wm_address, wm_name, wm_index, self.yoAccess, self.yoWaterCtrl, self.devInfo)
                    self.adr_list.append(wm_address)
                    logging.debug(f'Added Water Meter Node: {wm_name} at {wm_address}')
            self.sub_nodes_ready = True
            logging.debug(f'Registered node addresses for {self.name}: {self.adr_list}')

            #if self.scheduleSupport:
            #    pass  # schedule nodes created via create_schedule_nodes() after all main nodes are added
            #    # deferred: refreshSchedules() will be invoked after startup to avoid API bursts
        time.sleep(4)

        tries = 1
        while not self.yoWaterCtrl.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(300, tries * 5))
            tries += 1
        time.sleep(2)
            
        self.start_done()
        #self.updateData()  # not needed - updateStatus callback fires from initDevice response

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
        logging.info('Stop udiYoWaterMeterMultiController')
        #self.my_setDriver('GV30', 0)
        ctrl = self._get_water_ctrl('stop')
        if ctrl is not None and hasattr(ctrl, 'shut_down'):
            ctrl.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_water_ctrl(self, caller):
        ctrl = getattr(self, 'yoWaterCtrl', None)
        if ctrl is None:
            logging.warning('udiYoWaterMeterMulti.%s called before device initialization', caller)
        return ctrl

    def checkDataUpdate(self):
        ctrl = self._get_water_ctrl('checkDataUpdate')
        if ctrl is None:
            return
        if ctrl.data_updated():
            #self.yoWaterCtrl.refreshDevice() 
            self.updateData()

    def checkOnline(self):
        #get get info even if battery operated 
        ctrl = self._get_water_ctrl('checkOnline')
        if ctrl is None:
            return
        ctrl.refreshDevice()    


    def updateData(self):
        ctrl = self._get_water_ctrl('updateData')
        if ctrl is None:
            return
        try:
            if self.node is not None:
                while not self.system_ready or not self.configDone:
                    time.sleep(0.5)
                message_info = ctrl.get_message_type()
                message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
                message_action = message_info[1] if isinstance(message_info, (list, tuple)) and len(message_info) >= 2 else None
                unix_time = ctrl.get_report_time('time')
                self.my_setDriver('TIME', unix_time, 151)
                if self.meter_unit is None:
                    self.meter_unit = ctrl.getMeterUnit()
                    self.ISYwater_unit = self.yoAccess.get_water_unit()
                    self.ISYmeter_uom = self.water_meter_unit2uom(self.ISYwater_unit)
                if message_type and 'Schedules' in str(message_type):
                    # Route valve schedules to valve node
                    if 'Valve' in str(message_type) and self.schedule_valve is not None:
                        self.schedule_valve.update_schedule_data(source_device=ctrl)
                    # Route leak schedules to leak node
                    elif 'Leak' in str(message_type) and self.schedule_leak is not None:
                        self.schedule_leak.update_schedule_data(source_device=ctrl)
                    return
                logging.debug(f'updateData called with message_type: {message_type}, message_action: {message_action}')
                if ctrl.check_system_online():

                    if ctrl.emptyData():
                        logging.debug('Empty data received - skip updateData')
                        self.my_setDriver('GV20', 6)
                        return
                    if self.ISYmeter_uom is None:
                        self.meter_unit = ctrl.getMeterUnit()
                        logging.debug(f'meter unit : { self.meter_unit}')
                        #self.my_setDriver('GV4',  self.meter_unit, 25)          
                        self.ISYmeter_uom= self.water_meter_unit2uom( self.meter_unit)            
                    water_state = ctrl.get_data('waterFlowing', 'state')
                    logging.debug(f'water flowing : {water_state}')
                    if isinstance(water_state, dict):
                        active_water_flow = water_state.get('0') or water_state.get('1')
                        if active_water_flow is not None:
                            self.my_setDriver('ST', self.state2ISY(active_water_flow), type=message_type)
                        else:
                            logging.debug('Missing waterFlowing channel state for %s', self.nodeName)
                    pwr_mode, bat_lvl =  ctrl.getBattery()  
                    logging.debug('udiYoWaterMeterMultiController - getBattery: {},  {}  '.format(pwr_mode, bat_lvl))
                    if pwr_mode == 'PowerLine':
                        self.my_setDriver('BATLVL', 98, 25)
                    else:
                        self.my_setDriver('BATLVL', bat_lvl, 25, type=message_type)
                    leak = ctrl.get_data('leak', 'alarm')
                    logging.debug(f'leak : {leak}')
                    self.my_setDriver('GV5', self.state2ISY(leak))                 
               
                    if ctrl.suspended:
                        self.my_setDriver('GV20', 1)
                    else:
                        self.my_setDriver('GV20', 0)

                    for wm_index in range(0, ctrl.water_meter_count):
                        if wm_index in self.wm_nodes:
                            self.wm_nodes[wm_index].updateData()
                else:
                    self.my_setDriver('GV20', 2)
                
        except KeyError as e:
            logging.error(f'EXCEPTION - {e}')

    def update(self, command = None):
        logging.info('Update Status Executed')
        ctrl = self._get_water_ctrl('update')
        if ctrl is None:
            return
        ctrl.refreshDevice()
        time.sleep(2)
        # Keep schedule node synchronized on explicit UPDATE.
        if self.scheduleSupport:
            ctrl.refreshSchedules()
                    
    def updateStatus(self, data):
        logging.info('updateStatus - udiYoWaterMeterController')
        ctrl = self._get_water_ctrl('updateStatus')
        if ctrl is not None:        
            with self._update_lock:
                ctrl.updateStatus(data)  # always update device data immediately so check_system_online() can unblock start()
            self.updateData()

    commands = {
                'UPDATE': update,
                }


class udiYoSubWaterMeter(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,   w_unit2ISY, calculate_water_volume, get_meter_correction_factor, apply_meter_correction, save_cmd_state, water_meter_unit2uom, retrieve_cmd_state, bool2ISY, state2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key, checkNameSync

    id = 'yowatermeterSubL'
    '''
       drivers = [
            'GV0' = Manipulator State

            ]
    ''' 
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25}, # Water flowing
            {'driver': 'GV0', 'value': 99, 'uom': 25},#Valve state
            {'driver': 'GV1', 'value': 99, 'uom': 25}, #water use total
            {'driver': 'GV10', 'value':99, 'uom': 25}, #water use daily             
            {'driver': 'GV2', 'value': 99, 'uom': 25},  #wateruse recent
            {'driver': 'GV3', 'value': 99, 'uom': 25},  #Wateruse duration

            {'driver': 'GV6', 'value': 99, 'uom': 25}, #alarm
            {'driver': 'GV7', 'value': 99, 'uom': 25}, 
            {'driver': 'GV8', 'value': 99, 'uom': 25},                                              
            {'driver': 'GV9', 'value': 99, 'uom': 25}, 
            #{'driver': 'GV11', 'value': 99, 'uom' : 25}, # alarm
            {'driver': 'GV12', 'value': 99, 'uom' : 25}, #  alarm
            #{'driver': 'GV13', 'value': 99, 'uom' : 25}, # alarm
            #{'driver': 'GV14', 'value': 99, 'uom' : 25}, # Water flowing
            {'driver': 'GV22', 'value': 99, 'uom': 25}, #LeakLimit
            {'driver': 'GV23', 'value': 99, 'uom': 25}, #Overrtun limit
            {'driver': 'GV24', 'value': 99, 'uom': 25}, #Overrun Time
    
            {'driver': 'GV25', 'value': 99, 'uom': 25}, #Leak AC
            {'driver': 'GV26', 'value': 99, 'uom': 25}, #LEakAC
            {'driver': 'GV27', 'value': 99, 'uom': 25}, #Overrun AC
            {'driver': 'GV28', 'value': 99, 'uom': 25}, #OverrunTIme AC
            {'driver': 'GV20', 'value': 99, 'uom': 25}, #Connection state

             
            ]



    def  __init__(self, polyglot, primary, address, name, WMindex, yoAccess, wmAccess, devInfo=None):
        super().__init__( polyglot, primary, address, name)   
        logging.debug(f'udiYoWaterMeterSub- {name}')
        self.n_queue = []
        self.yoAccess = yoAccess
        self.devInfo = devInfo if devInfo is not None else {}
        self.temp_unit = self.yoAccess.get_temp_unit() 
        self.water_unit = self.yoAccess.get_water_unit()    
        if self.water_unit == 0:
            self.id = 'yowatermeterSubG'    
        elif self.water_unit == 3:
            self.id = 'yowatermeterSubL'   
        else:
            logging.error('Only Liter and Gallon supported for now')
        self.WM_index = WMindex
        
        self.yoWaterCtrl= wmAccess
        self.sub_node_ready = False
        self.configDone = False
        self.system_ready=False
        self.last_state = ''
        self._last_reported_state = None
        self.ISYmeter_uom= None
        self.meter_correction_factor = 1.0
        self.valveState = 99 # needed as class c device - keep value until online again 
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)


        #known_meters = ['YS5007','YS5018', 'YS5008', 'YS5009', 'YS5029']
        #if self.yoWaterCtrl.devInfo['model'] in known_meters:
        #    logging.debug(f'Known water meter model {self.yoWaterCtrl.devInfo["model"]}')   
        #    if self.yoWaterCtrl.devInfo['model'] in ['YS5029']: # dual channel model  -  no temps and not 

        # start processing events and create add our controller node
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.sub_node_ready = True



    def start(self):
        logging.info('Start - udiYoWaterMeterMultiController')
        while not self.sub_node_ready or not self.configDone:
            time.sleep(0.5)

        # No online check here - the main node already waited for the device
        # before creating subnodes; they share the same yoWaterCtrl reference.
        self.meter_unit =  self.yoWaterCtrl.getMeterUnit()
        self.ISYwater_unit = self.yoAccess.get_water_unit()     
        self.ISYmeter_uom= self.water_meter_unit2uom( self.ISYwater_unit)
        self.meter_correction_factor = self.get_meter_correction_factor(self.yoWaterCtrl, self.WM_index)
        logging.debug(f'meter unit : { self.meter_unit} ISY unit: { self.ISYwater_unit} uom: {self.ISYmeter_uom}')
        #self.yoWaterCtrl.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.my_setDriver('GV1', 0,  self.ISYmeter_uom)
        self.start_done()
        #self.updateData()  # not needed - updateStatus callback fires from initDevice response

    def stop (self):
        logging.info('Stop udiYoWaterMeterMultiController')

        ctrl = self._get_water_ctrl('stop')
        if ctrl is not None and hasattr(ctrl, 'shut_down'):
            ctrl.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_water_ctrl(self, caller):
        ctrl = getattr(self, 'yoWaterCtrl', None)
        if ctrl is None:
            logging.warning('udiYoSubWaterMeter.%s called before water-meter initialization', caller)
        return ctrl

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
        pass

    def checkDataUpdate(self):
        ctrl = self._get_water_ctrl('checkDataUpdate')
        if ctrl is None:
            return
        if ctrl.data_updated():
            self.updateData()


    def updateData(self):
        ctrl = self._get_water_ctrl('updateData')
        if ctrl is None:
            return
        try:
            if self.node is not None:
                while not self.sub_node_ready or not self.system_ready or not self.configDone:
                    time.sleep(0.5)
                message_info = ctrl.get_message_type()
                message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
                if ctrl.check_system_online():
                    #self.my_setDriver('GV30', 1)
                    if ctrl.emptyData():
                        logging.debug('Empty data received - skip updateData')
                        self.my_setDriver('GV20', 6)
                        return
                    if self.meter_unit is None:
                        self.meter_unit = ctrl.getMeterUnit()
                        self.ISYwater_unit = self.yoAccess.get_water_unit()
                        self.ISYmeter_uom = self.water_meter_unit2uom(self.ISYwater_unit)
                        self.meter_correction_factor = self.get_meter_correction_factor(ctrl, self.WM_index)

                    state = ctrl.get_data('valves', 'state', self.WM_index)
                    logging.debug(f'valve state : {state} {self.WM_index}')
                    if isinstance(state, dict):
                        state = state.get(str(self.WM_index))
                    logging.debug(f'valve state : {state}')

                    if isinstance(state, str):
                        if state.lower() == 'open':
                            self.valveState = 1
                            self.my_setDriver('GV0', self.valveState, type=message_type)
                        elif state.lower() in ['closed', 'close']:
                            self.valveState = 0
                            self.my_setDriver('GV0', self.valveState, type=message_type)
                        self._report_binary_state_change(state)
                        self.last_state = state

                    water_flowing = ctrl.get_data('waterFlowing', 'state', self.WM_index)
                    logging.debug(f'water flowing : {water_flowing}')       
                    self.my_setDriver('ST', self.state2ISY(water_flowing ), type=message_type)
                    total_meter = self.apply_meter_correction(ctrl.get_data('meters', 'state', self.WM_index), self.meter_correction_factor)
                    if total_meter is not None:
                        total_meter = round((float(self.calculate_water_volume(total_meter,  self.meter_unit,  self.ISYwater_unit))), 1)  
                    self.my_setDriver('GV10', total_meter,  self.ISYmeter_uom, type=message_type)
                    daily_use = self.apply_meter_correction(ctrl.get_data('amount', 'dailyUsage', self.WM_index), self.meter_correction_factor)
                    if daily_use is not None:
                        daily_use = round(float(self.calculate_water_volume(daily_use,  self.meter_unit,  self.ISYwater_unit)),1)
                    logging.debug(f'daily use : {daily_use}')   
                    self.my_setDriver('GV1', daily_use,  self.ISYmeter_uom, type=message_type)
                    recent_amount = self.apply_meter_correction(ctrl.get_data('amount', 'recentUsage', self.WM_index), self.meter_correction_factor)
                    if recent_amount is not None:
                        recent_amount = round(float(self.calculate_water_volume(recent_amount,  self.meter_unit,  self.ISYwater_unit)), 1)
                    logging.debug(f'recent amount : {recent_amount}')
                    self.my_setDriver('GV2', recent_amount,  self.ISYmeter_uom, type=message_type)
                    recent_duration = ctrl.get_data('duration', 'recentUsage', self.WM_index)
                    logging.debug(f'recent duration : {recent_duration}')
                    self.my_setDriver('GV3', recent_duration,  44, type=message_type)  
                    #meter_unit = self.yoWaterCtrl.get_data('attributes', 'meterUnit')
                    #logging.debug(f'meter unit : {meter_unit}')  
                    #self.my_setDriver('GV4', meter_unit, 25)        
                    #pwr_mode, bat_lvl =  self.yoWaterCtrl.getBattery()  
                    #logging.debug('udiYoWaterMeterMultiController - getBattery: {},  {}  '.format(pwr_mode, bat_lvl))
                    #if pwr_mode == 'PowerLine':
                    #    self.my_setDriver('BATLVL', 98, 25)
                    #else:
                    #    self.my_setDriver('BATLVL', bat_lvl, 25)

                    #leak = self.yoWaterCtrl.get_data('alarm', 'leak')
                    #logging.debug(f'leak : {leak}')
                    #self.my_setDriver('GV5', self.state2ISY(leak))

                    amount_overrun = ctrl.get_data('amountOverrun24H', 'alarm', self.WM_index ) #amountOverrun24H,amountOverrun 
                    if amount_overrun is None: # try alternate key
                        amount_overrun = ctrl.get_data('amountOverrun', 'alarm')
                    logging.debug(f'overrunAmount24H : {amount_overrun}')     
                    self.my_setDriver('GV6', self.state2ISY(amount_overrun), type=message_type)


                    duration_overrun = ctrl.get_data('durationOverrun', 'alarm', self.WM_index) #durationOverrun overrunDurationOnce
                    if duration_overrun is None: # try alternate key
                        duration_overrun = ctrl.get_data('overrunDurationOnce', 'alarm', self.WM_index)
                    logging.debug(f'duration overrun : {duration_overrun}')     
                    self.my_setDriver('GV7', self.state2ISY( duration_overrun), type=message_type)

                    times_overrun_24h = ctrl.get_data('timesOverrun24H', 'alarm', self.WM_index) #overrunTimes24H
                    logging.debug(f'times overrun 24h : {times_overrun_24h}')   
                    self.my_setDriver('GV8', self.state2ISY(times_overrun_24h), type=message_type)
                    #reminder = self.yoWaterCtrl.get_data('alarm', 'reminder', self.WM_index) #reminder
                    #logging.debug(f'reminder : {reminder}')     
                    #self.my_setDriver('GV9', self.state2ISY(reminder))

                    open_reminder = ctrl.get_data('reminder', 'alarm', self.WM_index) #openReminder
                    logging.debug(f'reminder : {open_reminder}')
                    self.my_setDriver('GV9', self.state2ISY(open_reminder), type=message_type)

                    valve_error = ctrl.get_data('valveError', 'alarm', self.WM_index)   #valveError
                    logging.debug(f'valve error : {valve_error}')   
                    self.my_setDriver('GV12', self.state2ISY(valve_error), type=message_type)   
                    #logging.debug(f'leak limit : {leak_limit}')
                    #self.my_setDriver('GV21', leak_limit, self.ISYmeter_uom)
                    #overrun_amount = self.yoWaterCtrl.get_data('attributes', 'overrunAmount', self.WM_index)
                    #if overrun_amount is not None:
                    #    overrun_amount = round(float(self.calculate_water_volume(overrun_amount,  self.meter_unit,  self.ISYwater_unit)), 1)                          

                    overrun24 = ctrl.get_data('overrunAmount24H', 'attributes', self.WM_index)

                    if overrun24 is not None:
                        overrun24= round(float(self.calculate_water_volume(overrun24,  self.meter_unit,  self.ISYwater_unit)), 1)
                    logging.debug(f'Overrun24  limit : {overrun24}')
                    self.my_setDriver('GV22', overrun24, self.ISYmeter_uom, type=message_type) 
                    nbroverrun = ctrl.get_data('overrunTimes24H', 'attributes', self.WM_index)
                    #if nbroverrun is not None:
                    #    overrun_amount = round(float(self.calculate_water_volume(overrun_amount,  self.meter_unit,  self.ISYwater_unit)), 1)                          
                    logging.debug(f'overrun times limit : {nbroverrun}')
                    self.my_setDriver('GV23', nbroverrun, 70, type=message_type)
                    overrun_duration = ctrl.get_data('overrunDuration', 'attributes', self.WM_index)
                    logging.debug(f'overrun duration limit : {overrun_duration}')
                    self.my_setDriver('GV24', overrun_duration, 44, type=message_type)

                    leak_ac = ctrl.get_data('leakDetection', 'autoCloseValve', self.WM_index)
                    logging.debug(f'leak ACV : {leak_ac}')
                    self.my_setDriver('GV25', self.bool2ISY(leak_ac))
                    overrun_ac = ctrl.get_data('overrunAmount24H', 'autoCloseValve', self.WM_index)
                    logging.debug(f'overrun amount24 ACV : {overrun_ac}')
                    self.my_setDriver('GV26', self.bool2ISY(overrun_ac), type=message_type)
                    overrun_time_ac = ctrl.get_data('overrunDuration', 'autoCloseValve', self.WM_index)
                    if overrun_time_ac is None:
                        overrun_time_ac = ctrl.get_data('overrunDurationOnce', 'autoCloseValve', self.WM_index)
                    logging.debug(f'overrun duration ACV : {overrun_time_ac}')
                    self.my_setDriver('GV27', self.bool2ISY(overrun_time_ac), type=message_type)
                    overrun_time_ac = ctrl.get_data('overrunTimes24H', 'autoCloseValve', self.WM_index)
                    logging.debug(f'overrun times ACV : {overrun_time_ac}')
                    self.my_setDriver('GV28', self.bool2ISY(overrun_time_ac), type=message_type)
                    

        except KeyError as e:
            logging.error(f'EXCEPTION - {e}')


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

        elif state == 0:
            self.yoWaterCtrl.setState('closed')

        elif state == 5:
            logging.info('udiYoWaterMeterMultiController set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60)
            self.yoWaterCtrl.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 
    '''

    def set_open(self, command = None):
        logging.info('udiYoWaterMeterMultiController - set_open')
        ctrl = self._get_water_ctrl('set_open')
        if ctrl is None:
            return
        ctrl.setValveState('open', self.WM_index)

    def set_close(self, command = None):
        logging.info('udiYoWaterMeterMultiController - set_close')
        ctrl = self._get_water_ctrl('set_close')
        if ctrl is None:
            return
        ctrl.setValveState('closed', self.WM_index)


    
    def set_attributes(self, command):
        logging.info(f'set_attributes {command}')
        query = command.get("query")
        data={}
        data['attributes'] = {}
        leak_lim = None
        or_lim = None
        if 'LLIMIT.uom69' in query:
            leak_lim = float(query.get('LLIMIT.uom69')) # gal = 0
            leak_lim = float(self.calculate_water_volume(leak_lim, 0, self.water_unit))
        elif 'LLIMIT.uom6' in query:
            leak_lim = float(query.get('LLIMIT.uom6')) # ccf = 1
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
        if or_lim:
            data['attributes'] ['overrunAmount'] = or_lim     
        if 'OROFF.uom25' in query:
            data['attributes'] ['overrunAmountACV'] = bool(query.get('OROFF.uom25')) 
        if 'ORTLIMIT.uom44' in query:
            data['attributes'] ['overrunDuration']  = int(query.get('ORTLIMIT.uom44'))
        if 'ORTOFF' in query:
            data['attributes'] ['overrunDurationACV']  = bool(query.get('ORTOFF.uom25'))

        ctrl = self._get_water_ctrl('set_attributes')
        if ctrl is None:
            return
        ctrl.setAttributes(data)


    def update(self, command = None):
        logging.info('Update Status Executed')
        ctrl = self._get_water_ctrl('update')
        if ctrl is None:
            return
        ctrl.refreshDevice()
        
    def program_delays(self, command):
        logging.info('udiYoOutlet program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        ctrl = self._get_water_ctrl('program_delays')
        if ctrl is None:
            return
        ctrl.setDelayList([{'ch':str(self.WM_index), 'on':self.onDelay, 'off':self.offDelay}]) 

    '''
    def updateStatus(self, data):
        logging.info('updateStatus - udiYoWaterMeterMultiController')
        self.yoWaterCtrl.updateStatus(data)  # always update device data immediately so check_system_online() can unblock start()
        self.updateData()
    '''

    commands = {
                'VOPEN'   : set_open,
                'VCLOSE'   : set_close,
                'SETATTRIB' : set_attributes,
                }






