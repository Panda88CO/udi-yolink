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
from yolinkMultiOutlet import YoLinkMultiOut

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
            {'driver': 'GV0', 'value': 2, 'uom': 25},
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

    def updateNode(self, outeletState, onDelay, offDelay):
        logging.debug('udiYoSubOutlet - updateNode')
        self.node.setDriver('GV0', outeletState, True, True)
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
            {'driver': 'GV0', 'value': 2, 'uom': 25},
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
        self.delaysActive = False


        self.devInfo =  deviceInfo   
        self.yoMulteOutlet = None
        self.n_queue = []

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)

        

        #self.switchState = self.yoMulteOutlet.getState()
        #self.switchPower = self.yoMulteOutlet.getEnergy()
        #udi_interface.__init__(self, polyglot, primary, address, name)

    def start(self):
        logging.debug('start - udiYoMultiOutlet')
        self.yoMulteOutlet  = YoLinkMultiOut(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        self.yoMulteOutlet.initNode()
        time.sleep(2)
        self.nbrOutlets = self.yoMulteOutlet.getNbrPorts()
        states = self.yoMulteOutlet.getMultiOutletState()
        delays = self.yoMulteOutlet.getDelays()
        logging.debug('init data {}, {}, {}'.format(self.nbrOutlets, states, delays))

        self.subnode = {}
        for port in range(0,self.nbrOutlets):
            try:
                self.subnode[port] = self.address+'s'+str(port+1),
                node = udiYoSubOutlet(self.poly, self.address, self.subnode[port], 'SubOutlet-'+str(port+1), port, self.subOutletUpdates)
                self.poly.addNode(node)
                self.wait_for_node_done()
            except Exception as e:
                logging.error('Failed to create {}: {}'.format(self.subnode[port], e))
        if self.nbrOutlets == 4: #controllable USB included
            try:
                self.subnode[4] = self.address+'u'+str(port+1)
                node = udiYoSubUSB(self.poly, self.address,self.subnode[4] , 'USB Ports', self.usbUpdates)
                self.poly.addNode(node)
                self.wait_for_node_done()
            except Exception as e:
                logging.error('Failed to create {}: {}'.format(self.subnode[4], e))
        self.node.setDriver('ST', 1, True, True)
        #time.sleep(3)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def subOutletUpdates(self, port, data):
        logging.info('subOutletUpdates not implemented')
        portList = []
        portList.append(port)
        self.yoMulteOutlet.setMultiOutletState(portList, data)


    def usbUpdates(self,  data):
        logging.info('usbUpdates not implemented')
        portList = []
        portList.append(4) #USB is port 4 (5th port)
        self.yoMulteOutlet.setMultiOutletState(portList, data)



    def stop (self):
        logging.info('Stop not implemented')
        self.node.setDriver('ST', 0, True, True)
        self.yoMulteOutlet.shut_down()


    def updateStatus(self, data):
        #outletNbr = [0:'port1', 1:'port2', 'port3':2, 'port4':3]
        logging.debug('updateStatus - TestYoLinkNode')
        self.yoMulteOutlet.updateCallbackStatus(data)
        logging.debug(data)
        self.delaysActive = False
        outletStates =  self.yoMulteOutlet.getMultiOutletData()
        if not self.nbrOutlets:
            self.nbrOutlets = self.yoMulteOutlet.getNbrPorts()
        for port in range(0,self.nbrOutlets):
            port = outletStates[port]['delays']['ch']
            node = self.subnode[port]
            State = outletStates[port]['state']
            onDelay = outletStates[port]['delays']['on']
            offDelay = outletStates[port]['delays']['off']
            if onDelay != 0 or offDelay != 0:
                self.delaysActive = True
            node.updateNode(State, onDelay,offDelay )
        if self.nbrOutlets == 4:
            logging.debug('need to add USB port support in data extraction ')
            USBport = outletStates[4]['state']
            self.subnode[4].updateNode(USBport)
        #Need to update USB port states 

        '''
        if self.node is not None:
            state =  self.yoMulteOutlet.getState()
            print(state)
            if state.upper() == 'ON':
                self.node.setDriver('GV0', 1, True, True)
            else:
                self.node.setDriver('GV0', 0, True, True)
            #tmp =  self.yoMulteOutlet.getEnergy()
            #power = tmp['power']
            #watt = tmp['watt']
            #self.node.setDriver('GV3', power, True, True)
            #self.node.setDriver('GV4', watt, True, True)
            self.node.setDriver('GV5', self.yoMulteOutlet.bool2Nbr(self.yoMulteOutlet.getOnlineStatus()), True, True)
        
        #while self.yoMulteOutlet.eventPending():
        #    print(self.yoMulteOutlet.getEvent())
        '''

    # Need to use shortPoll
    def pollDelays(self):
        if self.delaysActive: 
            delays =  self.yoMulteOutlet.getDelays()
            logging.debug('delays: ' + str(delays))
            delayActive = False
            #outletStates =  self.yoMulteOutlet.getMultiOutletData()
            for port in range(0,self.nbrOutlets):
                port = delays[port]['delays']['ch']
                node = self.subnode[port]
                State = delays[port]['state']
                onDelay = delays[port]['delays']['on']
                offDelay = delays[port]['delays']['off']
                node.updateNode(State, onDelay,offDelay )
                if onDelay != 0 or offDelay != 0:
                    delayActive = True
            #print('on delay: ' + str(delays['on']))
            #print('off delay: '+ str(delays['off']))
            self.delaysActive = delayActive
        
        
            '''
            if delays != None:
                if delays['on'] != 0 or delays['off'] !=0:
                    delays =  self.yoMulteOutlet.refreshDelays() # should be able to calculate without polling 
                    if 'on' in delays:
                        self.node.setDriver('GV1', delays['on'], True, True)
                    if 'off' in delays:
                        self.node.setDriver('GV2', delays['off'], True, True)               
            else:
                self.node.setDriver('GV1', 0, True, True)     
                self.node.setDriver('GV2', 0, True, True)     
            '''

    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if 'longPoll' in polltype:
            self.yoMulteOutlet.refreshMultiOutlet()
            #self.yoMulteOutlet.refreshSchedules()
        if 'shortPoll' in polltype:
            self.pollDelays()
            #update Delays calculated



    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoMulteOutlet.refreshState()
        #self.yoMulteOutlet.refreshSchedules()     


    commands = {
                'UPDATE': update                        

                }




