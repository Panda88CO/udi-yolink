#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""
from os import truncate
import udi_interface
import sys
import time

from udiYoSwitch import udiYoSwitch
from udiYoTHsensor import udiYoTHsensor 
from udiYoGarageDoor import udiYoGarageDoor
from udiYoMotionSensor import udiYoMotionSensor
from udiYoLeakSensor import udiYoLeakSensor

from yoLinkPACOauth import YoLinkDevices

logging = udi_interface.logging
Custom = udi_interface.Custom
polyglot = None
Parameters = None

client_id = '60dd7fa7960d177187c82039'
client_secret = '3f68536b695a435d8a1a376fc8254e70'
yolinkURL =  'https://api.yosmart.com/openApi' 
yolinkV2URL =  'https://api.yosmart.com/open/yolink/v2/api' 
tokenURL = "https://api.yosmart.com/open/yolink/token"





'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''
class YoLinkSetup (udi_interface.Node):
    def  __init__(self, polyglot, primary, address, name):
        super(YoLinkSetup, self).__init__( polyglot, primary, address, name)  
        
        
        UaID = "ua_D78FFCACB1A8465ABE5279E68E201E7B"
        SecID = "sec_v1_Tuqy3L7UqL/t/R3P5xpcBQ=="
        csid = '60dd7fa7960d177187c82039'
        csseckey = '3f68536b695a435d8a1a376fc8254e70'
        csName = 'Panda88'



        devInfo = { "deviceId": "d88b4c0100034906",
                    "deviceUDID": "e091320786e5447099c8b1c93ce47a60",
                    "name": "S Playground Switch",
                    "token": "7f43fbce-dece-4477-9660-97804b278190",
                    "type": "Switch"
                    }
        devInfo2 =  {
                    "deviceId": "d88b4c01000348a6",
                    "deviceUDID": "187bcd4f373e4a11bcc7d1486cfc7c95",
                    "name": "S Matias Garden",
                    "token": "4a9744d4-4c8e-4b01-a8bb-e84b639d0591",
                    "type": "Switch"
                    }
        outdoorTemp =  {
                "deviceId": "d88b4c010003598f",
                "deviceUDID": "bf9c17dadffd460d8edb233dfc3d7d8f",
                "name": "Temp Humidity Sensor",
                "token": "233cfde3-4282-4356-94f1-af3319b48afb",
                "type": "THSensor"
                }
        poolTemp =  {
                "deviceId": "d88b4c0100037f58",
                "deviceUDID": "c89a3e596c694ea3975449d1f264c0f3",
                "name": "Temperature Sensor",
                "token": "db22f34e-79c8-4984-ab50-5243780591f8",
                "type": "THSensor"
                }      
        winecooler =             {
                "deviceId": "d88b4c0200041f5e",
                "deviceUDID": "7bf50baa02364a8a8c1dbc963f56d217",
                "name": "Temp Humidity Sensor",
                "token": "b6696161-e039-4e5b-b57a-e5338709bc80",
                "type": "THSensor"
            }
        garageDoor = [
                {
                "deviceId": "d88b4c010003281d",
                "deviceUDID": "b408eb2c895e467bac5e8c812ac5fe48",
                "name": "Garage Door Sensor",
                "token": "775852f1-7026-4ca1-a2d1-2c1093aa4c3d",
                "type": "DoorSensor"
                },
                {
                "deviceId": "d88b4c0100038d31",
                "deviceUDID": "99836dc7826b4a469120930eef04efe4",
                "name": "Garage Door Controller",
                "token": "9f565525-67bf-42ae-8acb-307332d6d3a7",
                "type": "GarageDoor"
                 }

                 ]      
        motion =  {
                "deviceId": "d88b4c0200037b09",
                "deviceUDID": "397a811123a44476b898a50db4edd889",
                "name": "Motion Sensor",
                "token": "52b14813-dd4b-4568-966a-51307334a9c2",
                "type": "MotionSensor"
                }
        waterSensor =  {
                "deviceId": "d88b4c0300001596",
                "deviceUDID": "afb6f3f8e2294e44ae35f819c137c8b8",
                "name": "Leak Sensor",
                "token": "b4d750c0-a66b-4b9a-b96b-b2097cbf1e6a",
                "type": "LeakSensor"
                }

        '''
            {
                "deviceId": "d88b4c010002e621",
                "deviceUDID": "5c4a0f90dd3e48cf91c597bc0aba6e7d",
                "name": "Power Strip",
                "token": "65edd0ce-ad2a-445b-8218-2dd024643718",
                "type": "MultiOutlet"
            },
            {
                "deviceId": "d88b4c010003430a",
                "deviceUDID": "ef5f98b9fd694596a411f903df8f564d",
                "name": "YoLink Valve",
                "token": "f9550017-5f30-43e5-bba4-6082f1ebb990",
                "type": "Manipulator"
            },
            {
                "deviceId": "d88b4c01000341c3",
                "deviceUDID": "5e0769573c174be1b6aea67bf9f0ec95",
                "name": "YoLink Valve",
                "token": "54b358e9-5036-4064-8afc-b569ec559827",
                "type": "Manipulator"
            },

            {
                "deviceId": "d88b4c0100029ccf",
                "deviceUDID": "247baa1614714d459e6d27ee3a2d3966",
                "name": "Power Strip",
                "token": "aaa92779-633f-47ab-807d-f0470176521c",
                "type": "MultiOutlet"
            },

            {
                "deviceId": "d88b4c0100029e6e",
                "deviceUDID": "85392d2831884b90a1b186c7f23a81d8",
                "name": "S Deck Light",
                "token": "1267e6bd-0f16-4220-9576-fdb552a73c0f",
                "type": "MultiOutlet"
            },
            {
                "deviceId": "d88b4c02000177a0",
                "deviceUDID": "3a1ddca4536c48ca9a609a8eb07d90b9",
                "name": "S Door Sensor 1",
                "token": "275a6fcc-5e8c-45ca-ad45-ca2c159378f0",
                "type": "DoorSensor"
            },
            {
                "deviceId": "d88b4c01000301db",
                "deviceUDID": "56e4961b5a3246b6a90c23176447d92f",
                "name": "S USB Outlet 1",
                "token": "91a8ba8c-03bf-42c3-a1a8-23de834c7154",
                "type": "Outlet"
            },


        '''
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)

        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
       
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))
        self.hb = 0
      
        
        self.nodeDefineDone = False
        self.longPollCountMissed = 0

        logging.debug('Controller init DONE')
        
        self.poly.ready()
        self.poly.addNode(self)


        self.yoDevices = YoLinkDevices(UaID, SecID)
        self.deviceList = self.yoDevices.getDeviceList()
        logging.debug('{} devices detected'.format(len(self.deviceList)))
        for dev in range(0,len(self.deviceList))
            self.Parameters[self.deviceList[dev]['devideId']] =  self.deviceList[0]['name']


        #rememebr names must be small letters
        udiYoTHsensor(polyglot, 'yotemp', 'yotemp', 'Yolink Wine Twmp', csName, csid, csseckey, winecooler, self.yolinkURL,self.mqttURL, self.mqttPort)
        udiYoSwitch(polyglot, 'yoswitch', 'yoswitch', 'Playground', csName, csid, csseckey, devInfo, self.yolinkURL,self.mqttURL, self.mqttPort )
        udiYoSwitch(polyglot, 'yoswitch2', 'yoswitch2', 'Matias Garden', csName, csid, csseckey, devInfo2, self.yolinkURL,self.mqttURL, self.mqttPort )
        udiYoTHsensor(polyglot, 'yotemp1', 'yotemp1', 'Yolink Pool Temp', csName, csid, csseckey, poolTemp, self.yolinkURL,self.mqttURL, self.mqttPort )
        udiYoTHsensor(polyglot, 'yotemp2', 'yotemp2', 'Yolink Pool Temp', csName, csid, csseckey, outdoorTemp, self.yolinkURL,self.mqttURL, self.mqttPort )
        udiYoGarageDoor(polyglot, 'yogarage1', 'yogarage1', 'Yolink Grage Door', csName, csid, csseckey, garageDoor, self.yolinkURL,self.mqttURL, self.mqttPort )
        udiYoMotionSensor(polyglot, 'yomotion1', 'yomotion1', 'Yolink Motions Sensor', csName, csid, csseckey, motion, self.yolinkURL,self.mqttURL, self.mqttPort )
        udiYoLeakSensor(polyglot, 'yowater1', 'yowater1', 'Yolink Leak Sensor', csName, csid, csseckey, waterSensor, self.yolinkURL,self.mqttURL, self.mqttPort )

        mqtt_URL= 'api.yosmart.com'
        mqtt_port = 8003
        yolink_URL ='https://api.yosmart.com/openApi'


    def handleLevelChange(self, level):
        logging.info('New log level: {}'.format(level))

    def handleParams (self, userParam ):
        logging.debug('handleParams')
        self.Parameters.load(userParam)
        self.poly.Notices.clear()
        csid = '60dd7fa7960d177187c82039'
        csseckey = '3f68536b695a435d8a1a376fc8254e70'
        csName = 'Panda88'
        
        if 'USER_EMAIL' in userParam:
            email = userParam['LOCAL_USER_EMAIL']
        else:
            self.poly.Notices['ue'] = 'Missing User Email parameter'
            email = ''

        if 'USER_PASSWORD' in userParam:
            password = userParam['LOCAL_USER_PASSWORD']
        else:
            self.poly.Notices['up'] = 'Missing User Password parameter'
            password = ''
        
        if 'CSID' in userParam:
            self.csid = userParam['CSID']
        else:
            self.poly.Notices['csid'] = 'Missing csid parameter'
            self.csid = ''

        if 'CSSSECKEY' in userParam:
            self.cssseckey = userParam['CSSSECKEY']
        else:
            self.poly.Notices['cu'] = 'Missing cssSecKey parameter'
            self.csseckey = ''

        if 'CSNAME' in userParam:
            self.csname = userParam['CSNAME']
        else:
            self.poly.Notices['cp'] = 'Missing csName parameter'
            self.csname = ''
    
        if 'UAID' in userParam:
            self.uaid = userParam['UAID']
        else:
            self.poly.Notices['cp'] = 'Missing UAID parameter'
            self.uaid = ''

        if 'SECRET_KEY' in userParam:
            self.secretKey = userParam['SECRET_KEY']
        else:
            self.poly.Notices['cp'] = 'Missing SECRET_KEY parameter'
            self.secretKEy = ''
    
        if 'YOLINK_URL' in userParam:
            self.yolinkURL = userParam['YOLINK_URL']
        else:
            self.poly.Notices['cp'] = 'Missing YOLINK_URL parameter'
            self.yolinkURL = ''

        if 'YOLINKV2_URL' in userParam:
            self.yolinkV2URL = userParam['YOLINKV2_URL']
        else:
            self.poly.Notices['cp'] = 'Missing YOLINKV2_URL parameter'
            self.yolinkV2URL = ''

        if 'TOKEN_URL' in userParam:
            self.tokenURL = userParam['TOKEN_URL']
        else:
            self.poly.Notices['cp'] = 'Missing TOKEN_URL parameter'
            self.tokenURL = ''

        if 'MQTT_URL' in userParam:
            self.mqttURL = userParam['MQTT_URL']
        else:
            self.poly.Notices['cp'] = 'Missing MQTT_URL parameter'
            self.mqttURL = ''

        if 'MQTT_PORT' in userParam:
            self.mqttPort = userParam['MQTT_PORT']
        else:
            self.poly.Notices['cp'] = 'Missing MQTT_PORT parameter'
            self.mqttPort = 0

        '''
        if local_email != '' or local_password != '' or local_ip != '':
            logging.debug('local access true, cfg = {} {} {}'.format(local_email, local_password, local_ip))
            local_valid = True
            if local_email == '':
                self.poly.Notices['lu'] = 'Please enter the local user name'
                local_valid = False
            if local_password == '':
                self.poly.Notices['lp'] = 'Please enter the local user password'
                local_valid = False
            if local_ip == '':
                self.poly.Notices['ip'] = 'Please enter the local IP address'
                local_valid = False


        if cloud_email != '' or cloud_password != '' or cloud_token != '':
            logging.debug('cloud access true, cfg = {} {} {}'.format(cloud_email, cloud_password, cloud_token))
            cloud_valid = True
            if cloud_email == '':
                self.poly.Notices['cu'] = 'Please enter the cloud user name'
                cloud_valid = False
            if cloud_password == '':
                self.poly.Notices['cp'] = 'Please enter the cloud user password'
                cloud_valid = False
            if cloud_token == '':
                self.poly.Notices['ct'] = 'Please enter the Tesla Refresh Token - see readme for futher info '
                cloud_valid = False

        if local_valid:
            logging.debug('Local access is valid, configure....')
            self.localAccess = True

        if cloud_valid:
            logging.debug('Cloud access is valid, configure....')
            self.cloudAccess = True

        if cloud_valid or local_valid:
            self.tesla_initialize(local_email, local_password, local_ip, cloud_email, cloud_password)

        if not cloud_valid and not local_valid:
            self.poly.Notices['cfg'] = 'Tesla PowerWall NS needs configuration.'
        '''
        logging.debug('done with parameter processing')


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()
        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

