#!/usr/bin/env python3
"""
Polyglot  v3 node server 


MIT License
"""
import importlib
from os import truncate
import threading

from yolinkLeakSensorV3 import YoLinkLeakSensor
try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom
import time




class udiYoLeakSensor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  save_cmd_state, retrieve_cmd_state, state2ISY, node_queue, wait_for_node_done, checkNameSync

    id = 'yoleaksens'
    
        
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25}, #basic leak
            {'driver': 'GV0', 'value': 99, 'uom': 25}, # legacy basic leak 
            {'driver': 'BATLVL', 'value': 99, 'uom': 25}, #batlvl  GV1 - remember to notify
            {'driver': 'GV2', 'value': 0, 'uom': 25}, #Command state
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25}, # dev temp
            {'driver': 'GV3', 'value': int(time.time()), 'uom': 151}, #latest change 

            {'driver': 'GV4', 'value': 0, 'uom': 25}, #Beeping
            {'driver': 'GV5', 'value': 0, 'uom': 25}, #Operation Mode
            {'driver': 'GV6', 'value': 0, 'uom': 25}, #Sensitivity


            {'driver': 'GV7', 'value': 0, 'uom': 25}, #Sensor Move 
            {'driver': 'GV8', 'value': 0, 'uom': 25}, #Sensor Freeze Alert
            {'driver': 'GV9', 'value': 0, 'uom': 25}, #Sensor Detecto Error
            {'driver': 'GV10', 'value': 0, 'uom': 25}, #Reminder Alert            

            {'driver': 'GV20', 'value': 99, 'uom': 25},   
            {'driver': 'GV30', 'value': 99, 'uom': 25},

             {'driver': 'TIME', 'value': int(time.time()), 'uom': 151},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoLeakSensor  INIT - {}'.format(deviceInfo['name']))
        self.name = name
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo

        self._update_lock = threading.Lock()
        self.temp_unit = self.yoAccess.get_temp_unit()           
        if self.temp_unit == 1:
            self.id = 'yoleaksensF'
        
        self.yoLeakSensor  = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self.last_state = 99
        self.cmd_state = self.retrieve_cmd_state()
        self.n_queue = []   
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
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True



    def start(self):
        logging.info('start - YoLinkLeakSensor')
        while not self.node_ready or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0)
        self.yoLeakSensor  = YoLinkLeakSensor(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoLeakSensor.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoLeakSensor.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoLeakSensor.refreshDevice()   
            tries += 1
        #self.my_setDriver('ST', 1)
        self.start_done()

        #time.sleep(3)
    
    '''
    def initNode(self):
        self.yoLeakSensor.refreshSensor()
    '''
    
    def stop (self):
        logging.info('Stop udiYoLeakSensor ')
        self.my_setDriver('GV30', 0)
        sensor = self._get_sensor('stop')
        if sensor is not None:
            sensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)  

    def _get_sensor(self, caller):
        sensor = getattr(self, 'yoLeakSensor', None)
        if sensor is None:
            logging.warning('udiYoLeakSensor.%s called before device initialization', caller)
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
                waterState =   sensor.get_data('state', 'state')

                #logging.debug( 'Leak Sensor 0,1,8: {}  {} {}'.format(waterState,self.yoLeakSensor.getBattery(),self.yoLeakSensor.bool2Nbr(self.yoLeakSensor.online)  ))
                if waterState in ['alert' , 'wet']:
                    self.my_setDriver('GV0', 1, type=message_type)
                    self.my_setDriver('ST', 1, type=message_type)
                    if waterState != self.last_state:
                        if self.cmd_state in [0,1]:
                            self.node.reportCmd('DON')
                elif waterState in ['normal', 'dry']:
                    self.my_setDriver('GV0', 0, type=message_type)
                    self.my_setDriver('ST', 0, type=message_type)                    
                    if waterState != self.last_state:
                        if self.cmd_state in [0,2]:
                            self.node.reportCmd('DOF')
                else:
                    self.my_setDriver('GV0', 99, type=message_type)
                    self.my_setDriver('ST', 99, type=message_type)   
                self.last_state = waterState
    
                batlvl = sensor.get_data('battery', 'state')
                if isinstance(batlvl, (int, float)):
                    self.my_setDriver('BATLVL', batlvl, type=message_type)
                else:
                    self.my_setDriver('BATLVL', 99, type=message_type)

                self.my_setDriver('GV2', self.cmd_state, type=message_type)
                #self.my_setDriver('ST', 1)

                state_change = sensor.get_data('stateChangedAt', 'state')
                logging.debug('state_change : {}'.format(state_change))
                if state_change is not None:
                    self.my_setDriver('GV3', int(state_change/1000), type=message_type)
                else:
                    self.my_setDriver('GV3', 99, UOM=25, type=message_type)

                devTemp =  sensor.get_data('devTemperature', 'state')
                if isinstance(devTemp, (int, float)):
                    if self.temp_unit == 0:
                        self.my_setDriver('CLITEMP', round(devTemp,0), 4, type=message_type)
                    elif self.temp_unit == 1:
                        self.my_setDriver('CLITEMP', round(devTemp*9/5+32,0), 17, type=message_type)
                else:
                    self.my_setDriver('CLITEMP', 99, 25)
                beeping = sensor.get_data('beep')    
                self.my_setDriver('GV4', self.state2ISY(beeping), type=message_type)
                opmode= sensor.get_data('sensorMode', 'state')
                if opmode in ['WaterLeak', None]:   
                    self.my_setDriver('GV5', 0, type=message_type)
                elif opmode == 'WaterPeak':
                    self.my_setDriver('GV5', 1, type=message_type)
                sensitivity = sensor.get_data('sensitivity', 'state')
                if sensitivity in ['Low', 'low', None]:
                    self.my_setDriver('GV6', 0, type=message_type)
                else:
                    self.my_setDriver('GV6', 1, type=message_type)
                sensorMove = sensor.get_data('stayError', 'alarmState')
                self.my_setDriver('GV7', self.state2ISY(sensorMove), type=message_type)
                sensorFreeze = sensor.get_data('freezeError', 'alarmState')
                self.my_setDriver('GV8', self.state2ISY(sensorFreeze), type=message_type)
                sensorDetectError = sensor.get_data('detectorError', 'alarmState')  
                self.my_setDriver('GV9', self.state2ISY(sensorDetectError), type=message_type)
                reminderAlert = sensor.get_data('reminder', 'alarmState')
                self.my_setDriver('GV10', self.state2ISY(reminderAlert), type=message_type)

                self.my_setDriver('GV30', 1, type=message_type)
                if sensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)             
            else:

                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)       

    def updateStatus(self, data):
        logging.debug('updateStatus - yoLeakSensor')
        if self.yoLeakSensor is not None:
            with self._update_lock:
                self.yoLeakSensor.updateStatus(data)
            self.updateData()

    def set_beep_alert(self, command):
        beeping = int(command.get('value')) == 1   
        logging.info('Leak Sensor  set_beep_alert - {}'.format(beeping))        
        params = {
            'beep': beeping
        }   
        sensor = self._get_sensor('set_beep_alert')
        if sensor is None:
            return
        sensor.setAttributes(params)



    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('Leak Sensor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV2', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('Leak Sensor Update Status Executed')
        sensor = self._get_sensor('update')
        if sensor is None:
            return
        sensor.refreshDevice()
       
    def noop(self, command = None):
        pass

    commands = {
                'SETCMD': set_cmd,    
                'SETBEEP': set_beep_alert,    
                'UPDATE': update,
                #'DON'   : noop,
                #'DOF'   : noop
                }






