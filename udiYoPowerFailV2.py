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
        self.cmd_state = 3
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
        self.node.setDriver('ST', 1, True, True)
        self.adr_list = []
        self.adr_list.append(address)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def bool2ISY (self, data):
        if data:
            return(1)
        else:
            return(0)


    def start(self):
        logging.info('start - udiYoPowerFailSenor')
        self.node.setDriver('ST', 0, True, True)
        self.yoPowerFail  = YoLinkPowerFailSen(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoPowerFail.initNode()
        self.node_ready = True
        #self.node.setDriver('ST', 1, True, True)

    
    def stop (self):
        logging.info('Stop udiYoPowerFailSenor')
        self.node.setDriver('ST', 0, True, True)
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
            if self.yoPowerFail.online:               
                state = self.yoPowerFail.getAlertState()
                logging.debug('state GV0 : {}'.format(state))
                self.node.setDriver('GV0', state, True, True)
                if state != self.last_state:
                    if state ==1 and self.cmd_state in [0,1]:
                        self.node.reportCmd('DON')
                    elif state == 0 and self.cmd_state in [0,2]:
                        self.node.reportCmd('DOF')
                    
                self.node.setDriver('GV1', self.yoPowerFail.getBattery(), True, True)
                alert = self.yoPowerFail.getAlertType()
                logging.debug('AlertState GV2 : {}'.format(alert))
                self.node.setDriver('GV2', alert, True, True)
                powered = self.yoPowerFail.getPowerSupplyConnected()
                logging.debug('Powered  GV3 : {}'.format(powered))
                self.node.setDriver('GV3', self.bool2ISY(powered), True, True)
                muted = self.yoPowerFail.muted()
                logging.debug('Muted GV4 : {}'.format(muted))
                self.node.setDriver('GV4', self.bool2ISY(muted), True, True)                
                self.node.setDriver('ST', 1, True, True)
                if self.yoPowerFail.suspended:
                    self.node.setDriver('GV20', 1, True, True)
                else:
                    self.node.setDriver('GV20', 0)
            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV1', 99, True, True)
                self.node.setDriver('GV2', 99, True, True)
                self.node.setDriver('GV3', 99, True, True)
                self.node.setDriver('GV4', 99, True, True)

                self.node.setDriver('ST', 1, True, True)
                self.node.setDriver('GV20', 99, True, True)



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
        self.node.setDriver('GV7', self.cmd_state, True, True)

    def update(self, command = None):
        logging.info('udiYoPowerFailSenor Update  Executed')
        self.yoPowerFail.refreshDevice()
       

    def noop(self, command = None):
        pass

    commands = {
                'SETCMD': set_cmd,
                'UPDATE': update,
                'QUERY' : update, 
                'DON'   : noop,
                'DOF'   : noop
                }





