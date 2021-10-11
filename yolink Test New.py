#!/usr/bin/env python3

#import argparse
#import os
#import sys
#import yaml as yaml
import hashlib
import time
import json
import requests
import threading
#from logger import getLogger
from yolink_devices import YoLinkDevice
#from yolink_mqtt_client import YoLinkMQTTClient
from yolink_mqtt_device import YoLinkMultiOutlet
from yolink_mqtt_device import YoLinkTHsensor
#from oauthlib.oauth2 import BackendApplicationClient
#from requests.auth import HTTPBasicAuth
#from rauth import OAuth2Service
#from requests_oauthlib import OAuth2Session
#from requests_oauthlib import OAuth2Session



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
device_serial_numbers = [ '636D394CDEBF45BB91FAD12B5BC473A5', 'FEB3FC58AB2B4E5A88A5FE3381D3522D', '34E320948EF746AF98EF8AF6E72F2996']
print()

#print("Header:{0} Data:{1}\n".format(headers1, data))
#print(device_list)

#MultiOutput = YoLinkMultiOutlet(csName, csid, csseckey, yolinkURL,  mqttURL, 8003, device_serial_numbers[0])
WineCellarTHsensor =  YoLinkTHsensor(csName, csid, csseckey, yolinkURL,  mqttURL, 8003, device_serial_numbers[1])
PoolTHsensor =  YoLinkTHsensor(csName, csid, csseckey, yolinkURL,  mqttURL, 8003, device_serial_numbers[2])

#MultiOutput.setOutletState([1, 0], 'ON')
#MultiOutput.setOutletState([0], 'off')
#MultiOutput.refreshMultiOutletState()
#MultiOutput.refreshMultiOutletSchedule()
#MultiOutput.getMultiOutletVersion()
WineCellarTHsensor.refreshTHsensor()
PoolTHsensor.refreshTHsensor()
while True :
    time.sleep(10)

print('end')
#yolink_client.connect_to_broker()
'''

ports = 0
for step in range (6):
    ports = ports +1
    if ports == 4: 
        ports = 1
    if step <3:
        state = 'open'
    else:
        state = 'closed'
    print ('ports, state: ', ports, state)
    data={}
    data["method"] = 'MultiOutlet.setState'
    data["time"] = str(int(time.time())*1000)
    data["params"] = {}
    data["params"]["chs"] =  ports
    data["params"]['state'] = state
    data["targetDevice"] =  yolink_client.get_id()
    data["token"]= yolink_client.get_token()
    dataTemp = str(json.dumps(data))


    yolink_client.publish_data(dataTemp)
    time.sleep(1)
    if state == 'open':
        resetP = 'closed'
    else:
        resetP = 'open'
    data={}
    data["method"] = 'MultiOutlet.setState'
    data["time"] = str(int(time.time())*1000)
    data["params"] = {}
    data["params"]["chs"] =  0x3
    data["params"]['state'] = resetP
    data["targetDevice"] =  yolink_client.get_id()
    data["token"]= yolink_client.get_token()
    dataTemp = str(json.dumps(data))

    yolink_client.publish_data(dataTemp)
    time.sleep(5)

    yolink_client.request_data()
    #y.start()
    print('\n Completed loop: ' + str(step+1))




yolink_client.client.loop_stop()


yolink_client.subscribe_data(topic2)
time.sleep(2)
yolink_client.publish_data(topic1, dataTemp)
'''

#yolink_client.shurt_down()


