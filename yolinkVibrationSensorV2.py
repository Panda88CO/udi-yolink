import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_classV2 import YoLinkMQTTDevice


class YoLinkVibrationSen(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Alert' , 'getState', 'StatusChange']
        yolink.eventName = 'VibrationEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'VibrationSensor'
        #time.sleep(2)
       
    
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def getVibrationState(yolink):
        return(yolink.getState())
    
def refreshSensor(yolink):
        logging.debug(yolink.type+ ' - refreshSensor')
        return(yolink.refreshDevice( ))


class YoLinkVibrationSensor(YoLinkVibrationSen):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__( yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)