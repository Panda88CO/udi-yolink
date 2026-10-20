#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""

import importlib

try:
    udi_interface = importlib.import_module('udi_interface')
except ImportError:
    from udi_interface_fallback import udi_interface

logging = udi_interface.LOGGER
Custom = udi_interface.Custom

from os import truncate
import threading
#import udi_interface
#import sys
import time
from yolinkSpeakerHubV3 import YoLinkSpeakerH

class udiYoSpeakerHub(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, start_done, configDoneHandler,  bool2ISY, node_queue, wait_for_node_done, checkNameSync, apply_profile_driver_names
    id = 'YOSPEAKERH'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Nodeserver Status'},
            {'driver': 'GV0', 'value': 7, 'uom': 56, 'name': 'Speaker volume'}, 
            {'driver': 'GV1', 'value': 0, 'uom': 25, 'name': 'Command Beep'}, 
            {'driver': 'GV2', 'value': 0, 'uom': 25, 'name': 'Mute'}, 
            {'driver': 'GV3', 'value': 0, 'uom': 25, 'name': 'Tone Type'}, 
            {'driver': 'GV4', 'value': 0, 'uom': 56, 'name': 'Message'}, 
            {'driver': 'GV5', 'value': 0, 'uom': 56, 'name': 'Repeat'},        
            {'driver': 'GV30', 'value': 99, 'uom': 25, 'name': 'Online State'},
            {'driver': 'GV20', 'value': 99, 'uom': 25, 'name': 'Connection State'}, 
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151, 'name': 'Last device update'},
            ]
    '''
       drivers = [
            'GV0' = Volume
            'GV1' = BeepEnable
            'GV2' = Mute
            'GV3' = Tone
            'GV5' = Repeat

            'ST' = Online
            ]

    ''' 
   

    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoSpeakerHub INIT- {}'.format(deviceInfo['name']))
        self.name = name
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.yoSpeakerHub = None
        self.node_ready = False
        self.configDone = False
        self.system_ready=False
        self._update_lock = threading.Lock()
        self.n_queue = []

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.CONFIGDONE, self.configDoneHandler)
   
        # start processing events and create add our controller node
        self.apply_profile_driver_names(self.id)
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
        self.node_ready = True




    def start(self):
        logging.info('start - udiYoSpeakerHub')
        while not self.node_ready  or not self.configDone:
            time.sleep(0.5)
        self.my_setDriver('GV30', 0)
        self.my_setDriver('ST', 0)
        self.yoSpeakerHub  = YoLinkSpeakerH(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.volume = 8
        self.yoSpeakerHub.setVolume(self.volume)
        self.beepEnabled = False
        self.yoSpeakerHub.setBeepEnable(self.beepEnabled)
        self.mute = False
        self.yoSpeakerHub.setMute(self.mute)
        self.tone = 'none'
        self.repeat = 0
        self.messageNbr = 0
        self.yoSpeakerHub.setMessageNbr(self.messageNbr )
        self.tone_list=['none','Emergency','Alert','Warn','Tip'] 
        self.yoSpeakerHub.initNode()
        time.sleep(1)
        tries = 1
        while not self.yoSpeakerHub.check_system_online():
            logging.info(f'Waiting for device {self.name} to come online...')
            time.sleep(min(60, 2 * tries))
            #if tries % 10 == 0:
                #self.yoSpeakerHub.refreshDevice()
            tries += 1
        #self.updateData()
        #self.my_setDriver('GV30', 1)
        #time.sleep(3)
        self.start_done()

    def bool2nbr (self, boolean):
        if boolean:
            return(1)
        else:
            return(0)
    '''
    def nbr2tone(self, tone):
        try:
            tones=['none','Emergency','Alert','Warn','Tip']  
            #for index in range(1,len(self.yoSpeakerHub.toneList)-1):
            #if tone == self.yoSpeakerHub.toneList[index]:
            return(self.tone_list.index(tone))
        except KeyError as e:
            logging.debug(f'Key error in tone2Nbr {e}')# if not found return None = 0
            return(0)
    '''


    def stop (self):
        logging.info('Stop udiYoSpeakerHub')
        self.my_setDriver('GV30', 0)
        self.my_setDriver('ST', 0)
        speaker_hub = self.yoSpeakerHub
        if speaker_hub is not None:
            speaker_hub.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)

    def _get_speaker_hub(self, caller):
        if self.yoSpeakerHub is None:
            logging.warning(f'udiYoSpeakerHub - {caller} skipped; speaker hub not initialized yet')
            return None
        return self.yoSpeakerHub
            
    def checkOnline(self):
        speaker_hub = self._get_speaker_hub('checkOnline')
        if speaker_hub is None:
            return
        speaker_hub.refreshDevice() 
        
    def checkDataUpdate(self):
        speaker_hub = self._get_speaker_hub('checkDataUpdate')
        if speaker_hub is None:
            return
        if speaker_hub.data_updated():
            self.updateData()

    def updateLastTime(self):
        pass

    def updateData(self):
        if self.node is not None:
            while not self.node_ready or not self.system_ready or not self.configDone:
                time.sleep(0.5)
            speaker_hub = self._get_speaker_hub('updateData')
            if speaker_hub is None:
                return
            message_info = speaker_hub.get_message_type()
            if not isinstance(message_info, tuple) or len(message_info) != 2:
                return
            message_type = message_info[0]
            message_action = message_info[1]
            self.my_setDriver('TIME', speaker_hub.getLastUpdateTime(), 151)
            logging.debug(f'TIME {speaker_hub.getLastUpdateTime()}')
            if speaker_hub.check_system_online():
                self.my_setDriver('GV0', self.volume, type=message_type )
                self.my_setDriver('GV1', self.bool2ISY(self.beepEnabled), type=message_type )
                self.my_setDriver('GV2', self.bool2ISY(self.mute), type=message_type )
                self.my_setDriver('GV3', self.tone_list.index(self.tone), type=message_type )
                self.my_setDriver('GV4', self.messageNbr, type=message_type )
                self.my_setDriver('ST', self.messageNbr, type=message_type )
                self.my_setDriver('GV5', self.repeat, type=message_type )
                self.my_setDriver('GV30', 1 )
                self.my_setDriver('ST', 1, type=message_type )
                if speaker_hub.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                     self.my_setDriver('GV20', 0)
            else:
                self.my_setDriver('GV30', 0)
                self.my_setDriver('ST', 0)
                self.my_setDriver('GV20', 2)
                #self.pollDelays()



    def updateStatus(self, data):
        logging.info('updateStatus - speakerHub')
        if self.yoSpeakerHub is not None:
            with self._update_lock:
                self.yoSpeakerHub.updateStatus(data)
            self.updateData()


    def setWiFi (self, command):
        logging.info('setWiFi')
        
    def setSSID (self, ssid):
        logging.info('setSSID')
        self.WiFiSSID = ssid

    def setPassword (self, password ):
        logging.info('setPassword')
        self.WiFipassword = password

    '''
    def setTone(self, command ):
        logging.info('udiYoSpeakerHub setTone')
        tone =int(command.get('value'))
        self.my_setDriver('GV3', tone )
        if tone == 0:
            self.yoSpeakerHub.setTone('none')
        elif tone == 1:
            self.yoSpeakerHub.setTone('Emergency')
        elif tone == 2:
            self.yoSpeakerHub.setTone('Alert')
        elif tone == 3:
            self.yoSpeakerHub.setTone('Warn')
        elif tone == 4:
            self.yoSpeakerHub.setTone('Tip')                        
  

    def setRepeat(self, command):
        logging.info('udiYoSpeakerHub setRepeat')
        self.repeat =int(command.get('value'))
        self.my_setDriver('GV5', self.repeat )
        self.yoSpeakerHub.setRepeat(self.repeat)
    '''
    def setMute(self, command):
        logging.info('udiYoSpeakerHub setMute')
        speaker_hub = self._get_speaker_hub('setMute')
        if speaker_hub is None:
            return
        mute = int(command.get('value'))
        #self.my_setDriver('GV2', self.yoSpeakerHub.mute )
        #mute =  mute == 1
        self.mute = mute == 1
        speaker_hub.setMute(self.mute)
    
    def setBeepEnable(self, command):
        logging.info('udiYoSpeakerHub setBeepEnable')
        speaker_hub = self._get_speaker_hub('setBeepEnable')
        if speaker_hub is None:
            return
        beepEn =int(command.get('value'))
        #self.my_setDriver('GV1', self.beepEn )
        self.beepEnabled = beepEn == 1
      
        speaker_hub.setBeepEnable(self.beepEnabled )
    '''
    def setVolume(self, command):
        logging.info('udiYoSpeakerHub setVolume')
        volume =int(command.get('value'))
        self.yoSpeakerHub.volume = volume
        self.my_setDriver('GV0',self.yoSpeakerHub.volume )
        self.yoSpeakerHub.setVolume(self.yoSpeakerHub.volume )

    def setMessage(self, command):
        logging.info('udiYoSpeakerHub setMessage')
        self.messageNbr =int(command.get('value'))
        self.my_setDriver('GV4',self.messageNbr )
        self.yoSpeakerHub.setMessageNbr(self.messageNbr )
        logging.info('udiYoSpeakerHub setMessage {} {}'.format(self.messageNbr, self.yoAccess.TtsMessages[self.messageNbr]))

    def playMessage(self, command = None ):
        logging.info('udiYoSpeakerHub playMessage')
        self.yoSpeakerHub.playAudio()
    '''
    def playMessageNew(self, command ):
        try:
            logging.info(f'udiYoSpeakerHub playMessage {command}')
            speaker_hub = self._get_speaker_hub('playMessageNew')
            if speaker_hub is None:
                return
            query = command.get("query")
            self.messageNbr = int(query.get("message.uom25"))
            self.message = self.yoAccess.TtsMessages[self.messageNbr]
            logging.debug(f'message: {self.message}')
            #self.my_setDriver('GV4',self.messageNbr )
            self.volume =  int(query.get("volume.uom56"))
            #self.my_setDriver('GV0',self.volume  )
            self.tone_nbr =  int(query.get("tone.uom25"))
            self.tone = self.tone_list[self.tone_nbr]
            #self.my_setDriver('GV3', self.tone_nbr )
            logging.debug(f'tone: {self.tone }')
            self.repeat = int(query.get("repeat.uom56"))
            speaker_hub.repeat = self.repeat
            #self.my_setDriver('GV5', self.yoSpeakerHub.repeat  )
            logging.debug(f'play: {self.message} {self.tone} {self.volume } {self.repeat}')
            speaker_hub.playAudio(self.message, self.tone,self.volume, self.repeat)
            
        except KeyError as e:
            logging.error(f'Error playng message {e}')

    def update(self, command = None):
        logging.info('udiYoSpeakerHub Update Status')
        speaker_hub = self._get_speaker_hub('update')
        if speaker_hub is None:
            return
        speaker_hub.refreshDevice()
        #self.yoSpeakerHub.refreshSchedules()     


    commands = {
                'UPDATE'    : update,
                #'QUERY'     : update,
                #'VOLUME'    : setVolume,
                'BEEP'      : setBeepEnable,
                'MUTE'      : setMute,
                #'TONE'      : setTone,
                #'REPEAT'    : setRepeat,
                #'MESSAGE'   : setMessage,
                'PLAY'      : playMessageNew,

    }



