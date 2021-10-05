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

from yolink_mqtt_client import YoLinkMQTTClient
#log = getLogger(__name__)
'''
session = requests.Session()
headers = {}
data = {}
authURL = 'https://api.yosmart.com/oauth/v2/authorization.htm'
resp = session.get(authURL, headers=headers)
print(resp)

'''

def test_thread():
    print ('starting thread')
    topic1 = csName + '/aa/request'
    topic2 = csName + '/aa/response'
    time.sleep(5)

    i = 0
    state = 'closed'
    yolink_client.subscribe_data(topic2)
    while i<5: 
        i = i+1
        print(i)
        if state == 'closed':
            state = 'open'
        else:
            state = 'closed'

        data = {}
        data["method"] = yolink_device.get_type()+str('.getSchedules')
        data["time"] = str(int(time.time())*1000)
        data["token"]= yolink_device.get_token()
        #data["params"] =  {}
        #data["params"]["chs"] =  0x02
        #data["params"]["state"] = state
        data["targetDevice"] =  yolink_device.get_id()
        dataTemp = str(json.dumps(data))
        print(dataTemp)
        '''

        headers1['Content-type'] = 'application/json'
        headers1['ktt-ys-brand'] = 'yolink'
        headers1['YS-CSID'] = csid
        cskey =  dataTemp +  csseckey
        cskeyUTF8 = cskey.encode('utf-8')
        hash = hashlib.md5(cskeyUTF8)
        hashKey = hash.hexdigest()
        headers1['ys-sec'] = hashKey
        headersTemp = json.dumps(headers1)
       

        print("Header:{0} Data:{1}\n".format(headersTemp, dataTemp))
        r = requests.post(yolinkURL, data=dataTemp, headers=headers1)      
        #r = requests.post(yolinkURL, data=json.dumps(data), headers=headers1)        
        info = r.json()
        print (info)
        test = input() 
        dataTemp = str(json.dumps(data))
        print(dataTemp)
        '''
        
        time.sleep(1)
        yolink_client.publish_data(topic1, dataTemp)
        test = input() 

        
      
def monitor_thread():
    print ('starting Moitor thread')
    yolink_client.connect_to_broker()



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
device_serial_numbers = [ '636D394CDEBF45BB91FAD12B5BC473A5']
print()

for serial_num in device_serial_numbers:
    print(serial_num[0:10])
    yolink_device = YoLinkDevice(yolinkURL, csid, csseckey, serial_num)
    yolink_device.build_device_api_request_data()
    yolink_device.enable_device_api()
    device_list[yolink_device.get_id()] = yolink_device


    print(yolink_device.get_name())
    print(yolink_device.get_type())
    print(yolink_device.get_id())
    print(yolink_device.get_token())
    print(yolink_device.getMethods(str(yolink_device.get_type())))

    data = {}
    '''
    if yolink_device.get_type() == 'THSensor':
        data["method"] = 'THSensor.getState'
    elif yolink_device.get_type() == 'Manipulator':
        data["method"] = 'Manipulator.getState'
    elif yolink_device.get_type() == 'Hub':
        data["method"] = 'Hub.getState'
    '''
    type = yolink_device.get_type()
    actions = yolink_device.getMethods(type)
    getState = actions[0]

    data["method"] = type+'.'+getState
    data["time"] = str(int(time.time()*1000))
    #data["time"] = str(int(time.time()))
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
    print(str(info)+'\n')
    '''
    if serial_num == '86788EB527034A78B9EA472323EE2433':
        data = {}
        data["method"] = 'Manipulator.setState'
        data["time"] = str(int(time.time())*1000)
        data["params"] = {'state':'close'}
        data["targetDevice"] =  yolink_device.get_id()
        data["token"]= yolink_device.get_token()
        dataTemp = str(json.dumps(data))

        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['ktt-ys-brand'] = 'yolink'
        headers1['YS-CSID'] = csid
        cskey =  dataTemp +  csseckey
        cskeyUTF8 = cskey.encode('utf-8')
        hash = hashlib.md5(cskeyUTF8)
        hashKey = hash.hexdigest()
        headers1['ys-sec'] = hashKey
        headersTemp = json.dumps(headers1)

        print("Header:{0} Data:{1}\n".format(headersTemp, dataTemp))
        r = requests.post(yolinkURL, data=json.dumps(data), headers=headers1)        
        info = r.json()

        time.sleep(10)

        data["method"] = 'Manipulator.setState'
        data["time"] = str(int(time.time())*1000)
        data["params"] = {'state':'open'}
        data["targetDevice"] =  yolink_device.get_id()
        data["token"]= yolink_device.get_token()
        dataTemp = str(json.dumps(data))

        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['ktt-ys-brand'] = 'yolink'
        headers1['YS-CSID'] = csid
        cskey =  dataTemp +  csseckey
        cskeyUTF8 = cskey.encode('utf-8')
        hash = hashlib.md5(cskeyUTF8)
        hashKey = hash.hexdigest()
        headers1['ys-sec'] = hashKey
        headersTemp = json.dumps(headers1)

        print("Header:{0} Data:{1}\n".format(headersTemp, dataTemp))
        r = requests.post(yolinkURL, data=json.dumps(data), headers=headers1)        
        info = r.json()
    '''

#print("Header:{0} Data:{1}\n".format(headers1, data))
print(device_list)
print(COtopic)
yolink_client = YoLinkMQTTClient(csid, csseckey, COtopic, mqttURL, 8003, device_list)

x = threading.Thread(target = test_thread)
#y = threading.Thread(target = monitor_thread)

x.start()
time.sleep(1)
print ('starting Moitor thread')
yolink_client.connect_to_broker()
#y.start()

'''
yolink_client.subscribe_data(topic2)
time.sleep(2)
yolink_client.publish_data(topic1, dataTemp)
'''

#yolink_client.shurt_down()


