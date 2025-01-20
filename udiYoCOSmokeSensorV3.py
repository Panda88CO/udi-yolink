#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate

from yolinkCOSmokeSensorV2 import YoLinkCOSmokeSen
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
import time




class udiYoCOSmokeSensor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, bool2nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yoCOSmokesens'
    
    '''
       drivers = [

            'GV0' = Smoke Alert
            'GV1' = CO Alert
            'GV2' = HighTemp Alert
            'GV3' = Battery Alert
            'GV4' = Battery Level
            
            
            'GV5' = selfcheck result

            'GV7' = Command setting 
            'CLITEMP' = Device Temp
            'ST' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'ALARM', 'value': 99, 'uom': 25}, 
            {'driver': 'GV0', 'value': 99, 'uom': 25}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25}, 
            {'driver': 'GV2', 'value': 99, 'uom': 25}, 
            {'driver': 'GV3', 'value': 99, 'uom': 25}, 
            {'driver': 'GV4', 'value': 99, 'uom': 25}, 
            {'driver': 'GV5', 'value': 99, 'uom': 25}, 

            {'driver': 'GV7', 'value': 0,  'uom': 25}, 
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},   
             {'driver': 'TIME', 'value': int(time.time()), 'uom': 151},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoCOSmokeSensor  INIT - {}'.format(deviceInfo['name']))
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoCOSmokeSensor  = None
        self.node_ready = False
        self.last_state = 99
        self.cmd_state = self.retrieve_cmd_state()
        self.last_alert = False
        self.n_queue = []   
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
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.adr_list = []
        self.adr_list.append(address)

        


    def start(self):
        logging.info('start - YoLinkCOSmokeSensor')
        self.node.setDriver('ST', 0)
        self.yoCOSmokeSensor  = YoLinkCOSmokeSen(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoCOSmokeSensor.initNode()
        self.node_ready = True
        #self.node.setDriver('ST', 1)

        #time.sleep(3)
    
    '''
    def initNode(self):
        self.yoCOSmokeSensor.refreshSensor()
    '''
    
    def stop (self):
        logging.info('Stop udiYoCOSmokeSensor ')
        self.node.setDriver('ST', 0)
        if self.yoCOSmokeSensor:
            self.yoCOSmokeSensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)  

    def checkOnline(self):
        #we only get casched values - but MQTT remains alive
        self.yoCOSmokeSensor.refreshDevice()  

 


    def checkDataUpdate(self):
        if self.yoCOSmokeSensor.data_updated():
            self.updateData()

    def updateData(self):
        if self.node is not None:
            self.my_setDriver('TIME', self.yoCOSmokeSensor.getLastUpdateTime(), 151)

            if self.yoCOSmokeSensor.online:
                smoke_alert =   self.yoCOSmokeSensor.alert_state('smoke')  
                logging.debug('Smokedetector smoke: {}'.format(smoke_alert))
                self.node.setDriver('GV0', self.bool2nbr(smoke_alert))
                CO_alert =   self.yoCOSmokeSensor.alert_state('CO')
                logging.debug('Smokedetector CO: {}'.format(CO_alert))
                self.node.setDriver('GV1', self.bool2nbr(CO_alert))
                hight_alert =   self.yoCOSmokeSensor.alert_state('high_temp')  
                logging.debug('Smokedetector high temp: {}'.format(hight_alert))
                self.node.setDriver('GV2', self.bool2nbr(hight_alert))
                bat_alert =   self.yoCOSmokeSensor.alert_state('battery')  
                logging.debug('Smokedetector battery: {}'.format(bat_alert))
                self.node.setDriver('GV3', self.bool2nbr(bat_alert))
                self.node.setDriver('GV4', self.yoCOSmokeSensor.getBattery())
                alert = smoke_alert or CO_alert or hight_alert or bat_alert
                self.node.setDriver('ALARM', self.bool2nbr(alert))
                if alert != self.last_alert:
                    if alert:
                        if self.cmd_state in [0,1]:
                            self.node.reportCmd('DON')
                    else:
                        if self.cmd_state in [0,2]:
                            self.node.reportCmd('DOF')
                    self.last_alert = alert
                self.node.setDriver('GV5', self.bool2nbr(self.yoCOSmokeSensor.get_self_ckheck_state()))
                self.node.setDriver('ST', 1)
                devTemp =  self.yoCOSmokeSensor.getDeviceTemperature()
                if devTemp != 'NA':
                    if self.temp_unit == 0:
                        self.node.setDriver('CLITEMP', round(devTemp,0), 4)
                    elif self.temp_unit == 1:
                        self.node.setDriver('CLITEMP', round(devTemp*9/5+32,0), 17)
                    elif self.temp_unit == 2:
                        self.node.setDriver('CLITEMP', round(devTemp+273.15,0), 26)
                else:
                    self.node.setDriver('CLITEMP', 99, 25)
                self.node.setDriver('GV7', self.cmd_state)
                if self.yoCOSmokeSensor.suspended:
                    self.node.setDriver('GV20', 1)
                else:
                    self.node.setDriver('GV20', 0)

            else:
                #self.node.setDriver('GV0', 99)
                #self.node.setDriver('GV1', 99)
                #self.node.setDriver('GV2', 99)
                #self.node.setDriver('GV3', 99)
                #self.node.setDriver('GV4', 99)
                #self.node.setDriver('GV5', 99)
           
                #self.node.setDriver('CLITEMP', 99, 25)
                #self.node.setDriver('ALARM', 99)     
                self.node.setDriver('ST', 0)
                self.node.setDriver('GV20', 2)


    def updateStatus(self, data):
        logging.debug('updateStatus - yoCOSmokeSensor')
        logging.debug('device oneline {}'.format(self.yoCOSmokeSensor.online))
        self.yoCOSmokeSensor.updateStatus(data)
        self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('yoCOSmokeSensor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.node.setDriver('GV7', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('yoCOSmokeSensor Update Status Executed')
        self.yoCOSmokeSensor.refreshDevice()
       
    def noop(self, command = None):
        pass

    commands = {
                'SETCMD': set_cmd,
                'UPDATE': update,
                'QUERY' : update, 
                #'DON'   : noop,
                #'DOF'   : noop
                }





