
import sys
import time


from yoLink_init_V3 import YoLinkInitPAC

'''
'''

from yoLink_init_V3 import YoLinkInitPAC
from yolinkMultiOutletV3 import YoLinkMultiOut
from yolinkVibrationSensorV2 import YoLinkVibrationSen
from yolinkLeakSensorV2 import YoLinkLeakSen
from yolinkMotionSensorV2 import YoLinkMotionSen
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






class test_test (object):

    def __init__ (self):
        '''   '''
        self.uaid = 'ua_05E8E07C48EC4639BB2CE61CAFCC551A'
        self.secretKey = 'sec_v1_uufF2C3GIb+kcV5ipS+9tg=='        
        self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
        self.deviceList = self.yoAccess.getDeviceList()
        for dev in self.deviceList:
            if dev['type'] == 'MultiOutlet':
                self.mout = YoLinkMultiOut(self.yoAccess, dev, self.updateStatus_mout)
                time.sleep(1)
                self._mout.initNode()
                time.sleep(3)
                #self._mout.start()
            if dev['type'] == 'VibrationSensor':
                self.vibra = YoLinkVibrationSen(self.yoAccess, dev, self.updateStatus_vibra)
                time.sleep(1)
                self._mout.initNode()
                time.sleep(3)

            if dev['type'] == 'LeakSensor':
                self.leak = YoLinkLeakSen(self.yoAccess, dev, self.updateStatus_leak)
                time.sleep(1)
                self.leak.initNode()
                time.sleep(3)            

            if dev['type'] == 'MotionSensor':
                self.motion = YoLinkMotionSen(self.yoAccess, dev, self.updateStatus_motion)
                time.sleep(1)
                self.motion.initNode()
                time.sleep(3)
            
    def updateStatus_mout(self, data):
        
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self._mout.updateStatus(data)
        self.updateDatamOut()
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)


    def updateStatus_vibra(self, data):
        
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self._mout.updateStatus(data)
        self.updateStatus_vibraupdateData_leak
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)

    def updateStatus_leak(self, data):
        
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self._mout.updateStatus(data)
        self.updateStatus_leak()
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)
        # 

    def updateStatus_mout(self, data):
        
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self._mout.updateStatus(data)
        self.updateStatus_motion()
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)#         



    def updateDatamOut(self):
        self.m_outlet_s =  self._mout.getMultiOutStates()

    def updateStatus_vibra(self):
        self.vibra_s =  self.vibra.getState()

    def updateStatus_leak(self):
        self.leam_s =  self.leak.getState()

    def updateStatus_motion(self):
        self.motion_s =  self.motion.getState()                



    def set_mOut(self, state, port):
        self._mout.setMultiOutPortState(port, state)

test = test_test()
tmp1 = test.leak.getState()
tmp2 = test.motion.getState()
tmp3 = test.vibra.getState
tmp4 = test.mout.setMultiOutPortState( 'open', {'port0'})
tmp5 = test.mout.setMultiOutPortState( 'closed',{ 0})
tmp6 = test.mout.getMultiOutPortState({'port1'})
tmp7 = test.mout.getMultiOutStates()

test = input('Press any key') 
