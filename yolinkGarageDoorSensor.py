import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

class YoLinkGarageDoorSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        self.methodList = ['DoorSensor.getState' ]
        self.eventList = ['DoorSensor.Report']
        self.GarageName = 'GarageEvent'
        self.eventTime = 'Time'
        self.type = 'DoorSensor'

        time.sleep(2)
        self.refreshGarageDoorSensor()
  
    def refreshGarageDoorSensor(self):
        logging.debug('refreshGarageDoorSensor') 
        return(self.refreshDevice( ))

    '''
    def updateStatus(self, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                     self.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    eventData = {}
                    eventData[self.GarageName] = self.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))
    '''
    
    def doorState(self):
        return(self.getState())

    def doorData(self):
        return(self.getData())
    


