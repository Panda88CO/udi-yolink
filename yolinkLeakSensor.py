

import time
from yolink_mqtt_class import YoLinkMQTTDevice

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)




class YoLinkLeakSen(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey,  deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report','Alert']
        yolink.waterName = 'WaterEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'LeakSensor'
        time.sleep(1)
        #yolink.refreshSensor()

    def refreshSensor(yolink):
        logging.debug('refreshWaterSensor')
        return(yolink.refreshDevice())

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def initNode(yolink):
        yolink.refreshDevice()
        yolink.online = yolink.getOnlineStatus()
        if not yolink.online:
            logging.error('Leak Sensor not online')
    
    def probeState(yolink):
         return(yolink.getState() )

    def probeData(yolink):
        return(yolink.getData() )

class YoLinkLeakSensor(YoLinkLeakSen):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, deviceInfo, yolink.updateStatus, yolink_URL, mqtt_URL, mqtt_port)
        yolink.initNode()

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)
    

