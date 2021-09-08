#!/usr/bin/env python3

#import argparse
#import os
#import sys
import yaml as yaml
import hashlib
import time
import json

#from logger import getLogger
from yolink_devices import YoLinkDevice

from yolink_mqtt_client import YoLinkMQTTClient
#log = getLogger(__name__)


yolinkURL =  'https://api.yosmart.com/openApi' 
mqttURL = 'api.yosmart.com'
csid = '60dd7fa7960d177187c82039'
csseckey = '3f68536b695a435d8a1a376fc8254e70'

topic = 'Panda88/report'
csName = 'Panda88'

description = 'Enable Sensor APIs and subscribe to MQTT broker'

device_hash = {}
device_serial_numbers = ['9957FD6097124EE99B5E6B61A847C67D', '86788EB527034A78B9EA472323EE2433','34E320948EF746AF98EF8AF6E72F2996', 'AAF5A97CF38B4AD4BE840F293CAA55BE']

for serial_num in device_serial_numbers:
    yolink_device = YoLinkDevice(yolinkURL, csid, csseckey, serial_num)
    yolink_device.build_device_api_request_data()
    yolink_device.enable_device_api()

    device_hash[yolink_device.get_id()] = yolink_device

print(device_hash)
data = {}
data["method"] = 'THSensor.getState'
data["time"] = str(int(time.time())*1000)
#data["params"] = {'sn': self.serial_number}
#data["targetDevice"] = self.targetDevice
#data["token"]= self.token
header = {}
header['Content-type'] = 'application/json'
header['ktt-ys-brand'] = 'yolink'
header['YS-CSID'] = csid

# MD5(data + csseckey)
header['ys-sec'] = str(hashlib.md5((json.dumps(data) +
    csseckey).encode('utf-8')).hexdigest())

print("Header:{0} Data:{1}\n".format(header, data))






#yolink_client = YoLinkMQTTClient(csid, csseckey, topic, mqttURL, 8003, device_hash)
#yolink_client.connect_to_broker()

