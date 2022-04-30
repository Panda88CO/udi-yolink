import json
import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_classV2 import YoLinkMQTTDevice


class YoLinkHu(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState', 'setWiFi' ]
        yolink.eventList = ['Report']
        yolink.HubName = 'HubEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'Hub'
        yolink.refreshHub()
  
    def refreshHub(yolink):
        logging.debug('refreshHub') 
        return(yolink.refreshDevice( ))

    
    def updataStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

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


class YoLinkHub(YoLinkHu):        
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__( yoAccess,  deviceInfo,  yolink.updateStatus)    
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)