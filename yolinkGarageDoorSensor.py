import json
import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

from yolink_mqtt_class import YoLinkMQTTDevice


class YoLinkGarageDoorSen(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report']
        yolink.GarageName = 'GarageEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'DoorSensor'

        time.sleep(2)
        yolink.refreshGarageDoorSensor()
  
    def refreshGarageDoorSensor(yolink):
        logging.debug('refreshGarageDoorSensor') 
        return(yolink.refreshDevice( ))

    def initNode(yolink):
        yolink.refreshDevice()
    
    def updataStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def doorState(yolink):
        return(yolink.getState())

    def doorData(yolink):
        return(yolink.getData())
    


class YoLinkGarageDoorSensor(YoLinkGarageDoorSen):        
    def __init__(yolink, csName, csid, csseckey,  deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, deviceInfo, yolink.updateStatus, yolink_URL, mqtt_URL, mqtt_port)    
        yolink.initNode()

    # Enable Event Support (True below)
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)