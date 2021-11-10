import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

class YoLinkLeakSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey,  deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        self.methodList = ['getState' ]
        self.eventList = ['Report','Alert']
        self.waterName = 'WaterEvent'
        self.eventTime = 'Time'
        self.type = 'LeakSensor'
        time.sleep(1)
        self.refreshSensor()

    def refreshSensor(self):
        logging.debug('refreshWaterSensor')
        return(self.refreshDevice())

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
                    eventData[self.waterName] = self.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))
    '''
    
    def probeState(self):
         return(self.getState() )

    def probeData(self):
        return(self.getData() )

    

