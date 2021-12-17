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

    def  __init__(self, polyglot, primary, address, name, callback):
        super().__init__( polyglot, primary, address, name)   
        self.callback = callback
        #self.port = port
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
        logging.debug('MultiOutlet Node INIT')
 
        
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
        self.subNodesReady = False
        logging.debug('start - udiYoMultiOutlet')
        self.yoMulteOutlet  = YoLinkMultiOut(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        self.yoMulteOutlet.initNode()
        time.sleep(2)
        self.nbrOutlets = self.yoMulteOutlet.getNbrPorts()
        states = self.yoMulteOutlet.getMultiOutletState()
        delays = self.yoMulteOutlet.getDelays()
        logging.debug('init data {}, {}, {}'.format(self.nbrOutlets, states, delays))

        self.subnodeName = {}
        if self.yoMulteOutlet.online:
            for port in range(0,self.nbrOutlets):
                try:
                    self.subnodeName[port] = self.address+'s'+str(port+1)
                    node = udiYoSubOutlet(self.poly, self.address, self.subnodeName[port], 'SubOutlet-'+str(port+1), port, self.subOutletUpdates)
                    self.poly.addNode(node)
                    self.wait_for_node_done()
                    
                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subnodeName[port], e))
            if self.nbrOutlets == 4: #controllable USB included
                try:
                    self.subnodeName[4] = self.address+'u'+str(5)
                    node = udiYoSubUSB(self.poly, self.address,self.subnodeName[4] , 'USB Ports', self.usbUpdates)
                    self.poly.addNode(node)
                    self.wait_for_node_done()
            
                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subnodeName[port], e))
            self.node.setDriver('ST', 1, True, True)
            self.subNodesReady = True
            self.createdNodes = self.poly.getNodes()
        else:
            logging.info('MultiOulet is not online')
        #time.sleep(3)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def subOutletUpdates(self, port, data):
        logging.info('subOutletUpdates')
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
        logging.debug('updateStatus - udiYoMultiOutlet')
        self.yoMulteOutlet.updateCallbackStatus(data)

        logging.debug('updateCallbackStatus - udiYoMultiOutlet')
        logging.debug(data)
        self.nbrOutlets = self.yoMulteOutlet.getNbrPorts()
        logging.debug('nbr ports{} , online {}'.format(self.nbrOutlets, self.yoMulteOutlet.online ))
        logging.debug('udiYoMultiOutlet - nbrOutlets: {}'.format(self.nbrOutlets))
        self.delaysActive = False
        outletStates =  self.yoMulteOutlet.getMultiOutletState()
        logging.debug(outletStates)
        if self.subNodesReady:
            for port in range(0,self.nbrOutlets):
                if  self.yoMulteOutlet.online:
                    portName = 'port'+str(port)
                    port = outletStates[portName]['delays']['ch']
                    State = outletStates[portName]['state']
                    onDelay = outletStates[portName]['delays']['on']
                    offDelay = outletStates[portName]['delays']['off']
                else:
                    State =-1
                    onDelay = 0
                    offDelay = 0
                nodeName = self.subnodeName[port]
                if onDelay != 0 or offDelay != 0:
                    self.delaysActive = True
                for node in self.createdNodes:
                    if node.name == nodeName:
                        node.updateNode(State, onDelay,offDelay )
            if self.nbrOutlets == 4:
                logging.debug('need to add USB port support in data extraction ')
                portName = 'port4'
                nodeName = self.subnodeName[4]
                if  self.yoMulteOutlet.online:
                    USBport = outletStates[portName]['state']
                else:
                    USBport = -1
                for node in self.createdNodes:
                    logging.debug('search node name - {}'.format(node.name))
                    if node.name == nodeName:
                        node.updateNode(USBport)
  

                
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
        if self.delaysActive and self.yoMulteOutlet.online: 
            delays =  self.yoMulteOutlet.getDelays()
            logging.debug('delays: ' + str(delays))
            delayActive = False
            #outletStates =  self.yoMulteOutlet.getMultiOutletData()
            for port in range(0,self.nbrOutlets):
                portName = 'port'+str(port)
                port = delays[portName]['delays']['ch']
                State = delays[portName]['state']
                onDelay = delays[portName]['delays']['on']
                offDelay = delays[portName]['delays']['off']

                nodeName = self.subnodeName[port]
                if onDelay != 0 or offDelay != 0:
                    self.delaysActive = True
                for node in self.createdNodes:
                    if node.name == nodeName:
                        node.updateNode(State, onDelay,offDelay )
            self.delaysActive = delayActive
        
        
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




