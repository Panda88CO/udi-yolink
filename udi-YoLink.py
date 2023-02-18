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
from udiYoDoorSensorV2 import udiYoDoorSensor
from udiYoOutletV2 import udiYoOutlet
from udiYoMultiOutletV2 import udiYoMultiOutlet
from udiYoManipulatorV2 import udiYoManipulator
from udiYoHubV2 import udiYoHub
from udiYoSpeakerHubV2 import udiYoSpeakerHub
from udiYoLockV2 import udiYoLock
from udiYoInfraredRemoterV2 import udiYoInfraredRemoter
from udiYoDimmerV2 import udiYoDimmer
from udiYoVibrationSensorV2 import udiYoVibrationSensor
from udiYoSmartRemoterV3 import udiYoSmartRemoter
from udiYoPowerFailV2 import udiYoPowerFailSenor


import udiProfileHandler

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)



class YoLinkSetup (udi_interface.Node):
    def  __init__(self, polyglot, primary, address, name):
        super().__init__( polyglot, primary, address, name)  
        


        self.hb = 0
        self.poly=polyglot
        self.nodeDefineDone = False
        self.handleParamsDone = False
        self.pollStart = False
        self.debug = False
        self.address = address
        self.name = name
        self.yoAccess = None
        self.TTSstr = 'TTS'
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
                                'PowerFailureAlarm', 'SmartRemoter' ]
        #self.supportedYoTypes = ['PowerFailureAlarm', 'SmartRemoter' ]
        
        #self.supportedYoTypes = [ 'THSensor' ]

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
            self.debug = self.Parameters['TEMP_UNIT']
            self.yoAccess.set_debug(self.debug)
        else:
            self.debug = False
            self.yoAccess.set_debug(self.debug)
        
        self.deviceList = self.yoAccess.getDeviceList()
        #self.deviceList = self.getDeviceList2()

        logging.debug('{} devices detected : {}'.format(len(self.deviceList), self.deviceList) )
        self.addNodes(self.deviceList)

        #self.poly.updateProfile()



    def addNodes (self, deviceList):
        addressList = []
        '''
        logging.debug('Parsing Parameters for old elements')
        delparams = []
        for param in self.Parameters:
            logging.debug( 'Parameters - checking {}'.format(param))
            if param not in self.supportParams:             
                if param.find(self.TTSstr) == -1:     
                    logging.debug( 'Parameters - deleting {}'.format(param))               
                    delparams.append(param)
        for param in delparams:
            self.Parameters.delete(param)
            logging.debug( 'Parameters - deleting {}'.format(param))
        '''

        for dev in range(0,len(self.deviceList)):
            if self.deviceList[dev]['type']  in self.supportedYoTypes:
                logging.info('adding/checking device : {} - {}'.format(self.deviceList[dev]['name'], self.deviceList[dev]['type']))
                if self.deviceList[dev]['type'] == 'Hub':     
                    logging.info('Hub not added - ISY cannot do anything useful with it')    
                    #name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    #logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    #udiYoHub(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    #self.Parameters[name]  =  self.deviceList[dev]['name']
                elif self.deviceList[dev]['type'] == 'SpeakerHub':
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoSpeakerHub(self.poly, name, name, self.deviceList[dev]['name'],  self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name] =  self.deviceList[dev]['name']
                    addressList.append(name)
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
                    time.sleep(2) # add delay between adding devices

                elif self.deviceList[dev]['type'] == 'Switch':
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoSwitch(self.poly, name, name, self.deviceList[dev]['name'],  self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name] =  self.deviceList[dev]['name']
                    time.sleep(2) # add delay between adding devices

                elif self.deviceList[dev]['type'] == 'Dimmer':
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoDimmer(self.poly, name, name, self.deviceList[dev]['name'],  self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name] =  self.deviceList[dev]['name']
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                    

                elif self.deviceList[dev]['type'] == 'THSensor':      
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoTHsensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev])
                    self.Parameters[name] =  self.deviceList[dev]['name']
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                

                elif self.deviceList[dev]['type'] == 'MultiOutlet':
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoMultiOutlet(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']      
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                              

                elif self.deviceList[dev]['type'] == 'DoorSensor':
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoDoorSensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name'] 
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                               

                elif self.deviceList[dev]['type'] == 'Manipulator':
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoManipulator(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name] =  self.deviceList[dev]['name']  
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                                  

                elif self.deviceList[dev]['type'] == 'MotionSensor':     
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoMotionSensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name] =  self.deviceList[dev]['name']    
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                      

                elif self.deviceList[dev]['type'] == 'VibrationSensor':     
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoVibrationSensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name] =  self.deviceList[dev]['name']   
                    addressList.append(name)  
                    time.sleep(2) # add delay between adding devices                                   

                elif self.deviceList[dev]['type'] == 'Outlet':     
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoOutlet(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                    

                elif self.deviceList[dev]['type'] == 'GarageDoor': 
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoGarageDoor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']     
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                    

                elif self.deviceList[dev]['type'] == 'Finger': 
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoGarageFinger(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']   
                    addressList.append(name)
                    time.sleep(2) # add delay between adding devices                                        

                elif self.deviceList[dev]['type'] == 'Lock': 
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoLock(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']    
                    addressList.append(name)    
                    time.sleep(2) # add delay between adding devices

                elif self.deviceList[dev]['type'] == 'InfraredRemoter': 
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoInfraredRemoter(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']    
                    addressList.append(name)   
                    time.sleep(2) # add delay between adding devices                                    

                elif self.deviceList[dev]['type'] == 'LeakSensor': 
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoLeakSensor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']  
                    addressList.append(name)         
                    time.sleep(2) # add delay between adding devices

                elif self.deviceList[dev]['type'] == 'PowerFailureAlarm': 
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoPowerFailSenor(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']  
                    addressList.append(name)         
                    time.sleep(2) # add delay between adding devices

                elif self.deviceList[dev]['type'] == 'SmartRemoter': 
                    name = self.deviceList[dev]['deviceId'][-14:] #14 last characters - hopefully there is no repeats (first charas seems the same for all)
                    logging.info('Adding device {} ({}) as {}'.format( self.deviceList[dev]['name'], self.deviceList[dev]['type'], str(name) ))                                        
                    udiYoSmartRemoter(self.poly, name, name, self.deviceList[dev]['name'], self.yoAccess, self.deviceList[dev] )
                    self.Parameters[name]  =  self.deviceList[dev]['name']  
                    addressList.append(name)         
                    time.sleep(2) # add delay between adding devices


            else:
                logging.debug('Currently unsupported device : {}'.format(self.deviceList[dev]['type'] ))
        time.sleep(2)
        '''        
        deleteList = []
        nodes = self.poly.getNodes() 
        logging.debug('Added nodes : '.format(nodes))
        logging.debug('Checking for nodes that no longer exit')
        logging.debug('AddressList : {}'.format(addressList))
        for nde in nodes:
            logging.debug('Node address: {}'.format(nde[0:11]))
            found = False
            for adr in addressList:    
                if adr.find(nde[0:11]) >=0 :
                    found = True
            if not found and nde != 'setup':
                logging.debug('Node {} not in list'.format(nde))
                deleteList.append(nde)
        logging.debug('Delete List {}'.format(deleteList))

        for nde in deleteList:
                self.poly.delNode(nde)
                logging.debug('Node {} not in list - removing it'.format(nde))
        '''

        # checking params for erassed nodes 
        self.poly.updateProfile()
        self.pollStart = True

    def stop(self):
        try:
            logging.info('Stop Called:')
            #self.yoAccess.writeTtsFile() #save current TTS messages
            if 'self.node' in locals():
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
        except Exception as E:
            logging.error('Stop Exception : {}'.format(E))
            if self.yoAccess:
                self.yoAccess.shut_down()
            self.poly.stop()

    def heartbeat(self):
        logging.debug('heartbeat: ' + str(self.hb))
        
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

    def checkNodes(self):
        logging.info('Updating Nodes')
        self.deviceList = self.yoAccess.getDeviceList()
        nodes = self.poly.getNodes()
        for dev in range(0,len(self.deviceList)):
            devList = []
            name = self.deviceList[dev]['deviceId'][-14:]
            if name not in nodes:
                #device was likely off line during inital instellation or added afterwards
                devList.append(self.deviceList[dev])
                self.addNodes(devList)


    def systemPoll (self, polltype):
        if self.pollStart:
            logging.debug('System Poll executing: {}'.format(polltype))

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
                except Exception as e:
                    logging.debug('Exeption occcured during systemPoll : {}'.format(e))
                    #self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
                    #self.deviceList = self.yoAccess.getDeviceList()           
                
            if 'shortPoll' in polltype:
                self.heartbeat()
                nodes = self.poly.getNodes()
                for nde in nodes:
                    if nde != 'setup':   # but not the controller node
                        nodes[nde].checkDataUpdate()
    


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
            

            #for param in userParam:
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
          # {'driver': 'GV0', 'value':0, 'uom':25},
           ]


if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])

        polyglot.start('0.8.31')

        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

