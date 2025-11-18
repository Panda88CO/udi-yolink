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
    from  udiYolinkLib import my_setDriver, w_unit2ISY, save_cmd_state,water_meter_unit2uom,calculate_water_volume, retrieve_cmd_state, state2ISY, bool2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

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
            #{'driver': 'GV4', 'value': 99, 'uom' : 25}, # Unit
            {'driver': 'GV20', 'value': 0, 'uom': 25},
            {'driver': 'TIME', 'value' :0, 'uom': 151},                
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
        self.ISYmeter_uom= None
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
            self.meter_count = self.yoWaterCtrl.getMeterCount()
            if self.meter_count is None:
                logging.error('Water meter count not found')
                self.poly.Notices['nometer'] = 'No multi meter found - may be off line'
                return
            
            self.meter_unit =  self.yoWaterCtrl.getMeterUnit()
            self.ISYwater_unit = self.yoAccess.get_water_unit()     
            self.ISYmeter_uom= self.water_meter_unit2uom( self.ISYwater_unit)
            logging.debug(f'meter unit : { self.meter_unit} ISY unit: { self.ISYwater_unit} uom: {self.ISYmeter_uom}')

            self.my_setDriver('GV1', self.yoWaterCtrl.water_meter_count)
            if self.meter_count > 1:
                self.wm_nodes= {}
                for wm_index in range(0, self.meter_count):
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

                    if self.yoWaterCtrl.emptyData():
                        logging.debug('Empty data received - skip updateData')
                        self.my_setDriver('GV20', 6)
                        return
                    if self.ISYmeter_uom is None:
                        logging.debug(f'meter unit : { self.meter_unit}')
                        #self.my_setDriver('GV4',  self.meter_unit, 25)          
                        self.ISYmeter_uom= self.water_meter_unit2uom( self.meter_unit)            
                    water_state = self.yoWaterCtrl.getData('state', 'waterFlowing')
                    logging.debug(f'water flowing : {water_state}')
                    if water_state is not None and len(water_state) == 2:   
                        self.my_setDriver('ST', self.state2ISY(water_state['0'] or water_state['1']))
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
    from  udiYolinkLib import my_setDriver, w_unit2ISY, calculate_water_volume, save_cmd_state,water_meter_unit2uom, retrieve_cmd_state, bool2ISY, state2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

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
    
            {'driver': 'GV26', 'value': 99, 'uom': 25}, #LEakAC
            {'driver': 'GV27', 'value': 99, 'uom': 25}, #Overrun AC
            {'driver': 'GV28', 'value': 99, 'uom': 25}, #OverrunTIme AC                                             

             
            ]



    def  __init__(self, polyglot, primary, address, name, WMindex, yoAccess, wmAccess):
        super().__init__( polyglot, primary, address, name)   
        logging.debug(f'udiYoWaterMeterSub- {name}')
        self.n_queue = []
        self.yoAccess = yoAccess
        self.temp_unit = self.yoAccess.get_temp_unit() 
        self.water_unit = self.yoAccess.get_water_unit()    
        if self.water_unit == 0:
            self.id = 'yowatermeterSubG'    
        elif self.water_unit == 3:
            self.id = 'yowatermeterSubL'   
        else:
            logging.error('Only Litere and Gallon supported for now')
        self.WM_index = WMindex
        
        self.yoWaterCtrl= wmAccess
        self.node_ready = False
        self.last_state = ''
        self.ISYmeter_uom= None
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
        
        self.meter_unit =  self.yoWaterCtrl.getMeterUnit()
        self.ISYwater_unit = self.yoAccess.get_water_unit()     
        self.ISYmeter_uom= self.water_meter_unit2uom( self.ISYwater_unit)
        logging.debug(f'meter unit : { self.meter_unit} ISY unit: { self.ISYwater_unit} uom: {self.ISYmeter_uom}')
        #self.yoWaterCtrl.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
        self.my_setDriver('GV1', 0,  self.ISYmeter_uom)
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


    def updateData(self):
        try:
            if self.node is not None:
                if self.yoWaterCtrl.online:
                    #self.my_setDriver('GV30', 1)
                    if self.yoWaterCtrl.emptyData():
                        logging.debug('Empty data received - skip updateData')
                        self.my_setDriver('GV20', 6)
                        return
                    if self.ISYmeter_uom is None:
                        logging.debug(f'meter unit : { self.meter_unit}')
                        #self.my_setDriver('GV4',  self.meter_unit, 25)          
                        self.ISYmeter_uom= self.water_meter_unit2uom( self.meter_unit)
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
                    total_meter = self.yoWaterCtrl.getData('state','meters', self.WM_index)
                    if total_meter is not None:
                        total_meter = round((float(self.calculate_water_volume(total_meter,  self.meter_unit,  self.ISYwater_unit))), 1)  
                    self.my_setDriver('GV10', total_meter,  self.ISYmeter_uom)

                    daily_use = self.yoWaterCtrl.getData('dailyUsage', 'amount', self.WM_index)
                    if daily_use is not None:
                        daily_use = round(float(self.calculate_water_volume(daily_use,  self.meter_unit,  self.ISYwater_unit)),1)
                    logging.debug(f'daily use : {daily_use}')   
                    self.my_setDriver('GV1', daily_use,  self.ISYmeter_uom)
                    recent_amount = self.yoWaterCtrl.getData('recentUsage','amount', self.WM_index) 
                    if recent_amount is not None:
                        recent_amount = round(float(self.calculate_water_volume(recent_amount,  self.meter_unit,  self.ISYwater_unit)), 1)
                    logging.debug(f'recent amount : {recent_amount}')
                    self.my_setDriver('GV2', recent_amount,  self.ISYmeter_uom)
                    recent_duration = self.yoWaterCtrl.getData('recentUsage','duration', self.WM_index)
                    logging.debug(f'recent duration : {recent_duration}')
                    self.my_setDriver('GV3', recent_duration,  44)  
                    #meter_unit = self.yoWaterCtrl.getData('attributes', 'meterUnit')
                    #logging.debug(f'meter unit : {meter_unit}')  
                    #self.my_setDriver('GV4', meter_unit, 25)        
                    #pwr_mode, bat_lvl =  self.yoWaterCtrl.getBattery()  
                    #logging.debug('udiYoWaterMeterMultiController - getBattery: {},  {}  '.format(pwr_mode, bat_lvl))
                    #if pwr_mode == 'PowerLine':
                    #    self.my_setDriver('BATLVL', 98, 25)
                    #else:
                    #    self.my_setDriver('BATLVL', bat_lvl, 25)

                    #leak = self.yoWaterCtrl.getData('alarm', 'leak')
                    #logging.debug(f'leak : {leak}')
                    #self.my_setDriver('GV5', self.state2ISY(leak))

                    amount_overrun = self.yoWaterCtrl.getData('alarm', 'amountOverrun24H', self.WM_index ) #amountOverrun24H,amountOverrun 
                    if amount_overrun is None: # try alternate key
                        amount_overrun = self.yoWaterCtrl.getData('alarm', 'amountOverrun')
                    logging.debug(f'overrunAmount24H : {amount_overrun}')     
                    self.my_setDriver('GV6', self.state2ISY(amount_overrun))


                    duration_overrun = self.yoWaterCtrl.getData('alarm', 'durationOverrun', self.WM_index) #durationOverrun overrunDurationOnce
                    if duration_overrun is None: # try alternate key
                        duration_overrun = self.yoWaterCtrl.getData('alarm', 'overrunDurationOnce', self.WM_index)
                    logging.debug(f'duration overrun : {duration_overrun}')     
                    self.my_setDriver('GV7', self.state2ISY( duration_overrun))

                    times_overrun_24h = self.yoWaterCtrl.getData('alarm', 'timesOverrun24H', self.WM_index) #overrunTimes24H
                    logging.debug(f'times overrun 24h : {times_overrun_24h}')   
                    self.my_setDriver('GV8', self.state2ISY(times_overrun_24h))

                    #reminder = self.yoWaterCtrl.getData('alarm', 'reminder', self.WM_index) #reminder
                    #logging.debug(f'reminder : {reminder}')     
                    #self.my_setDriver('GV9', self.state2ISY(reminder))

                    open_reminder = self.yoWaterCtrl.getData('alarm', 'reminder', self.WM_index) #openReminder
                    logging.debug(f'reminder : {open_reminder}')
                    self.my_setDriver('GV9', self.state2ISY(open_reminder))

                    valve_error = self.yoWaterCtrl.getData('alarm', 'valveError', self.WM_index)   #valveError
                    logging.debug(f'valve error : {valve_error}')   
                    self.my_setDriver('GV12', self.state2ISY(valve_error))   
                    #logging.debug(f'leak limit : {leak_limit}')
                    #self.my_setDriver('GV21', leak_limit, self.ISYmeter_uom)
                    #overrun_amount = self.yoWaterCtrl.getData('attributes', 'overrunAmount', self.WM_index)
                    #if overrun_amount is not None:
                    #    overrun_amount = round(float(self.calculate_water_volume(overrun_amount,  self.meter_unit,  self.ISYwater_unit)), 1)                          

                    overrun24 = self.yoWaterCtrl.getData('attributes', 'overrunAmount24H', self.WM_index)

                    if overrun24 is not None:
                        overrun24= round(float(self.calculate_water_volume(overrun24,  self.meter_unit,  self.ISYwater_unit)), 1)
                    logging.debug(f'Overrun24  limit : {overrun24}')
                    self.my_setDriver('GV22', overrun24, self.ISYmeter_uom)
                    nbroverrun = self.yoWaterCtrl.getData('attributes', 'overrunTimes24H', self.WM_index)
                    #if nbroverrun is not None:
                    #    overrun_amount = round(float(self.calculate_water_volume(overrun_amount,  self.meter_unit,  self.ISYwater_unit)), 1)                          
                    logging.debug(f'overrun times limit : {nbroverrun}')
                    self.my_setDriver('GV23', nbroverrun, 70)
                    overrun_duration = self.yoWaterCtrl.getData('attributes', 'overrunDuration', self.WM_index)
                    logging.debug(f'overrun duration limit : {overrun_duration}')
                    self.my_setDriver('GV24', overrun_duration, 44)

                    leak_ac = self.yoWaterCtrl.getData('autoCloseValve', 'leakDetection', self.WM_index)
                    logging.debug(f'leak ACV : {leak_ac}')
                    self.my_setDriver('GV25', self.bool2ISY(leak_ac))
                    overrun_ac = self.yoWaterCtrl.getData('autoCloseValve', 'overrunAmount24H', self.WM_index)
                    logging.debug(f'overrun amount24 ACV : {overrun_ac}')
                    self.my_setDriver('GV26', self.bool2ISY(overrun_ac))
                    overrun_time_ac = self.yoWaterCtrl.getData('autoCloseValve', 'overrunDuration', self.WM_index)
                    if overrun_time_ac is None:
                        overrun_time_ac = self.yoWaterCtrl.getData('autoCloseValve', 'overrunDurationOnce', self.WM_index)
                    logging.debug(f'overrun duration ACV : {overrun_time_ac}')
                    self.my_setDriver('GV27', self.bool2ISY(overrun_time_ac))
                    overrun_time_ac = self.yoWaterCtrl.getData('autoCloseValve', 'overrunTimes24H', self.WM_index)
                    logging.debug(f'overrun times ACV : {overrun_time_ac}')
                    self.my_setDriver('GV28', self.bool2ISY(overrun_time_ac))
                    

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


    
    def set_attributes(self, command):
        logging.info(f'set_attributes {command}')
        query = command.get("query")
        data={}
        data['attributes'] = {}
        leak_lim = None
        or_lim = None
        if 'L_LIMIT.uom69' in query:
            leak_lim = float(query.get('L_LIMIT.uom69')) # gal = 0
            leak_lim = float(self.calculate_water_volume(leak_lim, 0, self.yoWaterCtrl.water_unit))
        elif 'L_LIMIT.uom6' in query:
            leak_lim = float(query.get('L_LIMIT.uom6')) # ccf = 1
            leak_lim = float(self.calculate_water_volume(leak_lim, 1, self.yoWaterCtrl.water_unit))  
        elif 'L_LIMIT.uom8' in query:
            leak_lim = float(query.get('L_LIMIT.uom8'))
            leak_lim = float(self.calculate_water_volume(leak_lim, 2, self.yoWaterCtrl.water_unit))  
        elif 'L_LIMIT.uom35' in query:
            leak_lim = float(query.get('L_LIMIT.uom35'))
            leak_lim = float(self.calculate_water_volume(leak_lim, 3, self.yoWaterCtrl.water_unit))
        if leak_lim:
            data['attributes'] ['leakLimit'] = leak_lim

        if 'L_OFF.uom25' in query:
            data['attributes'] ['autoCloseValve'] = bool(query.get('L_OFF.uom25'))

        if 'OR_LIMIT.uom69' in query:
            or_lim = float(query.get('OR_LIMIT.uom69'))
            or_lim = float(self.calculate_water_volume(or_lim, 0, self.yoWaterCtrl.water_unit))
        elif 'OR_LIMIT.uom6' in query:
            or_lim = float(query.get('OR_LIMIT.uom6'))
            or_lim = float(self.calculate_water_volume(or_lim, 1, self.yoWaterCtrl.water_unit)) 
        elif 'OR_LIMIT.uom8' in query:
            or_lim = float(query.get('OR_LIMIT.uom8'))
            or_lim = float(self.calculate_water_volume(or_lim, 2, self.yoWaterCtrl.water_unit))
        elif 'OR_LIMIT.uom35' in query:
            or_lim = float(query.get('OR_LIMIT.uom35')) 
            or_lim = float(self.calculate_water_volume(or_lim, 3, self.yoWaterCtrl.water_unit))
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




