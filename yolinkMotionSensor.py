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
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        self.YolinkSensor = YoLinkMQTTDevice(csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, self.updateStatus)
        self.methodList = ['MotionSensor.getState' ]
        self.eventList = ['MotionSensor.Alert' , 'MotionSensor.getState', 'MotionSensor.StatusChange']
        self.loopTimeSec = updateTimeSec

        self.eventName = 'MotionEvent'
        self.eventTime = 'Time'

        
        #self.YolinkSensor.monitorLoop(self.updateStatus, self.loopTimeSec  )
        time.sleep(2)
        self.refreshSensor()

    def refreshSensor(self):
        return(self.YolinkSensor.refreshDevice('MotionSensor.getState',  self.updateStatus, ))

    def updateStatus(self, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.YolinkSensor.getLastUpdate()):
                     self.YolinkSensor.updateStatusData(data)
        elif 'event' in data:
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.YolinkSensor.getLastUpdate()):
                    self.YolinkSensor.updateStatusData(data)
                    eventData = {}
                    eventData[self.eventName] = self.YolinkSensor.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.YolinkSensor.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    def motionState(self):
        return(self.YolinkSensor.getState())


    def getMotionData(self):
        return(self.YolinkSensor.getState())         

'''
class YoLinkMotionSensor(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)

        self.methodList = ['MotionSensor.getState' ]
        self.eventList = ['MotionSensor.Alert' , 'MotionSensor.getState', 'MotionSensor.StatusChange']
        self.loopTimeSec = updateTimeSec

        self.eventName = 'MotionEvent'
        self.eventTime = 'Time'

        self.connect_to_broker()
        self.loopTimeSec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimeSec  )
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
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))

    def motionState(self):
        return(self.getState())


    def getMotionData(self):
        return(self.dataAPI[self.deviceData])         
'''

