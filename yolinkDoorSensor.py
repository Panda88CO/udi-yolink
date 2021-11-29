import json
import time
import logging

from yolink_mqtt_class import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

class YoLinkDoorSensor(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report']
        yolink.GarageName = 'GarageEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'DoorSensor'

        time.sleep(2)
        yolink.refreshDoorSensor()
  
    def refreshDoorSensor(yolink):
        logging.debug(yolink.type+ ' - refreshDoorSensor') 
        return(yolink.refreshDevice( ))

    def doorState(yolink):
        return(yolink.getState())

    def doorData(yolink):
        return(yolink.getData())
        
    


