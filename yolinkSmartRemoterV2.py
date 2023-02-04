import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_classV3 import YoLinkMQTTDevice


class YoLinkSmartRemote(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Alert' , 'getState', 'StatusChange']
        yolink.eventName = 'SmartRemoteEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'SmartRemoter'
        #time.sleep(2)
       
    
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)


    def getDevTemperature(yolink):
        temp = yolink.getStateValue('devTemperature')
        logging.debug('getDevTemperature: {}'.format(temp))
        return(temp)

    def getEventData(yolink):
        temp = yolink.get_event_from_state()
        logging.debug('getEventData: {}'.format(temp))
        return(temp)


class YoLinkSmartRemoter(YoLinkSmartRemote):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__( yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)