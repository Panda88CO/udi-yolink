import json
import time


from yolink_mqtt_classV2 import YoLinkMQTTDevice
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
        yolink.volume = 5
        yolink.methodList = ['getState', 'setWiFi', 'playAudio', 'setOption' ]
        yolink.eventList = ['StatusChange', 'Report', 'getState']
        yolink.toneList = ['emergency', 'alert', 'warn', 'tip', 'none']
        yolink.eventTime = 'Time'
        yolink.type = 'SpeakerHub'
        #time.sleep(2)
        #print('yolink.refreshState')
        #yolink.refreshState()
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished initailizing')

    ''' Assume no event support needed if using MQTT'''
    def updataStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)
    '''
    def initNode(yolink):
        yolink.refreshState()
        time.sleep(2)
        if not yolink.online:
            logging.error('Switch not online')
        #    yolink.refreshSchedules()
        #else:
            
        #yolink.refreshFWversion()
        #print(' YoLinkSW - finished intializing')
    
    
    def getDelays(yolink):
        return super().getDelays()
    '''
    def getWiFiInfo(yolink):
        logging.debug('getWiFiInfo')
        return(yolink.dataAPI['lastMessage']['data']['wifi'])

    def getEthernetInfo(yolink):
        logging.debug('getEthernetInfo')
        return(yolink.dataAPI['lastMessage']['data']['eth'])

    def getOptionInfo(yolink):
        logging.debug('getOptionInfo')
        return(yolink.dataAPI['lastMessage']['data']['options'])

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
        while  not yolink.publish_data( data) and attempt <= maxAttempts:
               time.sleep(1)
               attempt = attempt + 1
        yolink.lastControlPacket = data



    
    def playAudio(yolink, tone, volume=-1, message='', repeat=0):
        logging.debug(yolink.type+' - playAudio')
        maxAttempts = 3
        #missing try
        data = {}

        data['method'] = yolink.type+'.playAudio'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        data['params'] = {}
        if tone in yolink.toneList and tone.lower() != 'none':
            tone= tone.capitalize()
            data['params']['tone'] = tone
        if volume <0 and volume > 16:
            volume = yolink.volume
        data['params']['volume'] = volume

        if message != '':
            if len(message ) > 200:
               message = message[0:200]
            data['params']['message'] = message
        if repeat >= 0 and repeat <= 10:
            data['params']['repeat'] = repeat
        while  not yolink.publish_data( data) and attempt <= maxAttempts:
               time.sleep(1)
               attempt = attempt + 1
        yolink.lastControlPacket = data


    def setOptions(yolink, volume, beep=False, mute=False):
        logging.debug(yolink.type+' - setOptions')
        maxAttempts = 3
        #missing try
        data = {}
        data['method'] = yolink.type+'.setOption'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token']
        data['params'] = {}
        if volume >0 and volume <= 16:
            data['params']['volume'] = volume
            yolink.volume = volume
        data['params']['enableBeep'] = beep
        data['params']['mute'] = mute
        while  not yolink.publish_data( data) and attempt <= maxAttempts:
               time.sleep(1)
               attempt = attempt + 1
        yolink.lastControlPacket = data


    def getState(yolink):
        logging.debug(yolink.type+' - getState')
        attempts = 0

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
    def getEnergy(yolink):
        logging.debug(yolink.type+' - getEnergy')
        return({'power':yolink.dataAPI[yolink.dData][yolink.dState]['power'], 'watt':yolink.dataAPI[yolink.dData][yolink.dState]['power']})
    '''

class YoLinkSpeakerHub(YoLinkSpeakerH):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(  yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()


    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)

