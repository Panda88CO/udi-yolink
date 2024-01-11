#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""

import sys
import time


from yoLink_init_V3 import YoLinkInitPAC
from udiYoSwitchV2 import udiYoSwitch
from udiYoTHsensorV2 import udiYoTHsensor 
from udiYoGarageDoorCtrlV2 import udiYoGarageDoor
from udiYoGarageFingerCtrlV2 import udiYoGarageFinger
from udiYoMotionSensorV2 import udiYoMotionSensor
from udiYoLeakSensorV2 import udiYoLeakSensor
from udiYoCOSmokeSensorV2 import udiYoCOSmokeSensor
from udiYoDoorSensorV2 import udiYoDoorSensor
from udiYoOutletV2 import udiYoOutlet
from udiYoMultiOutletV2 import udiYoMultiOutlet
from udiYoManipulatorV2 import udiYoManipulator
#from udiYoHubV2 import udiYoHub
from udiYoSpeakerHubV2 import udiYoSpeakerHub
from udiYoLockV2 import udiYoLock
from udiYoInfraredRemoterV2 import udiYoInfraredRemoter
from udiYoDimmerV2 import udiYoDimmer
from udiYoVibrationSensorV2 import udiYoVibrationSensor
from udiYoSmartRemoterV3 import udiYoSmartRemoter
from udiYoPowerFailV2 import udiYoPowerFailSenor
from udiYoSirenV2 import udiYoSiren

import udiProfileHandler

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

version = '0.9.90'

class YoLinkSetup (udi_interface.Node):

    def  __init__(self, polyglot, primary, address, name):
        super().__init__( polyglot, primary, address, name)  
        
        self.poly=polyglot
        self.hb = 0
        
        self.nodeDefineDone = False
        self.handleParamsDone = False
        self.pollStart = False
        self.debug = False
        self.address = address
        self.name = name
        self.yoAccess = None
        self.TTSstr = 'TTS'
        self.nbr_API_calls = 19
        self.nbr_dev_API_calls = 5
        self.supportParams = ['YOLINKV2_URL', 'TOKEN_URL','MQTT_URL', 'MQTT_PORT', 'UAID', 'SECRET_KEY', 'NBR_TTS', 'TEMP_UNIT' ]
        self.yolinkURL = 'https://api.yosmart.com/openApi'
        self.yolinkV2URL = 'https://api.yosmart.com/open/yolink/v2/api' 
        self.temp_unit = 0
        self.tokenURL = 'https://api.yosmart.com/open/yolink/token'
        self.mqttURL = 'api.yosmart.com'
        self.mqttPort = 8003

       
        
        logging.setLevel(10)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []
  
        self.Parameters = Custom(self.poly, 'customparams')
        self.Notices = Custom(self.poly, 'notices')
        logging.debug('YoLinkSetup init')
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))   
        self.poly.updateProfile()
        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)
        self.assigned_addresses = []
        self.assigned_addresses.append(self.address)   
        self.nodes_in_db = self.poly.getNodesFromDb()
        logging.debug('Nodes in Nodeserver - before cleanup: {} - {}'.format(len(self.nodes_in_db),self.nodes_in_db))
        logging.debug('YoLinkSetup init DONE')
        self.nodeDefineDone = True


    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def convert_temp_unit(self, tempStr):
        if tempStr.capitalize()[:1] == 'F':
            return(1)
        elif tempStr.capitalize()[:1] == 'K':
            return(2)
        else:
            return(0)


    def start (self):
        logging.info('Executing start - udi-YoLink')
        logging.info ('Access using PAC/UAC')
        #logging.setLevel(30)
        while not self.nodeDefineDone:
            time.sleep(1)
            logging.debug ('waiting for inital node to get created')
        #self.supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
        #                        'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
        #                        'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock', 'InfraredRemoter' ]
        self.supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
                                'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
                                'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock', 'Dimmer', 'InfraredRemoter',
                                'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren', 'WaterMeterController']
        #self.supportedYoTypes = ['MultiOutlet' ]
        

        if self.uaid == None or self.uaid == '' or self.secretKey==None or self.secretKey=='':
            logging.error('UAID and secretKey must be provided to start node server')
            exit() 


        self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)

        if 'TEMP_UNIT' in self.Parameters:
            self.temp_unit = self.convert_temp_unit(self.Parameters['TEMP_UNIT'])
        else:
            self.temp_unit = 0  
            self.Parameters['TEMP_UNIT'] = 'C'
            logging.debug('TEMP_UNIT: {}'.format(self.temp_unit ))

        self.yoAccess.set_temp_unit(self.temp_unit )

        if 'DEBUG_EN' in self.Parameters:
            self.debug = self.Parameters['DEBUG_EN']
            self.yoAccess.set_debug(self.debug)
        else:
            self.debug = False
            self.yoAccess.set_debug(self.debug)
        
        if 'CALLS_PER_MIN' in self.Parameters:
            self.nbr_API_calls = self.Parameters['CALLS_PER_MIN']
            self.nbr_dev_API_calls = self.Parameters['DEV_CALLS_PER_MIN']
            self.yoAccess.set_api_limits(self.nbr_API_calls, self.nbr_dev_API_calls)
        self.deviceList = self.yoAccess.getDeviceList()


        logging.debug('{} devices detected : {}'.format(len(self.deviceList), self.deviceList) )
        self.addNodes(self.deviceList)

        #self.poly.updateProfile()



    def addNodes (self, deviceList):
        for dev in deviceList:
            if dev['type']  in self.supportedYoTypes:
                logging.info('adding/checking device : {} - {}'.format(dev['name'], dev['type']))
                if dev['type'] == 'Hub':     
                    logging.info('Hub not added - ISY cannot do anything useful with it')    
                    #name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    #logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    #temp = udiYoHub(self.poly, address, address, dev['name'], self.yoAccess, dev )
                    #self.Parameters[address] =  dev['name']
                 
                elif dev['type'] == 'SpeakerHub':
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address] =  dev['name']
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSpeakerHub(self.poly, address, address, name,  self.yoAccess, dev )
                    
                    self.msgList=[]
                    logging.debug('Checking NBR_TTS')
                    if 'NBR_TTS' in self.Parameters:
                        self.nbrTTS = int(self.Parameters['NBR_TTS'])
                        logging.debug('NBR_TTS found: {}'.format(self.nbrTTS))
                    else:
                        self.nbrTTS = 1
                        self.Parameters['NBR_TTS'] = self.nbrTTS 
                    self.yoAccess.TtsMessages = {}
                    for n in range(0,self.nbrTTS):
                        index = self.TTSstr+str(n)
                        if index not in self.Parameters:
                            self.Parameters[index] = 'Message '+str(n)
                        self.yoAccess.TtsMessages[n] = self.Parameters[index]
                        logging.info ('Adding {} to Parameters'.format(self.Parameters[index] ))
                    #self.yoAccess.writeTtsFile()
                    logging.info('TTS messages : {}'.format(self.yoAccess.TtsMessages))
                    logging.info('Updating profile files ')
                    if udiProfileHandler.udiTssProfileUpdate(self.yoAccess.TtsMessages):
                        self.poly.Notices['tts'] = 'Speaker hub messages updated - PoI/ISY need to be restarted to take effect'
                    self.poly.updateProfile()   
                    for nbr in range(0,self.nbrTTS):
                        index = 'TTS'+str(nbr)
                        if index not in self.Parameters:
                            self.Parameters[index] = index
                        self.yoAccess.TtsMessages[nbr] = self.Parameters[index]

                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))                        
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)  

                elif dev['type'] == 'Switch':
                    name = dev['deviceId'][-14:]  #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address] =  dev['name']
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSwitch(self.poly, address, address, name,  self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)

                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)

                elif dev['type'] == 'Dimmer':
                    name = dev['deviceId'][-14:]  #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoDimmer(self.poly, address, address, name,  self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                    

                elif dev['type'] == 'THSensor':      
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoTHsensor(self.poly, address, address, name, self.yoAccess, dev)
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)
          
                elif dev['type'] == 'MultiOutlet':
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']
                    config = {}
                    if  'YS6802' in dev['modelName']:
                        config['usb'] = 0
                        config['outlet'] = 2
                    elif 'YS6801' in dev['modelName']:
                        config['usb'] = 1
                        config['outlet'] = 4
                    else:
                        logging.error('Unsupported MultiOutlet devicve : {}'.format(dev['modelName']))
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoMultiOutlet(self.poly, address, address, name, self.yoAccess, dev, config )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                     
                           
                elif dev['type'] == 'DoorSensor':
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoDoorSensor(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      
                         
                elif dev['type'] == 'Manipulator':
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoManipulator(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      
                          
                elif dev['type'] == 'MotionSensor':     
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoMotionSensor(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      

                elif dev['type'] == 'VibrationSensor':     
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoVibrationSensor(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                     
                            
                elif dev['type'] == 'Outlet':     
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoOutlet(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      
            
                elif dev['type'] == 'GarageDoor': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoGarageDoor(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      
            
                elif dev['type'] == 'Finger':
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoGarageFinger(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                                                       

                elif dev['type'] == 'Lock': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    temp = udiYoLock(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                        

                elif dev['type'] == 'InfraredRemoter': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoInfraredRemoter(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)      
                                 
                elif dev['type'] == 'LeakSensor': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoLeakSensor(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)       

                elif dev['type'] == 'COSmokeSensor': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoCOSmokeSensor(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)       


                elif dev['type'] == 'PowerFailureAlarm': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoPowerFailSenor(self.poly, address, address, name, self.yoAccess, dev )

                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                  

                elif dev['type'] == 'SmartRemoter': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSmartRemoter(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)


                elif dev['type'] == 'Siren': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSiren(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)


                elif dev['type'] == 'WaterMeterController': 
                    name = dev['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    address = self.poly.getValidAddress(name)
                    if address in self.Parameters:
                        name = self.Parameters[address]
                    else:
                        name = dev['name']
                        name = self.poly.getValidName(name)
                        self.Parameters[address]=  dev['name']                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoWaterMeterController(self.poly, address, address, name, self.yoAccess, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                        
                                                
            else:
                logging.debug('Currently unsupported device : {}'.format(dev['type'] ))
        time.sleep(1)
        # need to go through nodes to see if there are nodes that no longer exist in device list                
        logging.debug('assigned addresses nodes  :{} - {}'.format(len(self.assigned_addresses), self.assigned_addresses))
        logging.debug('Nodes in Nodeserver - before cleanup: {} - {}'.format(len(self.nodes_in_db),self.nodes_in_db))
        for nde in range(0, len(self.nodes_in_db)):
            node = self.nodes_in_db[nde]
            logging.debug('Scanning db for extra nodes : {}'.format(node))
            if node['address']  not in self.assigned_addresses and node['isPrimary'] == 1: # do not remove sub-nodes
                logging.debug('Removing node : {} {}'.format(node['name'], node))
                self.poly.delNode(node['address'])
                
        # checking params for erassed nodes
        self.poly.updateProfile()
        self.pollStart = True

    def stop(self):
        try:
            logging.info('Stop Called:')
            #self.yoAccess.writeTtsFile() #save current TTS messages

            self.node.setDriver('ST', 0, True, True)

            if self.yoAccess:
                self.yoAccess.shut_down()
            self.poly.stop()
            exit()
        except Exception as E:
            logging.error('Stop Exception : {}'.format(E))
            if self.yoAccess:
                self.yoAccess.shut_down()
            self.poly.stop()

    def heartbeat(self):
        logging.debug('heartbeat: ' + str(self.hb))
        if self.yoAccess.online:
            self.node.setDriver('ST', 1)
            if self.hb == 0:
                self.reportCmd('DON',2)
                self.hb = 1
            else:
                self.reportCmd('DOF',2)
                self.hb = 0
        else:
            self.node.setDriver('ST', 0)

    def checkNodes(self):
        logging.info('Updating Nodes')
        deviceList = self.yoAccess.getDeviceList()
        nodes = self.poly.getNodes()
        for dev in deviceList:
            devList = []
            name = dev['deviceId'][-14:]
            if name not in nodes:
                #device was likely off line during inital instellation or added afterwards
                devList.append(dev)
                self.addNodes(devList)


    def systemPoll (self, polltype):
        if self.pollStart:
            logging.debug('System Poll executing: {}'.format(polltype))
            if self.yoAccess.online:
                self.node.setDriver('ST', 1)
                if 'longPoll' in polltype:
                    #Keep token current
                    #self.node.setDriver('GV0', self.temp_unit, True, True)
                    try:
                        #if not self.yoAccess.refresh_token(): #refresh failed
                        #    while not self.yoAccess.request_new_token():
                        #            time.sleep(60)
                        #logging.info('Updating device status')
                        nodes = self.poly.getNodes()
                        
                        for nde in nodes:
                            if nde != 'setup':   # but not the controller node
                                nodes[nde].checkOnline()
                                logging.debug('longpoll {}'.format(nde))
                                time.sleep(5) # need to limit calls to 100 per  5 min - using 5 to allow other calls - updating is not critical
                    except Exception as e:
                        logging.debug('Exeption occcured during systemPoll : {}'.format(e))
                        #self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
                        #deviceList = self.yoAccess.getDeviceList()           
                    
                if 'shortPoll' in polltype:
                    self.heartbeat()

                    nodes = self.poly.getNodes()
                    for nde in nodes:
                        if nde != 'setup':   # but not the controller node
                            nodes[nde].checkDataUpdate()
                            logging.debug('shortpoll {}'.format(nde))
                            time.sleep(4)  # need to limit calls to 100 per  5 min - using 4 to allow other calls
            else:
                self.node.setDriver('ST', 0, True, True)
                


    def handleLevelChange(self, level):
        logging.info('New log level: {}'.format(level))
        logging.setLevel(level['level'])



    def handleParams (self, userParam ):
        logging.debug('handleParams')
        supportParams = ['YOLINKV2_URL', 'TOKEN_URL','MQTT_URL', 'MQTT_PORT', 'UAID', 'SECRET_KEY', 'NBR_TTS', 'TEMP_UNIT' ]
        self.Parameters.load(userParam)

       
        self.poly.Notices.clear()

        try:
            if 'YOLINKV2_URL' in userParam:
                self.yolinkV2URL = userParam['YOLINKV2_URL']
            #else:
            #    self.poly.Notices['yl2url'] = 'Missing YOLINKV2_URL parameter'
            #    self.yolinkV2URL = ''

            if 'TOKEN_URL' in userParam:
                self.tokenURL = userParam['TOKEN_URL']
            #else:
            #    self.poly.Notices['turl'] = 'Missing TOKEN_URL parameter'
            #    self.tokenURL = ''

            if 'MQTT_URL' in userParam:
                self.mqttURL = userParam['MQTT_URL']
            #else:
            #    self.poly.Notices['murl'] = 'Missing MQTT_URL parameter'
            #    self.mqttURL = ''

            if 'MQTT_PORT' in userParam:
                self.mqttPort = userParam['MQTT_PORT']
            #else:
            #    self.poly.Notices['mport'] = 'Missing MQTT_PORT parameter'
            #    self.mqttPort = 0

            if 'TEMP_UNIT' in userParam:
                self.temp_unit = self.convert_temp_unit(userParam['TEMP_UNIT'])
            else:
                self.temp_unit = 0

            if 'UAID' in userParam:
                self.uaid = userParam['UAID']
            else:
                self.poly.Notices['uaid'] = 'Missing UAID parameter'
                self.uaid = ''

            if 'SECRET_KEY' in userParam:
                self.secretKey = userParam['SECRET_KEY']
            else:
                self.poly.Notices['sk'] = 'Missing SECRET_KEY parameter'
                self.secretKey = ''

            if 'NBR_TTS' in userParam:
                self.nbrTTS = int(userParam['NBR_TTS'])
              
                #self.yoAccess.writeTtsFile()    
                
            if 'DEBUG_EN' in userParam:
                self.debug = True

            if 'CALLS_PER_MIN' in userParam:
                self.nbr_API_calls = int(userParam['CALLS_PER_MIN'])
         
            if 'DEV_CALLS_PER_MIN' in userParam:
                self.nbr_dev_API_calls = int(userParam['DEV_CALLS_PER_MIN'])   
            
            nodes = self.poly.getNodes()
            #logging.debug('nodes: {}'.format(nodes))
            for nde in nodes:
                #logging.debug('node : {}'.format(nde))
                if nde in userParam:

                    user_param_name = userParam[nde]
                    temp_node = nodes[nde]
                    #logging.debug('User param name : {}, node name {}'.format(user_param_name, temp_node.name))
                    if user_param_name != temp_node.name:
                        temp_node.rename(user_param_name)
                        logging.info('Renaming node {} to {}'.format(nde, temp_node.name))




            #    if param not in supportParams:
            #        del self.Parameters[param]
            #        logging.debug ('erasing key: ' + str(param))

            self.handleParamsDone = True


        except Exception as e:
            logging.debug('Error: {} {}'.format(e, userParam))

    '''
    def set_t_unit(self, command ):
        logging.info('set_t_unit ')
        unit = int(command.get('value'))
        if unit >= 1 and unit <= 3:
            self.temp_unit = unit
            #self.node.setDriver('GV0', self.temp_unit, True, True)
    '''

    id = 'setup'
    #commands = {
    #            'TEMPUNIT': set_t_unit,
    #            }

    drivers = [
            {'driver': 'ST', 'value':1, 'uom':25},
           #{'driver': 'GV20', 'value':99, 'uom':25},
           ]


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])


        polyglot.start(version)

        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)