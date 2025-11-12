#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""

import sys
import time
#from apscheduler.schedulers.background import BackgroundScheduler
from yoLink_init_V4 import YoLinkInitPAC

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

#version = '0.0.0
from udiCommonLib import version

class YoLinkSetup (udi_interface.Node):
    from udiYolinkLib import my_setDriver, node_queue, wait_for_node_done, updateEpochTime, convert_temp_unit, convert_water_unit
    from udiCommonLib import systemPoll, addNodes, heartbeat, configDoneHandler, checkNodes, handleLevelChange
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
        self.local_client_id = None
        self.local_client_secret = None
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
        self.yoLocal = None
        self.yoAccess = None
        
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



    def parse_device_lists (self, cloud_list = [], local_list =[]) -> list:
        logging.debug(f'parse_device_lists {cloud_list} {local_list}')
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
        
        #logging.setLevel(30)
        while not self.nodeDefineDone and self.handleParamsDone:
            time.sleep(1)
            logging.debug ('waiting for inital node to get created')

        #self.supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
        #                        'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
        #                        'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock' , 'LockV2', 'Dimmer', 'InfraredRemoter',
        #                        'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren', 'WaterMeterController',
        #                        'WaterDepthSensor', 'WaterMeterMultiController']
        logging.info (f'Access mode : {self.access_mode}')
        self.updateEpochTime()
        logging.debug(f'credentials {self.access_mode} {self.uaid} {self.secretKey} {self.local_client_id} {self.local_client_secret}')
        if 'cloud' in self.access_mode:
            if self.uaid == None or self.uaid == '' or self.secretKey==None or self.secretKey=='':
                logging.error('UAID and secretKey must be provided to start node server')
                self.poly.Notices['cloud'] = 'UAID and secretKey must be provided to start node server in cloud or hybrid mode'
                exit() 
            else:
                logging.debug(f'initialiing Cloud mode {self.uaid} {self.secretKey}')
                self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey )
        if 'local' in self.access_mode:
            if self.local_client_id == None or self.local_client_id == '' or self.local_client_secret==None or self.local_client_secret=='':
                logging.error('Client ID  and Client Secret must be provided to start node server')
                self.poly.Notices['local'] = 'Client ID  and Client Secret must be provided to start node server in local or hybrid mode'
                exit() 
            else:
                tokenURL = self.local_URL+'/open/yolink/token'
                apiURL = self.local_URL+'/open/yolink/v2/api'
                logging.debug(f'initializing Local mode {self.local_client_id} {self.local_client_secret} {tokenURL} {apiURL} {self.local_ip} {self.local_MQTT_port} {self.subnet_id} ')
                self.yoLocal = YoLinkInitPAC (self.local_client_id, self.local_client_secret, tokenURL, apiURL, self.local_ip, self.local_MQTT_port, self.subnet_id  )
   

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

        if 'WATER_UNIT' in self.Parameters:
            self.water_unit = self.convert_water_unit(self.Parameters['WATER_UNIT'])
        else:
            self.water_unit = 0  
            self.Parameters['WATER_UNIT'] = 'L'
            logging.debug('WATER_UNIT: {}'.format(self.water_unit ))
        if self.yoAccess:
            self.yoAccess.set_water_unit(self.water_unit )
        if self.yoLocal:
            self.yoLocal.set_water_unit(self.water_unit )   

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

            self.deviceList = self.addNodes(self.deviceList)
        else:
            self.my_setDriver('ST', 0)

            
        #self.poly.updateProfile()        
        #self.scheduler = BackgroundScheduler()
        #self.scheduler.add_job(self.display_update, 'interval', seconds=self.display_update_sec)
        #self.scheduler.start()
        #self.updateEpochTime()
        
    def stop(self):
        try:
            logging.info('Stop Called:')
            #self.yoAccess.writeTtsFile() #save current TTS messages

            self.my_setDriver('ST', 0)

            if self.yoAccess:
                self.yoAccess.shut_down()
            if self.yoLocal:
                self.yoLocal.shut_down()

            exit()
        except Exception as e:
            logging.error(f'Stop Exception : {e}')
            if self.yoAccess:
                self.yoAccess.shut_down()
            if self.yoLocal:
                self.yoLocal.shut_down()

            self.poly.stop()


    

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
            if 'WATER_UNIT' in userParam:
                self.water_unit = self.convert_water_unit(userParam['WATER_UNIT'])
            else:
                self.water_unit = 3
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
                mode = userParam['MODE'].lower()
                if mode in ['local']:
                    self.access_mode = ['local']
                elif mode in ['cloud']:
                    self.access_mode = ['cloud']
                elif mode in ['hybrid']:
                    self.access_mode = ['local', 'cloud']
                else:
                    self.poly.Notices['mode'] = 'Missing MODE parameter'

            logging.debug('Access mode set to: {}'.format(self.access_mode))
            if 'LOCAL_CLIENT_ID' in userParam:
                self.local_client_id = userParam['LOCAL_CLIENT_ID']
            else:
                self.local_client_id = None
        
            if 'LOCAL_CLIENT_SECRET' in userParam:
                self.local_client_secret = userParam['LOCAL_CLIENT_SECRET']
            else:
                self.local_client_secret = None

            if 'SUBNET_ID' in userParam:
                self.subnet_id = userParam['SUBNET_ID']
            else:
                self.subnet_id = None
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