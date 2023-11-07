
import sys
import time


from yoLink_init_V3 import YoLinkInitPAC
'''
from udiYoSwitchV2 import udiYoSwitch
from udiYoTHsensorV2 import udiYoTHsensor 
from udiYoGarageDoorCtrlV2 import udiYoGarageDoor
from udiYoGarageFingerCtrlV2 import udiYoGarageFinger
from udiYoMotionSensorV2 import udiYoMotionSensor
from udiYoLeakSensorV2 import udiYoLeakSensor
from udiYoCOSmokeSensorV2 import udiYoCOSmokeSensor
from udiYoDoorSensorV2 import udiYoDoorSensor
from udiYoOutletV2 import udiYoOutlet
from udiYoMultiOutletV2 import udiYoMultiOutlet
from udiYoManipulatorV2 import udiYoManipulator
#from udiYoHubV2 import udiYoHub
from udiYoSpeakerHubV2 import udiYoSpeakerHub
from udiYoLockV2 import udiYoLock
from udiYoInfraredRemoterV2 import udiYoInfraredRemoter
from udiYoDimmerV2 import udiYoDimmer
from udiYoVibrationSensorV2 import udiYoVibrationSensor
from udiYoSmartRemoterV3 import udiYoSmartRemoter
from udiYoPowerFailV2 import udiYoPowerFailSenor
from udiYoSirenV2 import udiYoSiren
'''
from yolinkMultiOutletV3 import YoLinkMultiOut

import udiProfileHandler

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)






class testmout (object):

    def __init__ (self):
        '''   '''
        self.uaid = 'ua_05E8E07C48EC4639BB2CE61CAFCC551A'
        self.secretKey = 'sec_v1_uufF2C3GIb+kcV5ipS+9tg=='        
        self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
        self.deviceList = self.yoAccess.getDeviceList()
        for dev in self.deviceList:
            if dev['type'] == 'MultiOutlet':
                self.mout = YoLinkMultiOut(self.yoAccess, dev, self.updateStatusmout)
                time.sleep(1)
                self.mout.initNode()
                time.sleep(3)
                #self.mout.start()
            
    def updateStatusmout(self, data):
        
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self.mout.updateStatus(data)
        self.updateDatamOut
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)

    def updateDatamOut(self):
        outletStates =  self.mout.getMultiOutStates()


    def set_mOut(self, state, port):
        self.mout.setMultiOutPortState(port, state)

testing = testmout()
testing.set_mOut( 'open', {'port0'})
testing.set_mOut( 'closed',{ 0})
