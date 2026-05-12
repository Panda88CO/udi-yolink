#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""
version = '1.8.51'
import sys
import re
import time
#from apscheduler.schedulers.background import BackgroundScheduler
import os
#import json
import xml.etree.ElementTree as ET


#from yoLink_init_V4 import YoLinkInitPAC
from udiYoSwitchV4 import udiYoSwitch
#from udiYoSwitchSecV2 import udiYoSwitchSec
#from udiYoSwitchPwrSecV2 import udiYoSwitchPwrSec
from udiYoTHsensorV4 import udiYoTHsensor 
from udiYoWaterDeptV4 import udiYoWaterDept 
from udiYoGarageDoorCtrlV4 import udiYoGarageDoor
from udiYoGarageFingerCtrlV4 import udiYoGarageFinger
from udiYoMotionSensorV4 import udiYoMotionSensor
from udiYoLeakSensorV4 import udiYoLeakSensor
from udiYoCOSmokeSensorV4 import udiYoCOSmokeSensor
from udiYoDoorSensorV4 import udiYoDoorSensor
from udiYoOutletV4 import udiYoOutlet
#from udiYoOutletPwrV2 import udiYoOutletPwr
from udiYoMultiOutletV4 import udiYoMultiOutlet
from udiYoManipulatorV4 import udiYoManipulator
from udiYoSpeakerHubV4 import udiYoSpeakerHub
from udiYoLock_V4 import udiYoLock, udiYoLockV2
from udiYoInfraredRemoterV4 import udiYoInfraredRemoter
from udiYoDimmerV4 import udiYoDimmer
from udiYoVibrationSensorV4 import udiYoVibrationSensor
from udiYoSmartRemoterV4 import udiYoSmartRemoter
from udiYoPowerFailV4 import udiYoPowerFailSenor
#from udiYoSprinklerV4 import udiYoSprinkler
from udiYoSprinkler2V4 import udiYoSprinkler2
from udiYoSoilSensorV4 import udiYoSoilSensor
from udiYoThermostatV4 import udiYoThermostat
from udiYoSirenV4 import udiYoSiren
from udiYoWaterMeterControllerV4 import udiYoWaterMeterController
from udiYoWaterMeterMultiControllerV4 import udiYoWaterMeterMulti 
#from udiYoWaterMeterOnlyV3 import udiYoWaterMeterOnly 
from udiYoHubV4 import udiYoHub, udiYoBatteryHub
#import udiProfileHandler

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_logging import resolve_log_level


NODE_READY_POLL_SECONDS = 0.2


def _resolve_node_ready_poll_seconds(self):
    configured_value = getattr(self, 'node_ready_poll_seconds', NODE_READY_POLL_SECONDS)
    try:
        poll_seconds = float(configured_value)
    except (TypeError, ValueError):
        logging.warning(
            'Invalid node_ready_poll_seconds=%s, using default %.2f',
            configured_value,
            NODE_READY_POLL_SECONDS,
        )
        return NODE_READY_POLL_SECONDS

    # Keep startup polling responsive while avoiding zero/negative busy loops.
    if poll_seconds < 0.05:
        return 0.05
    if poll_seconds > 2.0:
        return 2.0
    return poll_seconds








def udiTssProfileUpdate(messages):
    '''
        if (os.path.exists('./profile/editor/editor.xml')):
            #logging.debug('reading /devices.json')
            editor =  minidom.parse('./profile/editor/editor.xml')
        if (os.path.exists('./profile/nls/en_us.txt')):
            #logging.debug('reading /devices.json')
            nls = open(''./profile/nls/en_us.txt')
    '''
    foundChanges = False
    NLSstr = None
    if (os.path.exists('./profile/editor/editors.xml')):
        Tree = ET.parse('./profile/editor/editors.xml')
        #efile.close()
        editorRoot = Tree.getroot()
        indx = 0
        found = False

        while not found and indx < len(editorRoot):
            if editorRoot[indx].attrib['id'] == 'messages':
                found = True
                if editorRoot[indx][0].attrib['subset'] != "0-"+str(len(messages)-1):
                    editorRoot[indx][0].attrib['subset'] = "0-"+str(len(messages)-1)
                    foundChanges = True
                NLSstr = editorRoot[indx][0].attrib['nls']
            else:
                indx = indx + 1

        Tree.write('./profile/editor/editors.xml')
    else:
        logging.error('./profile/editor/editors.xml NOT FOUND ')

    if NLSstr is None:
        logging.error('messages editor entry not found in ./profile/editor/editors.xml')
        return foundChanges

    if (os.path.exists('./profile/nls/en_us.txt')):
        nfile = open('./profile/nls/en_us.txt', 'r')
        nls = nfile.readlines()
        nfile.close()

        # Gather existing message labels so we can compare old vs new values exactly.
        removedLines = {}
        for line in range(len(nls)-1, 0, -1):
            if nls[line].find(NLSstr, 0, len(NLSstr)) != -1:
                splitLine = re.split('=', nls[line], maxsplit=1)
                key_part = splitLine[0].strip()
                key_prefix = f'{NLSstr}-'
                if key_part.startswith(key_prefix):
                    idx_text = key_part[len(key_prefix):].strip()
                    if idx_text.isdigit():
                        index = int(idx_text)
                        TTS = splitLine[1].strip() if len(splitLine) > 1 else ''
                        removedLines[index] = TTS
                nls.pop(line)

        newLines = {}
        for line in range(0,len(messages)):
            msg = str(messages[line]).strip()
            newLines[line] = msg
            nls.append('{}-{} = {}\n'.format(NLSstr, line, msg))

        if removedLines != newLines:
            foundChanges = True

        nfile = open('./profile/nls/en_us.txt', 'w')
        nfile.writelines(nls)
        nfile.close()
    else:
        logging.error('./profile/nls/en_us.txt NOT FOUND ')
    return(foundChanges)

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
    #logging.debug('Nodes in Nodeserver - before cleanup: {} - {}'.format(len(self.nodes_in_db),self.nodes_in_db))
    self.configDone = True


def addNodes (self, deviceList) -> list:
    supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
                        'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
                        'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock' , 'LockV2', 'Dimmer', 'InfraredRemoter',
                        'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren', 'WaterMeterController',
                        'WaterDepthSensor', 'WaterMeterMultiController', 'SprinklerV2', 'Thermostat',
                        'SoilThcSensor']
    #supportedYoTypes = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 
    #                    'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 
    #                    'SpeakerHub', 'VibrationSensor', 'Finger', 'Lock' , 'LockV2', 'Dimmer', 'InfraredRemoter',
    #                    'PowerFailureAlarm', 'SmartRemoter', 'COSmokeSensor', 'Siren', 'WaterMeterController',
    #                    'WaterDepthSensor', ]    'WaterMeterController', 
    
    #supportedYoTypes = ['SprinklerV2', 'Sprinkler', 'Thermostat', 'SoilThcSensor', 'THSensor' ]     
    #supportedYoTypes = ['WaterMeterController', 'WaterMeterMultiController']   
    #supportedYoTypes = ['WaterMeterMultiController']     
    #supportedYoTypes = ['Hub', 'THSensor', 'LeakSensor']
    remove_list= []
    schedule_queue = []
    node_ready_poll = _resolve_node_ready_poll_seconds(self)
    for dev in deviceList:
        logging.debug(f'DEVICE BEING ANALYZED {dev}')
        temp = None
        
        if dev['type'] not  in supportedYoTypes:            
            logging.warning('Currently unsupported device type found: {} - {}'.format(dev['type'], dev['name'] ))        
            remove_list.append(dev)
        else:
            nodename = str(dev['deviceId'][-14:])
            address = self.poly.getValidAddress(nodename)
            if 'modelName' in dev:
                model = dev['modelName'][:6]
            else:
                model = 'Unknown'

            if self.yoLocal is not None and dev['access'] == 0:
                logging.debug('Local Access selected {}'.format(dev['name']))
                dev_access = self.yoLocal
            else:
                logging.debug('Cloud Access selected {}'.format(dev['name']))
                dev_access = self.yoAccess

            name = dev['name']
            name = self.poly.getValidName(name)
            #self.Parameters[address] =  dev['name']

            logging.info('adding/checking device : {} - {}'.format(dev['name'], dev['type']))
            if dev['type'] == 'Hub':   
                logging.debug(f'HUB date {dev}')
                #if  model in [ 'YS1606']: #Need to add local hub as cloud - does not seem to work as local - but it is not a device in the local network
                #    dev_access = self.yoAccess
                if model in ['YS1613', 'YS1605', 'YS1606']:
                    temp = udiYoBatteryHub(self.poly, address, address, name, dev_access, dev)
                else:
                    temp = udiYoHub(self.poly, address, address, name, dev_access, dev)
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)
            elif dev['type'] in ['SpeakerHub']:
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoSpeakerHub(self.poly, address, address, name,  dev_access, dev )                    
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
                    logging.info ('Adding {} to Parameters'.format(dev_access.TtsMessages[n] ))
                #self.yoAccess.writeTtsFile()
                logging.info('TTS messages : {}'.format(dev_access.TtsMessages))
                logging.info('Updating profile files ')
                tts_signature = '|'.join(
                    [str(dev_access.TtsMessages[idx]).strip() for idx in sorted(dev_access.TtsMessages.keys())]
                )
                tts_signature = f'{self.nbrTTS}:{tts_signature}'

                try:
                    custom_data = Custom(self.poly, 'customdata')
                    prev_tts_signature = custom_data.get('tts_signature')
                except Exception as e:
                    logging.debug(f'Unable to access customdata for tts signature tracking: {e}')
                    custom_data = None
                    prev_tts_signature = None

                profile_changed = udiTssProfileUpdate(dev_access.TtsMessages)
                tts_changed = (
                    prev_tts_signature is not None and prev_tts_signature != tts_signature
                )

                if tts_changed:
                    self.poly.Notices['tts'] = 'Speaker hub messages updated - Polisy/eISY need to be restarted to take effect'
                else:
                    self.poly.Notices.delete('tts')

                if custom_data is not None and (tts_changed or profile_changed):
                    custom_data['tts_signature'] = tts_signature
                self.poly.updateProfile()   
                #for nbr in range(0,self.nbrTTS):
                #    index = 'TTS'+str(nbr)
                #    if index not in self.Parameters:
                #        self.Parameters[index] = index
                #    self.yoAccess.TtsMessages[nbr] = self.Parameters[index]

                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))                        
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)  

            elif dev['type'] in ['Switch']:
                if  model in ['YS5708', 'YS5709']:
                    logging.info('Adding swithSec device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSwitch(self.poly, address, address, name,  dev_access, dev )
                elif  model in ['YS5716']:
                    logging.info('Adding swithPwr device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSwitch(self.poly, address, address, name,  dev_access, dev )
                else:
                    logging.info('Adding switch device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                    temp = udiYoSwitch(self.poly, address, address, name,  dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)

            elif dev['type'] in ['Dimmer']:
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoDimmer(self.poly, address, address, name,  dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                    

            elif dev['type'] in ['THSensor']:      
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoTHsensor(self.poly, address, address, name, dev_access, dev)
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)
        
            elif dev['type'] in ['MultiOutlet']:
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoMultiOutlet(self.poly, address, address, name, dev_access, dev)
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                     
                        
            elif dev['type'] in ['DoorSensor']:                 
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoDoorSensor(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                      
                        
            elif dev['type'] in ['Manipulator']:              
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoManipulator(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                      
                        
            elif dev['type'] in ['MotionSensor']:              
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoMotionSensor(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                      

            elif dev['type'] in  ['VibrationSensor']:                    
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoVibrationSensor(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                     
                        
            elif dev['type'] in  ['Outlet']:     
                #if  model in ['YS6803','YS6602','YS5716', 'YS6614']:
                #    logging.info('Adding device w. power {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                #    temp = udiYoOutletPwr(self.poly, address, address, name, dev_access, dev )
                #else:
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoOutlet(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                      
        
            elif dev['type'] in ['GarageDoor']:                 
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoGarageDoor(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                      
        
            elif dev['type'] in ['Finger']:                   
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoGarageFinger(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                                                       

            elif dev['type'] in ['Lock' ]:        
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                     
                temp = udiYoLock(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                        

            elif dev['type'] in ['LockV2']:        
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                     
                temp = udiYoLockV2(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)    

            elif dev['type'] == 'InfraredRemoter':           
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoInfraredRemoter(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)      
                                
            elif dev['type'] in ['LeakSensor']:                 
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoLeakSensor(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)     

            elif dev['type'] in ['WaterDepthSensor']:   #  YS7905-UC           
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoWaterDept(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)     

            elif dev['type'] in ['COSmokeSensor']:                
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoCOSmokeSensor(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)       

            elif dev['type'] in ['PowerFailureAlarm']:                 
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoPowerFailSenor(self.poly, address, address, name, dev_access, dev )

                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                  

            elif dev['type'] in ['SmartRemoter']:                    
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoSmartRemoter(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)

            elif dev['type'] in ['Siren']:                  
                logging.info('Adding device {} ({}) as {}'.format( dev['name'], dev['type'], str(name) ))                                        
                temp = udiYoSiren(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)

            elif dev['type'] in ['WaterMeterController']:
                logging.info('Adding device {} {} ({}) as {} -'.format( dev['name'], model, dev['type'], str(name) ))                       
                #if  model in ['YS5007']:    
                #    temp = udiYoWaterMeterOnly(self.poly, address, address, name, dev_access, dev )
                #elif model in ['YS5029']: 
                #    temp = udiYoWaterMeterMulti(self.poly, address, address, name, dev_access, dev )
                if model in ['YS5018', 'YS5008', 'YS5009', 'YS5007']:  
                    temp = udiYoWaterMeterController(self.poly, address, address, name, dev_access, dev )
                else:
                    logging.warning('Currently unsupported Water Meter Controller model: {} - {} - trying default '.format(model, dev['name'] ))
                    temp = udiYoWaterMeterController(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)     

            elif dev['type'] in ['WaterMeterMultiController']:
                logging.info('Adding device {} {} ({}) as {} -'.format( dev['name'], model, dev['type'], str(name) ))
                if model in ['YS5029']: 
                    temp = udiYoWaterMeterMulti(self.poly, address, address, name, dev_access, dev )
                else: 
                    temp = udiYoWaterMeterMulti(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                while not getattr(temp, 'sub_nodes_ready', True):
                    logging.debug( 'Waiting for sub-nodes {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                                                 

            elif dev['type'] in [ 'SprinklerV2']: #'Sprinkler',
                logging.info('Adding device {} {} ({}) as {} -'.format( dev['name'], model, dev['type'], str(name) ))

                temp = udiYoSprinkler2(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)   

            elif dev['type'] in ['Thermostat']:
                logging.info('Adding device {} {} ({}) as {} -'.format( dev['name'], model, dev['type'], str(name) ))

                temp = udiYoThermostat(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)                            

            elif dev['type'] in ['SoilThcSensor']:
                logging.info('Adding device {} {} ({}) as {} -'.format( dev['name'], model, dev['type'], str(name) ))

                temp = udiYoSoilSensor(self.poly, address, address, name, dev_access, dev )
                while not temp.node_ready:
                    logging.debug( 'Waiting for node {}-{} to be ready'.format(dev['type'] , dev['name']))
                    time.sleep(node_ready_poll)
                for adr in temp.adr_list:
                    self.assigned_addresses.append(adr)    

            if getattr(temp, 'scheduleSupport', False) and hasattr(temp, 'create_schedule_nodes'):
                schedule_queue.append(temp)

    # Second pass: create schedule nodes after all main device nodes are ready
    logging.info('Creating schedule nodes for {} devices'.format(len(schedule_queue)))
    for temp in schedule_queue:
        for adr in temp.create_schedule_nodes():
            self.assigned_addresses.append(adr)

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
    
    for remove_dev in remove_list:
        deviceList.remove(remove_dev)
        
    logging.debug('Device list after removals count: {}'.format(len(deviceList)))
  
    time.sleep(1)
    # checking params for erassed nodes
    self.poly.updateProfile()
    self.yolink_nodes = self.poly.getNodes()
    self.my_setDriver('GV1', 1)
    self.pollStart = True
    return (deviceList)
'''
def stop(self):
    try:
        logging.info('Stop Called:')
        #self.yoAccess.writeTtsFile() #save current TTS messages

        self.my_setDriver('ST', 0)

        if self.yoAccess:
            self.yoAccess.shut_down()
        self.poly.stop()
        exit()
    except Exception as e:
        logging.error(f'Stop Exception : {e}')
        if self.yoAccess:
            self.yoAccess.shut_down()
        self.poly.stop()
'''

def heartbeat(self):
    logging.debug('heartbeat: ' + str(self.hb))
    if self.yoAccess.online:
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


def saveNodeNames(self):
    """Check all Polyglot nodes for ISY-side name changes and persist via
    Polyglot customdata store (Custom(poly, 'customdata')).
    Called from longPoll so saves happen promptly after a user renames on ISY.
    """
    try:
        if not getattr(self, 'nodeDefineDone', False) or not getattr(self, 'configDone', False):
            logging.debug('saveNodeNames: skipped before setup/config is ready')
            return

        yolink_nodes = getattr(self, 'yolink_nodes', None)
        if not isinstance(yolink_nodes, dict):
            logging.debug('saveNodeNames: skipped before node cache is ready')
            return

        cd = Custom(self.poly, 'customdata')
        nodes = self.poly.getNodes()
        for addr, node in nodes.items():
            if addr == 'setup':
                continue
            try:
                current_name = getattr(node, 'name', None)
                if not current_name:
                    continue
                current_name = self.poly.getValidName(current_name)
                node_key = f"{addr}_saved_name"
                saved = cd.get(node_key)
                if saved != current_name:
                    cd[node_key] = current_name
                    if saved is not None:
                        logging.info(f'saveNodeNames: {addr} name changed \'{saved}\' -> \'{current_name}\' saved')
                    else:
                        logging.debug(f'saveNodeNames: {addr} name \'{current_name}\' saved for first time')
                    # update in-memory cache on any matching yolink_node
                    ynode = yolink_nodes.get(addr)
                    if ynode is not None:
                        ynode._name_sync_saved = current_name
            except Exception as e:
                logging.debug(f'saveNodeNames: error processing {addr}: {e}')
    except Exception as e:
        logging.error(f'saveNodeNames: unexpected error: {e}')


def systemPoll (self, polltype):
    if self.pollStart:
        logging.debug('System Poll executing: {}'.format(polltype))
        if self.yoAccess.online:
            self.updateEpochTime()
            self.my_setDriver('ST', 1)
            if 'longPoll' in polltype:
                #Keep token current
                #self.my_setDriver('GV0', self.temp_unit)
                try:
                    #if not if hasattr(self.yolink_nodes[nde], 'checkOnline'):
                    #    self.yoAccess.refresh_token(): #refresh failed
                    #    while not self.yoAccess.request_new_token():
                    #            time.sleep(60)
                    #logging.info('Updating device status')
                    #nodes = self.poly.getNodes()
                    
                    self.saveNodeNames()
                    for nde in self.yolink_nodes:
                        if nde != 'setup':   # but not the controller node
                            if hasattr(self.yolink_nodes[nde], 'checkOnline'):
                                self.yolink_nodes[nde].checkOnline()
                            if hasattr(self.yolink_nodes[nde], 'checkNameSync'):
                                self.yolink_nodes[nde].checkNameSync()
                            logging.debug('longpoll {}'.format(nde))
                            time.sleep(5) # need to limit calls to 100 per  5 min - using 5 to allow other calls - updating is not critical
                except Exception as e:
                    logging.error('Exeption occcured during systemPoll : {}'.format(e))
                    #self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
                    #deviceList = self.yoAccess.getDeviceList()           
                
            if 'shortPoll' in polltype:
                self.heartbeat()

                #nodes = self.poly.getNodes()
                for nde in self.yolink_nodes:
                    if nde != 'setup':   # but not the controller node
                        self.yolink_nodes[nde].checkDataUpdate()
                        logging.debug('shortpoll {}'.format(nde))
                        # no API calls so no need to spread out 
                        #time.sleep(node_ready_poll)  # need to limit calls to 100 per  5 min - using 4 to allow other calls
        #else:
        #    self.my_setDriver('ST', 0)
            


def handleLevelChange(self, level):
    logging.info('New log level: {}'.format(level))
    new_level = resolve_log_level(level['level'])
    set_level = getattr(logging, 'setLevel', None)
    if callable(set_level):
        set_level(new_level)
    else:
        import logging as std_logging
        std_logging.getLogger().setLevel(new_level)



    
    '''
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






if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])


        polyglot.start(version)

        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        '''