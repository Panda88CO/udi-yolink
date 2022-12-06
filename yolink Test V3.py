#!/usr/bin/env python3
#import ast
import os
import time
from datetime import datetime
#import pytz
import json
#import requests
#import threading
if (os.path.exists('./debug1.log')):
    os.remove('./debug1.log')
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    if (os.path.exists('./debug1.log')):
        os.remove('./debug1.log')
    import logging
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
    handlers=[
        logging.FileHandler("debug1.log"),
        logging.StreamHandler(sys.stdout) ]
    )

from yoLink_init_V2 import YoLinkInitPAC
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
from yolinkVibrationSensorV2 import YoLinkVibrationSensor
from yolinkOutletV2 import YoLinkOutlet
from yolinkDoorSensorV2 import YoLinkDoorSensor
from yolinkLockV2 import YoLinkLock
from yolinkInfraredRemoterV2 import YoLinkInfraredRemoter

from yolinkDimmerV2 import YoLinkDimmer


from yolinkHubV2 import YoLinkHub


def printDelay(timerList):
    logging.info('Timer - timerTest: {}' .format( timerList))

if (os.path.exists('./loginInfo.json')):
    #print('reading /devices.json')
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

#deviceTestList = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub', 'SpeakerHub', 'Lock', 'InfraredRemoter']
#deviceTestList = ['Lock', 'InfraredRemoter',  'VibrationSensor', ]
deviceTestList = ['Dimmer']
#deviceTestList = ['VibrationSensor', ]
#deviceTestList = ['Switch', 'THSensor', 'MultiOutlet', 'DoorSensor', 'MotionSensor', 'Outlet', 'LeakSensor', 'Hub', 'SpeakerHub', 'VibrationsSensor']
#deviceTestList = ['SpeakerHub', 'VibrationSensor']
#deviceTestList = ['Hub', 'DoorSensor', 'MultiOutlet' ]
#eviceTestList = [ 'DoorSensor',  'THSensor', 'MultiOutlet', 'Outlet']
yolinkURL =  'https://api.yosmart.com/openApi' 
mqttURL = 'api.yosmart.com'

yoAccess = YoLinkInitPAC (UAID, SECRET_KEY)

deviceList = yoAccess.getDeviceList()

devices = {}


for i in range(0,10):
    for dev in range(0,len(deviceList)) :
        #print(' Device ID: {} - concat {}'.format(deviceList[dev]['deviceId'], deviceList[dev]['deviceId'][-14:]))
        if deviceList[dev]['type'] in deviceTestList:
            print('adding/checking device : {} - {}'.format(deviceList[dev]['name'], deviceList[dev]['type']))


            if deviceList[dev]['type'] == 'Hub' and 'Hub' in deviceTestList:     
                print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkHub(yoAccess, deviceList[dev])
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
                        timeSec = int(devices[dev].getLastUpdate()/1000)
                        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
                        #print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                        print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
                        print('{} - getWiFiInfo: {}'.format(deviceList[dev]['name'], devices[dev].getWiFiInfo()))
                        print('{} - getEthernetInfo: {}'.format(deviceList[dev]['name'], devices[dev].getEthernetInfo()))
                        print('{} - setWiFi({}, {}):  {}'.format(deviceList[dev]['name'], WiFissid, WiFipwd, devices[dev].setWiFi(WiFissid, WiFipwd)))

                    #devices[dev].setWiFi('SSID', 'password')
                print( '\n')

            elif deviceList[dev]['type'] == 'SpeakerHub' and 'SpeakerHub' in deviceTestList:
                print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkSpeakerHub (yoAccess, deviceList[dev])
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
                        #timeSec = int(devices[dev].getLastUpdate()/1000)
                        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
                        print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                        print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
                        print('{} - getWiFiInfo(): {}'.format(deviceList[dev]['name'], devices[dev].getWiFiInfo()))
                        print('{} - getEthernetInfo(): {}'.format(deviceList[dev]['name'], devices[dev].getEthernetInfo())) #makes no sense but API provides it - maybe future product
                        print('{} - getOptionInfo(): {}'.format(deviceList[dev]['name'], devices[dev].getOptionInfo()))
                        print('{} - setWiFi({}, {}):  {}'.format(deviceList[dev]['name'], WiFissid, WiFipwd, devices[dev].setWiFi(WiFissid, WiFipwd)))
                        print('{} - setVolume({}):{}'.format(deviceList[dev]['name'], 5, devices[dev].setVolume(5)))
                        print('{} - setRepeat({}):{}'.format(deviceList[dev]['name'], 0, devices[dev].setRepeat(0)))
                        print('{} - setBeepEnable({}){}:'.format(deviceList[dev]['name'], True, devices[dev].setBeepEnable(True)))
                        print('{} - setMute({}){}:'.format(deviceList[dev]['name'], False, devices[dev].setMute(False)))
                        print('{} - setOptions() {}'.format(deviceList[dev]['name'],  devices[dev].setOptions()))
                        print('{} - setSetTone({}):{}'.format(deviceList[dev]['name'], 'Alert', devices[dev].setTone('Alert'))) #use 'none or empty toset no tone                       
                        #print('{} - playAudio({} ):{}'.format(deviceList[dev]['name'],'This is a test',devices[dev].playAudio('This is a test')))
                print( '\n')


            elif deviceList[dev]['type'] == 'Switch' and 'Switch' in deviceTestList:
                print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkSwitch(yoAccess, deviceList[dev])      
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))

                print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
                        timeSec = int(devices[dev].getLastUpdate()/1000)
                        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
                        print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                        print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
                        state = devices[dev].getState()
                        print('{} - getState(): {}'.format(deviceList[dev]['name'], state))
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
                        devices[dev].setState(state) # restore state 
                print('\n')

            elif deviceList[dev]['type'] == 'Dimmer' and 'Dimmer' in deviceTestList:
                print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkDimmer(yoAccess, deviceList[dev])      
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))

                print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
                        timeSec = int(devices[dev].getLastUpdate()/1000)
                        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
                        print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                        print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
                        state = devices[dev].getState()
                        print('{} - getState(): {}'.format(deviceList[dev]['name'], state))
                        print('{} - setState({}): {}'.format(deviceList[dev]['name'], 'on',devices[dev].setState('on')))
                        time.sleep(3)
                        print('{} - setState({}): {}'.format(deviceList[dev]['name'], 'off',devices[dev].setState('off')))
                        #devices[dev].delayTimerCallback(printDelay, 10) #call print delay every 10 sec
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
                        devices[dev].setState(state) # restore state 
                print('\n')

            elif deviceList[dev]['type'] == 'Outlet' and 'Outlet' in deviceTestList:     
                print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkOutlet(yoAccess, deviceList[dev])   
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))

                print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
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
                if dev not in devices:
                    devices[dev] = YoLinkManipulator(yoAccess, deviceList[dev])   
                else:     
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))

                print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
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
                if dev not in devices:
                    devices[dev] = YoLinkTHSensor(yoAccess, deviceList[dev])   
                    time.sleep(5)
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))

                print('{} - online: {} '.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
                        timeSec = int(devices[dev].getLastUpdate()/1000)
                        print('{} - getLastUpdate(): {} = {} '.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
                        print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                        print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
                        print('{} - getTempValueF(): {}'.format(deviceList[dev]['name'], devices[dev].getTempValueF()))
                        print('{} - getTempValueC(): {}'.format(deviceList[dev]['name'], devices[dev].getTempValueC()))
                        print('{} - getHumidityValue(): {}'.format(deviceList[dev]['name'], devices[dev].getHumidityValue()))
                        print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
                        print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))   
                        print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'],'alarm', devices[dev].getStateValue('alarm')))   
                        #time.sleep(10)
                print( '\n')

            elif deviceList[dev]['type'] == 'DoorSensor' and 'DoorSensor' in deviceTestList:
                print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkDoorSensor(yoAccess, deviceList[dev])     
                    time.sleep(5)
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                    
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
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
                if dev not in devices:
                    devices[dev] = YoLinkMotionSensor(yoAccess, deviceList[dev])     
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))

                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
                        timeSec = int(devices[dev].getLastUpdate()/1000)
                        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
                        print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                        print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
                        print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
                        print('{} - MotionState(): {}'.format(deviceList[dev]['name'], devices[dev].getMotionState()))
                        print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'], 'state', devices[dev].getStateValue('state'))) 
                        print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
                        print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))     
                print( '\n')
                

            elif deviceList[dev]['type'] == 'VibrationSensor' and 'VibrationSensor' in deviceTestList:     
                print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkVibrationSensor(yoAccess, deviceList[dev])     
                else:    
                    print('{} - refreshDevice: {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
                        timeSec = int(devices[dev].getLastUpdate()/1000)
                        print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
                        print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                        print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
                        print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
                        print('{} - VibrationState(): {}'.format(deviceList[dev]['name'], devices[dev].getVibrationState()))
                        print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'],'state', devices[dev].getStateValue('state'))) 
                        print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))  
                print( '\n')

            elif deviceList[dev]['type'] == 'LeakSensor' and 'LeakSensor' in deviceTestList: 
                print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkLeakSensor(yoAccess, deviceList[dev])   
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
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
                if dev not in devices:
                    devices[dev] = YoLinkLeakSensor(yoAccess, deviceList[dev])   
                else:
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
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
                if dev not in devices:
                    devices[dev] = YoLinkGarageDoorToggle(yoAccess, deviceList[dev])    
                print('{} - toggleDevice(): {}'.format(deviceList[dev]['name'], devices[dev].toggleDevice()))
                devices[dev].toggleDevice()
                print( '\n')
        
            elif deviceList[dev]['type'] == 'MultiOutlet' and 'MultiOutlet' in deviceTestList:
                print('{} - {}  : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkMultiOutlet(yoAccess, deviceList[dev])   
                else:             
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                print('{} - online: {}'.format(deviceList[dev]['name'], devices[dev].online))
                if devices[dev].online:
                    if devices[dev].data_updated():
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
                        if devices[dev].nbrUsb > 0:
                            print('{} - getMultiOutUsbState({}): {}'.format(deviceList[dev]['name'], 'Usb0', devices[dev].getMultiOutUsbState('Usb0'))) 
                        print('{} - setMultiOutState({}): {}'.format(deviceList[dev]['name'],"'Port0', 'ON'", devices[dev].setMultiOutState('Port0', 'ON')))
                        if devices[dev].nbrUsb > 0:
                            print('{} - setUsbState({}): {}'.format(deviceList[dev]['name'],"'Usb0', 'ON'",devices[dev].setUsbState('Usb0', 'ON')))
                        print('{} - setMultiOutPortState({}): {}'.format(deviceList[dev]['name'],"['port0', 'port1'], 'OFF'", devices[dev].setMultiOutPortState(['port0', 'port1'], 'OFF')))  
                        if devices[dev].nbrUsb > 0:
                            print('{} - setMultiOutUsbState({}): {}'.format(deviceList[dev]['name'], "['usb0'], 'OFF'", devices[dev].setMultiOutUsbState(['usb0'], 'OFF')))  
                            time.sleep(5)
                            print('{} - setMultiOutUsbState({}): {}'.format(deviceList[dev]['name'], "['usb0'], 'ON'", devices[dev].setMultiOutUsbState(['usb0'], 'ON')))  
                        devices[dev].delayTimerCallback(printDelay, 10) #call print delay every 10 sec
                        print('{} - setMultiOutDelayList({}): {}'.format(deviceList[dev]['name'],"[{'ch':1, 'on':1, 'offDelay':2},{'ch':0, 'on':3, 'offDelay':4}, ]", devices[dev].setMultiOutDelayList([{'ch':1, 'on':1, 'offDelay':2},{'ch':0, 'on':3, 'offDelay':4}, ])))
                        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
                        time.sleep(30)
                        print('{} - setMultiOutDelay({}): {}'.format(deviceList[dev]['name'],"'port1', 3, 4", devices[dev].setMultiOutDelay('port1', 3, 4)))  
                        print('{} - refreshDelays(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDelays()))
                        print('{} - setMultiOutOnDelay({}): {}'.format(deviceList[dev]['name'],"'port1', 3", devices[dev].setMultiOutOnDelay('port1', 3))) 
                        print('{} - setMultiOutOffDelay({}): {}'.format(deviceList[dev]['name'],"'port1', 4", devices[dev].setMultiOutOffDelay('port1', 3))) 
                        print('{} - setMultiOutOffDelay(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                print( '\n')



            elif deviceList[dev]['type'] == 'Lock' and 'Lock' in deviceTestList:
                print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkLock(yoAccess, deviceList[dev])   
                else:     
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                    print('{} - getLastUpdate(): {} = {}'.format(deviceList[dev]['name'], timeSec, str(datetime.fromtimestamp(timeSec).strftime("%m/%d/%Y, %H:%M:%S"))))
                    print('{} - getDataAll(): {}'.format(deviceList[dev]['name'], devices[dev].getDataAll()))
                    print('{} - getLastDataPacket(): {}'.format(deviceList[dev]['name'], devices[dev].getLastDataPacket()))
                    print('{} - getState(): {}'.format(deviceList[dev]['name'], devices[dev].getState()))
                    print('{} - fetchState(): {}'.format(deviceList[dev]['name'], devices[dev].fetchState()))
                    print('{} - setState(): {}'.format(deviceList[dev]['name'], devices[dev].setState('unlock')))
                    time.sleep(10)
                    print('{} - setState(): {}'.format(deviceList[dev]['name'], devices[dev].setState('lock')))
                    #print('{} - getStateValue({}): {}'.format(deviceList[dev]['name'],'state' , devices[dev].getStateValue('state'))) 
                    print('{} - getBattery(): {}'.format(deviceList[dev]['name'], devices[dev].getBattery()))
                    #print('{} - getAlarms(): {}'.format(deviceList[dev]['name'], devices[dev].getAlarms()))     

            elif deviceList[dev]['type'] == 'InfraredRemoter' and 'InfraredRemoter' in deviceTestList:
                print('{} - {} : {}'.format(deviceList[dev]['type'], deviceList[dev]['name'], dev))
                if dev not in devices:
                    devices[dev] = YoLinkInfraredRemoter(yoAccess, deviceList[dev])   
                else:     
                    print('{} - refreshDevice(): {}'.format(deviceList[dev]['name'], devices[dev].refreshDevice()))
                    #print('{} - dataAPI: {}'.format(deviceList[dev]['name'], devices[dev].dataAPI))
                    #print('{} - get_code_dict(): {}'.format(deviceList[dev]['name'], devices[dev].get_code_dict()))

                    print('{} - get_nbr_keys({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_nbr_keys()))
                    print('{} - get_last_message_type({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_last_message_type()))
                    '''
                    print('{} - send({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].send(dev)))
                    print('{} - get_last_message_type({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_last_message_type()))
                    print('{} - get_send_status({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_send_status()))
                    time.sleep(5)
                    print('{} - send({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].send(dev+1)))
                    print('{} - get_last_message_type({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_last_message_type()))
                    print('{} - get_send_status({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_send_status()))
                    time.sleep(5)
                    '''
                    print('{} - learn({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].learn(i+3)))
                    time.sleep(1)
                    time.sleep(1)
                    time.sleep(1)
                    time.sleep(1)
                    time.sleep(1)
                    time.sleep(1)
                    time.sleep(1)
                    time.sleep(1)
                    time.sleep(1)
                    time.sleep(1)
                    print('{} - get_last_message_type({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_last_message_type()))
                    time.sleep(1)
                    #print('{} - get_learn_status({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_learn_status()))
                    #print('{} - get_send_status({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_send_status()))
                    #print('{} - get_nbr_keys({}): {}'.format(deviceList[dev]['name'], dev, devices[dev].get_nbr_keys()))
                    #time.sleep(2)
            else:
                print('Currently unsupported device : {}'.format(deviceList[dev]['type'] ))

    time.sleep(10)
    print('looping - {}'.format(i))
print('end')





yoAccess.shut_down()

