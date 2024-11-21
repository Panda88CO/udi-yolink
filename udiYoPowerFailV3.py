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
from yolinkPowerFailV2 import YoLinkPowerFailSen



class udiYoPowerFailSenor(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, bool2ISY, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yopwralarm'
    
    '''
       drivers = [
            'GV0' = Power Failure Alert
            'GV1' = Battery Level
            'GV2' = AlertState
            'GV3' = Powered
            'GV4' = Muted
                        
            'ST' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25}, 
            {'driver': 'GV2', 'value': 99, 'uom': 25}, 
            {'driver': 'GV3', 'value': 99, 'uom': 25}, 
            {'driver': 'GV4', 'value': 99, 'uom': 25}, 
            {'driver': 'GV7', 'value': 0, 'uom': 25},      
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25}, 
            {'driver': 'TIME', 'value': 0, 'uom': 44},

            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #from  udiLib import node_queue, wait_for_node_done, getValidName, getValidAddress, send_temp_to_isy, isy_value, bool2ISY
        logging.debug('udiYoPowerFailSenor INIT- {}'.format(deviceInfo['name']))
        self.adress = address
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoVibrationSensor  = None
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
        #self.my_setDriver('ST', 0)
        self.adr_list = []
        self.adr_list.append(address)

  


    def start(self):
        logging.info('start - udiYoPowerFailSenor')
        self.my_setDriver('ST', 0)
        self.yoPowerFail  = YoLinkPowerFailSen(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoPowerFail.initNode()
        self.node_ready = True
        #self.my_setDriver('ST', 1)

    
    def stop (self):
        logging.info('Stop udiYoPowerFailSenor')
        self.my_setDriver('ST', 0)
        self.yoPowerFail.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkOnline(self):
        self.yoPowerFail.refreshDevice()   
    
    def checkDataUpdate(self):
        if self.yoPowerFail.data_updated():
            self.updateData()


    def updateData(self):
        if self.node is not None:
            self.my_setDriver('TIME', int(self.yoPowerFail.getDataTimestamp()/60))
            
            if self.yoPowerFail.online:               
                state = self.yoPowerFail.getAlertState()
                logging.debug('state GV0 : {}'.format(state))
                self.my_setDriver('GV0', state)
                if state != self.last_state:
                    if state ==1 and self.cmd_state in [0,1]:
                        self.node.reportCmd('DON')
                    elif state == 0 and self.cmd_state in [0,2]:
                        self.node.reportCmd('DOF')
                    
                self.my_setDriver('GV1', self.yoPowerFail.getBattery())
                alert = self.yoPowerFail.getAlertType()
                logging.debug('AlertState GV2 : {}'.format(alert))
                self.my_setDriver('GV2', alert)
                powered = self.yoPowerFail.getPowerSupplyConnected()
                logging.debug('Powered  GV3 : {}'.format(powered))
                self.my_setDriver('GV3', self.bool2ISY(powered))
                muted = self.yoPowerFail.muted()
                logging.debug('Muted GV4 : {}'.format(muted))
                self.my_setDriver('GV4', self.bool2ISY(muted))
                self.my_setDriver('ST', 1)
                if self.yoPowerFail.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                    self.my_setDriver('GV20', 0)
            else:
                #self.my_setDriver('GV0', 99)
                #self.my_setDriver('GV1', 99)
                #self.my_setDriver('GV2', 99)
                #self.my_setDriver('GV3', 99)
                #self.my_setDriver('GV4', 99)

                self.my_setDriver('ST', 1)
                self.my_setDriver('GV20', 2)



    def getPowerSupplyState(self):
        logging.debug('getPowerSupplyState')




    def updateStatus(self, data):
        logging.info('updateStatus - udiYoPowerFailSenor')
        self.yoPowerFail.updateStatus(data)
        self.updateData()

    def set_cmd(self, command):
        ctrl = int(command.get('value'))   
        logging.info('udiYoPowerFailSenor  set_cmd - {}'.format(ctrl))
        self.cmd_state = ctrl
        self.my_setDriver('GV7', self.cmd_state)
        self.save_cmd_state(self.cmd_state)

        
    def update(self, command = None):
        logging.info('udiYoPowerFailSenor Update  Executed')
        self.yoPowerFail.refreshDevice()
       

    def noop(self, command = None):
        pass

    commands = {
                'SETCMD': set_cmd,
                'UPDATE': update,
                'QUERY' : update, 
                #'DON'   : noop,
                #'DOF'   : noop
                }





