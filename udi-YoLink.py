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
        devTHsensor =  {
                "deviceId": "d88b4c010003598f",
                "deviceUDID": "bf9c17dadffd460d8edb233dfc3d7d8f",
                "name": "Temp Humidity Sensor",
                "token": "233cfde3-4282-4356-94f1-af3319b48afb",
                "type": "THSensor"
                }
        wineCooler =  {
                "deviceId": "d88b4c0100037f58",
                "deviceUDID": "c89a3e596c694ea3975449d1f264c0f3",
                "name": "Temperature Sensor",
                "token": "db22f34e-79c8-4984-ab50-5243780591f8",
                "type": "THSensor"
            }

        #rememebr names must be small letters
        udiYoTHsensor(polyglot, 'yotemp', 'yotemp', 'Yolink Wine Twmp', csName, csid, csseckey, devTHsensor )
        udiYoSwitch(polyglot, 'yoswitch', 'yoswitch', 'Playground', csName, csid, csseckey, devInfo )
        udiYoSwitch(polyglot, 'yoswitch2', 'yoswitch2', 'M Garden', csName, csid, csseckey, devInfo2 )
        udiYoTHsensor(polyglot, 'yotemp1', 'yotemp1', 'Yolink Pool Temp', csName, csid, csseckey, wineCooler )


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
        

