#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""

import sys
import time
#from apscheduler.schedulers.background import BackgroundScheduler


from yoLink_init_V3 import YoLinkInitPAC
#from yoLink_local_init_V3 import YoLinkInitLocal
from udiYoSwitchV2 import udiYoSwitch
#from udiYoSwitchV3H import udiYoSwitchL
from udiYoSwitchSecV2 import udiYoSwitchSec
from udiYoSwitchPwrSecV2 import udiYoSwitchPwrSec
from udiYoTHsensorV3 import udiYoTHsensor 
from udiYoWaterDeptV3 import udiYoWaterDept 
from udiYoGarageDoorCtrlV2 import udiYoGarageDoor
from udiYoGarageFingerCtrlV2 import udiYoGarageFinger
from udiYoMotionSensorV3 import udiYoMotionSensor
from udiYoLeakSensorV3 import udiYoLeakSensor
from udiYoCOSmokeSensorV3 import udiYoCOSmokeSensor
from udiYoDoorSensorV3 import udiYoDoorSensor
from udiYoOutletV2 import udiYoOutlet
from udiYoOutletPwrV2 import udiYoOutletPwr
from udiYoMultiOutletV2 import udiYoMultiOutlet
from udiYoManipulatorV2 import udiYoManipulator
from udiYoSpeakerHubV2 import udiYoSpeakerHub
from udiYoLockV2 import udiYoLock
from udiYoInfraredRemoterV2 import udiYoInfraredRemoter
from udiYoDimmerV2 import udiYoDimmer
from udiYoVibrationSensorV3 import udiYoVibrationSensor
from udiYoSmartRemoterV3 import udiYoSmartRemoter
from udiYoPowerFailV3 import udiYoPowerFailSenor
from udiYoSirenV2 import udiYoSiren
from udiYoWaterMeterControllerV2 import udiYoWaterMeterController
#from udiYoHubV2 import udiYoHub
import udiProfileHandler

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)




version = '0.0.7'


class YoLinkSetup (udi_interface.Node):
    from  udiYolinkLib import my_setDriver,node_queue, wait_for_node_done
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
        self.yoLocal = None
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
        self.display_update_sec=60
        self.uaid = ''
        self.secretKey = ''
        self.nbrTTS = None
        self.client_id = None
        self.client_secret = None
        self.local_ip = ''
        self.local_port = ':1080'
        self.local_URL = ''
        self.local_MQTT_port = 18080
        
        logging.setLevel(10)
        logging.info(f'Version {version}')
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
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
        self.my_setDriver('ST', 0)
        self.my_setDriver('GV1', 0)
        self.assigned_addresses = []
        self.assigned_addresses.append(self.address)   
        logging.debug('YoLinkSetup init DONE')
        self.nodeDefineDone = True


    def convert_temp_unit(self, tempStr):
        if tempStr.capitalize()[:1] == 'F':
            return(1)
        elif tempStr.capitalize()[:1] == 'K':
            return(2)
        else:
            return(0)

    def configDoneHandler(self):
        # We use this to discover devices, or ask to authenticate if user has not already done so
        self.poly.Notices.clear()
        logging.info('configDoneHandler called')
        #self.myNetatmo.updateOauthConfig()
        self.nodes_in_db = self.poly.getNodesFromDb()
        logging.debug('Nodes in Nodeserver - before cleanup: {} - {}'.format(len(self.nodes_in_db),self.nodes_in_db))
        self.configDone = True


    def parse_device_lists (self, cloud_list, local_list) -> list:
        logging.debug('parse_device_lists')
#[{'deviceId': 'd88b4c010004b251', 'deviceUDID': '49ddf0bc10664337a834310b63850ed3', 'name': 'Motion Sensor', 'token': 'BBBFA35BC4870C56325A7A30C72D22CC', 'type': 'MotionSensor', 'parentDeviceId': None, 'modelName': 'YS7805-UC', 'serviceZone': 'us_west_1'
        device_list = []
        
        cloud_devs = {}
        for dev in cloud_list:
            cloud_devs[dev['deviceId']] = dev       
        local_devs = {}
        for dev in local_list:
            local_devs[dev['deviceId']] = dev
    
        for dev in local_list:
                dev['access'] = 0
                if dev['deviceId'] in cloud_devs:
                    dev['modelName'] = cloud_devs[dev['deviceId']]['modelName'] 
                device_list.append(dev)        
        for dev in cloud_list:
            if dev['deviceId'] not in local_devs:
                dev['access'] = 1
                device_list.append(dev)

        logging.debug(f'Resulting Device List {device_list}')
        return(device_list)

    def start (self):
        logging.info('Executing start - udi-YoLink')
        logging.info ('Access using PAC/UAC')
        #logging.setLevel(30)
        while not self.nodeDefineDone and self.handleParamsDone:
            time.sleep(1)
            logging.debug ('waiting for inital node to get created')

        self.supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
                                'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
                                'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock' , 'LockV2', 'Dimmer', 'InfraredRemoter',
                                'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren', 'WaterMeterController',
                                'WaterDepthSensor']
        
        #self.supportedYoTypes = ['Switch','VibrationSensor', 'Outlet']
        self.supportedLocalYoTypes = self.supportedYoTypes 
        #self.supportedYoTypes = [ 'WaterDepthSensor', 'VibrationSensor']    
        self.updateEpochTime()
        logging.debug(f'credentials {self.access_mode} {self.uaid} {self.secretKey} {self.client_id} {self.client_secret}')
        if self.access_mode in ['cloud', 'hybrid']:
            if self.uaid == None or self.uaid == '' or self.secretKey==None or self.secretKey=='':
                logging.error('UAID and secretKey must be provided to start node server')
                self.poly.Notices['cloud'] = 'UAID and secretKey must be provided to start node server in cloud or hybrid mode'
                exit() 
            else:
                self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey )
        if self.access_mode in ['local', 'hybrid']:
            if self.client_id == None or self.client_id == '' or self.client_secret==None or self.client_secret=='':
                logging.error('Client ID  and Client Secret must be provided to start node server')
                self.poly.Notices['local'] = 'Client ID  and Client Secret must be provided to start node server in local or hybrid mode'
                exit() 
            else:
                tokenURL = self.local_URL+'/open/yolink/token'
                apiURL = self.local_URL+'/open/yolink/v2/api'
                self.yoLocal = YoLinkInitPAC (self.client_id, self.client_secret, tokenURL, apiURL, self.local_ip, self.local_MQTT_port, self.subnet_id  )
   

                       
        #if self.client_id in [None, ''] or self.client_secret  in [None, ''] or self.local_ip in [None, '']:
        #    logging.error('ClientAcces, ClientSecret and localIPmust be provided to start node server')
        #    self.poly.Notices['local_access'] = 'ClientAcces, ClientSecret and localIP must be specified in configuration'
        #    exit() 
            
        #else:
        #     self.yoLocal = YoLinkInitLocal(self.client_id, self.client_secret, self.local_URL:'+self.local_port, )
        #     if self.yoLocal:
        #        self.local_access = True
        #        self.deviceList = self.yoLocal.retrieve_device_list()
        #        self.addLocalNodes(self.deviceList )

        
        
        
        
        #exit()


        #if self.uaid == None or self.uaid == '' or self.secretKey==None or self.secretKey=='':
        #    logging.error('UAID and secretKey must be provided to start node server')
        #    exit() 

        #self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
        if self.yoAccess or self.yoLocal:
            self.my_setDriver('ST', 0)
        if 'TEMP_UNIT' in self.Parameters:
            self.temp_unit = self.convert_temp_unit(self.Parameters['TEMP_UNIT'])
        else:
            self.temp_unit = 0  
            self.Parameters['TEMP_UNIT'] = 'C'
            logging.debug('TEMP_UNIT: {}'.format(self.temp_unit ))

        if self.yoAccess:
            self.yoAccess.set_temp_unit(self.temp_unit )
        if self.yoLocal:
            self.yoLocal.set_temp_unit(self.temp_unit )        

        if 'DEBUG_EN' in self.Parameters:
            self.debug = self.Parameters['DEBUG_EN']
        else:
            self.debug = False
        if self.yoAccess:
            self.yoAccess.set_debug(self.debug)
        if self.yoLocal:
            self.yoLocal.set_debug(self.debug)                 
        
        if 'CALLS_PER_MIN' in self.Parameters:
            self.nbr_API_calls = self.Parameters['CALLS_PER_MIN']
            self.nbr_dev_API_calls = self.Parameters['DEV_CALLS_PER_MIN']
        if self.yoAccess:
            self.yoAccess.set_api_limits(self.nbr_API_calls, self.nbr_dev_API_calls)          
        
        # NEED TO DETERMINE IF LOCAL HUB EXISTS AND THEN GET LIST FROM THAT AS WELL 
        
        
        deviceListCloud=[]
        deviceListLocal=[]
        if self.yoAccess:  # get cloud and local devices
            self.yoAccess.retrieve_device_list()
            deviceListCloud = self.yoAccess.getDeviceList()
        
            #self.deviceList = self.yoAccess.get_device_list()

        if self.yoLocal: #get only local devices 
            self.yoLocal.retrieve_device_list()
            deviceListLocal = self.yoLocal.getDeviceList()

        self.deviceList = self.parse_device_lists(deviceListCloud, deviceListLocal )

        logging.debug('{} devices detected : {}'.format(len(self.deviceList), self.deviceList) )
        if self.yoAccess or self.yoLocal:
            self.my_setDriver('ST', 1)

            self.addNodes(self.deviceList)
        else:
            self.my_setDriver('ST', 0)
        #self.poly.updateProfile()
        
        #self.scheduler = BackgroundScheduler()
        #self.scheduler.add_job(self.display_update, 'interval', seconds=self.display_update_sec)
        #self.scheduler.start()
        #self.updateEpochTime()

    def addNodes (self, deviceList):
        for dev in deviceList:
            logging.debug(f'DEVICE ANALYZED {dev}')
            if dev['type']  in self.supportedYoTypes:
                dev_access = None
                model = None
                nodename = str(dev['deviceId'][-14:])
                address = self.poly.getValidAddress(nodename)
                #if 'modelName' in dev:
                #    model = str(dev['modelName'][:6])
                if dev['access'] == 0:
                    logging.debug('Local Access selected {}'.format(dev['name']))
                    dev_access = self.yoLocal
                else:
                    logging.debug('Cloud Access selected {}'.format(dev['name']))
                    dev_access = self.yoAccess
                #if address in self.Parameters:
                #    name = self.Parameters[address]
                #else:
                name = dev['name']
                name = self.poly.getValidName(name)
                self.Parameters[address] =  dev['name']

                logging.info('adding/checking device : {} - {} {}'.format(dev['name'], dev['type'], dev['access'] ))
                if dev['type'] == 'Hub':     
                    logging.info('Hub not added - ISY cannot do anything useful with it')    
                    #if  model in ['YS1606',]:
                    #    self.local_access = True
                    #    self.yoAccess.initializeLocalAccess(self.client_id, self.client_secret, self.local_ip)
                    #    self.poly.Notices['local_access'] = 'Local Hub detected - Enabling local access'


                elif dev['type'] in ['SpeakerHub']:

                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSpeakerHub(self.poly, address, address, name,  dev_access, dev )                    
                    #self.msgList=[]
                    logging.debug('Checking NBR_TTS')
                    if 'NBR_TTS' in self.Parameters:
                        self.nbrTTS = int(self.Parameters['NBR_TTS'])
                        logging.debug('NBR_TTS found: {}'.format(self.nbrTTS))
                    else:
                        self.nbrTTS = 1
                        self.Parameters['NBR_TTS'] = self.nbrTTS 
                    dev_access.TtsMessages = {}
                    for n in range(0,self.nbrTTS):
                        index = self.TTSstr+str(n)
                        if index not in self.Parameters:
                            self.Parameters[index] = 'Message '+str(n)
                        dev_access.TtsMessages[n] = self.Parameters[index]
                        logging.info ('Adding {} to Parameters'.format(self.Parameters[index] ))
                    #self.yoAccess.writeTtsFile()
                    logging.info('TTS messages : {}'.format(dev_access.TtsMessages))
                    logging.info('Updating profile files ')
                    if udiProfileHandler.udiTssProfileUpdate(dev_access.TtsMessages):
                        self.poly.Notices['tts'] = 'Speaker hub messages updated - PoI/ISY need to be restarted to take effect'
                    self.poly.updateProfile()   
                    for nbr in range(0,self.nbrTTS):
                        index = 'TTS'+str(nbr)
                        if index not in self.Parameters:
                            self.Parameters[index] = index
                        dev_access.TtsMessages[nbr] = self.Parameters[index]

                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))                        
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)  

                elif dev['type'] in ['Switch']:
                    model = None
                    if  model in ['YS5708', 'YS5709']:
                        logging.info('Adding swithSec device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                        temp = udiYoSwitchSec(self.poly, address, address, name,  dev_access, dev )
                    elif  model in ['YS5716']:
                        logging.info('Adding swithPwr device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                        temp = udiYoSwitchPwrSec(self.poly, address, address, name,  dev_access, dev )
                    else:
                        logging.info('Adding switch device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                        temp = udiYoSwitch(self.poly, address, address, name,  self.yoLocal, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)

                elif dev['type'] in ['Dimmer']:
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoDimmer(self.poly, address, address, name,  dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                    

                elif dev['type'] in ['THSensor']:      
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoTHsensor(self.poly, address, address, name, dev_access, dev)
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)
          
                elif dev['type'] in ['MultiOutlet']:
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoMultiOutlet(self.poly, address, address, name, dev_access, dev)
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                     
                           
                elif dev['type'] in ['DoorSensor']:                 
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoDoorSensor(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      
                         
                elif dev['type'] in ['Manipulator']:              
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoManipulator(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      
                          
                elif dev['type'] in ['MotionSensor']:              
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoMotionSensor(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      

                elif dev['type'] in  ['VibrationSensor']:                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoVibrationSensor(self.poly, address, address, name, self.yoLocal, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                     
                            
                elif dev['type'] in  ['Outlet']:     
                    if  model in ['YS6803','YS6602']:
                        logging.info('Adding device w. power {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                        temp = udiYoOutletPwr(self.poly, address, address, name, dev_access, dev )
                    else:
                        logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                        temp = udiYoOutlet(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      
            
                elif dev['type'] in ['GarageDoor']:                 
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoGarageDoor(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                      
            
                elif dev['type'] in ['Finger']:                   
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoGarageFinger(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                                                       

                elif dev['type'] in ['Lock', 'LockV2']:        
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                     
                    temp = udiYoLock(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                        

                elif dev['type'] == 'InfraredRemoter':           
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoInfraredRemoter(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)      
                                 
                elif dev['type'] in ['LeakSensor']:                 
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoLeakSensor(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)     

                elif dev['type'] in ['WaterDepthSensor']:   #  YS7905-UC           
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoWaterDept(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)     

                elif dev['type'] in ['COSmokeSensor']:                
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoCOSmokeSensor(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)       

                elif dev['type'] in ['PowerFailureAlarm']:                 
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoPowerFailSenor(self.poly, address, address, name, dev_access, dev )

                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)                  

                elif dev['type'] in ['SmartRemoter']:                    
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSmartRemoter(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)

                elif dev['type'] in ['Siren']:                  
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSiren(self.poly, address, address, name, dev_access, dev )
                    while not temp.node_ready:
                        logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                        time.sleep(4)
                    for adr in temp.adr_list:
                        self.assigned_addresses.append(adr)

                elif dev['type'] in ['WaterMeterController']:                 
                    logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoWaterMeterController(self.poly, address, address, name, dev_access, dev )
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
        while not self.configDone:
            logging.info('Waiting for ')
        logging.debug('Nodes in Nodeserver - before cleanup: {} - {}'.format(len(self.nodes_in_db),self.nodes_in_db))
        for nde, node  in enumerate(self.nodes_in_db):
            #node = self.nodes_in_db[nde]
            logging.debug('Scanning db for extra nodes : {}'.format(node))
            if node['primaryNode'] not in self.assigned_addresses:
                logging.debug('Removing node : {} {}'.format(node['name'], node))

                if node['address'] in self.Parameters:
                    logging.debug(f'self.Parameters {self.Parameters}')
                    logging.debug('node {}'.format(node['address']))
                    logging.debug('Params {}'.format(self.Parameters[node['address']]))
                    self.Parameters.delete(node['address'])
                self.poly.delNode(node['address'])

        time.sleep(1)
        # checking params for erassed nodes
        self.poly.updateProfile()
        self.yolink_nodes = self.poly.getNodes()
        self.my_setDriver('GV1', 1)
        self.pollStart = True

    def stop(self):
        try:
            logging.info('Stop Called:')
            #self.yoAccess.writeTtsFile() #save current TTS messages

            self.my_setDriver('ST', 0)

            if self.yoAccess:
                self.yoAccess.shut_down()
            if self.yoLocal:
                self.yoLocal.shut_down()
            self.poly.stop()
            exit()
        except Exception as e:
            logging.error(f'Stop Exception : {e}')
            #if self.yoAccess:
            #    self.yoAccess.shut_down()

            self.poly.stop()

    def heartbeat(self):
        logging.debug('heartbeat: ' + str(self.hb))
        connected = False
        if self.access_mode in ['hybrid', 'online']:
            if self.yoAccess.online:
                connected = True
        if self.access_mode in ['hybrid', 'local']:
            if self.yoLocal.online:
                connected = True
        if connected:
            self.my_setDriver('ST', 1)
            if self.hb == 0:
                self.reportCmd('DON',2)
                self.hb = 1
            else:
                self.reportCmd('DOF',2)
                self.hb = 0
        else:
            self.my_setDriver('ST', 0)

    #def display_update(self):
    #    logging.debug('display_update')
    #    self.updateEpochTime()
    #    for nde in self.yolink_nodes:
    #        if nde != 'setup':   # but not the controller node
    #            self.yolink_nodes[nde].updateLastTime()

    #def checkNodes(self):
    #    logging.info('Updating Nodes')
    #    deviceList = self.yoAccess.getDeviceList()
    #    nodes = self.poly.getNodes()
    #    for dev in deviceList:
    #        devList = []
    #        name = dev['deviceId'][-14:]
    #        if name not in nodes:
    #            #device was likely off line during inital instellation or added afterwards
    #            devList.append(dev)
    #            self.addNodes(devList)


    def systemPoll (self, polltype):
        if self.pollStart:
            logging.debug('System Poll executing: {}'.format(polltype))
            connected = False
            if self.access_mode in ['hybrid', 'online']:
                if self.yoAccess.online:
                    connected = True
            if self.access_mode in ['hybrid', 'local']:
                if self.yoLocal.online:
                    connected = True
            if connected:
                self.updateEpochTime()
                self.my_setDriver('ST', 1)
                if 'longPoll' in polltype:
                    #Keep token current
                    #self.my_setDriver('GV0', self.temp_unit)
                    try:
                        #if not self.yoAccess.refresh_token(): #refresh failed
                        #    while not self.yoAccess.request_new_token():
                        #            time.sleep(60)
                        #logging.info('Updating device status')
                        #nodes = self.poly.getNodes()
                        
                        for nde in self.yolink_nodes:
                            if nde != 'setup':   # but not the controller node
                                self.yolink_nodes[nde].checkOnline()
                                logging.debug('longpoll {}'.format(nde))
                                time.sleep(5) # need to limit calls to 100 per  5 min - using 5 to allow other calls - updating is not critical
                    except Exception as e:
                        logging.error('Exeption occcured during systemPoll : {}'.format(e))
                        #self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
                        #deviceList = self.yoAccess.getDeviceList()           
                    
                if 'shortPoll' in polltype:
                    self.heartbeat()

                    #nodes = self.poly.getNodes()
                    #for nde in self.yolink_nodes:
                    #    if nde != 'setup':   # but not the controller node
                    #        self.yolink_nodes[nde].checkDataUpdate()
                    #        logging.debug('shortpoll {}'.format(nde))
                            # no API calls so no need to spread out 
                            #time.sleep(4)  # need to limit calls to 100 per  5 min - using 4 to allow other calls
            #else:
            #    self.my_setDriver('ST', 0)
                


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
                self.uaid = str(userParam['UAID'])
                self.uaid = self.uaid.strip()
            else:
                self.poly.Notices['uaid'] = 'Missing UAID parameter'
                self.uaid = ''

            if 'SECRET_KEY' in userParam:
                self.secretKey = str(userParam['SECRET_KEY'])
                self.secretKey = self.secretKey.strip()
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

            # LOCAL ACCESS
            if 'MODE'in userParam:
                mode = userParam['MODE']
                if mode in ['local', 'cloud', 'hybrid']:
                    self.access_mode = mode
                else:
                    self.poly.Notices['mode'] = 'Missing MODE parameter'
            if 'LOCAL_CLIENT_ID' in userParam:
                self.client_id = userParam['LOCAL_CLIENT_ID']
            else:
                self.client_id = None
        
            if 'LOCAL_CLIENT_SECRET' in userParam:
                self.client_secret = userParam['LOCAL_CLIENT_SECRET']
            else:
                self.client_secret = None

            if 'SUBNET_ID' in userParam:
                self.subnet_id = userParam['SUBNET_ID']
            else:
                self.client_secret = None
            if 'LOCAL_IP' in  userParam:
                self.local_ip = str(userParam['LOCAL_IP'])
                self.local_ip = self.local_ip.strip()
                self.local_URL = 'http://'+self.local_ip+self.local_port
 
            else:
                self.poly.Notices['ck'] = 'Missing LOCAL_IP parameter'
                self.secretKey = 'x.x.x.x'

            
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


    def updateEpochTime(self, command=None ):
        logging.info('updateEpochTime ')
        #unit = int(command.get('value'))
        self.my_setDriver('TIME', int(time.time()))


    id = 'setup'
    commands = {
                #'EPOCHTIME': updateEpochTime,
                }

    drivers = [
            {'driver': 'ST', 'value':0, 'uom':25},
            {'driver': 'GV1', 'value':0, 'uom':25},
            {'driver': 'TIME', 'value':int(time.time()), 'uom':151},
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