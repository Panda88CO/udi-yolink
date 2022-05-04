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
    print('{} - timerTest: {}\n'.format( timerList))

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
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        #print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getWiFiInfo: {} \n'.format(deviceList[dev]['type'], devices[dev].getWiFiInfo()))
        print('{} - getEthernetInfo: {} \n'.format(deviceList[dev]['type'], devices[dev].getEthernetInfo()))
        devices[dev].setWiFi(WiFissid, WiFipwd)
        #devices[dev].setWiFi('SSID', 'password')
        print('\n')

    elif deviceList[dev]['type'] == 'SpeakerHub' and 'SpeakerHub' in deviceTestList:
        print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkSpeakerHub (yoAccess, deviceList[dev])
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        #print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getWiFiInfo: {} \n'.format(deviceList[dev]['type'], devices[dev].getWiFiInfo()))
        print('{} - getEthernetInfo: {} \n'.format(deviceList[dev]['type'], devices[dev].getEthernetInfo())) #makes no sense but API provides it - maybe future product
        print('{} - getOptionInfo: {} \n'.format(deviceList[dev]['type'], devices[dev].getOptionInfo()))
        devices[dev].setWiFi(WiFissid, WiFipwd)
        #devices[dev].setWiFi('SSID', 'password')

        volume = 5
        enableBeep = True
        mute = False 
        repeat = 0 
        devices[dev].setOptions(volume, enableBeep, mute)
        devices[dev].playAudio('alert', volume+1, 'This is a test', repeat)
        print('\n')


    elif deviceList[dev]['type'] == 'Switch' and 'Switch' in deviceTestList:
        print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkSwitch(yoAccess, deviceList[dev])                               
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getState: {} \n'.format(deviceList[dev]['type'], devices[dev].getState()))
        devices[dev].setState('on')
        time.sleep(3)
        devices[dev].setState('off')
        devices[dev].delayTimerCallback(printDelay, 10) #call print delay every 10 sec
        devices[dev].setDelayList([{'delayOn':2,'off':3}])
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays) )
        time.sleep(30)
        devices[dev].setDelays(3, 4) # on = 3 min, off = 4 min
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        time.sleep(30)
        devices[dev].setOnDelay(5) 
        time.sleep(15)
        devices[dev].setOffDelay(5) 
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        devices[dev].refreshDevice()
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print(' \n')

    elif deviceList[dev]['type'] == 'Outlet' and 'Outlet' in deviceTestList:     
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkOutlet(yoAccess, deviceList[dev])   
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getState: {} \n'.format(deviceList[dev]['type'], devices[dev].getState()))
        print('{} - setState: {} \n'.format(deviceList[dev]['type'],devices[dev].setState('on')))
        time.sleep(3)
        print('{} - setState: {} \n'.format(deviceList[dev]['type'],devices[dev].setState('off')))
    
        devices[dev].setState('off')
        devices[dev].delayTimerCallback(printDelay, 10) #call print delay every 10 sec
        devices[dev].setDelayList([{'delayOn':2,'off':3}])
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        time.sleep(30)
        devices[dev].setDelays(3, 4) # on = 3 min, off = 4 min
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        time.sleep(30)
        devices[dev].setOnDelay(5) 
        time.sleep(15)
        devices[dev].setOffDelay(5) 
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        devices[dev].refreshDevice()
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))

        print('\n')

    elif deviceList[dev]['type'] == 'Manipulator' and 'Manipulator' in deviceTestList:
        print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkManipulator(yoAccess, deviceList[dev])             
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getState: {} \n'.format(deviceList[dev]['type'], devices[dev].getState()))
        
       
        devices[dev].setState('closed')
        time.sleep(3)
        devices[dev].setState('open')
        devices[dev].delayTimerCallback(printDelay, 10) #call print delay every 10 sec
        devices[dev].setDelayList([{'delayOn':2,'off':3}])
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        time.sleep(30)
        devices[dev].setDelays(3, 4) # on = 3 min, off = 4 min
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        time.sleep(30)
        devices[dev].setOnDelay(5) 
        time.sleep(15)
        devices[dev].setOffDelay(5) 
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        devices[dev].refreshDevice()
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print(' \n')

    elif deviceList[dev]['type'] == 'THSensor' and 'THSensor' in deviceTestList:      
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkTHSensor(yoAccess, deviceList[dev])   
        devices[dev].refreshDevice()
        
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getTempValueF: {} \n'.format(deviceList[dev]['type'], devices[dev].getTempValueF()))
        print('{} - getTempValueC: {} \n'.format(deviceList[dev]['type'], devices[dev].getTempValueC()))
        print('{} - getHumidityValue: {} \n'.format(deviceList[dev]['type'], devices[dev].getHumidityValue()))
        print('{} - getBattery: {} \n'.format(deviceList[dev]['type'], devices[dev].getBattery()))
        print('{} - getAlarms: {} \n'.format(deviceList[dev]['type'], devices[dev].getAlarms()))   
        print('{} - getStateValue: {} \n'.format(deviceList[dev]['type'], devices[dev].getStateValue('alarm')))   
        print(' \n')

    elif deviceList[dev]['type'] == 'DoorSensor' and 'DoorSensor' in deviceTestList:
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkDoorSensor(yoAccess, deviceList[dev])     
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getState: {} \n'.format(deviceList[dev]['type'], devices[dev].getState()))
        print('{} - getStateValue: {} \n'.format(deviceList[dev]['type'], devices[dev].getStateValue('state'))) 
        print('{} - getBattery: {} \n'.format(deviceList[dev]['type'], devices[dev].getBattery()))
        print('{} - getAlarms: {} \n'.format(deviceList[dev]['type'], devices[dev].getAlarms()))   
        print('\n')

    elif deviceList[dev]['type'] == 'MotionSensor' and 'MotionSensor' in deviceTestList:     
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkMotionSensor(yoAccess, deviceList[dev])         
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getState: {} \n'.format(deviceList[dev]['type'], devices[dev].getState()))
        print('{} - getStateValue: {} \n'.format(deviceList[dev]['type'], devices[dev].getStateValue('state'))) 
        print('{} - getBattery: {} \n'.format(deviceList[dev]['type'], devices[dev].getBattery()))
        print('{} - getAlarms: {} \n'.format(deviceList[dev]['type'], devices[dev].getAlarms()))     
        print('\n')
        
    elif deviceList[dev]['type'] == 'LeakSensor' and 'LeakSensor' in deviceTestList: 
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkLeakSensor(yoAccess, deviceList[dev])   
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getState: {} \n'.format(deviceList[dev]['type'], devices[dev].getState()))
        print('{} - getStateValue: {} \n'.format(deviceList[dev]['type'], devices[dev].getStateValue('state'))) 
        print('{} - getBattery: {} \n'.format(deviceList[dev]['type'], devices[dev].getBattery()))
        print('{} - getAlarms: {} \n'.format(deviceList[dev]['type'], devices[dev].getAlarms()))     
        print('\n')
    
    elif deviceList[dev]['type'] == 'VibrationSensor' and 'VibrationSensor' in deviceTestList: 
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkLeakSensor(yoAccess, deviceList[dev])   
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - getState: {} \n'.format(deviceList[dev]['type'], devices[dev].getState()))
        print('{} - getStateValue: {} \n'.format(deviceList[dev]['type'], devices[dev].getStateValue('state'))) 
        print('{} - getBattery: {} \n'.format(deviceList[dev]['type'], devices[dev].getBattery()))
        print('{} - getAlarms: {} \n'.format(deviceList[dev]['type'], devices[dev].getAlarms()))     
        print('\n')
    
    elif deviceList[dev]['type'] == 'GarageDoor' and 'GarageDoor' in deviceTestList: 
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkGarageDoorToggle(yoAccess, deviceList[dev])    
        devices[dev].toggleDevice()
        print('\n')
  
    elif deviceList[dev]['type'] == 'MultiOutlet' and 'MultiOutlet' in deviceTestList:
        print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
        devices[dev] = YoLinkMultiOutlet(yoAccess, deviceList[dev])                
        devices[dev].refreshDevice()
        print('{} - Online status: {}'.format(deviceList[dev]['type'], devices[dev].online))
        timeSec = int(devices[dev].getLastUpdate()/1000)
        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['type'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
        print('{} - getDataAll: {} \n'.format(deviceList[dev]['type'], devices[dev].getDataAll()))
        print('{} - getLastDataPacket: {} \n'.format(deviceList[dev]['type'], devices[dev].getLastDataPacket()))
        print('{} - nbrPorts: {} \n'.format(deviceList[dev]['type'], devices[dev].nbrPorts))
        print('{} - nbrOutlets: {} \n'.format(deviceList[dev]['type'], devices[dev].nbrOutlets))
        print('{} - nbrUsb: {} \n'.format(deviceList[dev]['type'], devices[dev].nbrUsb))
      
        print('{} - getMultiOutStates: {} \n'.format(deviceList[dev]['type'], devices[dev].getMultiOutStates()))
        print('{} - getMultiOutPortState: {} \n'.format(deviceList[dev]['type'], devices[dev].getMultiOutPortState('0'))) 
        print('{} - getMultiOutPortState: {} \n'.format(deviceList[dev]['type'], devices[dev].getMultiOutPortState('Port1'))) 
        print('{} - getMultiOutUsbState: {} \n'.format(deviceList[dev]['type'], devices[dev].getMultiOutUsbState('Usb0'))) 

        print('{} - setMultiOutState: {} \n'.format(deviceList[dev]['type'], devices[dev].setMultiOutState('Port0', 'ON')))
        print('{} - setUsbState: {} \n'.format(deviceList[dev]['type'], devices[dev].setUsbState('Usb0', 'ON')))


        print('{} - setMultiOutPortState: {} \n'.format(deviceList[dev]['type'], devices[dev].setMultiOutPortState(['port0', 'port1'], 'OFF')))  
        print('{} - setMultiOutUsbState: {} \n'.format(deviceList[dev]['type'], devices[dev].setMultiOutUsbState(['usb0'], 'OFF')))  

        devices[dev].setMultiOutDelayList([{'ch':1, 'on':1, 'offDelay':2},{'ch':0, 'on':3, 'offDelay':4}, ])
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))
        time.sleep(30)
        devices[dev].setMultiOutDelay('port1', 3, 4) # on = 3 min, off = 4 min
        print('{} - refreshDelays: {} \n'.format(deviceList[dev]['type'], devices[dev].refreshDelays))

        devices[dev].setMultiOutOnDelays('port1', 3) # on = 3min
        devices[dev].setMultiOutOffDelays('port1', 4) # on = 3min
        print(devices[dev].getDataAll())


    else:
        logging.debug('Currently unsupported device : {}'.format(deviceList[dev]['type'] ))







while True :
    time.sleep(10)
print('{} - end')

yolink_client.shurt_down()

