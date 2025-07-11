#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

from os import truncate
#import udi_interface
#import sys
import time
from yolinkSpeakerHubV3 import YoLinkSpeakerH

class udiYoSpeakerHub(udi_interface.Node):
    from  udiYolinkLib import my_setDriver
    id = 'yospeakerh'
    drivers = [
            {'driver': 'GV0', 'value': 7, 'uom': 56}, 
            {'driver': 'GV1', 'value': 0, 'uom': 25}, 
            {'driver': 'GV2', 'value': 0, 'uom': 25}, 
            {'driver': 'GV3', 'value': 0, 'uom': 25}, 
            {'driver': 'GV4', 'value': 0, 'uom': 56}, 
            {'driver': 'GV5', 'value': 0, 'uom': 56},        
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 99, 'uom': 25}, 
            {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},
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
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.yoSpeakerHub = None
        self.node_ready = False
        self.n_queue = []

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
   
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)
    
    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()



    def start(self):
        logging.info('start - udiYoSpeakerHub')
        self.my_setDriver('ST', 0)
        self.yoSpeakerHub  = YoLinkSpeakerH(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoSpeakerHub.volume = 5
        self.yoSpeakerHub.beepEnabled = False
        self.yoSpeakerHub.mute = False
        self.yoSpeakerHub.tone = 'none'
        self.yoSpeakerHub.repeat = 0
        self.messageNbr = 0
        self.yoSpeakerHub.setMessageNbr(self.messageNbr )
        self.yoSpeakerHub.initNode()
        self.node_ready = True
        #self.my_setDriver('ST', 1)
        #time.sleep(3)

 
    def bool2nbr (self, boolean):
        if boolean:
            return(1)
        else:
            return(0)
    
    def tone2nbr(self, tone):
        try:
            tones=['none','Emergency','Alert','Warn','Tip']  
            #for index in range(1,len(self.yoSpeakerHub.toneList)-1):
            #if tone == self.yoSpeakerHub.toneList[index]:
            return(tones[tone])
        except KeyError as e:
            logging.debug(f'Key error in tone2Nbr {e}')# if not found return None = 0
            return(0)

    def msg2nbr(self, msg):
        #dummy for now
        return(0)


    def stop (self):
        logging.info('Stop udiYoSpeakerHub')
        self.my_setDriver('ST', 0)
        self.yoSpeakerHub.shut_down()
        #if self.node:
        #    self.poly.delNode(self.node.address)
            
    def checkOnline(self):
        self.yoSpeakerHub.refreshDevice() 
        
    def checkDataUpdate(self):
        if self.yoSpeakerHub.data_updated():
            self.updateData()

    def updateLastTime(self):
        pass

    def updateData(self):
        if self.node is not None:
            #state =  self.yoSpeakerHub.getState().upper()
            if self.yoSpeakerHub.online:
                self.my_setDriver('GV0', self.yoSpeakerHub.volume)
                self.my_setDriver('GV1', self.bool2nbr(self.yoSpeakerHub.beepEnabled))
                self.my_setDriver('GV2', self.bool2nbr(self.yoSpeakerHub.mute))
                self.my_setDriver('GV3', self.tone2nbr(self.yoSpeakerHub.tone))
                self.my_setDriver('GV4', self.messageNbr)
                self.my_setDriver('GV5', self.yoSpeakerHub.repeat)
                self.my_setDriver('ST', 1)
                if self.yoSpeakerHub.suspended:
                    self.my_setDriver('GV20', 1)
                else:
                     self.my_setDriver('GV20', 0)
            else:
                self.my_setDriver('ST', 0)
                self.my_setDriver('GV20', 2)
                #self.pollDelays()



    def updateStatus(self, data):
        logging.info('updateStatus - speakerHub')
        self.yoSpeakerHub.updateStatus(data)
        self.updateData()


    def setWiFi (self, command):
        logging ('setWiFi')
        
    def setSSID (self, ssid):
        logging ('setSSID')
        self.WiFiSSID = ssid

    def setPassword (self, password ):
        logging ('setPassword')
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
        self.mute = int(command.get('value'))
        self.my_setDriver('GV2', self.mute )
        if self.mute == 1:
            self.yoSpeakerHub.mute = True
        else:
            self.yoSpeakerHub.mute = False
    
    def setBeepEnable(self, command):
        logging.info('udiYoSpeakerHub setBeepEnable')
        self.beepEn =int(command.get('value'))
        self.my_setDriver('GV1', self.beepEn )
        if self.beepEn == 1:
            self.yoSpeakerHub.beepEnabled = True
        else:
            self.yoSpeakerHub.beepEnabled = False
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
            query = command.get("query")
            self.message_nbr = int(query.get("message.uom25"))
            message = self.yoAccess.TtsMessages[self.message_nbr]
            logging.debug(f'message: {message}')
            self.my_setDriver('GV4',self.message_nbr )
            self.yoSpeakerHub.volume =  int(query.get("volume.uom56"))
            self.my_setDriver('GV0',self.yoSpeakerHub.volume  )
            tone_nbr =  int(query.get("tone.uom25"))
            self.yoSpeakerHub.tone = self.tone2nbr([tone_nbr])
            self.my_setDriver('GV3', tone_nbr )
            logging.debug(f'tone: {self.yoSpeakerHub.tone }')
            self.yoSpeakerHub.repeat = int(query.get("repeat.uom56"))
            self.my_setDriver('GV5', self.yoSpeakerHub.repeat  )
            logging.debug(f'play: {message} {self.yoSpeakerHub.tone} {self.yoSpeakerHub.volume } {self.yoSpeakerHub.repeat}')
            self.yoSpeakerHub.playAudio(message, self.yoSpeakerHub.tone,self.yoSpeakerHub.volume, self.yoSpeakerHub.repeat)
            
        except KeyError as e:
            logging.error(f'Error playng message {e}')

    def update(self, command = None):
        logging.info('udiYoSpeakerHub Update Status')
        self.yoSpeakerHub.refreshDevice()
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


