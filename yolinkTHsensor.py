import json
import time
import logging

from yolink_mqtt_class1 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

class YoLinkTHSensor(YoLinkMQTTDevice):

    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)    
        self.methodList = ['THSensor.getState' ]
        self.eventList = ['THSensor.Report']
        self.tempName = 'THEvent'
        self.temperature = 'Temperature'
        self.humidity = 'Humidity'
        self.eventTime = 'Time'

        time.sleep(2)
        self.refreshSensor()
        
    def refreshSensor(self):
        logging.debug('refreshTHsensor')
        return(self.refreshDevice('THSensor.getState',  self.updateStatus, ))

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
                    eventData[self.tempName] = self.getState()
                    eventData[self.temperature] = self.getTempValueC()
                    eventData[self.humidity] = self.getHumidityValue()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))


    def getTempValueF(self):
        return(self.getInfoValue('temperature')*9/5+32)
    
    def getTempValueC(self):
        return(self.getInfoValue('temperature'))

    def getHumidityValue(self):
        return(self.getInfoValue('humidity'))

    def getAlarms(self):
        return(self.getInfoValue('alarms'))