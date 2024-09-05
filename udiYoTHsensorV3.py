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
    from  udiYolinkLib import save_cmd_state, retrieve_cmd_state, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

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
            {'driver': 'ST', 'value': 0, 'uom': 25},

            {'driver': 'GV10', 'value': 0, 'uom': 4},
            {'driver': 'GV11', 'value': 0, 'uom': 4},
            {'driver': 'GV12', 'value': 0, 'uom': 51},
            {'driver': 'GV13', 'value': 0, 'uom': 51},
            {'driver': 'GV20', 'value': 99, 'uom': 25},            
            #{'driver': 'ST', 'value': 0, 'uom': 25},
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
        self.node.setDriver('ST', 0, True, True)
        self.yoTHsensor  = YoLinkTHSen(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoTHsensor.initNode()
        time.sleep(2)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.node_ready = True
        #self.node.setDriver('ST', 1, True, True)

    def initNode(self):
        self.yoTHsensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoTHsensor')
        self.node.setDriver('ST', 0, True, True)
        self.yoTHsensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkOnline(self):
        self.yoTHsensor.refreshDevice()

    def checkDataUpdate(self):
        if self.yoTHsensor.data_updated():
            self.updateData()


    def updateData(self):
        alarms = self.yoTHsensor.getAlarms()
        limits = self.yoTHsensor.getLimits()
        
        if self.node is not None:
            if self.yoTHsensor.online:
                logging.debug("yoTHsensor temp: {}".format(self.yoTHsensor.getTempValueC()))
                if self.temp_unit == 0:
                    self.node.setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC(),1), True, True, 4)
                    if 'tempLimit' in limits:
                        self.node.setDriver('GV10', limits['tempLimit']['min'], True, True, 4)
                        self.node.setDriver('GV11', limits['tempLimit']['max'], True, True, 4)
                elif self.temp_unit == 1:
                    self.node.setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC()*9/5+32,1), True, True, 17)
                    if 'tempLimit' in limits:
                        self.node.setDriver('GV10', round(limits['tempLimit']['min']*9/5+32,1), True, True, 17)
                        self.node.setDriver('GV11', round(limits['tempLimit']['max']*9/5+32,1), True, True, 17)                    
                elif self.temp_unit == 2:
                    self.node.setDriver('CLITEMP', round(self.yoTHsensor.getTempValueC()+273.15,1), True, True, 26)
                    if 'tempLimit' in limits:
                        self.node.setDriver('GV10', round(limits['tempLimit']['min']+273.15,1), True, True, 26)
                        self.node.setDriver('GV11', round(limits['tempLimit']['max']+273.15,1), True, True, 26)    
                else:
                    self.node.setDriver('CLITEMP', 99, True, True, 25)
                self.node.setDriver('GV1', self.yoTHsensor.bool2Nbr(alarms['lowTemp']))
                self.node.setDriver('GV2', self.yoTHsensor.bool2Nbr(alarms['highTemp']))
                self.node.setDriver('CLIHUM', self.yoTHsensor.getHumidityValue())
                if 'humidityLimit' in limits:
                        self.node.setDriver('GV12', limits['humidityLimit']['min'])
                        self.node.setDriver('GV13', limits['humidityLimit']['max'])
                self.node.setDriver('GV4', self.yoTHsensor.bool2Nbr(alarms['lowHumidity']))
                self.node.setDriver('GV5', self.yoTHsensor.bool2Nbr(alarms['highHumidity']))
                self.node.setDriver('BATLVL', self.yoTHsensor.getBattery())
                self.node.setDriver('GV7', self.yoTHsensor.bool2Nbr(alarms['lowBattery']))
                self.node.setDriver('GV8', self.state2Nbr(self.yoTHsensor.getState()))
                self.node.setDriver('GV9', self.cmd_state)

                self.node.setDriver('ST', 1)

                if self.yoTHsensor.suspended:
                    self.node.setDriver('GV20', 1, True, True)
                else:
                    self.node.setDriver('GV20', 0)
                
            else:
                self.node.setDriver('CLITEMP', 99, True, True, 25)
                self.node.setDriver('GV1',99)
                self.node.setDriver('GV2', 99)
                self.node.setDriver('CLIHUM', 0, True, True)
                self.node.setDriver('GV4',99)
                self.node.setDriver('GV5',99)
                self.node.setDriver('BATLVL', 99)
                self.node.setDriver('GV7',99)
                #self.node.setDriver('ST', 0, True, True)
                self.node.setDriver('GV20', 2)



    def updateStatus(self, data):
        logging.debug('udiYoTHsensor - updateStatus')
        self.yoTHsensor.updateStatus(data)
        self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoTHsensor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.node.setDriver('GV9', self.cmd_state, True, True)
        self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('THsensor Update')
        self.yoTHsensor.refreshDevice()
       


    commands = {
                'SETCMD': set_cmd,             
                'UPDATE': update,
                'QUERY' : update, 
                }




