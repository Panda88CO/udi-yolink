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
        
    


