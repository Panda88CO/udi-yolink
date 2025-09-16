#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
#import sys
import time
from yolinkTHsensorV2 import YoLinkTHSen



class udiYoTHsensor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yothsens'
    
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
            {'driver': 'GV30', 'value': 0, 'uom': 25},            
            {'driver': 'GV20', 'value': 99, 'uom': 25},            
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},    
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoTHsensor INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []  
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoTHsensor  = None
        self.node_ready = False
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.cmd_state = self.retrieve_cmd_state()
        model = str(self.devInfo['modelName'][:6])
        if model in ['YS8017', 'YS8014', 'YS8004', 'US8008']:
            self.meas_support = ['temp']
        else:
            self.meas_support = ['temp', 'hum']
        self.alarm_state = False
        #self.address = address
        #self.poly = polyglot

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
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
        logging.info('Start udiYoTHsensor')
        self.my_setDriver('GV30', 0)
        self.yoTHsensor  = YoLinkTHSen(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(1)
        self.yoTHsensor.initNode()
        time.sleep(1)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.node_ready = True
        self.alarm_state = self.get_alarms_state()
        #self.my_setDriver('GV30', 1)

    def initNode(self):
        self.yoTHsensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoTHsensor')
        self.my_setDriver('GV30', 0)
        self.yoTHsensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkOnline(self):
        self.yoTHsensor.refreshDevice()

    def checkDataUpdate(self):
        if self.yoTHsensor.data_updated():
            self.updateData()


    def get_alarms_state (self):
        alarm_on = False
        alarms = self.yoTHsensor.getAlarms()
        logging.debug(f'Alarms: {alarms}')
        if alarms:
            for a_type in alarms:
                if alarms[a_type]:
                    alarm_on = True
        return(alarm_on)
                    

    def updateData(self):
        alarms = self.yoTHsensor.getAlarms()
        limits = self.yoTHsensor.getLimits()

        alarm_det = self.get_alarms_state()
        if alarm_det != self.alarm_state:
            if alarm_det and self.cmd_state in [0,1]:
                self.node.reportCmd('DON')
            if not alarm_det and self.cmd_state in [0,2]:  
                self.node.reportCmd('DOF')
            self.alarm_state = alarm_det
            
        if self.node is not None:
            self.my_setDriver('TIME', self.yoTHsensor.getLastUpdateTime(), 151)

            if self.yoTHsensor.online:
                logging.debug("yoTHsensor temp: {}".format(self.yoTHsensor.getTempValueC()))
                if self.temp_unit == 0:
                    self.my_setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC(),1),  4)
                    self.my_setDriver('ST', round(self.yoTHsensor.getTempValueC(),1),  4)
                    if 'tempLimit' in limits:
                        self.my_setDriver('GV10', limits['tempLimit']['min'],  4)
                        self.my_setDriver('GV11', limits['tempLimit']['max'],  4)
                elif self.temp_unit == 1:
                    self.my_setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC()*9/5+32,1),  17)
                    self.my_setDriver('ST', round(self.yoTHsensor.getTempValueC()*9/5+32,1),  17)
                    if 'tempLimit' in limits:
                        self.my_setDriver('GV10', round(limits['tempLimit']['min']*9/5+32,1),  17)
                        self.my_setDriver('GV11', round(limits['tempLimit']['max']*9/5+32,1),  17)                    
                elif self.temp_unit == 2:
                    self.my_setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC()+273.15,1), 26)
                    self.my_setDriver('ST', round(self.yoTHsensor.getTempValueC()+273.15,1), 26)
                    if 'tempLimit' in limits:
                        self.my_setDriver('GV10', round(limits['tempLimit']['min']+273.15,1), 26)
                        self.my_setDriver('GV11', round(limits['tempLimit']['max']+273.15,1),  26)    
                else:
                    self.my_setDriver('CLITEMP', 99, 25)
                    self.my_setDriver('ST', 99, 25)

                self.my_setDriver('GV1', self.yoTHsensor.bool2Nbr(alarms['lowTemp']))
                self.my_setDriver('GV2', self.yoTHsensor.bool2Nbr(alarms['highTemp']))
                if 'hum' in self.meas_support:
                    self.my_setDriver('CLIHUM', self.yoTHsensor.getHumidityValue())
                    if 'humidityLimit' in limits:
                            self.my_setDriver('GV12', limits['humidityLimit']['min'])
                            self.my_setDriver('GV13', limits['humidityLimit']['max'])
                    self.my_setDriver('GV4', self.yoTHsensor.bool2Nbr(alarms['lowHumidity']))
                    self.my_setDriver('GV5', self.yoTHsensor.bool2Nbr(alarms['highHumidity']))
                else:
                    self.my_setDriver('CLIHUM', 98, 25)
                    self.my_setDriver('GV12', 98, 25)
                    self.my_setDriver('GV13', 98, 25)
                    self.my_setDriver('GV4', 98, 25)
                    self.my_setDriver('GV5', 98, 25)

                self.my_setDriver('BATLVL', self.yoTHsensor.getBattery())
                self.my_setDriver('GV7', self.yoTHsensor.bool2Nbr(alarms['lowBattery']))
                self.my_setDriver('GV8', self.yoTHsensor.bool2Nbr(self.alarm_state))
                self.my_setDriver('GV9', self.cmd_state)
   

                self.my_setDriver('GV30', 1)

                if self.yoTHsensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
                
            else:
                #self.my_setDriver('CLITEMP', 99, 25)
                #self.my_setDriver('GV1',99)
                #self.my_setDriver('GV2', 99)
                #self.my_setDriver('CLIHUM', 0)
                #self.my_setDriver('GV4',99)
                #self.my_setDriver('GV5',99)
                #self.my_setDriver('BATLVL', 99)
                #self.my_setDriver('GV7',99)
                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)



    def updateStatus(self, data):
        logging.debug('udiYoTHsensor - updateStatus')
        self.yoTHsensor.updateStatus(data)
        self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoTHsensor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV9', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('THsensor Update')
        self.yoTHsensor.refreshDevice()
       


    commands = {
                'SETCMD': set_cmd,             
                'UPDATE': update,
                }




