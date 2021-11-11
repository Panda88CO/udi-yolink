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
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Alert' , 'getState', 'StatusChange']


        yolink.eventName = 'MotionEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'MotionSensor'
        time.sleep(2)
        yolink.refreshDevice()

    def refreshSensor(yolink):
        yolink.refreshDevice()
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
                    eventData[yolink.eventName] = yolink.getState()
                    eventData[yolink.eventTime] = data[yolink.messageTime]
                    yolink.eventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))
    '''
    def motionState(yolink):
        return(yolink.getState())
    

    def motionData(yolink):
        return(yolink.getData())         

