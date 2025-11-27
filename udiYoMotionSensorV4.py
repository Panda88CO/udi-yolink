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

import time

from yolinkMotionSensorV2 import YoLinkMotionSens



class udiYoMotionSensor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, convert_timestr_to_epoch, state2ISY, bool2ISY, retrieve_cmd_state, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yomotionsens'
    
    '''
       drivers = [
            'GV0' = Motion Alert
            'GV1' = Battery Level
            'GV2' = Command Setting

            'ST' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25}, 
            {'driver': 'GV2', 'value': 0, 'uom': 25},      
            {'driver': 'CLITEMP', 'value': 99, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},
            ]
    



    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('YoLinkMotionSensor INIT- {}'.format(deviceInfo['name']))
        self.address = address
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo

        self.temp_unit = self.yoAccess.get_temp_unit()           
        if self.temp_unit == 1:
            self.id = 'yomotionsensF'

        self.yoMotionsSensor  = None
        self.node_ready = False
        self.last_state = 99
        self.cmd_state = self.retrieve_cmd_state()
        
        self.n_queue = []
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
        self.temp_unit = self.yoAccess.get_temp_unit()
        self.adr_list = []
        self.adr_list.append(address)

        
    def start(self):
        logging.info('start - udiYoLinkMotionSensor')
        self.my_setDriver('GV30', 0)
        self.yoMotionsSensor  = YoLinkMotionSens(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoMotionsSensor.initNode()
        self.node_ready = True
        #self.my_setDriver('GV30', 1)

    
    def stop (self):
        logging.info('Stop udiYoMotionSensor')
        self.my_setDriver('GV30', 0)
        if self.yoMotionsSensor:
            self.yoMotionsSensor.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
                
    def checkOnline(self):
        self.yoMotionsSensor.refreshDevice()

    

    def getMotionState(self):
        if self.yoMotionsSensor.online:
            if  self.yoMotionsSensor.get_data('state', 'state') == 'normal':
                return(0)
            else:
                return(1)
        else:
            return(99)

    def checkDataUpdate(self):
        if self.yoMotionsSensor.data_updated():
            self.updateData()



    def updateData(self):
        if self.node is not None:
            unix_time = self.yoMotionsSensor.get_report_time('reportAt')
            self.my_setDriver('TIME', unix_time, 151)
            if self.yoMotionsSensor.online:
                logging.debug('Motion sensor CMD setting: {}'.format(self.cmd_state))
                motion_state = self.yoMotionsSensor.get_data('state', 'state')
                if motion_state in ['normal'] :
                    self.my_setDriver('GV0', 1)  
                    self.my_setDriver('ST', 1)                
                    if  self.cmd_state in [0,1]:
                        self.node.reportCmd('DON')
                elif motion_state in ['alert']:
                    self.my_setDriver('GV0', motion_state)
                    self.my_setDriver('ST', motion_state)
                    if self.cmd_state in [0,2]:
                        self.node.reportCmd('DOF')
                else:
                    self.my_setDriver('GV0', 99)
                    self.my_setDriver('ST', 99)
                self.last_state = motion_state
                self.my_setDriver('GV1', self.yoMotionsSensor.get_data('state', 'battery'))
                self.my_setDriver('GV2', self.cmd_state)
                self.my_setDriver('GV30', 1)
                devTemp =  self.yoMotionsSensor.get_data('state', 'devTemperature')
                if devTemp != None:
                    if self.temp_unit == 0:
                        self.my_setDriver('CLITEMP', round(devTemp,0), 4)
                    elif self.temp_unit == 1:
                        self.my_setDriver('CLITEMP', round(devTemp*9/5+32,0), 17)
                    #elif self.temp_unit == 2:
                    #    self.my_setDriver('CLITEMP', round(devTemp+273.15,0), 26)
                else:
                    self.my_setDriver('CLITEMP', 99, 25)
                if self.yoMotionsSensor.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)         
            else:

                self.my_setDriver('GV30', 0)
                self.my_setDriver('GV20', 2)       




    def updateStatus(self, data):
        logging.info('updateStatus - udiYoLinkMotionSensor')
        self.yoMotionsSensor.updateStatus(data)
        #time.sleep(1)
        self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoMotionSensor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV2', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

    def update(self, command = None):
        logging.info('udiYoMotionSensor Update  Executed')
        self.yoMotionsSensor.refreshDevice()
       

    def noop(self, command = None):
        pass

    commands = {
                'SETCMD': set_cmd,
                'UPDATE': update,
    
                #'DON'   : noop,
                #'DOF'   : noop
                }





