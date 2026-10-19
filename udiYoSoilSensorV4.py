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

from yolinkSoilSensorV2 import YoLinkSoilSensor



class udiYoSoilSensor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  save_cmd_state, retrieve_cmd_state, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names

    id = 'yosoilsensor'
    
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
            {'driver': 'ST', 'value': 0, 'uom': 70, 'name': 'Soil Conductivity (mS/cm)'},
            {'driver': 'CLITEMP', 'value': 0, 'uom': 4, 'name': 'Sensor Temperature'},
            {'driver': 'CLIHUM', 'value': 0, 'uom': 51, 'name': 'Current Rel Humidity (%)'},
            {'driver': 'GV1', 'value': 2, 'uom': 25, 'name': 'Low Conductivity Alarm'}, 
            {'driver': 'GV2', 'value': 2, 'uom': 25, 'name': 'High Conductivity Alarm'},           
            {'driver': 'GV3', 'value': 2, 'uom': 25, 'name': 'Low Temp Alarm'}, 
            {'driver': 'GV4', 'value': 2, 'uom': 25, 'name': 'High Temp Alarm'},
            {'driver': 'GV5', 'value': 2, 'uom': 25, 'name': 'Low Humidity Alarm'},
            {'driver': 'GV6', 'value': 2, 'uom': 25, 'name': 'High Humidity Alarm'},             
            {'driver': 'GV7', 'value': 2, 'uom': 25, 'name': 'Period Alarm'},
            {'driver': 'GV8', 'value': 2, 'uom': 25, 'name': 'Alarm triggered'},            
            {'driver': 'BATLVL', 'value': 99, 'uom': 25, 'name': 'Battery Level'},

            {'driver': 'GV9', 'value': 99, 'uom': 25, 'name': 'Command Setting'},
            {'driver': 'GV10', 'value': 0, 'uom': 4, 'name': 'Low Temp Alarm Limit'},
            {'driver': 'GV11', 'value': 0, 'uom': 4, 'name': 'High Temp Alarm Limit'},
            {'driver': 'GV12', 'value': 0, 'uom': 51, 'name': 'Low Humidity Alarm Limit'},
            {'driver': 'GV13', 'value': 0, 'uom': 51, 'name': 'High Humidity Alarm Limit'},
            {'driver': 'GV14', 'value': 0, 'uom': 70, 'name': 'Low Conductivity Alarm Limit (mS/cm)'},
            {'driver': 'GV15', 'value': 0, 'uom': 70, 'name': 'High Conductivity Alarm Limit (mS/cm)'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},            
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},            
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},    
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoSoilSensor INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.n_queue = []  
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoSoilSensor  = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.temp_unit = self.yoAccess.get_temp_unit()   


        self.cmd_state = self.retrieve_cmd_state()
        self.meas_support = []
        model = str(self.devInfo['modelName'][:6])
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
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()

        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True


 

    def start(self):
        logging.info('Start udiYoSoilSensor')
        while not self.node_ready  or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0)
        self.yoSoilSensor  = YoLinkSoilSensor(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(1)
        self.yoSoilSensor.initNode()
        time.sleep(1)
        time.sleep(1)
        tries = 1
        while not self.yoSoilSensor.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoSoilSensor.refreshDevice()
            tries += 1
        self.temp_unit = self.yoAccess.get_temp_unit()
        #self.my_setDriver('GV30', 1)
        self.start_done()

    def initNode(self):
        sensor = self._get_sensor('initNode')
        if sensor is None:
            return
        sensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoSoilSensor')
        self.my_setDriver('GV30', 0)
        sensor = self._get_sensor('stop')
        if sensor is not None:
            sensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_sensor(self, caller):
        sensor = getattr(self, 'yoSoilSensor', None)
        if sensor is None:
            logging.warning('udiYoSoilSensor.%s called before device initialization', caller)
        return sensor

    def checkOnline(self):
        sensor = self._get_sensor('checkOnline')
        if sensor is None:
            return
        sensor.refreshDevice()

    def checkDataUpdate(self):
        sensor = self._get_sensor('checkDataUpdate')
        if sensor is None:
            return
        if sensor.data_updated():
            self.updateData()


    def get_alarms_state (self):
        alarm_on = False
        sensor = self._get_sensor('get_alarms_state')
        if sensor is None:
            return False
        alarms = sensor.getAlarms()
        logging.debug(f'Alarms: {alarms}')
        if alarms:
            for a_type in alarms:
                if alarms[a_type]:
                    alarm_on = True
        return(alarm_on)


    def updateData(self):
        #alarms = self.yoSoilSensor.getAlarms()
        #limits = self.yoSoilSensor.getLimits()
        logging.info('yoSoilSensor -  updateData')
        alarm_det = False 
        sensor = self._get_sensor('updateData')
        if sensor is None:
            return
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)                
            message_info = sensor.get_message_type()
            message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
            unix_time = sensor.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)
            if sensor.check_system_online():
                conductivity = sensor.get_data('conductivity', 'state')
                lowCondAlarm = sensor.get_data('lowConductivity', 'alarm')
                highCondAlarm = sensor.get_data('highConductivity', 'alarm')
                alarm_det = alarm_det or lowCondAlarm or highCondAlarm
                if isinstance(conductivity, (int, float)):
                    self.my_setDriver('ST', round(conductivity/1000,1),  70, type=message_type)
                else:
                    self.my_setDriver('ST', 99,  25)
                self.my_setDriver('GV1', sensor.bool2Nbr(lowCondAlarm), type=message_type)
                self.my_setDriver('GV2', sensor.bool2Nbr(highCondAlarm), type=message_type) 
                min_conduct = sensor.get_data('min', 'conductivityLimit')
                max_conduct = sensor.get_data('max', 'conductivityLimit')
                if isinstance(min_conduct, (int, float)):
                    self.my_setDriver('GV14', round(min_conduct/1000,1),  70, type=message_type)
                else:
                    self.my_setDriver('GV14', 99,  25)
                if isinstance(max_conduct, (int, float)):
                    self.my_setDriver('GV15', round(max_conduct/1000,1),  70, type=message_type)    
                else:
                    self.my_setDriver('GV15', 99,  25)
                tempC = sensor.get_data('temperature', 'state')
                tempLimMin = sensor.get_data('min', 'tempLimit')
                tempLimMax = sensor.get_data('max', 'tempLimit')    
                lowTempAlarm = sensor.get_data('lowTemp', 'alarm')
                highTempAlarm = sensor.get_data('highTemp', 'alarm')     
                if isinstance(tempC, (int, float)):
                    if self.temp_unit == 0:
                        self.my_setDriver('CLITEMP', round(tempC,1),  4, type=message_type)

                        #if 'tempLimit' in limits:
                        self.my_setDriver('GV10', tempLimMin,  4, type=message_type)
                        self.my_setDriver('GV11', tempLimMax,  4, type=message_type)
                
                    elif self.temp_unit == 1:
                        self.my_setDriver('CLITEMP', round(tempC*9/5+32,1),  17, type=message_type)
                        self.my_setDriver('ST', round(tempC*9/5+32,1),  17, type=message_type)
                        if isinstance(tempLimMin, (int, float)):
                            self.my_setDriver('GV10', round(tempLimMin*9/5+32,1),  17, type=message_type)
                        if isinstance(tempLimMax, (int, float)):
                            self.my_setDriver('GV11', round(tempLimMax*9/5+32,1),  17, type=message_type) 
          
                else:
                    self.my_setDriver('CLITEMP', 99,  25)
                    self.my_setDriver('ST', 99,  25)
                    self.my_setDriver('GV10', 99, 25)
                    self.my_setDriver('GV11', 99, 25)            
                self.my_setDriver('GV3', sensor.bool2Nbr(lowTempAlarm), type=message_type)
                self.my_setDriver('GV4', sensor.bool2Nbr(highTempAlarm), type=message_type)

                hum = sensor.get_data('humidity', 'state')
                humLimMin = sensor.get_data('min', 'humidityLimit')
                humLimMax = sensor.get_data('max', 'humidityLimit') 
                lowHumAlarm = sensor.get_data('lowHumidity', 'alarm')
                highHumAlarm = sensor.get_data('highHumidity', 'alarm')  
                alarm_det = alarm_det or lowHumAlarm or highHumAlarm

                if isinstance(hum,(int,float)):
                    self.my_setDriver('CLIHUM', hum, 51, type=message_type )
    
                    self.my_setDriver('GV12', humLimMin, 51, type=message_type)
                    self.my_setDriver('GV13', humLimMax, 51, type=message_type)

                else:   
                    self.my_setDriver('CLIHUM', 99, 25)
                    self.my_setDriver('GV12', 99, 25)
                    self.my_setDriver('GV13', 99, 25)      

                self.my_setDriver('GV5', sensor.bool2Nbr(lowHumAlarm), type=message_type)
                self.my_setDriver('GV6', sensor.bool2Nbr(highHumAlarm), type=message_type)




                periodAlarm = sensor.get_data('period', 'alarm')
                alarm_det = alarm_det or periodAlarm
                self.my_setDriver('GV7', sensor.bool2Nbr(periodAlarm), type=message_type)
                self.my_setDriver('GV8', sensor.bool2Nbr(alarm_det), type=message_type)                
                bat_lvl = sensor.get_data('battery')
                self.my_setDriver('BATLVL', bat_lvl, 25, type=message_type)


                if alarm_det != self.alarm_state:
                    if alarm_det and self.cmd_state in [0,1]:
                        self.node.reportCmd('DON')
                    if not alarm_det and self.cmd_state in [0,2]:  
                        self.node.reportCmd('DOF')
                    self.alarm_state = alarm_det                               
                    self.my_setDriver('GV9', self.cmd_state)

                self.my_setDriver('GV30', 1)

                if sensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)                
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)



    def updateStatus(self, data):
        logging.debug('udiYoSprinkler - updateStatus')
        if self.yoSoilSensor is not None:
            with self._update_lock:
                self.yoSoilSensor.updateStatus(data)
            self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoSprinkler  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV9', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('THsensor Update')
        sensor = self._get_sensor('update')
        if sensor is None:
            return
        sensor.refreshDevice()
       
    commands = {
                'SETCMD': set_cmd,             
                'UPDATE': update,
                }





