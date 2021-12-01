#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""
from os import truncate
import udi_interface
import sys
import time

from udiYoSwitch import udiYoSwitch
from udiYoTHsensor import udiYoTHsensor 
from udiYoGarageDoor import udiYoGarageDoor
from udiYoMotionSensor import udiYoMotionSensor
from udiYoLeakSensor import udiYoWaterSensor


logging = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None
Parameters = None





'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''
class YoLinkSetup (udi_interface.Node):
    def  __init__(self, polyglot, primary, address, name):
        super(YoLinkSetup, self).__init__( polyglot, primary, address, name)  
        csid = '60dd7fa7960d177187c82039'
        csseckey = '3f68536b695a435d8a1a376fc8254e70'
        csName = 'Panda88'
        devInfo = { "deviceId": "d88b4c0100034906",
                    "deviceUDID": "e091320786e5447099c8b1c93ce47a60",
                    "name": "S Playground Switch",
                    "token": "7f43fbce-dece-4477-9660-97804b278190",
                    "type": "Switch"
                    }
        devInfo2 =  {
                    "deviceId": "d88b4c01000348a6",
                    "deviceUDID": "187bcd4f373e4a11bcc7d1486cfc7c95",
                    "name": "S Matias Garden",
                    "token": "4a9744d4-4c8e-4b01-a8bb-e84b639d0591",
                    "type": "Switch"
                    }
        outdoorTemp =  {
                "deviceId": "d88b4c010003598f",
                "deviceUDID": "bf9c17dadffd460d8edb233dfc3d7d8f",
                "name": "Temp Humidity Sensor",
                "token": "233cfde3-4282-4356-94f1-af3319b48afb",
                "type": "THSensor"
                }
        poolTemp =  {
                "deviceId": "d88b4c0100037f58",
                "deviceUDID": "c89a3e596c694ea3975449d1f264c0f3",
                "name": "Temperature Sensor",
                "token": "db22f34e-79c8-4984-ab50-5243780591f8",
                "type": "THSensor"
                }      
        winecooler =             {
                "deviceId": "d88b4c0200041f5e",
                "deviceUDID": "7bf50baa02364a8a8c1dbc963f56d217",
                "name": "Temp Humidity Sensor",
                "token": "b6696161-e039-4e5b-b57a-e5338709bc80",
                "type": "THSensor"
            }
        garageDoor = [
                {
                "deviceId": "d88b4c010003281d",
                "deviceUDID": "b408eb2c895e467bac5e8c812ac5fe48",
                "name": "Garage Door Sensor",
                "token": "775852f1-7026-4ca1-a2d1-2c1093aa4c3d",
                "type": "DoorSensor"
                },
                {
                "deviceId": "d88b4c0100038d31",
                "deviceUDID": "99836dc7826b4a469120930eef04efe4",
                "name": "Garage Door Controller",
                "token": "9f565525-67bf-42ae-8acb-307332d6d3a7",
                "type": "GarageDoor"
                 }

                 ]      
        motion =  {
                "deviceId": "d88b4c0200037b09",
                "deviceUDID": "397a811123a44476b898a50db4edd889",
                "name": "Motion Sensor",
                "token": "52b14813-dd4b-4568-966a-51307334a9c2",
                "type": "MotionSensor"
                }
        waterSensor =  {
                "deviceId": "d88b4c0300001596",
                "deviceUDID": "afb6f3f8e2294e44ae35f819c137c8b8",
                "name": "Leak Sensor",
                "token": "b4d750c0-a66b-4b9a-b96b-b2097cbf1e6a",
                "type": "LeakSensor"
                }

        '''
            {
                "deviceId": "d88b4c010002e621",
                "deviceUDID": "5c4a0f90dd3e48cf91c597bc0aba6e7d",
                "name": "Power Strip",
                "token": "65edd0ce-ad2a-445b-8218-2dd024643718",
                "type": "MultiOutlet"
            },
            {
                "deviceId": "d88b4c010003430a",
                "deviceUDID": "ef5f98b9fd694596a411f903df8f564d",
                "name": "YoLink Valve",
                "token": "f9550017-5f30-43e5-bba4-6082f1ebb990",
                "type": "Manipulator"
            },
            {
                "deviceId": "d88b4c01000341c3",
                "deviceUDID": "5e0769573c174be1b6aea67bf9f0ec95",
                "name": "YoLink Valve",
                "token": "54b358e9-5036-4064-8afc-b569ec559827",
                "type": "Manipulator"
            },

            {
                "deviceId": "d88b4c0100029ccf",
                "deviceUDID": "247baa1614714d459e6d27ee3a2d3966",
                "name": "Power Strip",
                "token": "aaa92779-633f-47ab-807d-f0470176521c",
                "type": "MultiOutlet"
            },

            {
                "deviceId": "d88b4c0100029e6e",
                "deviceUDID": "85392d2831884b90a1b186c7f23a81d8",
                "name": "S Deck Light",
                "token": "1267e6bd-0f16-4220-9576-fdb552a73c0f",
                "type": "MultiOutlet"
            },
            {
                "deviceId": "d88b4c02000177a0",
                "deviceUDID": "3a1ddca4536c48ca9a609a8eb07d90b9",
                "name": "S Door Sensor 1",
                "token": "275a6fcc-5e8c-45ca-ad45-ca2c159378f0",
                "type": "DoorSensor"
            },
            {
                "deviceId": "d88b4c01000301db",
                "deviceUDID": "56e4961b5a3246b6a90c23176447d92f",
                "name": "S USB Outlet 1",
                "token": "91a8ba8c-03bf-42c3-a1a8-23de834c7154",
                "type": "Outlet"
            },


        '''
        #rememebr names must be small letters
        udiYoTHsensor(polyglot, 'yotemp', 'yotemp', 'Yolink Wine Twmp', csName, csid, csseckey, winecooler)
        udiYoSwitch(polyglot, 'yoswitch', 'yoswitch', 'Playground', csName, csid, csseckey, devInfo )
        udiYoSwitch(polyglot, 'yoswitch2', 'yoswitch2', 'Matias Garden', csName, csid, csseckey, devInfo2 )
        udiYoTHsensor(polyglot, 'yotemp1', 'yotemp1', 'Yolink Pool Temp', csName, csid, csseckey, poolTemp )
        udiYoTHsensor(polyglot, 'yotemp2', 'yotemp2', 'Yolink Pool Temp', csName, csid, csseckey, outdoorTemp )
        udiYoGarageDoor(polyglot, 'yogarage1', 'yogarage1', 'Yolink Grage Door', csName, csid, csseckey, garageDoor )
        udiYoMotionSensor(polyglot, 'yomotion1', 'yomotion1', 'Yolink Motions Sensor', csName, csid, csseckey, motion )
        udiYoWaterSensor(polyglot, 'yowater1', 'yowater1', 'Yolink Motions Sensor', csName, csid, csseckey, waterSensor )

        mqtt_URL= 'api.yosmart.com'
        mqtt_port = 8003
        yolink_URL ='https://api.yosmart.com/openApi'





if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()
        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

