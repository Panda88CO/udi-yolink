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
from yolink_mqtt_class import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)



class YoLinkMotionSen(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)
        yolink.methodList = ['getState' ]
        yolink.eventList = ['Alert' , 'getState', 'StatusChange']


        yolink.eventName = 'MotionEvent'
        yolink.eventTime = 'Time'
        yolink.type = 'MotionSensor'
        time.sleep(2)
        yolink.refreshDevice()

    def initNode(yolink):
        yolink.refreshDevice()
    
    def refreshSensor(yolink):
        yolink.refreshDevice()

    def updataStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)

    def motionState(yolink):
        return(yolink.getState())
    
    def motionData(yolink):
        return(yolink.getData())         

class YoLinkMotionSensor(YoLinkMotionSen):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, yolink.updateStatus)
        yolink.initNode()

    def updataStatus(yolink, data):
        yolink.updateCallbackStatus(data, True)