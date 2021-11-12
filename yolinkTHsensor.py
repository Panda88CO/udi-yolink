import json
import time
import logging

from yolink_mqtt_class import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

class YoLinkTHSensor(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey,  deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)    
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Report']
        yolink.tempName = 'THEvent'
        yolink.temperature = 'Temperature'
        yolink.humidity = 'Humidity'
        yolink.eventTime = 'Time'
        yolink.type = 'THSensor'

        time.sleep(2)
        yolink.refreshSensor()
        
    def refreshSensor(yolink):
        logging.debug(yolink.type+ ' - refreshSensor')
        return(yolink.refreshDevice( ))

    def getTempValueF(yolink):
        return(yolink.getInfoValue('temperature')*9/5+32)
    
    def getTempValueC(yolink):
        return(yolink.getInfoValue('temperature'))

    def getHumidityValue(yolink):
        return(yolink.getInfoValue('humidity'))

    def getAlarms(yolink):
        return(yolink.getInfoValue('alarms'))

    def probeState(yolink):
         return(yolink.getState() )

    def probeData(yolink):
        return(yolink.getData() )