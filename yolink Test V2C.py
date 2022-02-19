#!/usr/bin/env python3
import ast
import os
import time
import pytz
import json
import requests
import threading
from yolinkHubV2 import YoLinkHub
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

#from logger import getLogger
from yolink_devices import YoLinkDevice
#from yolink_mqtt_client import YoLinkMQTTClient
from yolinkMultiOutletV2 import YoLinkMultiOutlet
from yolinkTHsensorV2 import YoLinkTHSensor
from yolinkLeakSensorV2 import YoLinkLeakSensor
from yolinkManipulatorV2 import YoLinkManipulator
from yolinkSwitchV2 import YoLinkSwitch
from yolinkGarageDoorToggleV2 import YoLinkGarageDoorToggle
from yolinkGarageDoorSensorV2 import YoLinkGarageDoorSensor
from yolinkMotionSensorV2 import YoLinkMotionSensor
from yolinkOutletV2 import YoLinkOutlet
from yolinkDoorSensorV2 import YoLinkDoorSensor
from yolinkHubV2 import YoLinkHub
from yoLinkInit import YoLinkInitPAC

from cryptography.fernet import Fernet
#from yolink_mqtt_device import YoLinkGarageDoor
#from oauthlib.oauth2 import BackendApplicationClient
#from requests.auth import HTTPBasicAuth
#from rauth import OAuth2Service
from requests_oauthlib import OAuth2Session
'''
if (os.path.exists('./devices.json')):
    #logging.debug('reading /devices.json')
    dataFile = open('./devices.json', 'r')
    tmp= json.load(dataFile)
    dataFile.close()
    deviceList = tmp['data']['list']


def getDeviceList1(self):
    logging.debug ('getDeviceList1')

    self.yoDevices = YoLinkDevices(self.csid, self.csseckey)
    webLink = self.yoDevices.getAuthURL()
    #self.Parameters['REDIRECT_URL'] = ''
    self.poly.Notices['url'] = 'Copy this address to browser. Follow screen to long. After screen refreshes copy resulting  redirect URL (address bar) into config REDICRECT_URL: ' + str(webLink) 


def getDeviceList2(self):
    logging.debug('Start executing getDeviceList2')
    self.supportedYoTypes = ['switch', 'THsensor', 'MultiOutlet', 'DoorSensor','Manipulator', 'MotionSensor', 'Outlet', 'GarageDoor', 'LeakSensor', 'Hub' ]
    self.yoDevices = YoLinkDevicesPAC(self.uaid, self.secretKey)
    self.deviceList = self.yoDevices.getDeviceList()

'''




'''
    CSID : 60dd7fa7960d177187c82039

    CSName : Panda88

    CSSecKey : 3f68536b695a435d8a1a376fc8254e70

    SVR_URL : https://api.yosmart.com 

    API Doc : http://www.yosmart.com/doc/lorahomeapi/#/YLAS/
'''
'''
Hub
1374B849C6164E93989C8CFD56B00E89
Garage relay
D36C052E35BC4B62A409B200EB3CB0A5
Garage sensor
43B25F8585AE45D89300FFE08CFE2C52
Motion sensor
A69DA7A252D74CFDA1E7CEF416245B98



    
# decrypt the file
decrypt_file = fernet.decrypt(file)
# open the file and wite the encrypted data
with open('test.txt', 'wb') as decrypted_file:
    decrypted_file.write(decrypt_file)
print('File is decrypted')
'''
'''
# read the key
with open('file_key.key', 'rb') as filekey:
    key = filekey.read()
    ffilekey.close()
# crate instance of Fernet
# with encryption key
fernet = Fernet(key)
# read the file to decrypt
with open('yolinkDeviceList.txt', 'rb') as f:
    file = f.read()
    f.close()
devfile = fernet.decrypt(file)
devstr = devfile.decode('utf-8')

with open('devicesNew.json', 'r') as f:
    devstr = f.read()
    f.close()
InstalledDev
'''
def printDelay(timerList):
    print('timerTest: {}\n'.format( timerList))

UAID = 'ua_93BF42449446432EA43E49887492C3FC'
SECRET_KEY = 'sec_v1_2IQ13RYyyvxMBpPK3POF0A=='

yolinkURL =  'https://api.yosmart.com/openApi' 
mqttURL = 'api.yosmart.com'
csid = '60dd7fa7960d177187c82039'
csseckey = '3f68536b695a435d8a1a376fc8254e70'
csName = 'Panda88'

yoAccess = YoLinkInitPAC (UAID, SECRET_KEY)


DeviceList = yoAccess.getDeviceList()

'''
WineCoolerTemp =DeviceList[2] 
spatemp = DeviceList[0] 
PoolLevel = DeviceList[13]
'''

HubUS           = DeviceList[18]
HubDS           = DeviceList[17]
WineCoolerTemp  = DeviceList[16] 
MultiOUtlet2    = DeviceList[15]
OutdoorTemp     = DeviceList[14]
PoolLevel       = DeviceList[13]
GarageSensor    = DeviceList[12]
GarageCTRL      = DeviceList[11]
USB_Outlet      = DeviceList[10]
Playground      = DeviceList[9]
GardenPlayground = DeviceList[8]
DoorSensor      = DeviceList[7]
DeckLight       = DeviceList[6]
BathIndoorTemp  = DeviceList[5]
PoolTemp        = DeviceList[4]
MotionSensor1   = DeviceList[3]
Irrigation      = DeviceList[2]
HouseValve      = DeviceList[1]
FishTank        = DeviceList[0]




#FishMultiOutput = YoLinkMultiOutlet(yoAccess, FishTank)

MultiOutput = YoLinkMultiOutlet(yoAccess, MultiOUtlet2)
MultiOutput.delayTimerCallback(printDelay, 10)

#WineCellarTemp =  YoLinkTHSensor(yoAccess, WineCoolerTemp)
#PoolTemp =  YoLinkTHSensor(yoAccess, PoolTemp)
#WaterLevel = YoLinkLeakSensor(yoAccess, PoolLevel)
#GarageController = YoLinkGarageDoorToggle(yoAccess, GarageCTRL)
#GarageSensor = YoLinkGarageDoorSensor(yoAccess, GarageSensor)
#MotionSensor = YoLinkMotionSensor(yoAccess, MotionSensor1 )
#IrrigationValve = YoLinkManipulator(yoAccess, Irrigation )
#HouseValve = YoLinkManipulator(yoAccess, HouseValve )
#DeckLight = YoLinkMultiOutlet(yoAccess, DeckLight)
#PlaygroundGardenLight = YoLinkSwitch(yoAccess, GardenPlayground)
#PlaygroundLight = YoLinkSwitch(yoAccess, Playground)
USB_Outlet = YoLinkOutlet(yoAccess, USB_Outlet)
USB_Outlet.delayTimerCallback(printDelay, 5)
#DoorSensor1 = YoLinkDoorSensor(yoAccess, DoorSensor)
#OutdoorTemp = YoLinkTHSensor(yoAccess, OutdoorTemp)
#bathRTemp =  YoLinkTHSensor(yoAccess, BathIndoorTemp)
Hub1 = YoLinkHub(yoAccess, HubDS)
'''
test = MultiOutput.getMultiOutStates()

MO15 = MultiOutput.nbrPorts
MO15a = MultiOutput.nbrOutlets
MO15b = MultiOutput.nbrUsb
MO1 = MultiOutput.getSchedules()
MO2 = MultiOutput.getDelays()
MO3 = MultiOutput.getStatus()
MO4 = MultiOutput.getInfoAll()
MO5 = MultiOutput.getInfoAPI()
MO6 = MultiOutput.getMultiOutStates()
MO7 = MultiOutput.getMultiOutPortState('0')
MO8 = MultiOutput.getMultiOutPortState('port1')
MO9 = MultiOutput.getMultiOutUsbState('usb0')
MO9a = MultiOutput.setMultiOutPortState(['port0'], 'OFF')
#MO9b = MultiOutput.setMultiOutUsbState(['usb0'], 'ON')


MO11 = MultiOutput.outletSetDelayList([{'ch':1, 'on':1, 'offDelay':2},{'ch':0, 'on':3, 'offDelay':4}, ])
time.sleep(300)
MO10 = MultiOutput.outletSetDelay('port0', 1, 2)


FT16 = FishMultiOutput.getMultiOutStates()
FT15 = FishMultiOutput.nbrPorts
FT15 = FishMultiOutput.nbrOutlets
FT15a = FishMultiOutput.nbrUsb

FT1 = FishMultiOutput.getSchedules()
FT2 = FishMultiOutput.getDelays()
#MO = MultiOutput.getStatus()
#MO = MultiOutput.getInfoAll()
FT5 = FishMultiOutput.getInfoAPI()

FT6 = FishMultiOutput.getMultiOutStates()
FT7 = FishMultiOutput.getMultiOutPortState('port0')
FT8 = FishMultiOutput.getMultiOutPortState('port4')
FT9 = FishMultiOutput.getMultiOutUsbState('usb0')
FT9a = FishMultiOutput.setMultiOutUsbState(['usb0'], 'ON')
FT9b = FishMultiOutput.setMultiOutPortState(['port3'], 'ON')
'''

#IV1 = IrrigationValve.getState()


#WC1 = WineCellarTemp.getTempValueC()
#WC2 = WineCellarTemp.getTempValueF()
#WC3 = WineCellarTemp.getHumidityValue()
#WC4 = WineCellarTemp.getAlarms()

#GS1 = GarageSensor.getState()
#GCT1 = GarageController.toggleDevice()


#PG1= PlaygroundLight.getState()

#MultiOutput.setState([1, 0], 'ON')
#MultiOutput.setState([0], 'off')
#print(MultiOutput.getInfoAPI())
#MultiOutput.refreshMultiOutput()
#print(MultiOutput.getInfoAPI())
#MultiOutput.refreshSchedules()

#print(MultiOutput.getInfoAPI())
#MultiOutput.refreshFWversion()
#WineCellarTemp.refreshSensor()
'''
swTest3 = PlaygroundLight.getSchedules()
#input('press enter')
swTest4 = PlaygroundLight.setDelay([{'delayOn':1, 'delayOff':2}])
#input('press enter')
swTest5 = PlaygroundLight.setState('ON')
#input('press enter')
swTest6 = PlaygroundLight.getState()
#input('press enter')
swTest8 = PlaygroundLight.getInfoAPI()
swTest9 = PlaygroundLight.setState('OFF')
sch1indx = PlaygroundLight.addSchedule({'week':['mon','wed', 'fri'], 'on':'16:30', 'off':'17:30','isValid':False })
sch2indx =PlaygroundLight.addSchedule({'week':['thu','tue', 'sun'], 'on':'16:31', 'off':'17:30','isValid':False})
sch3indx = PlaygroundLight.addSchedule({'week':['mon','wed', 'sat'], 'on':'16:32', 'off':'17:00','isValid':False})

test = PlaygroundLight.activateSchedules(sch3indx, True)

test = PlaygroundLight.deleteSchedule(sch2indx)
sch2 =PlaygroundLight.addSchedule({'week':['thu','tue', 'sun'], 'off':'17:30','isValid':True })
swTest3 = PlaygroundLight.getSchedules()
test = PlaygroundLight.setSchedules()
'''
'''
PoolTemp.refreshSensor()
print(str(PoolTemp.getTempValue())  )
print(str(PoolTemp.getHumidityValue() ))
print(str(PoolTemp.getAlarms()))
print()
print(str(PoolTemp.sensorOnline()))
print()
info = PoolTemp.getInfoAPI()
print()
PoolTemp.eventPending()

WineCellarTemp.refreshSensor()
print(str(WineCellarTemp.getTempValue()))
print(str(WineCellarTemp.getHumidityValue()))
print(str(WineCellarTemp.getAlarms()))
print()
print(str(WineCellarTemp.eventPending()))
print()
print(str(WineCellarTemp.sensorOnline()))
print()
info = WineCellarTemp.getInfoAPI()

WaterLevel.refreshSensor()
print(str(WaterLevel.probeState() ))
print(str(WaterLevel.eventPending()))
print()
print(str(WaterLevel.sensorOnline()))
print()
info = WaterLevel.getInfoAPI()
'''
while True :
    
    #test = input('Press any key')
    '''
    DoorSensor1.refreshDevice()
    DS1 = DoorSensor1.getState()
    DS2 = DoorSensor1.getBattery()

    WineCellarTemp.refreshDevice()
    WC1 = WineCellarTemp.getTempValueC()
    WC2 = WineCellarTemp.getTempValueF()
    WC3 = WineCellarTemp.getHumidityValue()
    WC4 = WineCellarTemp.getAlarms()

    OutdoorTemp.refreshDevice()
    OD1 = OutdoorTemp.getTempValueC()
    OD2 = OutdoorTemp.getBattery()
    OD4 = OutdoorTemp.getAlarms()

    GarageSensor.refreshDevice()
    GS1 = GarageSensor.getState()
    GCT1 = GarageController.toggleDevice()
    
    IrrigationValve.refreshDevice()
    IR1 = IrrigationValve.getState()
    IR2 = IrrigationValve.getBattery()
 
    PlaygroundLight.refreshDevice()
    PG1= PlaygroundLight.getState()
    
    Hub1.refreshDevice()
    HU1 = Hub1.getState()
    '''
    '''
    test = MultiOutput.getMultiOutStates()

    MO15 = MultiOutput.nbrPorts
    MO15a = MultiOutput.nbrOutlets
    MO15b = MultiOutput.nbrUsb
    MO1 = MultiOutput.getSchedules()
    MO2 = MultiOutput.getDelays()
    MO3 = MultiOutput.refreshDevice()
    #MO4 = MultiOutput.getInfoAll()
    MO5 = MultiOutput.getInfoAPI()
    MO6 = MultiOutput.getMultiOutStates()
    MO7 = MultiOutput.getMultiOutPortState('0')
    MO8 = MultiOutput.getMultiOutPortState('port1')
    MO9 = MultiOutput.getMultiOutUsbState('usb0')
    MO9a = MultiOutput.setMultiOutPortState(['port0'], 'OFF')
    #MO9b = MultiOutput.setMultiOutUsbState(['usb0'], 'ON')
    '''


    
    MO11 = MultiOutput.setMultiOutDelayList([{'ch':1, 'on':1, 'delayOff':2},{'ch':0, 'on':3, 'delayOff':4} ], printDelay)
    MO12 = MultiOutput.refreshDevice()
    MO2 = MultiOutput.getDelays()
    
    
    time.sleep(10)
    #MO10 = MultiOutput.setMultiOutDelays('port0', 1, 2, printDelay)
    
    #USB1 = USB_Outlet.refreshDevice()
    #USB1a = USB_Outlet.getState()
    #USB2 = USB_Outlet.setState('on')
    #time.sleep(5)
    #USB3 = USB_Outlet.setState('off')
    USB4 = USB_Outlet.setDelayList([{'delayOn':2,'off':3}], printDelay )
    USB5 = USB_Outlet.refreshDevice()
    time.sleep(15)
    USB4 = USB_Outlet.setDelayList([{'delayOn':3,'off':4}], printDelay )


    time.sleep(300)

    #print(MultiOutput.getMultiOutletState())
    #print(MultiOutput.getSchedules())
    #print(MultiOutput.getDelays())
 #
    #print(MultiOutput.getInfoAll())
    #print(MultiOutput.getInfoAPI())

    #MultiOutput.setMultiOutletState([1, 0], 'ON')
    #MultiOutput.setMultiOutletState([0], 'off')
    #MultiOutput.getMultiOutletData()
    #print(MultiOutput.getInfoAPI())
    #MultiOutput.refreshMultiOutlet()
    #print(MultiOutput.getInfoAPI())
    #MultiOutput.refreshSchedules()

    #print(MultiOutput.getInfoAPI())
    
    #oTest1 = USB_Outlet.refreshState()
    #input('press enter')
    #oTest2 = USB_Outlet.getState()
    #while USB_Outlet.eventPending():
    #    print('USB_outlet event: ' + USB_Outlet.getEvent())
    #input('press enter')

    #WaterLevel.refreshSensor()
    #print(str(WaterLevel.probeState() ))
    #print(str(WaterLevel.eventPending()))
    #print()
    #print(str(WaterLevel.sensorOnline()))
    #print()

    #info = WaterLevel.getInfoAPI()


    '''
    temp1 = PoolTemp.getTempValueC()
    temp2 = PoolTemp.getHumidityValue()
    temp3 = PoolTemp.getAlarms()

    temp4 = PoolTemp.getData()
    temp5 = PoolTemp.getBattery()
    '''

    #swTest1 = PlaygroundLight.refreshState()
    #input('press enter')
    #swTest2 = PlaygroundLight.getState()
    #swTest3 = PlaygroundLight.getDelays()
    #while PlaygroundLight.eventPending():
    #    print('PlaygroundLight event: ' + PlaygroundLight.getEvent())
    #input('press enter')

    #gtest = GarageController.toggleDevice()

    #mtest = MotionSensor.motionState()
    #mtest2 = MotionSensor.motionData()
    #while MotionSensor.eventPending():
    #    print('MotionSensor event: ' + MotionSensor.getEvent())

    #swTest3 = PlaygroundLight.getSchedules()
    #input('press enter')
    #swTest4 = PlaygroundLight.setDelay([{'delayOn':1, 'delayOff':2}])
    #input('press enter')
    #swTest5 = PlaygroundLight.setState('ON')
    #input('press enter')
    #swTest6 = PlaygroundLight.getState()
    #input('press enter')
    #swTest7 = PlaygroundLight.getEnergy()
    #input('press enter')
    #swTest8 = PlaygroundLight.getInfoAPI()

    #sch1indx = PlaygroundLight.addSchedule({'week':['mon','wed', 'fri'], 'on':'16:30', 'off':'17:30','isValid':False })
    #sch2indx =PlaygroundLight.addSchedule({'week':['thu','tue', 'sun'], 'on':'16:31', 'off':'17:30','isValid':False})
    #sch3indx = PlaygroundLight.addSchedule({'week':['mon','wed', 'sat'], 'on':'16:32', 'off':'17:00','isValid':False})
    #print (IrrigationValve.scheduleList)
    #test = PlaygroundLight.activateSchedules(sch3indx, True)

    #test = PlaygroundLight.deleteSchedule(sch2indx)
    #sch2 =PlaygroundLight.addSchedule({'week':['thu','tue', 'sun'], 'off':'17:30','isValid':True })
    #swTest3 = PlaygroundLight.getSchedules()
    #test = PlaygroundLight.setSchedules()
    '''
    iTest1 = IrrigationValve.refreshState()
    iTest2 = IrrigationValve.getState()
    iTmp = IrrigationValve.refreshSchedules() 
    #iTest3 = IrrigationValve.refreshDelays() 
  
    iDel2 = MultiOutput.setDelay([{'OnDelay':2, 'OffDelay':1}])
    iDel3 = MultiOutput.setDelay()
    #IrrigationValve.refreshFWversion()
    
    mTest = MultiOutput.refreshMultiOutlet()
    mState = MultiOutput.getMultiOutletState()
    mSchedules = MultiOutput.getSchedules()
    mDelays = MultiOutput.getDelays()
    mRes1 = MultiOutput.setMultiOutletState([0, 1], 'ON')
    mRes2 = MultiOutput.setMultiOutletState([1], 'CLOSED')
    mDel1 = MultiOutput.resetDelayList()
    mDel2 = MultiOutput.appendDelay({'port':0,'OnDelay':2, 'OffDelay':1})
    mDel3 = MultiOutput.setDelay()
    mTmp = MultiOutput.getInfoAPI()
    #print(MultiOutput.getInfoAPI())
    #MotionSensor.refreshSensor()
    #print(str(MotionSensor.motionState() ))
    #print(str(MotionSensor.getMotionData()))

    #print(str(MotionSensor.eventPending()))
    #if MotionSensor.eventPending():
    #    print('Motion Event:')
    #    print(str(MotionSensor.extractEventData()))
    #print()
    #print(str(MotionSensor.sensorOnline()))
    print()
    #info = MotionSensor.getInfoAPI()
    '''

#print(PoolTemp.getInfoAll())
#print(PoolTemp.getTemp())
#print(PoolTemp.getHumidity())
#print(PoolTemp.getState())
'''

GarageController.toggleGarageDoorCtrl()


GarageSensor.refreshGarageDoorSensor()
print(str(GarageSensor.DoorState() ))
print(str(GarageSensor.sensorOnline()))
print()
print(str(GarageSensor.eventPending()))
print()
info = GarageSensor.getInfoAPI()

#GarageSensor.refreshGarageDoorSensor()

WaterLevel.refreshSensor()
print(str(WaterLevel.probeState() ))
print(str(WaterLevel.eventPending()))
print()
print(str(WaterLevel.sensorOnline()))
print()
info = WaterLevel.getInfoAPI()


MotionSensor.refreshSensor()
print(str(MotionSensor.motionState() ))
print(str(MotionSensor.getMotionData()))
print()
print(str(MotionSensor.eventPending()))
print()
print(str(MotionSensor.sensorOnline()))
print()
info = MotionSensor.getInfoAPI()

'''

'''
IrrigationValve.refreshState()
IrrigationValve.refreshSchedules()
#IrrigationValve.refreshFWversion()

IrrigationValve.resetSchedules()
sch1 = IrrigationValve.addSchedule({'days':['mon','wed', 'fri'], 'onTime':'16:30', 'offTime':'17:30','isValid':'Disabled' })
sch2 =IrrigationValve.addSchedule({'days':['thu','tue', 'sun'], 'onTime':'16:31', 'offTime':'17:30','isValid':'Disabled' })
sch3 = IrrigationValve.addSchedule({'days':['mon','wed', 'sat'], 'onTime':'16:32', 'offTime':'17:00','isValid':'Disabled' })
#print (IrrigationValve.scheduleList)
test = IrrigationValve.activateSchedules(sch3, True)
#print (IrrigationValve.scheduleList)
#test = IrrigationValve.deleteSchedule(sch2)
print (IrrigationValve.scheduleList)
sch2 =IrrigationValve.addSchedule({'days':['thu','tue', 'sun'], 'offTime':'17:30','isValid':'Enabled' })

test = IrrigationValve.transferSchedules()
IrrigationValve.refreshState()
IrrigationValve.refreshSchedules()
IrrigationValve.refreshFWversion()

#WaterLevel.refreshSensor()

#print(str(WaterLevel.getState())  )
#print(str(WaterLevel.getInfoAll()) )
#print(str(WaterLevel.getTimeSinceUpdate())+'\n')

IrrigationValve.refreshState()


'''
while True :
    time.sleep(10)
print('end')

yolink_client.shurt_down()

