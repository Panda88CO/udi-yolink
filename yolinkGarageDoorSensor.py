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
from yolink_mqtt_class1 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

class YoLinkGarageDoorSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num,  updateTimeSec):
        logging.debug('YoLinkGarageDoorSensor init') 
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)

        self.methodList = ['DoorSensor.getState' ]
        self.eventList = ['DoorSensor.Report']
        self.GarageName = 'GarageEvent'
        self.eventTime = 'Time'

        self.connect_to_broker()
        self.loopTimesec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimesec  )
        time.sleep(2)
        self.refreshGarageDoorSensor()
  
    def refreshGarageDoorSensor(self):
        logging.debug('refreshGarageDoorSensor') 
        return(self.refreshDevice( 'DoorSensor.getState', self.updateStatus))


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

    
    def DoorState(self):
         return(self.getState())
    


