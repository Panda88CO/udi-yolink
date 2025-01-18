

import time
from yolink_mqtt_classV3 import YoLinkMQTTDevice

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)




class YoLinkLeakSen(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(yoAccess,  deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report','Alert']
        yolink.waterName = 'WaterEvent'
        yolink.eventTime = 'Time'
        yolink.type = deviceInfo['type']
        #time.sleep(1)
        #yolink.refreshSensor()

    def refreshSensor(yolink):
        logging.debug('refreshLeakSensor')
        #time.sleep(2)
        if yolink.online:   
            return(yolink.refreshDevice())

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)
    '''
    def initNode(yolink):
        yolink.refreshDevice()
        #time.sleep(2)
        #yolink.online = yolink.getOnlineStatus()
        if not yolink.online:
            logging.error('Leak Sensor not online')
    '''
    
    def probeState(yolink):
         return(yolink.getState() )

    def probeData(yolink):
        return(yolink.getData() )

class YoLinkLeakSensor(YoLinkLeakSen):
    def __init__(yolink, yoAccess,  deviceInfo):
        super().__init__(   yoAccess,  deviceInfo, yolink.updateStatus)
        yolink.initNode()

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)
    

