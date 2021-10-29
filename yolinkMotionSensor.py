import hashlib
import json
import os
import sys
import time
import threading
import paho.mqtt.client as mqtt
import logging
import datetime
import pytz

from queue import Queue
from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)



class YoLinkMotionSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        self.methodList = ['MotionSensor.getState' ]
        self.eventList = ['MotionSensor.Alert' , 'MotionSensor.getState', 'MotionSensor.StatusChange']


        self.eventName = 'MotionEvent'
        self.eventTime = 'Time'
        time.sleep(2)
        self.refreshSensor()

    def refreshSensor(self):
        return(self.refreshDevice('MotionSensor.getState',  self.updateStatus, ))

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
                    eventData[self.eventName] = self.getState()
                    eventData[self.eventTime] = data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    def motionState(self):
        return(self.getState())


    def getMotionData(self):
        return(self.getState())         

