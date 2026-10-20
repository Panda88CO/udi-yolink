#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
import importlib
from os import truncate
import threading

from yolinkCOSmokeSensorV3 import YoLinkCOSmokeSensor
try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom
import time




class udiYoCOSmokeSensor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  save_cmd_state, retrieve_cmd_state, bool2nbr, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names

    id = 'YOCOSMOKESENS'
    
    '''
       drivers = [

            'GV0' = Smoke Alert
            'GV1' = CO Alert
            'GV2' = HighTemp Alert
            'GV3' = Battery Alert
            'GV4' = Battery Level
            'GV30' = Device Online
            
            'GV5' = selfcheck result

            'GV7' = Command setting 
            'CLITEMP' = Device Temp
            'ST' = Alarm
            ]

    ''' 
        
    drivers = [ {'driver': 'ALARM', 'value': 99, 'uom': 25, 'name': 'Alert Detected'}, 
            {'driver': 'GV0', 'value': 99, 'uom': 25, 'name': 'Smoke Detection'}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25, 'name': 'CO Detection'}, 
            {'driver': 'GV2', 'value': 99, 'uom': 25, 'name': 'High Temp Detection'}, 
            {'driver': 'GV3', 'value': 99, 'uom': 25, 'name': 'Battery Problem Detection'}, 
            {'driver': 'GV4', 'value': 99, 'uom': 25, 'name': 'Sensor Battery Level'}, 
            {'driver': 'GV5', 'value': 99, 'uom': 25, 'name': 'Self-check'}, 
            {'driver': 'GV7', 'value': 0,  'uom': 25, 'name': 'Command Setting'}, 
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25, 'name': 'Sensor Temperature'},
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Alarm'},
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'},   
             {'driver': 'TIME', 'value': int(time.time()), 'uom': 151, 'name': 'Last device update'},]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoCOSmokeSensor  INIT - {}'.format(deviceInfo['name']))
        self.name = name
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo

        self.temp_unit = self.yoAccess.get_temp_unit()
        
        self.yoCOSmokeSensor  = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.last_state = 99
        self.cmd_state = self.retrieve_cmd_state()
        self.last_alert = False
        self.n_queue = []   
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        self.poly.subscribe(self.poly.START, self.start, self.address)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
             
        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True
        



    def start(self):
        logging.info('start - YoLinkCOSmokeSensor')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        #self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        self.yoCOSmokeSensor  = YoLinkCOSmokeSensor(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoCOSmokeSensor.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoCOSmokeSensor.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
            #   self.yoCOSmokeSensor.refreshDevice()            
            tries += 1

        #self.my_setDriver('ST', 1)
        self.start_done()

        #time.sleep(3)
    
    '''
    def initNode(self):
        self.yoCOSmokeSensor.refreshSensor()
    '''
    
    def stop (self):
        logging.info('Stop udiYoCOSmokeSensor ')
        #self.my_setDriver('ST', 0)
        self.my_setDriver('GV30', 0)
        sensor = self._get_sensor('stop')
        if sensor is not None:
            sensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)  

    def _get_sensor(self, caller):
        sensor = getattr(self, 'yoCOSmokeSensor', None)
        if sensor is None:
            logging.warning('udiYoCOSmokeSensor.%s called before device initialization', caller)
        return sensor

    def checkOnline(self):
        #we only get casched values - but MQTT remains alive
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
                smoke_alert =   sensor.get_data('smoke', 'state')  
                logging.debug('Smokedetector smoke: {}'.format(smoke_alert))
                self.my_setDriver('GV0', self.bool2nbr(smoke_alert), type=message_type)
                CO_alert =   sensor.get_data('CO', 'state')  
                logging.debug('Smokedetector CO: {}'.format(CO_alert))
                self.my_setDriver('GV1', self.bool2nbr(CO_alert), type=message_type)
                hight_alert =   sensor.get_data('high_temp', 'state')   
                logging.debug('Smokedetector high temp: {}'.format(hight_alert))
                self.my_setDriver('GV2', self.bool2nbr(hight_alert), type=message_type)
                bat_alert =   sensor.get_data('sLowBattery', 'state')   
                logging.debug('Smokedetector battery: {}'.format(bat_alert))
                self.my_setDriver('GV3', self.bool2nbr(bat_alert), type=message_type)
                self.my_setDriver('GV4', sensor.get_data('battery', 'state'), type=message_type)
                alert = smoke_alert or CO_alert or hight_alert or bat_alert
                self.my_setDriver('ALARM', self.bool2nbr(alert), type=message_type)
                self.my_setDriver('ST', self.bool2nbr(alert), type=message_type)
                if alert != self.last_alert:
                    if alert:
                        if self.cmd_state in [0,1]:
                            self.node.reportCmd('DON')
                    else:
                        if self.cmd_state in [0,2]:
                            self.node.reportCmd('DOF')
                    self.last_alert = alert
                self.my_setDriver('GV5', self.bool2nbr(sensor.get_data('inspect', 'metadata')))
                #self.my_setDriver('ST', 1)
                self.my_setDriver('GV30', 1)
                devTemp =  sensor.get_data('devTemperature', 'state')
                if devTemp != 'NA':
                    if self.temp_unit == 0:
                        self.my_setDriver('CLITEMP', round(devTemp,0), 4)
                    elif self.temp_unit == 1:
                        self.my_setDriver('CLITEMP', round(devTemp*9/5+32,0), 17)
                    elif self.temp_unit == 2:
                        self.my_setDriver('CLITEMP', round(devTemp+273.15,0), 26)
                else:
                    self.my_setDriver('CLITEMP', 99, 25)
                self.my_setDriver('GV7', self.cmd_state)
                if sensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)

            else:
                #self.my_setDriver('GV0', 99)
                #self.my_setDriver('GV1', 99)
                #self.my_setDriver('GV2', 99)
                #self.my_setDriver('GV3', 99)
                #self.my_setDriver('GV4', 99)
                #self.my_setDriver('GV5', 99)
           
                #self.my_setDriver('CLITEMP', 99, 25)
                #self.my_setDriver('ALARM', 99)     
                #self.my_setDriver('ST', 0)
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)


    def updateStatus(self, data):
        logging.debug('updateStatus - yoCOSmokeSensor')
        if self.yoCOSmokeSensor is not None:
            with self._update_lock:
                self.yoCOSmokeSensor.updateStatus(data)
            self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('yoCOSmokeSensor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV7', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('yoCOSmokeSensor Update Status Executed')
        sensor = self._get_sensor('update')
        if sensor is None:
            return
        sensor.refreshDevice()
       
    def noop(self, command = None):
        pass

    commands = {
                'SETCMD': set_cmd,
                'UPDATE': update,
                #'QUERY' : update, 
                #'DON'   : noop,
                #'DOF'   : noop
                }






