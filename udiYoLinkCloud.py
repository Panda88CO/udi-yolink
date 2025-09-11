#!/usr/bin/env python3
"""
Yolink Control Main Node  program 
MIT License
"""

import sys
import time
#from apscheduler.schedulers.background import BackgroundScheduler


#from yoLink_init_V3 import YoLinkInitPAC
#from udiYoSwitchV2 import udiYoSwitch
#from udiYoSwitchSecV2 import udiYoSwitchSec
#from udiYoSwitchPwrSecV2 import udiYoSwitchPwrSec
#from udiYoTHsensorV3 import udiYoTHsensor 
#from udiYoWaterDeptV3 import udiYoWaterDept 
#from udiYoGarageDoorCtrlV2 import udiYoGarageDoor
#from udiYoGarageFingerCtrlV2 import udiYoGarageFinger
#from udiYoMotionSensorV3 import udiYoMotionSensor
#from udiYoLeakSensorV3 import udiYoLeakSensor
#from udiYoCOSmokeSensorV3 import udiYoCOSmokeSensor
#from udiYoDoorSensorV3 import udiYoDoorSensor
#from udiYoOutletV2 import udiYoOutlet
#from udiYoOutletPwrV2 import udiYoOutletPwr
#from udiYoMultiOutletV2 import udiYoMultiOutlet
#from udiYoManipulatorV2 import udiYoManipulator
#from udiYoSpeakerHubV2 import udiYoSpeakerHub
#from udiYoLockV2 import udiYoLock
#from udiYoInfraredRemoterV3 import udiYoInfraredRemoter
#from udiYoDimmerV2 import udiYoDimmer
#from udiYoVibrationSensorV3 import udiYoVibrationSensor
#from udiYoSmartRemoterV3 import udiYoSmartRemoter
#from udiYoPowerFailV3 import udiYoPowerFailSenor
#from udiYoSirenV2 import udiYoSiren
#from udiYoWaterMeterControllerV3 import udiYoWaterMeterController
#from udiYoWaterMeterOnlyV3 import udiYoWaterMeterOnly
#from udiYoHubV2 import udiYoHub, udiYoBatteryHub
#import udiProfileHandler

from udiYoLink import YoLinkSetup

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)


version = '1.5.3'

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])


        polyglot.start(version)

        YoLinkSetup(polyglot, 'setup', 'setup', 'YoLinkSetup')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)