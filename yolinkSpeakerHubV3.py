#import json
import time

from yolink_mqtt_classV3 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class YoLinkSpeakerH(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.WiFipassword = ''
        yolink.WiFiSSID = ''
        yolink.methodList = ['getState', 'setWiFi', 'playAudio', 'setOption' ]
        yolink.eventList = ['StatusChange', 'Report', 'getState']
        yolink.toneList = ['none', 'Emergency', 'Alert', 'Warn', 'Tip'] #index used
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']

        yolink.volume = 5
        yolink.repeat = 0
        yolink.mute = False
        yolink.tone = None
        yolink.beepEnabled = False
        yolink.TtsMessageNbr = 0
        #time.sleep(2)
        #print('yolink.refreshState')
        #yolink.refreshState()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished initailizing')

    ''' Assume no event support needed if using MQTT'''
    def updateStatus(yolink, data):
        print('SpeakerHub update data {}'.format(data))
        yolink.updateCallbackStatus(data, False)
        if data['code'] == '000000':
                if  '.getState' in data['method'] :
                    yolink.volume = data['data']['options']['volume']
                    yolink.mute = data['data']['options']['mute']
                    yolink.beepEnabled = data['data']['options']['enableBeep']
             
 

    def getWiFiInfo(yolink):
        logging.debug('getWiFiInfo')
        if 'data' in yolink.dataAPI['lastMessage']:
            if 'wifi' in yolink.dataAPI['lastMessage']['data']:
                return(yolink.dataAPI['lastMessage']['data']['wifi'])
        else:
            return(None)

    def getEthernetInfo(yolink):
        logging.debug('getEthernetInfo')
        if 'data' in yolink.dataAPI['lastMessage']:
            if 'eth' in yolink.dataAPI['lastMessage']['data']:
                return(yolink.dataAPI['lastMessage']['data']['eth'])
        else:
            return(None)
            
    def getOptionInfo(yolink):
        logging.debug('getOptionInfo')
        return({'volume':yolink.volume, 'mute':yolink.mute, 'enableBeep':yolink.beepEnabled})

    def setWiFi (yolink, SSID, password):
        logging.debug(yolink.type+' - setWiFi')
        maxAttempts = 3
        if password != '' and SSID != '':
            data = {}
            data['params'] = {}
            data['method'] = yolink.type+'.setWiFi'
            data["targetDevice"] =  yolink.deviceInfo['deviceId']
            data["token"]= yolink.deviceInfo['token']
            data['params']['ssid'] = SSID
            data['params']['password'] = password
        while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
               time.sleep(1)
               attempt = attempt + 1
        yolink.lastControlPacket = data

    def setVolume(yolink, volume):
        logging.debug(yolink.type+' - setVolume: {}'.format(volume))
        yolink.volume = volume
        if yolink.volume < 0:
            yolink.volume = 0 
        if yolink.volume> 16:
            yolink.volume = 16
        yolink.setOptions()
        return(yolink.volume)

    def setRepeat(yolink, repeat):
        logging.debug(yolink.type+' - setRepat: {}'.format(repeat))
        yolink.repeat = repeat
        if yolink.repeat < 0:
            yolink.repeat = 0

        if yolink.repeat > 10:
            yolink.repeat = 10
        
        return(yolink.repeat)

    def setMute(yolink, mute):
        logging.debug(yolink.type+' - setMute: {}'.format(mute))
        yolink.mute = mute
        yolink.setOptions()

    def setBeepEnable(yolink, beep):
        logging.debug(yolink.type+' - setMute: {}'.format(beep))
        yolink.beepEnabled = beep
        yolink.setOptions()

    def setTone(yolink, tone):
        logging.debug(yolink.type+' - setTone: {}'.format(tone))
        if tone.capitalize() in yolink.toneList and tone.lower() != 'none' and tone:
            yolink.tone= tone
        else:
            yolink.tone = None
    
    def setMessageNbr(yolink, messageNbr):
        if messageNbr > 0:
            #logging.debug(yolink.type+' - setMessage: {} = {}'.format(messageNbr, yolink.yoAccess.TtsMessages[messageNbr]))
            yolink.TtsMessageNbr = messageNbr


def playAudio(yolink, message_nbr, ):
        logging.debug(yolink.type+' - playAudio')
        maxAttempts = 3
        attempt = 0
        #missing try
        message = yolink.yoAccess.TtsMessages[message_nbr]
        data = {}
        data['method'] = yolink.type+'.playAudio'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        data['params'] = {}
        data['params']['tone'] = yolink.tone
        data['params']['volume'] = yolink.volume
        data['params']['repeat'] = yolink.repeat
        if len(message ) > 200:
            message = message[0:200]
        data['params']['message'] = message
        logging.debug('playAudio: {}'.format(data))
        while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
               time.sleep(4)
               attempt = attempt + 1
        yolink.lastControlPacket = data

    '''
    def playAudio(yolink):
        logging.debug(yolink.type+' - playAudio')
        maxAttempts = 3
        attempt = 0
        #missing try
        message = yolink.yoAccess.TtsMessages[yolink.TtsMessageNbr]
        data = {}
        data['method'] = yolink.type+'.playAudio'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        data['params'] = {}
        data['params']['tone'] = yolink.tone
        data['params']['volume'] = yolink.volume
        data['params']['repeat'] = yolink.repeat
        if len(message ) > 200:
            message = message[0:200]
        data['params']['message'] = message
        logging.debug('playAudio: {}'.format(data))
        while  not yolink.yoAccess.publish_data( data) and attempt <= maxAttempts:
               time.sleep(4)
               attempt = attempt + 1
        yolink.lastControlPacket = data
    '''

    def setOptions(yolink):
        logging.debug(yolink.type+' - setOptions')
        maxAttempts = 3
        attempt = 1
        #missing try
        data = {}
        data['method'] = yolink.type+'.setOption'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        data['params'] = {}
        data['params']['volume'] = yolink.volume
        data['params']['enableBeep'] = yolink.beepEnabled
        data['params']['mute'] = yolink.mute
        print('dataStr: {}'.format(data))
        yolink.yoAccess.publish_data( data)
        yolink.lastControlPacket = data

    '''
    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        attempts = 0
        yolink.refreshDevice
        while yolink.dState not in yolink.dataAPI[yolink.dData] and attempts < 5:
            time.sleep(1)
            attempts = attempts + 1
        if attempts < 5 and 'state' in yolink.dataAPI[yolink.dData][yolink.dState]:
            if  yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'open':
                return('on')
            elif yolink.dataAPI[yolink.dData][yolink.dState]['state'] == 'closed':
                return('off')
            else:
                return('Unkown')
        else:
            return('Unkown')
    '''
 

class YoLinkSpeakerHub(YoLinkSpeakerH):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        #yolink.updateStatus(data) 
        print('SpeakerHub update data {}'.format(data))
        if 'method' in  data:
            if data['code'] == '000000':                
                yolink.online = yolink.checkOnlineStatus(data)
                if  '.setWiFi' in data['method'] :
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        #yolink.updateStatusData(data)       
                        logging.debug('Do Nothing for now')
                elif  '.playAudio' in data['method'] :
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        logging.debug('Do Nothing for now')
                        #yolink.updateStatusData(data)      
                elif  '.setOption' in data['method'] :
                    if int(data['time']) > int(yolink.getLastUpdate()):
                        logging.debug('Do Nothing for now')
                        #yolink.updateStatusData(data)   
                elif  '.getState' in data['method'] :
                    if int(data['time']) > int(yolink.getLastUpdate()):
                       yolink.updateOptionData(data)   
                yolink.updateCallbackStatus(data, True)
            else:
                yolink.deviceError(data)
                yolink.online = yolink.checkOnlineStatus(data)
                logging.error(yolink.type+ ': ' + data['desc'])
        else:
            yolink.updateCallbackStatus(data, True)

