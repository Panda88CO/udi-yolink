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
            'GV0' = Outlet1 state
            'GV1' = OnDelay
            'GV2' = OffDelay
            'GV4' = outletNbr
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 44}, 
            {'driver': 'GV2', 'value': 0, 'uom': 44}, 
            {'driver': 'GV4', 'value': 0, 'uom': 25},           
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]

    
    def  __init__(self, polyglot, primary, address, name, yolink,  port ):
        super().__init__( polyglot, primary, address, name )
        self.yolink = yolink
        self.port = port

        logging.debug('udiYoSubOutlet - init')
        logging.debug('self.address : ' + str(self.address))
        logging.debug('self.name :' + str(self.name))          
        
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)

        self.poly.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)
        self.node.setDriver('GV4', self.port, True, True)
        

    def start (self):
        logging.debug('udiYoSubOutlet - start')
      
    def stop (self):
        logging.debug('udiYoSubOutlet - stop')
        self.node.setDriver('ST', 0, True, True)

    def updateOutNode(self, outeletstate, onDelay, offDelay):
        logging.debug('udiYoSubOutlet - updateOutNode: {} {} {}'.format(outeletstate, onDelay, offDelay))
        self.node.setDriver('GV0', outeletstate, True, True)
        self.node.setDriver('GV1', onDelay, True, False)
        self.node.setDriver('GV2', offDelay, True, False)
        self.node.setDriver('GV4', self.port, False, False)
      

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
            'GV0' = usb state
            ]
    ''' 
    drivers = [
            {'driver': 'GV0', 'value': 99, 'uom': 25},    
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]

    def  __init__(self, polyglot, primary, address, name,  yolink):
        super().__init__( polyglot, primary, address, name)   
        self.yolink = yolink
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


    def updateUsbNode(self, gv0):
        logging.debug('udiYoSubUSB - updateUsbNode: {}'.format(gv0))
        self.node.setDriver('GV0', gv0, True, True)

    def usbControl(self, command):
        logging.info('switchControl')

        state = int(command.get('value'))     
        if state == 1:
            self.yolink.setMultiOutletstate(self.port,'ON' )
        else:
            self.yolink.setMultiOutletstate(self.port,'OFF' )
        self.node.setDriver('GV0', state, True, True)


    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yolink.getMultiOutletstate()

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
        self.yoMultiOutlet = None
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

        

        #self.switchstate = self.yoMultiOutlet.getstate()
        #self.switchPower = self.yoMultiOutlet.getEnergy()
        #udi_interface.__init__(self, polyglot, primary, address, name)

    def start(self):
        self.subNodesReady = False
        self.usbExists = True
        logging.debug('start - udiYoMultiOutlet')
        self.yoMultiOutlet  = YoLinkMultiOut(self.csName, self.csid, self.csseckey, self.devInfo, self.updateStatus)
        self.yoMultiOutlet.initNode()
        time.sleep(2)
        logging.debug('multiOutlet past initNode')
        self.nbrOutlets = self.yoMultiOutlet.getNbrPorts()
        #states = self.yoMultiOutlet.getMultiOutletstate()
        delays = self.yoMultiOutlet.getDelays()
        logging.debug('init data {}, {}'.format(self.nbrOutlets, delays))
        self.suboutlet = {}
        self.subnodeAdr = {}
        if self.yoMultiOutlet.online:
            self.node.setDriver('GV8', 1, True, True)
            for port in range(0,self.nbrOutlets):
                try:
                    self.subnodeAdr[port] = self.address+'s'+str(port+1)
                    self.suboutlet[port] = udiYoSubOutlet(self.poly, self.address, self.subnodeAdr[port], 'SubOutlet-'+str(port+1),self.yoMultiOutlet, port)
                    self.poly.addNode(self.suboutlet[port])
                    self.wait_for_node_done()
                                       
                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subnodeAdr[port], e))
            if self.nbrOutlets == 4: #controllable USB included
                try:
                    self.subnodeAdr[4] = self.address+'u'+str(5)
                    self.usbOut = udiYoSubUSB(self.poly, self.address,self.subnodeAdr[4] , 'USB Ports',self.yoMultiOutlet)
                    self.poly.addNode(self.usbOut)
                    self.wait_for_node_done()
                    self.usbExists = True
                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subnodeAdr[port], e))
            self.node.setDriver('ST', 1, True, True)
            self.subNodesReady = True
            self.createdNodes = self.poly.getNodes()
            logging.info('udiYoMultiOutlet - finished creating sub nodes')
            #logging.debug(self.subnodeAdr)
            logging.debug(self.createdNodes)
        else:
            logging.info('MultiOulet is not online')
   
        self.yoMultiOutlet.refreshMultiOutlet()
        logging.debug('Finished  MultiOutlet start')


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
        self.yoMultiOutlet.setMultiOutletState(portList, data)


    def usbUpdates(self,  data):
        logging.info('usbUpdates not implemented')
        portList = []
        portList.append(4) #USB is port 4 (5th port)
        self.yoMultiOutlet.setMultiOutletState(portList, data)



    def stop (self):
        logging.info('Stop not implemented')
        self.node.setDriver('ST', 0, True, True)
        self.yoMultiOutlet.shut_down()


    def updateStatus(self, data):
        #outletNbr = [0:'port1', 1:'port2', 'port3':2, 'port4':3]
        logging.debug('updateStatus - udiYoMultiOutlet')
        self.yoMultiOutlet.updateCallbackStatus(data)

        logging.debug('updateCallbackStatus - udiYoMultiOutlet')
        logging.debug(data)
        self.nbrOutlets = self.yoMultiOutlet.getNbrPorts()
        logging.debug('nbr ports{} , online {}'.format(self.nbrOutlets, self.yoMultiOutlet.online ))
        logging.debug('udiYoMultiOutlet - nbrOutlets: {}'.format(self.nbrOutlets))
        self.delaysActive = False
        outletstates =  self.yoMultiOutlet.getMultiOutletStates()
        logging.debug('outlet states: {}'.format (outletstates))
        logging.debug(outletstates)
        if self.subNodesReady:
            for port in range(0,self.nbrOutlets):
                if  self.yoMultiOutlet.online:
                    portName = 'port'+str(port)

                    #portnbr = outletstates[portName]['delays']['ch']

                    if outletstates[portName]['state'] == 'open':
                        state = 1
                    elif outletstates[portName]['state'] == 'closed':
                        state = 0
                    else:
                        state = 99
                    onDelay = outletstates[portName]['delays']['on']
                    offDelay = outletstates[portName]['delays']['off']
                else:
                    state = 99
                    onDelay = 0
                    offDelay = 0
                #nodeAdr = self.subnodeAdr[port]
                if onDelay != 0 or offDelay != 0:
                    self.delaysActive = True
                #for node in self.createdNodes:
                #    logging.debug('Subnode Address: {} {}'.format(nodeAdr, self.createdNodes[node].address))
                #    if self.createdNodes[node].address == nodeAdr:
                if self.yoMultiOutlet.online:
                    logging.debug('Updating subnode : {} {}'.format(port, state))
                    self.suboutlet[port].updateOutNode(state, onDelay,offDelay )
            if self.usbExists:
                logging.debug('Updating USB ')
                portName = 'port4'
                usbState =  self.yoMultiOutlet.getMultiOutletPortState(4)
                #nodeAdr = self.subnodeAdr[4]
                if  self.yoMultiOutlet.online:
                    if usbState == 'open':
                        state = 1
                    elif usbState == 'closed':
                        state = 0
                    else:
                        state = 99

                else:
                    state = 99
                #for node in self.createdNodes:
                #    logging.debug('search node name - {}'.format(self.createdNodes[node].address))
                #    if self.createdNodes[node].address == nodeAdr:
                self.usbOut.updateUsbNode(state)


    # Need to use shortPoll
    def pollDelays(self):
        if self.delaysActive and self.yoMultiOutlet.online: 
            delays =  self.yoMultiOutlet.getDelays()
            logging.debug('delays: ' + str(delays))
            delayActive = False
            #outletstates =  self.yoMultiOutlet.getMultiOutletData()
            for port in range(0,self.nbrOutlets):
                portName = 'port'+str(port)
                port = delays[portName]['delays']['ch']
                state = delays[portName]['state']
                onDelay = delays[portName]['delays']['on']
                offDelay = delays[portName]['delays']['off']

                nodeAdr = self.subnodeAdr[port]
                if onDelay != 0 or offDelay != 0:
                    self.delaysActive = True
                self.suboutlet[port].updateOutNode(state, onDelay,offDelay )
            self.delaysActive = delayActive
        
        
    def poll(self, polltype):
        logging.debug('ISY poll ')
        logging.debug(polltype)
        if 'longPoll' in polltype:
            self.yoMultiOutlet.refreshMultiOutlet()
            #self.yoMultiOutlet.refreshSchedules()
        if 'shortPoll' in polltype:
            self.pollDelays()
            #update Delays calculated



    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yoMultiOutlet.refreshMultiOutlet()
        #self.yoMultiOutlet.refreshSchedules()     


    commands = {
                'UPDATE': update                        

                }




