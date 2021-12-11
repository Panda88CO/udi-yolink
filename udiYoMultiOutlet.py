#!/usr/bin/env python3
"""
MIT License
"""

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

import sys
import time
from yolinkMultiOutlet import YoLinkOutl

polyglot = None
Parameters = None
n_queue = []
count = 0

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''
class udiYoSubOutlet(udi_interface.Node):
    
    id = 'yosubout'
    '''
       drivers = [
            'GV0' = Outlet1 State
            'GV1' = OnDelay
            'GV2' = OffDelay
            'GV4' = outletNbr
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 0, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 30}, 
            {'driver': 'GV2', 'value': 0, 'uom': 33}, 
            {'driver': 'GV4', 'value': 0, 'uom': 33},           
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]

    
    def  __init__(self, polyglot, primary, address, name, port, callback ):
        super().__init__( polyglot, primary, address, name )
        self.port = port
        self.callback = callback
        logging.debug('udiYoSubOutlet - init')
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))          
        
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))   

        self.poly.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)
        self.node.setDriver('GV4', self.port+1, True, True)

    def start (self):
        logging.debug('udiYoSubOutlet - start')
      
    def stop (self):
        logging.debug('udiYoSubOutlet - stop')
        self.node.setDriver('ST', 0, True, True)

    def updateNode(self, outeletStata, onDelay, offDelay):
        logging.debug('udiYoSubOutlet - updateNode')
        self.node.setDriver('GV0', outeletStata, True, True)
        self.node.setDriver('GV1', onDelay, True, False)
        self.node.setDriver('GV2', offDelay, True, False)
        self.node.setDriver('GV4', self.port+1, False, False)

    def switchControl(self, command):
        logging.info('switchControl')
        state = int(command.get('value'))     
        if state == 1:
            self.callback(self.port, {'switch':'ON'})
        else:
            self.callback(self.port, {'switch':'OFF'})
        self.node.setDriver('GV0', state, True, True)
        
    def setOnDelay(self, command ):
        logging.info('setOnDelay')
        delay =int(command.get('value'))
        self.callback(self.port, {'delayOn':delay})
        

    def setOffDelay(self, command):
        logging.info('setOnDelay Executed')
        delay =int(command.get('value'))
        self.callback(self.port,{'delayOff':delay})
        self.node.setDriver('GV2', delay, True, True)



    def update(self, command = None):
        logging.info('Update Status Executed')
  


    commands = {
                'SWCTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay,
                'update' : update
                }


class udiYoSubUSB(udi_interface.Node):
    id = 'yosubusb'
    '''
       drivers = [
            'GV0' = usb State
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]

    def  __init__(self, polyglot, primary, address, name, port, callback):
        super().__init__( polyglot, primary, address, name)   
        self.callback = callback
        self.port = port
        logging.debug('udiYoSubUSB - init')
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))    


        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)

        self.poly.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)

    def start (self):
       logging.debug('udiYoSubUSB - start')

    def stop (self):
        logging.debug('udiYoSubUSB - stop')
        self.node.setDriver('ST', 0, True, True)


    def updateNode(self, gv0):
        logging.debug('udiYoSubUSB - updateNode')
        self.node.setDriver('GV0', gv0, True, True)

    def usbControl(self, command):
        logging.info('switchControl')
        state = int(command.get('value'))     
        if state == 1:
            self.callback(self.port, {'switch':'ON'})
        else:
            self.callback(self.port, {'switch':'OFF'})
        self.node.setDriver('GV0', state, True, True)

    def update(self, command = None):
        logging.info('Update Status Executed')

    commands = {
                 'USBCTRL': usbControl, 
                 'UPDATE' : update
                }

class udiYoMultiOutlet(udi_interface.Node):
    #def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, devInfo):
    id = 'yomultiout'
 
    '''
       drivers = [
            'GV8' = online
            ]
    ''' 
    drivers = [
            {'driver': 'GV8', 'value': 0, 'uom': 25},
            {'driver': 'ST', 'value': 0, 'uom': 25}, 
            ]
    

    def  __init__(self, polyglot, primary, address, name, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('TestYoLinkNode INIT')
 
        
        self.csid = csid
        self.csseckey = csseckey
        self.csName = csName

        self.mqtt_URL= mqtt_URL
        self.mqtt_port = mqtt_port
        self.yolink_URL = yolink_URL

        self.devInfo =  deviceInfo   
        self.yoOutlet = None

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)

        #self.switchState = self.yoOutlet.getState()
        #self.switchPower = self.yoOutlet.getEnergy()
        #udi_interface.__init__(self, polyglot, primary, address, name)

    def start(self):
        logging.debug('start - udiYoMultiOutlet')
        self.yoOutlet  = YoLinkOutl(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        self.yoOutlet.initNode()
        nbrOutlets = self.yoOutlet.getNbrPorts()
        states = self.yoOutlet.getMultiOutletState()
        delays = self.yoOutlet.getDelays()

        self.subnode = []
        for port in range(0,nbrOutlets):
            try:
                self.subnode[port] = udiYoSubOutlet(self.poly, self.address, self.address+str(port+1), 'SubOutlet'+str(port+1), port, self.subOutletUpdates)
                self.poly.addNode(self.subnode[port])
                self.wait_for_node_done()
            except Exception as e:
                logging.error('Failed to create {}: {}'.format(e))
        if nbrOutlets == 4: #controllable USB included
            try:
                self.subnode[nbrOutlets] = udiYoSubUSB(self.poly, self.address, self.address+str(nbrOutlets+1), 'UsbOutput', self.usbUpdates)
                self.poly.addNode(self.subnode[nbrOutlets])
                self.wait_for_node_done()
            except Exception as e:
                logging.error('Failed to create {}: {}'.format(e))
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)


    def subOutletUpdates(self, port, data):
        logging.info('subOutletUpdates not implemented')
        


    def usbUpdates(self,  data):
        logging.info('usbUpdates not implemented')



    '''
    def heartbeat(self):
        #logging.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd('DON',2)
            self.hb = 1
        else:
            self.reportCmd('DOF',2)
            self.hb = 0

    def parameterHandler(self, params):
        self.Parameters.load(params)
    '''
    def stop (self):
        logging.info('Stop not implemented')
        self.node.setDriver('ST', 0, True, True)
        self.yoOutlet.shut_down()


    def updateStatus(self, data):
        logging.debug('updateStatus - TestYoLinkNode')
        self.yoOutlet.updateCallbackStatus(data)
        print(data)
        if self.node is not None:
            state =  self.yoOutlet.getState()
            print(state)
            if state.upper() == 'ON':
                self.node.setDriver('GV0', 1, True, True)
            else:
                self.node.setDriver('GV0', 0, True, True)
            #tmp =  self.yoOutlet.getEnergy()
            #power = tmp['power']
            #watt = tmp['watt']
            #self.node.setDriver('GV3', power, True, True)
            #self.node.setDriver('GV4', watt, True, True)
            self.node.setDriver('GV5', self.yoOutlet.bool2Nbr(self.yoOutlet.getOnlineStatus()), True, True)
        
        #while self.yoOutlet.eventPending():
        #    print(self.yoOutlet.getEvent())


    # Need to use shortPoll
    def pollDelays(self):
        delays =  self.yoOutlet.getDelays()
        logging.debug('delays: ' + str(delays))
        #print('on delay: ' + str(delays['on']))
        #print('off delay: '+ str(delays['off']))
        if delays != None:
            if delays['on'] != 0 or delays['off'] !=0:
                delays =  self.yoOutlet.refreshDelays() # should be able to calculate without polling 
                if 'on' in delays:
                    self.node.setDriver('GV1', delays['on'], True, True)
                if 'off' in delays:
                    self.node.setDriver('GV2', delays['off'], True, True)               
        else:
            self.node.setDriver('GV1', 0, True, True)     
            self.node.setDriver('GV2', 0, True, True)     

    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if 'longPoll' in polltype:
            self.yoOutlet.refreshState()
            self.yoOutlet.refreshSchedules()
        if 'shortPoll' in polltype:
            self.pollDelays()
            #update Delays calculated



    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoOutlet.refreshState()
        #self.yoOutlet.refreshSchedules()     


    commands = {
                'UPDATE': update                        

                }




