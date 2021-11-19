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


logging = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None
Parameters = None
n_queue = []
count = 0

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



mqtt_URL= 'api.yosmart.com'
mqtt_port = 8003
yolink_URL ='https://api.yosmart.com/openApi'




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
        udiYoSwitch(polyglot, 'yoswitch', 'yoswitch', 'Yolink Switch', csName, csid, csseckey, devInfo )
        udiYoSwitch(polyglot, 'yoswitch2', 'yoswitch2', 'Yolink Switch2', csName, csid, csseckey, devInfo2 )


        mqtt_URL= 'api.yosmart.com'
        mqtt_port = 8003
        yolink_URL ='https://api.yosmart.com/openApi'





if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()
        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')
        #udiYoSwitch(polyglot, 'yoswitch', 'yoswitch', 'Yolink Switch', csName, csid, csseckey, devInfo )
        #udiYoSwitch(polyglot, 'yoswitch2', 'yoswitch2', 'Yolink Switch2', csName, csid, csseckey, devInfo2 )

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

