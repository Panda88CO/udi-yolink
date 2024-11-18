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
from yolinkWaterDeptV2 import YoLinkWaterDept



class udiYoWaterDept(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, bool2ISY, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yowaterdept'
    
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
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            {'driver': 'GV1', 'value': 0, 'uom': 56}, 
            {'driver': 'GV2', 'value': 0, 'uom': 56}, 
            {'driver': 'GV3', 'value': 0, 'uom': 25},
            {'driver': 'GV4', 'value': 0, 'uom': 25},
            {'driver': 'GV5', 'value': 0, 'uom': 25},
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
            {'driver': 'TIME', 'value': 99, 'uom': 25},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoWaterDept INIT- {}'.format(deviceInfo['name']))
        self.n_queue = []  
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoWaterDept  = None
        self.node_ready = False
        #self.temp_unit = self.yoAccess.get_temp_unit()
        #self.cmd_state = self.retrieve_cmd_state()
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
        logging.info('Start udiYoWaterDept')
        self.node.setDriver('ST', 0, True, True)
        self.yoWaterDept  = YoLinkWaterDept(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoWaterDept.initNode()
        time.sleep(2)
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.node_ready = True
        #self.node.setDriver('ST', 1, True, True)

    def initNode(self):
        self.yoWaterDept.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoWaterDept')
        self.node.setDriver('ST', 0, True, True)
        self.yoWaterDept.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkOnline(self):
        self.yoWaterDept.refreshDevice()

    def checkDataUpdate(self):
        if self.yoWaterDept.data_updated():
            self.updateData()


    def updateData(self):
        #alarms = self.yoWaterDept.getAlarms()
        #limits = self.yoWaterDept.getLimits()
        try:
            if self.node is not None:
                if self.yoWaterDept.online:
                    logging.debug("yoWaterDept : UpdateData")
                    self.my_setDriver('GV0', self.yoWaterDept.getWaterDepth())
                    settings = self.yoWaterDept.getAlarmSettings()
                    logging.debug(f'settings {settings}')
                    if settings != {}:
                        self.my_setDriver('GV1', settings['low'])
                        self.my_setDriver('GV2', settings['high'])
                    alarms =  self.yoWaterDept.getAlarms()
                    logging.debug(f'alarms {alarms}')
                    if 'low' in alarms:
                        self.my_setDriver('GV3', self.bool2ISY(alarms['low']))
                    
                        self.my_setDriver('GV4', self.bool2ISY(alarms['high']))
                        self.my_setDriver('GV5', self.bool2ISY(alarms['error']))

                    self.my_setDriver('BATLVL', self.yoWaterDept.getBattery())
                    logging.debug('Last  tamp {}'.format(int(self.yoWaterDept.lastUpdate()/60)))
                    logging.debug('date tamp {}'.format(int(self.yoWaterDept.getDataTimestamp()/60)))
                    self.my_setDriver('TIME', int(self.yoWaterDept.getDataTimestamp()/60))
                    self.my_setDriver('ST', 1)
                    
                else:

                    self.my_setDriver('TIME', int(self.yoWaterDept.getDataTimestamp()/60))
                    self.my_setDriver('ST', 0)
                    #self.node.setDriver('ST', 0, True, True)
        except Exception as e:
                    logging.error(f'Exception updateData {e}')
                    self.my_setDriver('TIME', int(self.yoWaterDept.getDataTimestamp()/60))       
            


    def updateStatus(self, data):
        logging.debug('udiYoWaterDept - updateStatus')
        self.yoWaterDept.updateStatus(data)
        self.updateData()

    def set_attributes(self, command):
        logging.info('udiYoWaterDept  set_attributes - {}'.format(command))
        query = command.get("query")
        highAlarm = int(query.get("waterHighAlarm.uom56"))
        lowAlarm= int(query.get("waterLowAlarm.uom56"))
        self.node.setDriver('GV1', lowAlarm, True, True)
        self.node.setDriver('GV2', highAlarm, True, True)
        self.yoWaterDept.setAttributes([{'low':lowAlarm, 'high':highAlarm}]) 

    def update(self, command = None):
        logging.info('WaterDept Update')
        self.yoWaterDept.refreshDevice()
       


    commands = {
                'SETATTR': set_attributes,             
                'UPDATE': update,
                }




