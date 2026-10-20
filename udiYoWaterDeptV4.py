#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
import importlib
from os import truncate
try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom
#import sys
import time
import threading
from yolinkWaterDeptV3 import YoLinkWaterDeptSensor



class udiYoWaterDept(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  retrieve_cmd_state, bool2ISY, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names

    id = 'YOWATERDEPT'
    
    '''
       drivers = [
            'GV0' = Level ?
            'GV1' = Low Level 
            'GV2' = High Level 
            'GV3' = Low Water Alarm 25
            'GV4' = High Water Alarm  25
            'GV5' = Detect Error Alarm 25            
            'BATLVL' = BatteryLevel 25
            'TIME' = Epoc time of data
            'ST' = Online
            ]

    ''' 
        
    drivers = [

            {'driver': 'GV0', 'value': 0, 'uom': 56, 'name': 'Water Level (Legacy)'},
            {'driver': 'GV1', 'value': 0, 'uom': 56, 'name': 'Low water Level Alarm setting'}, 
            {'driver': 'GV2', 'value': 0, 'uom': 56, 'name': 'High water Level Alarm setting'}, 
            {'driver': 'GV3', 'value': 0, 'uom': 25, 'name': 'Low Water Level'},
            {'driver': 'GV4', 'value': 0, 'uom': 25, 'name': 'High Water Level'},
            {'driver': 'GV5', 'value': 0, 'uom': 25, 'name': 'Sensor Error'},
            {'driver': 'BATLVL', 'value': 99, 'uom': 25, 'name': 'Battery Level'},
            {'driver': 'ST', 'value': 0, 'uom': 56, 'name': 'Water Level (0-1000)'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},            
            {'driver': 'GV20', 'value': 0, 'uom': 25, 'name': 'Connection State'},            
            {'driver': 'TIME', 'value': int(time.time()), 'uom': 151, 'name': 'Last Data Update'},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoWaterDept INIT- {}'.format(deviceInfo['name']))
        self.name = name
        
        self.poly = polyglot
        self.n_queue = []  
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoWaterDept  = None
        self._update_lock = threading.Lock()
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        #self.temp_unit = self.yoAccess.get_temp_unit()
        #self.cmd_state = self.retrieve_cmd_state()
        #self.address = address
        #self.poly = polyglot

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(self.poly.START, self.start, self.address)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
        #self.poly.subscribe(self.poly.STARTDONE, self.start_done)
                     
        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()

        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True


  

    def start(self):
        logging.info('Start udiYoWaterDept')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0, True, True)
        self.yoWaterDept  = YoLinkWaterDeptSensor(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoWaterDept.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoWaterDept.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoWaterDept.refreshDevice()    
            tries += 1
        time.sleep(2)
        self.temp_unit = self.yoAccess.get_temp_unit()
        #self.my_setDriver('GV30', 1, True, True)
        self.start_done()
      

        
    def initNode(self):
        sensor = self._get_sensor('initNode')
        if sensor is None:
            return
        sensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoWaterDept')
        self.my_setDriver('GV30', 0, True, True)
        sensor = self._get_sensor('stop')
        if sensor is not None:
            sensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_sensor(self, caller):
        sensor = getattr(self, 'yoWaterDept', None)
        if sensor is None:
            logging.warning('udiYoWaterDept.%s called before device initialization', caller)
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


    def updateData(self):
        #alarms = self.yoWaterDept.getAlarms()
        #limits = self.yoWaterDept.getLimits()
        sensor = self._get_sensor('updateData')
        if sensor is None:
            return
        try:
            if self.node is not None:
                while not self.node_ready or not self.system_ready or not self.configDone:
                    time.sleep(0.5)
            message_info = sensor.get_message_type()
            message_type = message_info[0] if isinstance(message_info, (list, tuple)) and len(message_info) >= 1 else None
            unix_time = sensor.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)


            if sensor.check_system_online():
                water_dept = sensor.get_data('waterDepth', 'state')
                logging.debug(f"yoWaterDept : {water_dept}")
            
                self.my_setDriver('GV0', water_dept, type=message_type)
                self.my_setDriver('ST', water_dept, type=message_type)
                settings_low  = sensor.get_data('low', 'alarmSettings')
                settings_high  = sensor.get_data('high', 'alarmSettings')
                self.my_setDriver('GV1', settings_low, 56)
                self.my_setDriver('GV2', settings_high, 56)
                alarms =  sensor.getAlarms()
                alarm_low = sensor.get_data('lowAlarm', 'alarm')
                alarm_high = sensor.get_data('highAlarm', 'alarm')
                alarm_error = sensor.get_data('detectorError', 'alarm')
                self.my_setDriver('GV3', self.bool2ISY(alarm_low), type=message_type)
                self.my_setDriver('GV4', self.bool2ISY(alarm_high), type=message_type)
                self.my_setDriver('GV5', self.bool2ISY(alarm_error), type=message_type)

                self.my_setDriver('BATLVL', sensor.get_data('battery', 'state'), type=message_type)
                #logging.debug('Last  tamp {}'.format(int(self.yoWaterDept.lastUpdate()/60)))
                #logging.debug('date tamp {}'.format(int(self.yoWaterDept.getDataTimestamp()/60)))
                #self.my_setDriver('TIME', int(self.yoWaterDept.getDataTimestamp()/60), 44)
                self.my_setDriver('GV30', 1)
                if sensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)                    
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 0)  
        except Exception as e:
                    logging.error(f'Exception updateData {e}')
                    self.my_setDriver('TIME', int(sensor.getDataTimestamp()/60))       
            


    def updateStatus(self, data):
        logging.debug('udiYoWaterDept - updateStatus')
        if self.yoWaterDept is not None:        
            with self._update_lock:
                self.yoWaterDept.updateStatus(data)
            self.updateData()

    def set_attributes(self, command):
        logging.info('udiYoWaterDept  set_attributes - {}'.format(command))
        attribs = {}
        query = command.get("query")
        highAlarm = int(query.get("waterHighAlarm.uom56"))
        lowAlarm= int(query.get("waterLowAlarm.uom56"))
        attribs['high'] = highAlarm
        attribs['low'] = lowAlarm
        sensor = self._get_sensor('set_attributes')
        if sensor is None:
            return
        sensor.setAttributes(attribs)
        self.my_setDriver('GV1', 98, 25)
        self.my_setDriver('GV2', 98, 25)


    def update(self, command = None):
        logging.info('WaterDept Update')
        sensor = self._get_sensor('update')
        if sensor is None:
            return
        sensor.refreshDevice()
       


    commands = {
                'SETATTR': set_attributes,             
                'UPDATE': update,
                }






