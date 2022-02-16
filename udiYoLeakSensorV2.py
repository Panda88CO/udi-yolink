#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate

from yolinkLeakSensorV2 import YoLinkLeakSen
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

polyglot = None
Parameters = None
n_queue = []
count = 0



class udiYoLeakSensor(udi_interface.Node):
    id = 'yoleaksens'
    
    '''
       drivers = [
            'GV0' = Water Alert
            'GV1' = Battery Level
            'GV8' = Online
            ]

    ''' 
        
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25}, 
            {'driver': 'GV1', 'value': 99, 'uom': 25}, 
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]


    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('udiYoLeakSensor  INIT')
        self.yoAccess = yoAccess
        self.devInfo =  deviceInfo   
        self.yoTHsensor  = None
        #self.address = address
        #self.poly = polyglot

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        

        #self.switchState = self.yoSwitch.getState()
        #self.switchPower = self.yoSwitch.getEnergy()
        #udi_interface.__init__(self, polyglot, primary, address, name)

    def start(self):
        print('start - YoLinkLeakSensor')
        self.yoLeakSensor  = YoLinkLeakSen(self.yoAccess, self.devInfo, self.updateStatus)
        if self.yoLeakSensor:
            self.yoLeakSensor.initNode()
            self.node.setDriver('ST', 1, True, True)
        else:
            logging.error('Not able to connect leakSensor')
        #time.sleep(3)
    

    def initNode(self):
        self.yoLeakSensor.refreshSensor()

    
    def stop (self):
        logging.info('Stop udiYoLeakSensor ')
        self.node.setDriver('ST', 0, True, True)
        self.yoLeakSensor.shut_down()

    '''
    def yoTHsensor.bool2Nbr(self, bool):
        if bool:
            return(1)
        else:
            return(0)
    '''
    
    def waterState(self):
        if self.yoLeakSensor.online:
            if  self.yoLeakSensor.probeState() == 'normal' or self.yoLeakSensor.probeState() == 'dry' :
                return(0)
            else:
                return(1)
        else:
            return(99)

    def updateStatus(self, data):
        logging.debug('updateStatus - yoLeakSensor')
        self.yoLeakSensor.updateCallbackStatus(data)
        #motionState = self.yoLeakSensor.getMootion()

        logging.debug(data)
        if self.node is not None:
            if self.yoLeakSensor.online:
                waterState =   self.waterState()  
                logging.debug( 'Leak Sensor 0,1,8: {}  {} {}'.format(waterState,self.yoLeakSensor.getBattery(),self.yoLeakSensor.bool2Nbr(self.yoLeakSensor.getOnlineStatus())  ))
                self.node.setDriver('GV0', waterState, True, True)
                self.node.setDriver('GV1', self.yoLeakSensor.getBattery(), True, True)
                self.node.setDriver('GV8', 1, True, True)
            else:
                self.node.setDriver('GV0', 99, True, True)
                self.node.setDriver('GV1', 99, True, True)
                self.node.setDriver('GV8', 0, True, True)


    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if 'longPoll' in polltype:
            self.yoLeakSensor.refreshSensor()

    def update(self, command = None):
        logging.info('THsensor Update Status Executed')
        self.yoLeakSensor.refreshState()
       

    commands = {
                'UPDATE': update,
                }





