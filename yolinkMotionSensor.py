import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_class import YoLinkMQTTDevice


class YoLinkMotionSen(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Alert' , 'getState', 'StatusChange']
        yolink.eventName = 'MotionEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'MotionSensor'
        time.sleep(2)
       

    def initNode(yolink):
        yolink.refreshDevice()
    
    def refreshSensor(yolink):
        yolink.refreshDevice()

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def motionState(yolink):
        return(yolink.getState())
    
    def motionData(yolink):
        return(yolink.getData())         

class YoLinkMotionSensor(YoLinkMotionSen):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, deviceInfo, yolink.updateStatus, yolink_URL, mqtt_URL, mqtt_port)
        yolink.initNode()

    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)