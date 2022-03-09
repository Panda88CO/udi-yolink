#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""

import sys
import time
from yoLinkInit import YoLinkInitPAC
from udiYoSwitchV2 import udiYoSwitch
from udiYoTHsensorV2 import udiYoTHsensor 
from udiYoGarageDoorCtrlV2 import udiYoGarageDoor
from udiYoMotionSensorV2 import udiYoMotionSensor
from udiYoLeakSensorV2 import udiYoLeakSensor
from udiYoDoorSensorV2 import udiYoDoorSensor
from udiYoOutletV2 import udiYoOutlet
from udiYoMultiOutletV2 import udiYoMultiOutlet
from udiYoManipulatorV2 import udiYoManipulator


#from oldStuff.yoLinkPACOauth import YoLinkDevicesPAC
#from oldStuff.yoLinkOauth import YoLinkDevices

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
polyglot = None
#Parameters = None






class YoLinkSetup (udi_interface.Node):
    def  __init__(self, polyglot, primary, address, name):
        super(YoLinkSetup, self).__init__( polyglot, primary, address, name)  
        self.hb = 0
        self.devicesReady = False
        self.nodeDefineDone = False
        self.longPollCountMissed = 0
        self.address = address
        self.name = name

        #logging.setLevel(20)
        self.poly.subscribe(self.poly.STOP, self.stop)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.handleParams)
        self.poly.subscribe(self.poly.POLL, self.systemPoll)

        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
       
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))   
        
        self.poly.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(self.address)
        time.sleep(2)
        self.node.setDriver('ST', 1, True, True)
        
        logging.debug('YoLinkSetup init DONE')
        self.nodeDefineDone = True
     
    def start (self):
        logging.info('Start executing start')
        logging.info ('Access using PAC/UAC')
        logging.setLevel(20)
        self.tokenObtained = False
        self.supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub' ]
        yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
        self.yoAccess = yoAccess
        self.deviceList = yoAccess.getDeviceList()
        while  self.devicesReady:
            time.sleep(2)
            logging.info('Waiting to retrieve devise list')
        #self.deviceList = self.getDeviceList2()

        logging.debug('{} devices detected : {}'.format(len(self.deviceList), self.deviceList) )
        #logging.setLevel(10)

        for dev in range(0,len(self.deviceList)):
            logging.debug('adding/checking device : {} - {}'.format(self.deviceList[dev]['name'], self.deviceList[dev]['type']))

            if self.deviceList[dev]['type'] == 'Hub':     
                logging.info('Hub not added - UDI cannot do anything useful with it')    
                #name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                #logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                #udiYoHub(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                #self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']

            elif self.deviceList[dev]['type'] == 'Switch':
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoSwitch(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
            elif self.deviceList[dev]['type'] == 'THSensor':      
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoTHsensor(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
            elif self.deviceList[dev]['type'] == 'MultiOutlet':
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoMultiOutlet(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']                
            elif self.deviceList[dev]['type'] == 'DoorSensor':
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoDoorSensor(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']            
            elif self.deviceList[dev]['type'] == 'Manipulator':
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoManipulator(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']                
            elif self.deviceList[dev]['type'] == 'MotionSensor':     
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoMotionSensor(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']                
            elif self.deviceList[dev]['type'] == 'Outlet':     
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoOutlet(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']
            elif self.deviceList[dev]['type'] == 'GarageDoor': 
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoGarageDoor(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']                
            elif self.deviceList[dev]['type'] == 'LeakSensor': 
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoLeakSensor(polyglot, name, name, self.deviceList[dev]['name'],  yoAccess, self.deviceList[dev] )
                self.Parameters[self.deviceList[dev]['deviceId']] =  self.deviceList[dev]['name']                  
            else:
                logging.debug('Currently unsupported device : {}'.format(self.deviceList[dev]['type'] ))
    


    def stop(self):
        logging.info('Stop Called:')
        self.node.setDriver('ST', 0, True, True)
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'setup':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)
        
        exit()
    '''
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
    '''
    def heartbeat(self):
        logging.debug('heartbeat: ' + str(self.hb))
        
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0
    def systemPoll (self, polltype):
        pass

    '''
    def systemPoll (self, polltype):
        if self.nodeDefineDone:
            logging.info('System Poll executing')
            if 'longPoll' in polltype:
                #Keep token current
                if not self.yoAccess.refresh_token(): #refresh failed
                    while not self.yoAccess.request_new_token()
                            time.sleep(60)
                logging.info('Updating device status')
                nodes = self.poly.getNodes()
                for node in nodes:
                    if node != 'setup':   # but not the controller node
                        nodes[node].checkOnline()
                
                
            if 'shortPoll' in polltype:
                self.heartbeat()
    '''


    def handleLevelChange(self, level):
        logging.info('New log level: {}'.format(level))
        logging.setLevel(level['level'])



    def handleParams (self, userParam ):
        logging.debug('handleParams')
        
        self.Parameters.load(userParam)
        self.poly.Notices.clear()
        try:
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
        except:
            logging.debug('Error: {}'.format(userParam))

 

    
    id = 'setup'


    drivers = [
           {'driver': 'ST', 'value':1, 'uom':25},
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
        

