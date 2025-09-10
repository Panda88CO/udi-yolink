#!/usr/bin/env python3
"""
MIT License
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

from ctypes import set_errno
from os import truncate
#import udi_interface
#import sys
import time
from yolinkInfraredRemoterV2 import YoLinkInfraredRem



class udiYoInfraredRemoter(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, bool2ISY, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yoirremote'
    '''
       drivers = [
            'GV0' = Nbr codes
            'GV1' = Battery Level
            'GV2' = Command status
            'GV5' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 0, 'uom': 107},
            {'driver': 'GV1', 'value': 99, 'uom': 25}, 
            {'driver': 'GV2', 'value': 99, 'uom': 25}, 
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},       
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},                 
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiIRremote INIT- {}'.format(deviceInfo['name']))

        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo
        self.yoIRrem = None
        self.node_ready = False
        self.powerSupported = True # assume 
        self.n_queue = []     

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
        logging.info('start - YoLinkOutlet')
        self.my_setDriver('ST', 0)
        self.yoIRrem  = YoLinkInfraredRem(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoIRrem.initNode()
        time.sleep(2)
        #self.my_setDriver('ST', 1)
        self.node_ready = True
    
    def stop (self):
        logging.info('Stop udiIRremote')
        self.my_setDriver('ST', 0)
        self.yoIRrem.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def checkDataUpdate(self):
        if self.yoIRrem.data_updated():
            self.updateData()

    def err_code2nbr(self, status_code):
        if status_code == 'notLearn':
            return(0)
        elif status_code == 'success': 
            return(1)
        elif status_code == 'keyError': 
            return(2)
        else:
            return(99)


    def updateData(self):
        if self.node is not None:
            logging.debug('updateData - {}'.format(self.yoIRrem.online))
            self.my_setDriver('TIME', self.yoIRrem.getLastUpdateTime(), 151)

        if  self.yoIRrem.online:
            self.my_setDriver('ST', 1)
            self.my_setDriver('GV0',self.yoIRrem.nbr_codes )                  
            self.my_setDriver('GV1',self.yoIRrem.getBattery())
            self.my_setDriver('GV2',self.err_code2nbr(self.yoIRrem.get_status_code()))
            if self.yoIRrem.suspended:
                self.my_setDriver('GV20', 1)
            else:
                self.my_setDriver('GV20', 0)
        else:
            #self.my_setDriver('GV0', 0)
            #self.my_setDriver('GV1', 99)
            #self.my_setDriver('GV2', 99)
            self.my_setDriver('ST', 0)
            self.my_setDriver('GV20', 2)



    def updateStatus(self, data):
        logging.info('udiIRremote updateStatus')
        self.yoIRrem.updateStatus(data)
        self.updateData()



    
    def checkOnline(self):
        self.yoIRrem.refreshDevice()


    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoIRrem.refreshDevice()
    
    def send_IRcode(self, command):
        logging.info('udiIRremote send_IRcode')
        code = int(command.get('value'))
        self.yoIRrem.send_code(code)

    '''
    def learn_IRcode(self, command):
        logging.info('udiIRremote learn_IRcode')
        code = int(command.get('value'))
        if self.yoIRrem.learn_code(code):
            logging.info('Code {}learned'.format(code))
        else:
            logging.info('Unsuccessful learn of code {}'.format(code))
    '''


    commands = {
                'UPDATE': update,
                'QUERY' : update,
                'TXCODE': send_IRcode,
                #'LEARNCODE' : learn_IRcode,
                }




