#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""
from os import truncate
import sys
import os
import json
import time

from udiYoSwitch import udiYoSwitch
from udiYoTHsensor import udiYoTHsensor 
from udiYoGarageDoorCtrl import udiYoGarageDoor
from udiYoMotionSensor import udiYoMotionSensor
from udiYoLeakSensor import udiYoLeakSensor
from udiYoDoorSensor import Parameters, udiYoDoorSensor
from udiYoOutlet import udiYoOutlet
from yoLinkPACOauth import YoLinkDevicesPAC
from yoLinkOauth import YoLinkDevices

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)
polyglot = None
#Parameters = None

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
        
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)


        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
       
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))   
        
        self.nodeDefineDone = False
        self.longPollCountMissed = 0

        self.poly.ready()
        self.poly.addNode(self)

        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)
        self.devicesReady = False
        logging.debug('YoLinkSetup init DONE')


    def start (self):
        logging.debug('Start executing start')
        self.redirectURL = "" 
        self.tokenObtined = False
        self.deviceList = None
        self.supportedYoTypes = ['Switch', 'THsensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub' ]
        logging.info('getDeviceList3')
        self.getDeviceList3()
                
        while not self.devicesReady:
            time.sleep(2)
            logging.info('Waiting to retrieve devise list')
        #self.deviceList = self.getDeviceList2()

        logging.debug( self.deviceList)
        logging.debug('{} devices detected'.format(len(self.deviceList)))
        isyNbr = 0
        isyName = 'yolink'  # has to be lower case and less than 13 chars
        for dev in range(0,len(self.deviceList)):
            logging.debug('adding/checking device : {}'.format(self.deviceList[dev]['type']))
            if self.deviceList[dev]['type'] in self.supportedYoTypes:
                isyNbr += 1
                if self.deviceList[dev]['type'] == 'Switch':
                    logging.info('Adding device {}'.format( self.deviceList[dev]['type']))
                    udiYoSwitch(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    if self.deviceList[dev]['deviceId'] not in self.Parameters:
                        self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                        logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                elif self.deviceList[dev]['type'] == 'THsensor':
                    logging.info('Adding device {}'.format( self.deviceList[dev]['type']))
                    udiYoTHsensor(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    if self.deviceList[dev]['deviceId'] not in self.Parameters:
                        self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                        logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])
                        
                elif self.deviceList[dev]['type'] == 'MultiOutlet':
                    logging.info('Adding device {}'.format( self.deviceList[dev]['type']))
                    isyNbr -= 1  
                    #udiYoMultiOutlet(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    #if self.deviceList[dev]['deviceId'] not in self.Parameters:
                    #    self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                    #    logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                elif self.deviceList[dev]['type'] == 'DoorSensor':
                    logging.info('Adding device {}'.format( self.deviceList[dev]['type']))
                    
                    udiYoDoorSensor(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    if self.deviceList[dev]['deviceId'] not in self.Parameters:
                        self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                        logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                elif self.deviceList[dev]['type'] == 'Manipulator':
                    logging.info('Not supported yet - Adding device {}'.format( self.deviceList[dev]['type']))
                    isyNbr -= 1  
                    #udiYoManipulator(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    #if self.deviceList[dev]['deviceId'] not in self.Parameters:
                    #    self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                    #    logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                elif self.deviceList[dev]['type'] == 'MotionSensor':     
                    logging.info('Adding device {}'.format( self.deviceList[dev]['type']))
            
                    udiYoMotionSensor(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    if self.deviceList[dev]['deviceId'] not in self.Parameters:
                        self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                        logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                elif self.deviceList[dev]['type'] == 'Outlet':     
                    logging.info('Adding device {}'.format( self.deviceList[dev]['type']))
               
                    udiYoOutlet(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    if self.deviceList[dev]['deviceId'] not in self.Parameters:
                        self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                        logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                elif self.deviceList[dev]['type'] == 'GarageDoor': 
                    logging.info('Adding device {}'.format( self.deviceList[dev]['type']))
                    udiYoGarageDoor(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    if self.deviceList[dev]['deviceId'] not in self.Parameters:
                        self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                        logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                elif self.deviceList[dev]['type'] == 'LeakSensor': 
                    logging.info('Adding device {}'.format( self.deviceList[dev]['type']))
                    udiYoLeakSensor(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    if self.deviceList[dev]['deviceId'] not in self.Parameters:
                        self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                        logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                elif self.deviceList[dev]['type'] == 'Hub':     
                    logging.info('Hub not added')    
                    isyNbr -= 1  
                    #udiYoLeakHub(polyglot, str(isyName+str(isyNbr)), str(isyName+str(isyNbr)), self.deviceList[dev]['name'], self.csname, self.csid, self.csseckey, self.deviceList[dev], self.yolinkURL,self.mqttURL, self.mqttPort )
                    #if self.deviceList[dev]['deviceId'] not in self.Parameters:
                    #    self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
                    #    logging.debug('adding :' + self.deviceList[dev]['deviceId'] + '  ' +  self.deviceList[dev]['type'])

                else:
                    logging.debug('unsupported device : {}'.format(self.deviceList[dev]['type'] ))
        logging.debug(self.Parameters)

    def stop(self):
        logging.info('Stop Called:')
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'setup':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)
        self.node.setDriver('ST', 0, True, True)
        exit()

    def getDeviceList1(self):
        logging.debug ('getDeviceList1')
    
        self.yoDevices = YoLinkDevices(self.csid, self.csseckey)
        webLink = self.yoDevices.getAuthURL()
        #self.Parameters['REDIRECT_URL'] = ''
        self.poly.Notices['url'] = 'Copy this address to browser. Follow screen to long. After screen refreshes copy resulting  redirect URL (address bar) into config REDICRECT_URL: ' + str(webLink) 


    def getDeviceList2(self):
        logging.debug('Start executing getDeviceList2')
        self.supportedYoTypes = ['switch', 'THsensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub' ]
        self.yoDevices = YoLinkDevicesPAC(self.uaid, self.secretKey)
        self.deviceList = self.yoDevices.getDeviceList()

    def getDeviceList3(self):
        logging.debug('reading /devices.json')
        logging.debug(os.getcwd())
        if (os.path.exists('./devices.json')):
            logging.debug('reading /devices.json')
            dataFile = open('./devices.json', 'r')
            tmp= json.load(dataFile)
            logging.debug(tmp)
            dataFile.close()
            self.deviceList = tmp['data']['list']
            logging.debug(self.deviceList)
            self.devicesReady = True
        else:
             logging.debug('devices.json does not exist')


    def systemPoll (self, type):
        logging.info('System Poll executing')

    def handleLevelChange(self, level):
        logging.info('New log level: {}'.format(level))

    def handleParams (self, userParam ):
        logging.debug('handleParams')
        self.Parameters.load(userParam)
        self.poly.Notices.clear()
        
        if 'USER_EMAIL' in userParam:
            email = userParam['USER_EMAIL']
        else:
            self.poly.Notices['ue'] = 'Missing User Email parameter'
            email = ''

        if 'USER_PASSWORD' in userParam:
            password = userParam['USER_PASSWORD']
        else:
            self.poly.Notices['up'] = 'Missing User Password parameter'
            password = ''
        
        if 'CSID' in userParam:
            self.csid = userParam['CSID']
        else:
            self.poly.Notices['csid'] = 'Missing csid parameter'
            self.csid = ''

        if 'CSSSECKEY' in userParam:
            self.csseckey = userParam['CSSSECKEY']
        else:
            self.poly.Notices['css'] = 'Missing cssSecKey parameter'
            self.csseckey = ''

        if 'CSNAME' in userParam:
            self.csname = userParam['CSNAME']
        else:
            self.poly.Notices['csname'] = 'Missing csName parameter'
            self.csname = ''
    
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
    
        if 'YOLINK_URL' in userParam:
            self.yolinkURL = userParam['YOLINK_URL']
        else:
            self.poly.Notices['ylurl'] = 'Missing YOLINK_URL parameter'
            self.yolinkURL = ''

        if 'YOLINKV2_URL' in userParam:
            self.yolinkV2URL = userParam['YOLINKV2_URL']
        else:
            self.poly.Notices['yl2url'] = 'Missing YOLINKV2_URL parameter'
            self.yolinkV2URL = ''

        if 'TOKEN_URL' in userParam:
            self.tokenURL = userParam['TOKEN_URL']
        else:
            self.poly.Notices['turl'] = 'Missing TOKEN_URL parameter'
            self.tokenURL = ''

        if 'MQTT_URL' in userParam:
            self.mqttURL = userParam['MQTT_URL']
        else:
            self.poly.Notices['murl'] = 'Missing MQTT_URL parameter'
            self.mqttURL = ''

        if 'MQTT_PORT' in userParam:
            self.mqttPort = userParam['MQTT_PORT']
        else:
            self.poly.Notices['mport'] = 'Missing MQTT_PORT parameter'
            self.mqttPort = 0

        if 'REDIRECT_URL' in userParam:
            self.redirect_URL = userParam['REDIRECT_URL']
        else:
            self.poly.Notices['redirect'] = 'Missing REDIRECT_URL parameter'
            self.redirectURL = ''       
        

        '''
        if self.redirectURL != "" :
            #self.poly.Notices['url'] = 'Input redirected address to REDIRECR address field'       
            logging.debug(self.redirect_URL)
            logging.debug('getting token ')  
            self.token = self.yoDevices.getToken(self.csseckey, self.redirect_URL)
            logging.debug(self.token)
            temp = self.yoDevices.getDeviceList(self.token, self.csid, self.csseckey)
            logging.debug(temp)
            self.deviceList = temp['data']['list']
            logging.debug( self.deviceList)
        '''
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
 
    id = 'setup'
    drivers = [
           {'driver': 'ST', 'value':0, 'uom':25},
           ]

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()
        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

