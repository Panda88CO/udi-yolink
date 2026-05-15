#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
import importlib
from os import truncate
import threading
try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom
#import sys
import time

from yolinkSprinklerV2 import YoLinkSprinkler



class udiYoSprinkler(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  save_cmd_state, retrieve_cmd_state, node_queue, wait_for_node_done, checkNameSync

    id = 'yosprinkler'
    
    '''
       drivers = [
            'GV0' = TempC
            'GV1' = Low Temp Alarm
            'GV2' = high Temp Alarm 
            'GV3' = Humidity
            'GV4' = Low Humidity Alarm
            'GV5' = High Humidity Alarm
            'GV6' = BatteryLevel
            'GV7' = BatteryAlarm
            'GV8' = ALARM
            'GV9' = command setting 
            'ST' = Online
            ]

    ''' 
        
    drivers = [

            {'driver': 'CLITEMP', 'value': 0, 'uom': 4},
            {'driver': 'GV1', 'value': 2, 'uom': 25}, 
            {'driver': 'GV2', 'value': 2, 'uom': 25},           
            {'driver': 'CLIHUM', 'value': 0, 'uom': 51},
            {'driver': 'GV4', 'value': 2, 'uom': 25},
            {'driver': 'GV5', 'value': 2, 'uom': 25},
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
            {'driver': 'GV7', 'value': 2, 'uom': 25},
            {'driver': 'GV8', 'value': 2, 'uom': 25},
            {'driver': 'GV9', 'value': 99, 'uom': 25},
            {'driver': 'GV10', 'value': 0, 'uom': 4},
            {'driver': 'GV11', 'value': 0, 'uom': 4},
            {'driver': 'GV12', 'value': 0, 'uom': 51},
            {'driver': 'GV13', 'value': 0, 'uom': 51},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 99, 'uom': 25},            
            {'driver': 'GV20', 'value': 99, 'uom': 25},            
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},    
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoSprinkler INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.n_queue = []  
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoSprinkler  = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.temp_unit = self.yoAccess.get_temp_unit()   

        self.meas_support = []
        self.cmd_state = self.retrieve_cmd_state()
        model = str(self.devInfo['modelName'][:6])

        '''        if model in ['YS8017', 'YS8014', 'YS8004', 'YS8008', 'YS8003']:
            self.meas_support = ['temp']
        else:
            self.meas_support = ['temp', 'hum']
        if self.temp_unit == 1:
            if 'hum' not in self.meas_support:
                self.id = 'yotsensF'
            else:
                self.id = 'yothsensF'   
        else:
            if 'hum' not in self.meas_support:
                self.id = 'yotsens'  
        '''
        self.alarm_state = False
        self.sensordata_24_hours = {}
        #self.address = address
        #self.poly = polyglot

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
                     
        # start processing events and create add our controller node
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()

        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True


  


    def start(self):
        logging.info('Start udiYoSprinkler')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0)
        self.yoSprinkler  = YoLinkSprinkler(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(1)
        self.yoSprinkler.initNode()
        time.sleep(1)
        time.sleep(1)
        tries = 1
        while not self.yoSprinkler.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoSprinkler.refreshDevice()
            tries += 1
        self.temp_unit = self.yoAccess.get_temp_unit()
        #self.my_setDriver('GV30', 1)
        self.start_done()

    def initNode(self):
        sprinkler = self._get_sprinkler('initNode')
        if sprinkler is None:
            return
        sprinkler.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoSprinkler')
        self.my_setDriver('GV30', 0)
        sprinkler = self._get_sprinkler('stop')
        if sprinkler is not None:
            sprinkler.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_sprinkler(self, caller):
        sprinkler = getattr(self, 'yoSprinkler', None)
        if sprinkler is None:
            logging.warning('udiYoSprinkler.%s called before device initialization', caller)
        return sprinkler

    def checkOnline(self):
        # Guard: defer if initialization not complete
        if not self.node_ready or not self.configDone:
            return
        sprinkler = self._get_sprinkler('checkOnline')
        if sprinkler is None:
            return
        sprinkler.refreshDevice()

    def checkDataUpdate(self):
        # Guard: defer if initialization not complete
        if not self.node_ready or not self.configDone:
            return
        sprinkler = self._get_sprinkler('checkDataUpdate')
        if sprinkler is None:
            return
        if sprinkler.data_updated():
            self.updateData()


    def get_alarms_state (self):
        alarm_on = False
        sprinkler = self._get_sprinkler('get_alarms_state')
        if sprinkler is None:
            return False
        alarms = sprinkler.getAlarms()
        logging.debug(f'Alarms: {alarms}')
        if alarms:
            for a_type in alarms:
                if alarms[a_type]:
                    alarm_on = True
        return(alarm_on)


    def updateData(self):
        #alarms = self.yoSprinkler.getAlarms()
        #limits = self.yoSprinkler.getLimits()
        logging.info('yoSprinkler -  updateData')
        alarm_det = False 
        sprinkler = self._get_sprinkler('updateData')
        if sprinkler is None:
            return
        if self.node is not None:
            while not self.node_ready or not self.system_ready or self.configDone:
                time.sleep(0.5)
                
            message_info = sprinkler.get_message_type()
            message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
            unix_time = sprinkler.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)
            if sprinkler.check_system_online():
                tempC = sprinkler.get_data('temperature', 'state')
                tempLimMin = sprinkler.get_data('min', 'tempLimit')
                tempLimMax = sprinkler.get_data('max', 'tempLimit')    
                lowTempAlarm = sprinkler.get_data('lowTemp', 'alarms')
                highTempAlarm = sprinkler.get_data('highTemp', 'alarms')     
                alarm_det = alarm_det or lowTempAlarm or highTempAlarm        
                hum = None
                humLimMin = None
                humLimMax = None
                lowHumAlarm = False
                highHumAlarm = False
                if 'hum' in self.meas_support:
                    hum = sprinkler.get_data('humidity', 'state')
                    humLimMin = sprinkler.get_data('min', 'humidityLimit')
                    humLimMax = sprinkler.get_data('max', 'humidityLimit') 
                    lowHumAlarm = sprinkler.get_data('lowHumidity', 'alarms')
                    highHumAlarm = sprinkler.get_data('highHumidity', 'alarms')  
                    alarm_det = alarm_det or lowHumAlarm or highHumAlarm
                tempMeasMin, tempMeasMax, humMeasMin, humMeasMax = sprinkler.update_data_24_hours(unix_time, tempC, hum)
                bat_lvl = sprinkler.get_data('battery', 'state')
                bat_alarm = sprinkler.get_data('batteryLow', 'alarms')
                #tempMeas = self.yoSprinkler.get_data('temperature', 'statistics')
                #if isinstance(tempMeas, dict):
                #    tempMeasMin = tempMeas.get('min', None)
                ##    tempMeasMax = tempMeas.get('max', None)
                #else:

                #    tempMeasMin = None
                #    tempMeasMax = None
                
                if isinstance(tempC, (int, float)):
                    if self.temp_unit == 0:
                        self.my_setDriver('CLITEMP', round(tempC,1),  4, type=message_type)
                        self.my_setDriver('ST', round(tempC,1),  4)
                        #if 'tempLimit' in limits:
                        self.my_setDriver('GV10', tempLimMin,  4, type=message_type)
                        self.my_setDriver('GV11', tempLimMax,  4, type=message_type)
                        self.my_setDriver('GV14', tempMeasMin,  4, type=message_type)
                        self.my_setDriver('GV15', tempMeasMax,  4, type=message_type)                        

                    elif self.temp_unit == 1:
                        self.my_setDriver('CLITEMP', round(tempC*9/5+32,1),  17, type=message_type)
                        self.my_setDriver('ST', round(tempC*9/5+32,1),  17, type=message_type)
                        if isinstance(tempLimMin, (int, float)):
                            self.my_setDriver('GV10', round(tempLimMin*9/5+32,1),  17, type=message_type)
                        if isinstance(tempLimMax, (int, float)):
                            self.my_setDriver('GV11', round(tempLimMax*9/5+32,1),  17, type=message_type) 
                        if isinstance(tempMeasMin, (int, float)):   
                            self.my_setDriver('GV14', round(tempMeasMin*9/5+32,1),  17, type=message_type)
                        if isinstance(tempMeasMax, (int, float)):   
                            self.my_setDriver('GV15', round(tempMeasMax*9/5+32,1),  17, type=message_type)      
                else:
                    self.my_setDriver('CLITEMP', 99,  25)
                    self.my_setDriver('ST', 99,  25)
                    self.my_setDriver('GV10', 99, 25)
                    self.my_setDriver('GV11', 99, 25)
                    self.my_setDriver('GV14', 99, 25)
                    self.my_setDriver('GV15', 99, 25)
   
                
            
                self.my_setDriver('GV1', sprinkler.bool2Nbr(lowTempAlarm), type=message_type)
                self.my_setDriver('GV2', sprinkler.bool2Nbr(highTempAlarm), type=message_type)

                if 'hum' in self.meas_support:
                    if isinstance(hum,(int,float)):
                        self.my_setDriver('CLIHUM', hum, 51, type=message_type )
        
                        self.my_setDriver('GV12', humLimMin, 51, type=message_type)
                        self.my_setDriver('GV13', humLimMax, 51, type=message_type)
                        self.my_setDriver('GV16', humMeasMin, 51, type=message_type)
                        self.my_setDriver('GV17', humMeasMax, 51, type=message_type)
                    self.my_setDriver('GV4', sprinkler.bool2Nbr(lowHumAlarm), type=message_type)
                    self.my_setDriver('GV5', sprinkler.bool2Nbr(highHumAlarm), type=message_type)
                    if alarm_det or lowHumAlarm or highHumAlarm:
                        alarm_det = True
                else:
                    self.my_setDriver('CLIHUM', 98, 25)
                    self.my_setDriver('GV12', 98, 25)
                    self.my_setDriver('GV13', 98, 25)
                    self.my_setDriver('GV16', 98, 25)
                    self.my_setDriver('GV17', 98, 25)   
                    self.my_setDriver('GV4', 98, 25)
                    self.my_setDriver('GV5', 98, 25)


                self.my_setDriver('BATLVL', bat_lvl, 25, type=message_type)
                self.my_setDriver('GV7', sprinkler.bool2Nbr(bat_alarm))
                alarm_det = alarm_det or bat_alarm

                if alarm_det != self.alarm_state:
                    if alarm_det and self.cmd_state in [0,1]:
                        self.node.reportCmd('DON')
                    if not alarm_det and self.cmd_state in [0,2]:  
                        self.node.reportCmd('DOF')
                    self.alarm_state = alarm_det                


                    self.my_setDriver('GV8', sprinkler.bool2Nbr(self.alarm_state))
                    self.my_setDriver('GV9', self.cmd_state)

                self.my_setDriver('GV30', 1)

                if sprinkler.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)                
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)



    def updateStatus(self, data):
        logging.debug('udiYoSprinkler - updateStatus')
        sprinkler = self._get_sprinkler('updateStatus')
        if sprinkler is None:
            return
        if self.node is not None:
            while not self.node_ready or not self.system_ready:
                time.sleep(0.5)
        with self._update_lock:
            sprinkler.updateStatus(data)
        self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoSprinkler  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV9', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

    def start_stop(self, command):
        # Legacy sprinkler node keeps this command as local command state.
        self.set_cmd(command)

    def set_attributes(self, command):
        # Legacy yosprinkler has no attribute write path in this class.
        logging.info('udiYoSprinkler set_attributes not implemented for legacy node: %s', command)

    def update(self, command = None):
        logging.info('THsensor Update')
        sprinkler = self._get_sprinkler('update')
        if sprinkler is None:
            return
        sprinkler.refreshDevice()
       
    commands = {
                'STARTSTOP': start_stop,
                'SETATTRIB': set_attributes,
                'UPDATE': update,
                }





