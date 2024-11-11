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
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, state2Nbr, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yowaterdept'
    
    '''
       drivers = [
            'GV0' = Level ? 18/38
            'GV1' = Low Level 18/38
            'GV2' = High Level 18/38
            'GV3' = Detect Error Alarm 25
            'GV4' = Low Water Alarm 25
            'GV5' = High Water Alarm  25
            'BATLVL' = BatteryLevel 25
            #'GV7' = BatteryAlarm
            #'GV8' = ALARM
            #'GV9' = command setting 
            'ST' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 0, 'uom': 18},
            {'driver': 'GV1', 'value': 2, 'uom': 18}, 
            {'driver': 'GV2', 'value': 2, 'uom': 18}, 
            {'driver': 'gv3', 'value': 0, 'uom': 25},
            {'driver': 'GV4', 'value': 2, 'uom': 25},
            {'driver': 'GV5', 'value': 2, 'uom': 25},
            {'driver': 'BATLVL', 'value': 99, 'uom': 25},
         
            {'driver': 'ST', 'value': 0, 'uom': 25},
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
        
        if self.node is not None:
            if self.yoWaterDept.online:
                logging.debug("yoWaterDept : UpdateData")

                self.my_setDriver('GV0', None)
                self.my_setDriver('GV1', None)
                self.my_setDriver('GV2', None)
                self.my_setDriver('GV3', None)
                self.my_setDriver('GV4', None)
                self.my_setDriver('GV5', None)
                self.my_setDriver('BATLVL', self.yoWaterDept.getBattery())
                self.my_setDriver('ST', 1)           
                
            else:
                self.my_setDriver('GV0', None)
                self.my_setDriver('GV1', None)
                self.my_setDriver('GV2', None)
                self.my_setDriver('GV3', None)
                self.my_setDriver('GV4', None)
                self.my_setDriver('GV5', None)
                self.my_setDriver('BATLVL',  None)
                self.my_setDriver('ST', 0)
                #self.node.setDriver('ST', 0, True, True)
            


    def updateStatus(self, data):
        logging.debug('udiYoWaterDept - updateStatus')
        self.yoWaterDept.updateStatus(data)
        self.updateData()

    def set_attributes(self, command):
        logging.info('udiYoWaterDept  set_attributes - {}'.format(command))
        
        #self.node.setDriver('GV9', self.cmd_state, True, True)
        #self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('WaterDept Update')
        self.yoWaterDept.refreshDevice()
       


    commands = {
                'SETATTR': set_attributes,             
                'UPDATE': update,
                }




