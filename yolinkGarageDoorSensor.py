import json
import time
import logging

from yolink_mqtt_class import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

class YoLinkGarageDoorSensor(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)
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

    '''
    def updateStatus(yolink, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in yolink.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(yolink.getLastUpdate()):
                     yolink.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in yolink.eventList:
                if int(data['time']) > int(yolink.getLastUpdate()):
                    yolink.updateStatusData(data)
                    eventData = {}
                    eventData[yolink.GarageName] = yolink.getState()
                    eventData[yolink.eventTime] = yolink.data[yolink.messageTime]
                    yolink.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))
    '''
    
    def doorState(yolink):
        return(yolink.getState())

    def doorData(yolink):
        return(yolink.getData())
    


