#!/usr/bin/env python3
#import ast
import os
import time
from datetime import datetime
#import pytz
import json
import requests
#import threading

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)



from yoLinkInitV2 import YoLinkInitPAC
from yolinkHubV2 import YoLinkHub
from yolinkSpeakerHubV2 import YoLinkSpeakerHub
from yolinkMultiOutletV2 import YoLinkMultiOutlet
from yolinkTHsensorV2 import YoLinkTHSensor
from yolinkLeakSensorV2 import YoLinkLeakSensor
from yolinkManipulatorV2 import YoLinkManipulator
from yolinkSwitchV2 import YoLinkSwitch
from yolinkGarageDoorToggleV2 import YoLinkGarageDoorToggle
from yolinkDoorSensorV2 import YoLinkDoorSensor
from yolinkMotionSensorV2 import YoLinkMotionSensor
from yolinkOutletV2 import YoLinkOutlet
from yolinkDoorSensorV2 import YoLinkDoorSensor
from yolinkHubV2 import YoLinkHub


def printDelay(timerList):
    print('Timer - timerTest: {}' .format( timerList))

if (os.path.exists('./loginInfo.json')):
    #logging.debug('reading /devices.json')
    dataFile = open('./loginInfo.json', 'r')
    tmp= json.load(dataFile)
    dataFile.close()

    UAID = tmp['UAID']
    SECRET_KEY = tmp['SECRET_KEY']
    csid = tmp['csid']
    csseckey = tmp['csseckey']
    csName = tmp['csName']
    WiFissid = tmp['WiFissid']
    WiFipwd = tmp['WiFipassword']

#deviceTestList = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 'SpeakerHub']
deviceTestList = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor', 'MotionSensor', 'Outlet', 'LeakSensor', 'Hub', 'SpeakerHub']

yolinkURL =  'https://api.yosmart.com/openApi' 
mqttURL = 'api.yosmart.com'

yoAccess = YoLinkInitPAC (UAID, SECRET_KEY)

deviceList = yoAccess.getDeviceList()

devices = {}
for dev in range(0,len(deviceList)):
    logging.debug('adding/checking device : {} - {}'.format(deviceList[dev]['name'], deviceList[dev]['type']))


    if deviceList[dev]['type'] == 'Hub' and 'Hub' in deviceTestList:     
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkHub(yoAccess, deviceList[dev])
        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getWiFiInfo: {}'.format(deviceList[dev]['name'], devices[dev].getWiFiInfo()))
            print('{} - getEthernetInfo: {}'.format(deviceList[dev]['name'], devices[dev].getEthernetInfo()))
            print('{} - setWiFi({}, {}):  {}'.format(deviceList[dev]['name'], WiFissid, WiFipwd, devices[dev].setWiFi(WiFissid, WiFipwd)))

            #devices[dev].setWiFi('SSID', 'password')
        print( '\n')

    elif deviceList[dev]['type'] == 'SpeakerHub' and 'SpeakerHub' in deviceTestList:
        print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkSpeakerHub (yoAccess, deviceList[dev])
        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getWiFiInfo(): {}'.format(deviceList[dev]['name'], devices[dev].getWiFiInfo()))
            print('{} - getEthernetInfo(): {}'.format(deviceList[dev]['name'], devices[dev].getEthernetInfo())) #makes no sense but API provides it - maybe future product
            print('{} - getOptionInfo(): {}'.format(deviceList[dev]['name'], devices[dev].getOptionInfo()))
            print('{} - setWiFi({}, {}):  {}'.format(deviceList[dev]['name'], WiFissid, WiFipwd, devices[dev].setWiFi(WiFissid, WiFipwd)))
            volume = 5
            enableBeep = True
            mute = False 
            repeat = 0 
            print('{} - setOptions({}, {}, {}): {}'.format(deviceList[dev]['name'], volume, enableBeep,mute, devices[dev].setOptions(volume, enableBeep, mute)))
            print('{} - playAudio( {}, {}, {},{} ):{}'.format(deviceList[dev]['name'], 'alert', volume+1,'This is a test', repeat, devices[dev].playAudio('alert', volume+1, 'This is a test', repeat)))

            devices[dev].playAudio('alert', volume+1, 'This is a test', repeat)
        print( '\n')


    elif deviceList[dev]['type'] == 'Switch' and 'Switch' in deviceTestList:
        print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkSwitch(yoAccess, deviceList[dev])                               
        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
            print('{} - setState({}): {}'.format(deviceList[dev]['name'], 'on',devices[dev].setState('on')))
            time.sleep(3)
            print('{} - setState({}): {}'.format(deviceList[dev]['name'], 'off',devices[dev].setState('off')))
            devices[dev].delayTimerCallback(printDelay, 10) #call print delay every 10 sec
            print('{} - setDelayList({}): {}'.format(deviceList[dev]['name'], "[{'delayOn':2,'off':3}]",devices[dev].setDelayList([{'delayOn':2,'off':3}])))
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()) )
            time.sleep(30)
            print('{} - setDelays({}): {}'.format(deviceList[dev]['name'],'3,4',devices[dev].setDelays(3, 4))) # on = 3 min, off = 4 min
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            time.sleep(30)
            print('{} - setOnDelay({}): {}'.format(deviceList[dev]['name'], 5, devices[dev].setOnDelay(5))) 
            time.sleep(15)
            print('{} - setOffDelay({}): {}'.format(deviceList[dev]['name'],5, devices[dev].setOffDelay(5))) 
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
        print('\n')

    elif deviceList[dev]['type'] == 'Outlet' and 'Outlet' in deviceTestList:     
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkOutlet(yoAccess, deviceList[dev])   
        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
            print('{} - setState({}): {}'.format(deviceList[dev]['name'], 'on',devices[dev].setState('on')))
            time.sleep(3)
            print('{} - setState({}): {}'.format(deviceList[dev]['name'], 'off',devices[dev].setState('off')))
            devices[dev].delayTimerCallback(printDelay, 10) #call print delay every 10 sec
            print('{} - setDelays({}): {}'.format(deviceList[dev]['name'],'3,4',devices[dev].setDelays(3, 4))) # on = 3 min, off = 4 min
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            time.sleep(30)
            print('{} - setDelays({}): {}'.format(deviceList[dev]['name'],'3,4',devices[dev].setDelays(3, 4))) # on = 3 min, off = 4 min
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            time.sleep(30)
            print('{} - setOnDelay({}): {}'.format(deviceList[dev]['name'], 5, devices[dev].setOnDelay(5))) 
            time.sleep(15)
            print('{} - setOffDelay({}):{}'.format(deviceList[dev]['name'],5, devices[dev].setOffDelay(5))) 
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
        print( '\n')

    elif deviceList[dev]['type'] == 'Manipulator' and 'Manipulator' in deviceTestList:
        print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkManipulator(yoAccess, deviceList[dev])             
        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
            print('{} - setState({}): {}'.format(deviceList[dev]['name'], 'closed',devices[dev].setState('closed')))
            time.sleep(30)
            print('{} - setState({}): {}'.format(deviceList[dev]['name'], 'open',devices[dev].setState('open')))
            devices[dev].delayTimerCallback(printDelay, 10) #call print delay every 10 se
            print('{} - setDelays({}): {}'.format(deviceList[dev]['name'],'3,4',devices[dev].setDelays(3, 4))) # on = 3 min, off = 4 min
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            time.sleep(30)
            print('{} - setOnDelay({}): {}'.format(deviceList[dev]['name'], 5, devices[dev].setOnDelay(5))) 
            time.sleep(15)
            print('{} - setOffDelay({}):{}'.format(deviceList[dev]['name'],5, devices[dev].setOffDelay(5))) 
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
        print( '\n')

    elif deviceList[dev]['type'] == 'THSensor' and 'THSensor' in deviceTestList:      
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkTHSensor(yoAccess, deviceList[dev])   
        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getTempValueF(): {}'.format(deviceList[dev]['name'], devices[dev].getTempValueF()))
            print('{} - getTempValueC(): {}'.format(deviceList[dev]['name'], devices[dev].getTempValueC()))
            print('{} - getHumidityValue(): {}'.format(deviceList[dev]['name'], devices[dev].getHumidityValue()))
            print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
            print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))   
            print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'],'alarm', devices[dev].getStateValue('alarm')))   
        print( '\n')

    elif deviceList[dev]['type'] == 'DoorSensor' and 'DoorSensor' in deviceTestList:
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkDoorSensor(yoAccess, deviceList[dev])     
        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
            print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'],'state', devices[dev].getStateValue('state'))) 
            print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
            print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))   
        print( '\n')

    elif deviceList[dev]['type'] == 'MotionSensor' and 'MotionSensor' in deviceTestList:     
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkMotionSensor(yoAccess, deviceList[dev])         
        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
            print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'], 'state', devices[dev].getStateValue('state'))) 
            print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
            print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))     
        print( '\n')
        

    elif deviceList[dev]['type'] == 'VibrationSensor' and 'VibrationSensor' in deviceTestList:     
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkMotionSensor(yoAccess, deviceList[dev])         
        print('{} - refreshDevice: {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
            print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'],'state', devices[dev].getStateValue('state'))) 
            print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
            print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))     
        print( '\n')

    elif deviceList[dev]['type'] == 'LeakSensor' and 'LeakSensor' in deviceTestList: 
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkLeakSensor(yoAccess, deviceList[dev])   
        print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
            print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'],'state', devices[dev].getStateValue('state'))) 
            print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
            print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))     
        print( '\n')
    
    elif deviceList[dev]['type'] == 'VibrationSensor' and 'VibrationSensor' in deviceTestList: 
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkLeakSensor(yoAccess, deviceList[dev])   
        print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
            print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'],'state' , devices[dev].getStateValue('state'))) 
            print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
            print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))     
        print( '\n')
    
    elif deviceList[dev]['type'] == 'GarageDoor' and 'GarageDoor' in deviceTestList: 
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkGarageDoorToggle(yoAccess, deviceList[dev])    
        print('{} - toggleDevice(): {}'.format(deviceList[dev]['name'], devices[dev].toggleDevice()))
        devices[dev].toggleDevice()
        print( '\n')
  
    elif deviceList[dev]['type'] == 'MultiOutlet' and 'MultiOutlet' in deviceTestList:
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkMultiOutlet(yoAccess, deviceList[dev])                
        print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
        print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
        if devices[dev].online:
            timeSec = int(devices[dev].getLastUpdate()/1000.0)
            print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
            print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
            print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
            print('{} - nbrPorts: {}'.format(deviceList[dev]['name'], devices[dev].nbrPorts))
            print('{} - nbrOutlets: {}'.format(deviceList[dev]['name'], devices[dev].nbrOutlets))
            print('{} - nbrUsb: {}'.format(deviceList[dev]['name'], devices[dev].nbrUsb))     
            print('{} - getMultiOutStates(): {}'.format(deviceList[dev]['name'], devices[dev].getMultiOutStates()))
            print('{} - getMultiOutPortState({}): {}'.format(deviceList[dev]['name'], 0, devices[dev].getMultiOutPortState('0'))) 
            print('{} - getMultiOutPortState({}): {}'.format(deviceList[dev]['name'], 'Port1',devices[dev].getMultiOutPortState('Port1'))) 
            print('{} - getMultiOutUsbState({}): {}'.format(deviceList[dev]['name'], 'Usb0', devices[dev].getMultiOutUsbState('Usb0'))) 
            print('{} - setMultiOutState({}): {}'.format(deviceList[dev]['name'],"'Port0', 'ON'", devices[dev].setMultiOutState('Port0', 'ON')))
            print('{} - setUsbState({}): {}'.format(deviceList[dev]['name'],"'Usb0', 'ON'",devices[dev].setUsbState('Usb0', 'ON')))
            print('{} - setMultiOutPortState({}): {}'.format(deviceList[dev]['name'],"['port0', 'port1'], 'OFF'", devices[dev].setMultiOutPortState(['port0', 'port1'], 'OFF')))  
            print('{} - setMultiOutUsbState({}): {}'.format(deviceList[dev]['name'], "['usb0'], 'OFF'", devices[dev].setMultiOutUsbState(['usb0'], 'OFF')))  
            print('{} - setMultiOutDelayList({}): {}'.format(deviceList[dev]['name'],"[{'ch':1, 'on':1, 'offDelay':2},{'ch':0, 'on':3, 'offDelay':4}, ]", devices[dev].setMultiOutDelayList([{'ch':1, 'on':1, 'offDelay':2},{'ch':0, 'on':3, 'offDelay':4}, ])))
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            time.sleep(30)
            print('{} - setMultiOutDelay({}): {}'.format(deviceList[dev]['name'],"'port1', 3, 4", devices[dev].setMultiOutDelay('port1', 3, 4)))  
            print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
            print('{} - setMultiOutOnDelay({}): {}'.format(deviceList[dev]['name'],"'port1', 3", devices[dev].setMultiOutOnDelay('port1', 3))) 
            print('{} - setMultiOutOffDelay({}): {}'.format(deviceList[dev]['name'],"'port1', 4", devices[dev].setMultiOutOffDelay('port1', 3))) 
            print('{} - setMultiOutOffDelay(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
        print( '\n')

    else:
        logging.debug('Currently unsupported device : {}'.format(deviceList[dev]['type'] ))







while True :
    time.sleep(10)
print('end')

yolink_client.shurt_down()

