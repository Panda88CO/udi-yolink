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
from yolinkSpeakerHubV2 import YoLinkSpeakerH

class udiYoSpeakerHub(udi_interface.Node):
  
    id = 'yospeakerh'
    drivers = [
            {'driver': 'GV0', 'value': 5, 'uom': 12}, 
            {'driver': 'GV1', 'value': 0, 'uom': 25}, 
            {'driver': 'GV2', 'value': 0, 'uom': 25}, 
            {'driver': 'GV3', 'value': 0, 'uom': 25}, 
            {'driver': 'GV4', 'value': 0, 'uom': 25}, 
            {'driver': 'GV5', 'value': 0, 'uom': 0},        
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]
    '''
       drivers = [
            'GV0' = Volume
            'GV1' = BeepEnable
            'GV2' = Mute
            'GV3' = Tone
            'GV4' = MessageStr
            'GV5' = Repeat

            'GV8' = Online
            ]

    ''' 

    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        logging.debug('udiYoSpeakerHub INIT- {}'.format(deviceInfo['name']))
        self.devInfo =  deviceInfo   
        self.yoAccess = yoAccess
        self.yoSpeakerHub = None

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []        

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)
    
    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()


    def start(self):
        logging.info('start - udiYoSpeakerHub')
        self.yoSpeakerHub  = YoLinkSpeakerH(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(2)
        self.yoSpeakerHub.initNode()
        
        if not self.yoSpeakerHub.online:
            logging.error('Device {} not on-line - remove node'.format(self.devInfo['name']))
            self.yoSpeakerHub.shut_down()
            self.poly.delNode(self.node)
        else:
            self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    def updateDelayCountdown (self, delayRemaining ) :
        logging.debug('updateDelayCountdown {}'.format(delayRemaining))

    def stop (self):
        logging.info('Stop udiYoSpeakerHub')
        self.node.setDriver('ST', 0, True, True)
        self.yoSpeakerHub.shut_down()

    def checkOnline(self):
        self.yoSpeakerHub.refreshDevice() 

    def updateStatus(self, data):
        logging.info('updateStatus - speakerHub')
        self.yoSpeakerHub.updateCallbackStatus(data)

        if self.node is not None:
            state =  self.yoSpeakerHub.getState().upper()
            if self.yoSpeakerHub.online:
                logging.debug('testing text')
                #if state == 'ON':
                #    self.node.setDriver('GV0', 1, True, True)
                #elif  state == 'OFF':
                #    self.node.setDriver('GV0', 0, True, True)
                #else:
                #    self.node.setDriver('GV0', 99, True, True)
                #self.node.setDriver('GV8', 1, True, True)
            else:
                self.node.setDriver('GV8', 0, True, True)
                #self.pollDelays()
           
    def setWiFi (self, command):
        logging ('setWiFi')
        
    def setSSID (self, ssid):
        logging ('setSSID')
        self.WiFiSSID = ssid

    def setPassword (self, password ):
        logging ('setPassword')
        self.WiFipassword = password
        
    def getMessage(self, command):
        logging.info('udiYoSpeakerHub getMesage')
        state = int(command.get('value'))     
        if state == 1:
            self.yoSpeakerHub.setState('ON')
        else:
            self.yoSpeakerHub.setState('OFF')
        
    def setTone(self, command ):
        logging.info('udiYoSpeakerHub setTone')
        tone =int(command.get('value'))

        self.node.setDriver('GV3', tone, True, True)

    def setRepeat(self, command):
        logging.info('udiYoSpeakerHub setRepeat')
        repeat =int(command.get('value'))
        self.node.setDriver('GV5', repeat, True, True)

    def setMute(self, command = None):
        logging.info('udiYoSpeakerHub setMute')
        mute = int(command.get('value'))
        self.node.setDriver('GV2', mute, True, True)
    
    def setBeepEnable(self, command = None):
        logging.info('udiYoSpeakerHub setBeepEnable')
        beepEn =int(command.get('value'))
        self.node.setDriver('GV1',beepEn, True, True)

    def setVolume(self, command = None):
        logging.info('udiYoSpeakerHub setVolume')
        volume =int(command.get('value'))
        self.node.setDriver('GV0',volume, True, True)

    def inputMessage(self, command = None):
        logging.info('udiYoSpeakerHub inputMessage')
        message = command.get('value')
        self.node.setDriver('GV4',message, True, True)

    def playMessage(self, command = None ):
        logging.info('udiYoSpeakerHub playMessage')
        state = int(command.get('value'))     
        if state == 1:
            self.yoSpeakerHub.setState('ON')
        else:
            self.yoSpeakerHub.setState('OFF')
    
    def update(self, command = None):
        logging.info('udiYoSpeakerHub Update Status')
        self.yoSpeakerHub.refreshState()
        #self.yoSpeakerHub.refreshSchedules()     


    commands = {
                'UPDATE'    : update,
                'BEEP'      : setBeepEnable,
                'MUTE'      : setMute,
                'REPEAT'    : setRepeat,
                'VOLUME'    : setVolume,
                'TONE'      : setTone,
                'TTSMESSAGE': inputMessage,
                'PLAY'      : playMessage,

    }


