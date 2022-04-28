#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""

import sys
import time

from yoLinkInitV2 import YoLinkInitPAC
from udiYoSwitchV2 import udiYoSwitch
from udiYoTHsensorV2 import udiYoTHsensor 
from udiYoGarageDoorCtrlV2 import udiYoGarageDoor
from udiYoMotionSensorV2 import udiYoMotionSensor
from udiYoLeakSensorV2 import udiYoLeakSensor
from udiYoDoorSensorV2 import udiYoDoorSensor
from udiYoOutletV2 import udiYoOutlet
from udiYoMultiOutletV2 import udiYoMultiOutlet
from udiYoManipulatorV2 import udiYoManipulator

#from udiYoSpeakerHubV2 import udiYoSpeakerHub


try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom

except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)







class YoLinkSetup (udi_interface.Node):
    def  __init__(self, polyglot, primary, address, name):
        super().__init__( polyglot, primary, address, name)  
        self.hb = 0
        self.poly=polyglot
        self.nodeDefineDone = False
        self.handleParamsDone = False
        self.address = address
        self.name = name
        self.yolinkURL = 'https://api.yosmart.com/openApi'
        self.yolinkV2URL = 'https://api.yosmart.com/open/yolink/v2/api'

        self.tokenURL = 'https://api.yosmart.com/open/yolink/token'
        self.mqttURL = 'api.yosmart.com'
        self.mqttPort = 8003

        #logging.setLevel(30)
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
        
        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()

        self.node = self.poly.getNode(self.address)
        self.node.setDriver('ST', 1, True, True)
        logging.debug('YoLinkSetup init DONE')
        self.nodeDefineDone = True


    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start (self):
        logging.info('Executing start - udi-YoLink')
        logging.info ('Access using PAC/UAC')
        #logging.setLevel(30)
        while not self.nodeDefineDone:
            time.sleep(1)
            logging.debug ('waiting for inital node to get created')
        self.supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub' ]
        if self.uaid == None or self.uaid == '' or self.secretKey==None or self.secretKey=='':
            logging.error('UAID and secretKey must be provided to start node server')
            exit() 
        self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
        self.deviceList = self.yoAccess.getDeviceList()
        #self.deviceList = self.getDeviceList2()

        logging.debug('{} devices detected : {}'.format(len(self.deviceList), self.deviceList) )
        

        for dev in range(0,len(self.deviceList)):
            logging.debug('adding/checking device : {} - {}'.format(self.deviceList[dev]['name'], self.deviceList[dev]['type']))


            if self.deviceList[dev]['type'] == 'Hub':     
                logging.info('Hub not added - ISY cannot do anything useful with it')    
                #name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                #logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                #udiYoHub(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                #self.Parameters[name]  =  self.deviceList[dev]['name']

            elif self.deviceList[dev]['type'] == 'Switch':
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoSwitch(self.poly, name, name, self.deviceList[dev]['name'],  self.yoAccess, self.deviceList[dev] )
                self.Parameters[name] =  self.deviceList[dev]['name']
            elif self.deviceList[dev]['type'] == 'THSensor':      
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoTHsensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                self.Parameters[name] =  self.deviceList[dev]['name']
            elif self.deviceList[dev]['type'] == 'MultiOutlet':
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoMultiOutlet(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                self.Parameters[name]  =  self.deviceList[dev]['name']                
            elif self.deviceList[dev]['type'] == 'DoorSensor':
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoDoorSensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                self.Parameters[name]  =  self.deviceList[dev]['name']            
            elif self.deviceList[dev]['type'] == 'Manipulator':
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoManipulator(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                self.Parameters[name] =  self.deviceList[dev]['name']                
            elif self.deviceList[dev]['type'] == 'MotionSensor':     
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoMotionSensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                self.Parameters[name] =  self.deviceList[dev]['name']                
            elif self.deviceList[dev]['type'] == 'Outlet':     
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoOutlet(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                self.Parameters[name]  =  self.deviceList[dev]['name']
            elif self.deviceList[dev]['type'] == 'GarageDoor': 
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoGarageDoor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                self.Parameters[name]  =  self.deviceList[dev]['name']                
            elif self.deviceList[dev]['type'] == 'LeakSensor': 
                name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                udiYoLeakSensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                self.Parameters[name]  =  self.deviceList[dev]['name']                  
            else:
                logging.debug('Currently unsupported device : {}'.format(self.deviceList[dev]['type'] ))

        self.poly.updateProfile()


    def stop(self):
        logging.info('Stop Called:')
        if self.node:
            self.node.setDriver('ST', 0, True, True)
            #nodes = self.poly.getNodes()
            #for node in nodes:
            #    if node != 'setup':   # but not the controller node
            #        nodes[node].setDriver('ST', 0, True, True)
            time.sleep(2)
        if self.yoAccess:
            self.yoAccess.shut_down()
        self.poly.stop()
        exit()
 

    def heartbeat(self):
        logging.debug('heartbeat: ' + str(self.hb))
        
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0


    def systemPoll (self, polltype):
        if self.nodeDefineDone:
            logging.debug('System Poll executing: {}'.format(polltype))
            if 'longPoll' in polltype:
                #Keep token current
                try:
                    if not self.yoAccess.refresh_token(): #refresh failed
                        while not self.yoAccess.request_new_token():
                                time.sleep(60)
                    #logging.info('Updating device status')
                    nodes = self.poly.getNodes()
                    for node in nodes:
                        if node != 'setup':   # but not the controller node
                            nodes[node].checkOnline()
                except Exception as e:
                    logging.debug('Exeption occcured during request_new_token : {}'.format(e))
                    self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
                    self.deviceList = self.yoAccess.getDeviceList()           
                
            if 'shortPoll' in polltype:
                self.heartbeat()
    


    def handleLevelChange(self, level):
        logging.info('New log level: {}'.format(level))
        logging.setLevel(level['level'])



    def handleParams (self, userParam ):
        logging.debug('handleParams')
        supportParams = ['YOLINKV2_URL', 'TOKEN_URL','MQTT_URL', 'MQTT_PORT', 'UAID', 'SECRET_KEY' ]
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

            #for param in userParam:
            #    if param not in supportParams:
            #        del self.Parameters[param]
            #        logging.debug ('erasing key: ' + str(param))

            self.handleParamsDone = True


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
        

