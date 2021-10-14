#!/usr/bin/env python3

import time
import pytz
import json
import requests
import threading
#from logger import getLogger
from yolink_devices import YoLinkDevice
#from yolink_mqtt_client import YoLinkMQTTClient
from yolink_mqtt_device import YoLinkMultiOutlet
from yolink_mqtt_device import YoLinkTHSensor
from yolink_mqtt_device import YoLinkWaterSensor
from yolink_mqtt_device import YoLinkManipulator
#from oauthlib.oauth2 import BackendApplicationClient
#from requests.auth import HTTPBasicAuth
#from rauth import OAuth2Service
from requests_oauthlib import OAuth2Session




yolinkURL =  'https://api.yosmart.com/openApi' 
mqttURL = 'api.yosmart.com'
csid = 'XXXX'
csseckey = 'XXX'
csName = 'XX'

description = 'Enable Sensor APIs and subscribe to MQTT broker'

device_list = {}

'''

'''
device_serial_numbers = [ '111111111111111111111111', '222222222222222222222222', '33333333333333333333333333', '4444444444444444444444444444','555555555555555555555555555']
print()
print(pytz.utc)
#print("Header:{0} Data:{1}\n".format(headers1, data))
#print(device_list)

#MultiOutput = YoLinkMultiOutlet(csName, csid, csseckey, yolinkURL,  mqttURL, 8003, device_serial_numbers[0], 3)
#WineCellarTHSensor =  YoLinkTHSensor(csName, csid, csseckey, yolinkURL,  mqttURL, 8003, device_serial_numbers[1], 2)
#PoolTemp =  YoLinkTHSensor(csName, csid, csseckey, yolinkURL,  mqttURL, 8003, device_serial_numbers[2], 3)
WaterLevel = YoLinkWaterSensor(csName, csid, csseckey, yolinkURL,  mqttURL, 8003, device_serial_numbers[3], 3)
IrrigationValve = YoLinkManipulator(csName, csid, csseckey, yolinkURL,  mqttURL, 8003, device_serial_numbers[4], 5)



#print(MultiOutput.getState())
#print(MultiOutput.getSchedules())
#print(MultiOutput.getDelays())
#print(MultiOutput.getStatus())
#print(MultiOutput.getInfoAll())


#MultiOutput.setState([1, 0], 'ON')
#MultiOutput.setState([0], 'off')
#MultiOutput.refreshtState()
#MultiOutput.refreshSchedules()


#MultiOutput.getFWversion()
#WineCellarTHSensor.refreshSensor()
#PoolTemp.refreshSensor()
#print(PoolTemp.getInfoAll())
#print(PoolTemp.getTemp())
#print(PoolTemp.getHumidity())
#print(PoolTemp.getState())

WaterLevel.refreshSensor()
print(WaterLevel.getState()+'\n')
print(WaterLevel.getInfoAll()+'\n')
print(WaterLevel.getTimeSinceUpdate()+'\n')

IrrigationValve.refreshState()
IrrigationValve.refreshSchedules()
IrrigationValve.refreshFWversion()

WaterLevel.refreshSensor()
print(WaterLevel.getState()+'\n')
print(WaterLevel.getInfoAll()+'\n')
print(WaterLevel.getTimeSinceUpdate()+'\n')



while True :
    time.sleep(10)
print('end')

#yolink_client.shurt_down()


