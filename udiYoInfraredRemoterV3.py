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

class udiYoInfraredCode(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, node_queue, wait_for_node_done

    id = 'yoircode'
    '''
       drivers = [

            'GV2' = Command status
            'GV5' = Online
            ]
    ''' 
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},       
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},                 
            ] 
    def  __init__(self, polyglot, primary, address, name, code_indx, yoIRrem):
        logging.debug('udiIRcode'.format(code_indx))
        super().__init__( polyglot, primary, address, name)   
        self.yoIRrem = yoIRrem
        self.code = code_indx
        self.n_queue = []   
        self.poly.ready()
       
        #self.poly.subscribe(polyglot.START, self.start, self.address)
        #self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        time.sleep(2)
        self.updateData()

    def checkDataUpdate(self):
        if self.yoIRrem.data_updated():

            self.updateData()
            
    def checkOnline(self):
        pass  #is it a sub node - do nothing

    def updateData(self):
        if self.node is not None:
            logging.debug('updateData - {}'.format(self.yoIRrem.online))
            self.my_setDriver('TIME', self.yoIRrem.getLastUpdateTime(), 151)
            #self.my_setDriver('ST', 0)
            if self.yoIRrem.suspended:
                self.my_setDriver('GV20', 1)
            else:
                self.my_setDriver('GV20', 0)
        else:
            self.my_setDriver('GV20', 2)

    def clear_delay(self, delay=5):
        time.sleep(delay)
        self.my_setDriver('ST', 0)

    def send_IRcode(self, command=None):
        try:
            logging.info('udiIRremote send_IRcode')
            if self.yoIRrem.send_code( self.code):
                time.sleep(0.5)
                res = self.yoIRrem.get_send_status()
                while res is {} and self.yoIRrem.online:
                    time.sleep(1)
                    res = self.yoIRrem.get_send_status()
                logging.debug(f'Send code {self.code} {res}')
                if res['success'] == True and res['key'] == self.code:
                    logging.info('Code {} sent successfully'.format(self.code))
                    self.node.reportCmd('DON')  
                    self.my_setDriver('ST', 1)
                    self.clear_delay(5)
                    return
                else:
                    logging.info('Failed to send code {}'.format(self.code))
                    self.my_setDriver('ST', 2)
                    self.clear_delay(5)
                    return
            else:
                logging.info('Failed to send code {}'.format(self.code))
                self.my_setDriver('ST', 2)
                self.clear_delay(5)
                return
        except Exception as E:
            logging.error('udiIRcode send_IRcode - Exception: {}'.format(E))        
        '''   
            if 'success' in res:
                if  res['success'] == True:
                    logging.info('Code {} sent successfully'.format(self.code))
                    self.node.reportCmd('DON')  
                    self.my_setDriver('ST', 1)
                else:
                    self.my_setDriver('ST', 0)
            else:
                self.my_setDriver('ST', 0)              
        else:
            self.my_setDriver('ST', 0)
        
        if self.yoIRrem.suspended:
            self.my_setDriver('GV20', 1)
        else:
            self.my_setDriver('GV20', 0)  
        '''
    commands = {
            'TXCODE': send_IRcode,
            }


class udiYoInfraredRemoter(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, save_cmd_state, retrieve_cmd_state, bool2ISY, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key

    id = 'yoirremote'
    '''
       drivers = [
            'GV0' = Nbr codes
            'GV1' = Battery Level
            'GV2' = Command status
            ]
    ''' 
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV30', 'value': 0, 'uom': 25},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            {'driver': 'GV1', 'value': 0, 'uom': 25},
            {'driver': 'GV2', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25},       
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},                 
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   

        logging.debug('udiIRremote INIT- {}'.format(deviceInfo['name']))

        self.yoAccess = yoAccess
        self.poly = polyglot
        self.devInfo =  deviceInfo
        self.address = address
        self.primary = primary
        self.yoIRrem = None
        self.node_ready = False
        self.powerSupported = True # assume 
        self.n_queue = []     

        self.poly.subscribe(polyglot.START, self.start, self.address)
        self.poly.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
          

        # start processing events and create add our controller node
        self.poly.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)   
        self.codes_used = []
        self.code_nodes = {}


    def start(self):
        logging.info('start - YoLinkOutlet')
        self.my_setDriver('ST', 0)
        self.yoIRrem  = YoLinkInfraredRem(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoIRrem.initNode()
        time.sleep(2)
        #self.my_setDriver('ST', 1)
        self.my_setDriver('GV30', 1)
        code_dict_temp = self.yoIRrem.get_code_dict()
        logging.debug(f'Code dict temp: {code_dict_temp}')
        while not self.yoIRrem.check_system_online():
            logging.warning('System offline - need to obtain learned codes before continuing - trying again')
            time.sleep(5)
            self.yoIRrem.refreshDevice()
            time.sleep(2)  
            code_dict_temp = self.yoIRrem.get_code_dict()
            logging.debug(f'Code dict temp: {code_dict_temp}')

        for code in range(0, len(code_dict_temp)):
            if code_dict_temp[code]:
                logging.info(f'Adding code {code} to node list')
                self.codes_used.append(code)
                nde_address =self.address[-11:] +'x'+ str(code)
                logging.debug(f'ircode {self.primary} {code} {nde_address}')
                if code < 9:
                    self.code_nodes[code] = self.poly.addNode(udiYoInfraredCode(self.poly, self.primary, nde_address, 'Code 0'+ str(code+1),code, self.yoIRrem ), conn_status = None, rename = True)
                else:
                    self.code_nodes[code] = self.poly.addNode(udiYoInfraredCode(self.poly, self.primary, nde_address, 'Code '+ str(code+1),code, self.yoIRrem ), conn_status = None, rename = True)
        
        #self.poly.setCustomParams({'yoirremote': self.address})
        #self.poly.saveCustomParams()
        self.poly.updateProfile()
        #self.poly.addCustomProfile(self.id, 'YoLink Infrared Remoter', 'YoLink Infrared Remoter', 'YoLink Infrared Remoter')
        logging.info('YoLink Infrared Remoter Node Ready')
        self.updateData()


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
            self.my_setDriver('ST', self.err_code2nbr(self.yoIRrem.get_status_code()))
            self.my_setDriver('GV0',len(self.codes_used) )                 
            self.my_setDriver('GV1',self.yoIRrem.getBattery())
            self.my_setDriver('GV2',self.err_code2nbr(self.yoIRrem.get_status_code()))
            self.my_setDriver('GV30', 1)
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
            self.my_setDriver('GV30', 0)


    def updateStatus(self, data):
        logging.info('udiIRremote updateStatus')
        self.yoIRrem.updateStatus(data)
        self.updateData()
        res = self.yoIRrem.getIRstatus_info()
        logging.debug(f'IR status info: {res}')
        logging.debug(f'Code nodes: {self.code_nodes}')
        for code in self.code_nodes:
            logging.debug(f'Checking code node {code}')
            if self.code_nodes[code] is not None:
                self.code_nodes[code].updateData()
                if res['key'] == code:
                    if res['success'] == True:
                        self.code_nodes[code].my_setDriver('ST', 1)
                    else:
                        self.code_nodes[code].my_setDriver('ST', 2)
                else:
                    self.code_nodes[code].my_setDriver('ST', 0)


                
    def checkOnline(self):
        self.yoIRrem.refreshDevice()


    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoIRrem.refreshDevice()
    
    
    def find_next_code(self):  
        for code in range(1, 65):
            if code not in self.codes_used:
                return(code)
        return(None)


    
    def learn_IRcode(self, command=None):
        logging.info('udiIRremote learn_IRcode')
        if self.yoIRrem.nbr_codes < 64:
            code = self.find_next_code()
            logging.info(f'Learning code {code}')     
            self.yoIRrem.learn(code)
            time.sleep(1)
            res = self.yoIRrem.check_learn_completed(code)
            logging.debug(f'Initial learn res: {res}')  
            attempts = 1
            while res in ['learning', 'ignore'] and attempts < 10:
                time.sleep(1)
                res = self.yoIRrem.check_learn_completed(code)
                attempts += 1   
                logging.debug(f'Learn res: {res}')  

            if res == 'success':
                logging.info(f'Learned code {code} successfully')
                logging.info(f'Code {code} learned - creating new node')
                nde_address =self.address[-11:] +'x'+ str(code)
                if code < 9:
                    self.code_nodes[code] = self.poly.addNode(udiYoInfraredCode(self.poly, self.primary, nde_address, 'Code 0'+ str(code+1),code, self.yoIRrem ), conn_status = None, rename = True)
                else:
                    self.code_nodes[code] = self.poly.addNode(udiYoInfraredCode(self.poly, self.primary, nde_address, 'Code '+ str(code+1),code, self.yoIRrem ), conn_status = None, rename = True)
                                                                   
                self.yoIRrem.refreshDevice()
                #self.updateData()
            else:
                logging.info('Unsuccessful learn of code {}'.format(code))
    


    commands = {
                'UPDATE': update,

                #'TXCODE': send_IRcode,
                'LEARNCODE' : learn_IRcode,
                }




