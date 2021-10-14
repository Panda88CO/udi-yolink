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
csid = '60dd7fa7960d177187c82039'
csseckey = '3f68536b695a435d8a1a376fc8254e70'

COtopic = 'Panda88/aa/report'
csName = 'Panda88'

description = 'Enable Sensor APIs and subscribe to MQTT broker'

device_list = {}

'''
device_serial_numbers = ['9957FD6097124EE99B5E6B61A847C67D', '86788EB527034A78B9EA472323EE2433','34E320948EF746AF98EF8AF6E72F2996', 'AAF5A97CF38B4AD4BE840F293CAA55BE'
                        ,'668AD084C86A412FB5F9CAA652E99AAA', '5F167C2C61254FC1AB5472DC482016B3','CED643F4AB7C46F6A180387BD1C756F6', '636D394CDEBF45BB91FAD12B5BC473A5'
                        ,'FEB3FC58AB2B4E5A88A5FE3381D3522D',
                        ]

'''
device_serial_numbers = [ '636D394CDEBF45BB91FAD12B5BC473A5', 'FEB3FC58AB2B4E5A88A5FE3381D3522D', '34E320948EF746AF98EF8AF6E72F2996', 'CED643F4AB7C46F6A180387BD1C756F6','86788EB527034A78B9EA472323EE2433']
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


