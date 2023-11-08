
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
#from yolink_mqtt_classV3 import YoLinkMQTTDevice

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


class LeakSens (object):
    def __init__ (self, access, dev):
        self.yoAccess = access
        self.leak = self.mout = YoLinkLeakSen(self.yoAccess, dev, self.updateStatus)
        time.sleep(1)
        self.leak.initNode()
        time.sleep(3)

    def updateStatus(self, data):
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self.leak.updateStatus(data)
        #self.updateStatus_leak()
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)

    def getState(self):
        self.leak_s =  self.leak.getState()        
        return(self.leak_s)

    def refreshDevice(self):
        self.leak.refreshDevice()

class VibrationSens (object):
    def __init__ (self, access, dev):
        self.yoAccess = access
        self.vibra = self.mout = YoLinkVibrationSen(self.yoAccess, dev, self.updateStatus)
        time.sleep(1)
        self.vibra.initNode()
        time.sleep(3)

    def updateStatus(self, data):
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self.vibra.updateStatus(data)
        #self.updateStatus_leak()
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)
    def refreshDevice(self):
        self.vibra.refreshDevice()

    def getState(self):
        self.vibra_s =  self.vibra.getState()
        return(self.vibra_s )

class MotionSens (object):
    def __init__ (self, access, dev):
        self.yoAccess = access
        self.motion = self.motion = YoLinkMotionSen(self.yoAccess, dev, self.updateStatus)
        time.sleep(1)
        self.motion.initNode()
        time.sleep(3)

    def updateStatus(self, data):
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self.motion.updateStatus(data)
        #self.updateStatus_leak()
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)        

    def getState(self):
        self.motion_s =  self.motion.getState()     
        return(self.motion_s )
    
    def refreshDevice(self):
        self.motion.refreshDevice()    
    
class MultiOut (object):
    def __init__ (self, access, dev):
        self.yoAccess = access
        self.mout = self.mout = YoLinkMultiOut(self.yoAccess, dev, self.updateStatus)
        time.sleep(1)
        self.mout.initNode()
        time.sleep(3)


    def updateData(self):
        self.m_outlet_s =  self.mout.getMultiOutStates()


    def getStates(self):
        self.m_outlet_s =  self.mout.getMultiOutStates()
        return(self.m_outlet_s)
    
    def refreshDevice(self):
        self.mout.refreshDevice()    


    def updateStatus(self, data):
        #logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.dev['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self.mout.updateStatus(data)
        #self.updateStatus_leak()
        #logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        #if not self.node_fully_config: # Device was never initialized
        ##    logging.debug('Node server not fully configured yet')
        #    self.node_ready = True
        #    #self.yoMultiOutlet.refreshDevice()
        #    time.sleep(10.1)
        #    self.start()
        #    time.sleep(3)

    def set_mOut(self, port, state):
        return(self.mout.setMultiOutPortState(port, state))

class test_test (object):
    def __init__ (self):
        '''   '''
        self.uaid = 'ua_05E8E07C48EC4639BB2CE61CAFCC551A'
        self.secretKey = 'sec_v1_uufF2C3GIb+kcV5ipS+9tg=='        
        self.yoAccess = YoLinkInitPAC (self.uaid, self.secretKey)
        self.deviceList = self.yoAccess.getDeviceList()
        for dev in self.deviceList:
            if dev['type'] == 'MultiOutlet':
                self.mout = MultiOut(self.yoAccess, dev)
                #self._mout.start()
            if dev['type'] == 'VibrationSensor':
                self.vibra = VibrationSens(self.yoAccess, dev)

            if dev['type'] == 'LeakSensor':
                self.leak = LeakSens(self.yoAccess, dev)
       

            if dev['type'] == 'MotionSensor':
                self.motion = MotionSens(self.yoAccess, dev)





           



    def run_tests(self):
       
        self.leak.refreshDevice()
        tmp1 = self.leak.getState()
        time.sleep(2)
        self.motion.refreshDevice()

        tmp2 = self.motion.getState()
        time.sleep(2)
        self.vibra.refreshDevice()
        tmp3 = self.vibra.getState()

        tmp4 = self.mout.set_mOut(  {'port0'}, 'open')
        time.sleep(2)        
        tmp5 = self.mout.set_mOut( {1}, 'closed')
        time.sleep(2)        
        tmp5a = self.mout.refreshDevice()
        time.sleep(2)        
        tmp6 = self.mout.getStates()
        time.sleep(2)        
        tmp4a = self.mout.set_mOut(  {'port1'}, 'open')
        time.sleep(2)        
        tmp4 = self.mout.set_mOut(  {'port0'}, 'closed')
        time.sleep(2)        
        tmp5a = self.mout.refreshDevice()
        time.sleep(2)        
        tmp7 = self.mout.getStates()

test = test_test()
test.run_tests()
test1 = input('Press any key') 
