#!/usr/bin/env python3
"""
Polyglot TEST v3 node server 


MIT License
"""
from os import truncate
import udi_interface
import sys
import time
from yolinkSwitch import YoLinkSW
logging = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None
Parameters = None
n_queue = []
count = 0

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''

class TestYoLinkNode(udi_interface.Node):
    #def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, devInfo):
    id = 'yoswitch'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 30}, 
            {'driver': 'GV2', 'value': 0, 'uom': 33}, 
            {'driver': 'GV3', 'value': 0, 'uom': 44},
            {'driver': 'GV4', 'value': 0, 'uom': 44},
            ]


    def  __init__(self, polyglot, primary, address, name):
        super(TestYoLinkNode, self).__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('TestYoLinkNode INIT')
        self.csid = '60dd7fa7960d177187c82039'
        self.csseckey = '3f68536b695a435d8a1a376fc8254e70'
        self.csName = 'Panda88'
        self.devInfo = { "deviceId": "d88b4c0100034906",
                    "deviceUDID": "e091320786e5447099c8b1c93ce47a60",
                    "name": "S Playground Switch",
                    "token": "7f43fbce-dece-4477-9660-97804b278190",
                    "type": "Switch"
                    }
        self.mqtt_URL= 'api.yosmart.com'
        self.mqtt_port = 8003
        self.yolink_URL ='https://api.yosmart.com/openApi'
        self.yoSwitch = None
        
        #self.poly = polyglot
        #self.count = 0
        #self.n_queue = []

        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, address)
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)


        #self.switchState = self.yoSwitch.getState()
        #self.switchPower = self.yoSwitch.getEnergy()
        #udi_interface.__init__(self, polyglot, primary, address, name)

    def start(self):
        print('start - YoLinkSw')
        self.yoSwitch  = YoLinkSW(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        self.yoSwitch.initNode()
        #time.sleep(3)
    
    def heartbeat(self):
        #LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

    def updateStatus(self, data):
        #while not self.yoSwitch:
        #    time.sleep(2)
        logging.debug('updateStatus - TestYoLinkNode')
        self.yoSwitch.updateCallbackStatus(data)
        print(data)
        self.node = polyglot.getNode('yoswitch')
        if self.node is not None:
            state =  self.yoSwitch.getState()
            print(state)
            if state.upper() == 'ON':
                self.node.setDriver('GV0', 1, True, True)
            else:
                self.node.setDriver('GV0', 0, True, True)
            tmp =  self.yoSwitch.getEnergy()
            print(tmp)
            power = tmp['power']
            watt = tmp['watt']
            print ('power ' + str(power) + ', watt ' +str(watt))
            self.node.setDriver('GV1', power, True, True)
            self.node.setDriver('GV2', watt, True, True)
            self.pollDelays()

    def pollDelays(self):
        delays =  self.yoSwitch.getDelays()
        #logging.debug('delays: ' + str(delays))
        #print('on delay: ' + str(delays['on']))
        #print('off delay: '+ str(delays['off']))
        if delays != None:
            while delays['on'] != 0 or delays['off'] !=0:
                delays =  self.yoSwitch.refreshDelays() # should be able to calculate without polling 
                delayActve = False
                if 'on' in delays:
                    if delays['on'] != 0:
                        delayActve = True
                    self.node.setDriver('GV3', delays['on'], True, True)
                if 'off' in delays:
                    if delays['off'] != 0:
                        delayActve = True
                    self.node.setDriver('GV4', delays['off'], True, True)               
                if not delayActve:
                    break
                time.sleep(30) # shortPoll???
            self.node.setDriver('GV4', delays['off'], True, True)     
            self.node.setDriver('GV3', delays['on'], True, True)
        else:
            self.node.setDriver('GV4', 0, True, True)     
            self.node.setDriver('GV3', 0, True, True)     

    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if 'longPoll' in polltype:
            self.yoSwitch.refreshState()
            self.yoSwitch.refreshSchedules()

    def switchControl(self, command):
        logging.info('switchControl')
        state = int(command.get('value'))
        if state == 1:
            self.yoSwitch.setState('ON')
        else:
            self.yoSwitch.setState('OFF')

    def setOnDelay(self, command):
        logging.info('setOnDelay')
        delay = int(command.get('value'))
        self.yoSwitch.setDelays([{'delayOn':int(delay)}])

        

    def setOffDelay(self, command):
        logging.info('setOnDelay')
        delay = int(command.get('value'))
        self.yoSwitch.setDelays([{'delayOff':int(delay)}])


    def parameterHandler(self, params):
        self.Parameters.load(params)

    def stop (self):
        logging.info('Stop not implemented')
        self.yoSwitch.shut_down()

    def update(self):
        logging.info('Update')
        self.yoSwitch.refreshState()
        self.yoSwitch.refreshSchedules()     


    commands = {'UPDATE': update,
                'SWCTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay 
                }



if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

       
        TestYoLinkNode(polyglot, 'yoswitch', 'yoswitch', 'Yolink Switch')


        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

