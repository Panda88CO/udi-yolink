#!/usr/bin/env python3

#import argparse
#import os
#import sys
import yaml as yaml
import hashlib
import time
import json
import requests
#from logger import getLogger
from yolink_devices import YoLinkDevice

from yolink_mqtt_client import YoLinkMQTTClient
#log = getLogger(__name__)


yolinkURL =  'https://api.yosmart.com/openApi' 
mqttURL = 'api.yosmart.com'
csid = '60dd7fa7960d177187c82039'
csseckey = '3f68536b695a435d8a1a376fc8254e70'

topic = 'Panda88\report'
csName = 'Panda88'

description = 'Enable Sensor APIs and subscribe to MQTT broker'

device_list = {}
device_serial_numbers = ['9957FD6097124EE99B5E6B61A847C67D', '86788EB527034A78B9EA472323EE2433','34E320948EF746AF98EF8AF6E72F2996', 'AAF5A97CF38B4AD4BE840F293CAA55BE']

for serial_num in device_serial_numbers:
    yolink_device = YoLinkDevice(yolinkURL, csid, csseckey, serial_num)
    yolink_device.build_device_api_request_data()
    yolink_device.enable_device_api()
    device_list[yolink_device.get_id()] = yolink_device

    
    print(yolink_device.get_name())
    print(yolink_device.get_id())
    print(yolink_device.get_token())

    data = {}
    if yolink_device.get_name() == 'Temperature Sensor':
        data["method"] = 'THSensor.getState'
    elif yolink_device.get_name() == 'YoLink Valve':
        data["method"] = 'Manipulator.getState'
    elif yolink_device.get_name() == 'YoLink Hub':
        data["method"] = 'Hub.getState'

    data["time"] = str(int(time.time())*1000)
    data["params"] = {}
    data["targetDevice"] =  yolink_device.get_id()
    data["token"]= yolink_device.get_token()
    dataTemp = str(json.dumps(data))

    headers1 = {}
    headers1['Content-type'] = 'application/json'
    headers1['ktt-ys-brand'] = 'yolink'
    headers1['YS-CSID'] = csid

    # MD5(data + csseckey)

    cskey =  dataTemp +  csseckey
    cskeyUTF8 = cskey.encode('utf-8')
    hash = hashlib.md5(cskeyUTF8)
    hashKey = hash.hexdigest()
    headers1['ys-sec'] = hashKey
    headersTemp = json.dumps(headers1)

    print("Header:{0} Data:{1}\n".format(headersTemp, dataTemp))
    r = requests.post(yolinkURL, data=json.dumps(data), headers=headers1)        
    info = r.json()


#print("Header:{0} Data:{1}\n".format(headers1, data))

yolink_client = YoLinkMQTTClient(csid, csseckey, topic, mqttURL, 8003, device_list)
yolink_client.connect_to_broker()

