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
from yolinkMultiOutletV2 import YoLinkMultiOut

polyglot = None
Parameters = None
n_queue = []
count = 0

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
            {'driver': 'GV1', 'value': 0, 'uom': 57}, 
            {'driver': 'GV2', 'value': 0, 'uom': 57}, 
            {'driver': 'GV4', 'value': 0, 'uom': 25},           
            {'driver': 'ST', 'value': 0, 'uom': 25},
            ]

    
    def  __init__(self, polyglot, primary, address, name, port, yolink):
        super().__init__( polyglot, primary, address, name )
        self.yolink = yolink
        self.port = int(port )
        logging.debug('udiYoSubOutlet - init - port {}'.format(self.port))
        self.yolink.delayTimerCallback (self.updateDelayCountdown, 5)
    
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)

        self.poly.ready()
        self.poly.addNode(self)
        self.node = polyglot.getNode(address)
        self.node.setDriver('ST', 1, True, True)
        self.node.setDriver('GV4', self.port, True, True)
        

    def start (self):
        logging.debug('udiYoSubOutlet - start')
        try:
            state = self.yolink.getMultiOutPortState(str(self.port))
            if state.upper() == 'ON' or  state.upper() == 'OPEN':
                self.node.setDriver('GV0', 1, True, True) 
                self.portState = 1
            else:
                self.node.setDriver('GV0', 0, True, True) 
                self.portState = 0
        except Exception as e:
            logging.debug('Exception: {}'.format(e))


    def stop (self):
        logging.debug('udiYoSubOutlet - stop')
        self.node.setDriver('ST', 0, True, True)
       

    def updateOutNode(self, outeletstate, onDelay, offDelay):
        logging.debug('udiYoSubOutlet - updateOutNode: {} {} {}'.format(outeletstate, onDelay, offDelay))
        self.node.setDriver('GV0', outeletstate, True, True)
        self.node.setDriver('GV1', onDelay, True, False)
        self.node.setDriver('GV2', offDelay, True, False)
        #self.node.setDriver('GV4', self.port, False, False)
      
    def updateDelayCountdown(self, timeRemaining):
        logging.debug('updateDelayCountDown: port {} delays {}'.format(self.port, timeRemaining))
        ch = self.port 
        for delayInfo in range(0, len(timeRemaining)):
            if 'ch' in timeRemaining[delayInfo]:
                if timeRemaining[delayInfo]['ch'] == ch:
                    if 'on' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV1', timeRemaining[delayInfo]['on'], True, False)
                    if 'off' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV2', timeRemaining[delayInfo]['off'], True, False)
        

    def switchControl(self, command):
        logging.info('switchControl')
        state = int(command.get('value'))  
        logging.debug('switchControl pot: {}, state: {}'.format(self.port, state))   
        if state == 1:
            self.yolink.setMultiOutState(self.port, 'ON')

        else:
            self.yolink.setMultiOutState(self.port, 'OFF')
        self.node.setDriver('GV0', state, True, True)

        
    def setOnDelay(self, command ):
        logging.info('setOnDelay')
        self.onDelay =int(command.get('value'))
        self.yolink.setMultiOutDelayList([{'ch':self.port, 'on':self.onDelay}]  )
        self.node.setDriver('GV1', self.onDelay * 60, True, True)

        

    def setOffDelay(self, command):
        logging.info('setOnDelay Executed')
        self.offDelay =int(command.get('value'))
        self.yolink.setMultiOutDelayList([{'ch':self.port, 'off':self.offDelay }]  )
        self.node.setDriver('GV2', self.offDelay * 60 , True, True)


    def update(self, command = None):
        logging.info('Update Status Executed')

    commands = {
                'SWCTRL': switchControl, 
                'ONDELAY' : setOnDelay,
                'OFFDELAY' : setOffDelay,
                'UPDATE' : update
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

    def  __init__(self, polyglot, primary, address, name, usbPort, yolink):
        super().__init__( polyglot, primary, address, name)   
        self.yolink = yolink
        self.usbPort = usbPort
        #self.port = port
        logging.debug('udiYoSubUSB - init - port {}'.format(self.usbPort))
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
            self.yolink.setUsbState(self.usbPort, 'ON')
        else:
            self.yolink.setUsbState(self.usbPort, 'OFF')
        self.node.setDriver('GV0', state, True, True)



    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yolink.getMultiOutStates()

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
            {'driver': 'ST', 'value': 0, 'uom': 25}
            ]
    

    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        #  
        logging.debug('MultiOutlet Node INIT')
 
        self.nodeName = address
        self.yoAccess = yoAccess
        self.delaysActive = False


        self.devInfo =  deviceInfo   
        self.yoMultiOutlet = None
        self.n_queue = []

        #self.Parameters = Custom(polyglot, 'customparams')
        # subscribe to the events we want
        #polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        #polyglot.subscribe(polyglot.POLL, self.poll)
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
        self.yoMultiOutlet  = YoLinkMultiOut(self.yoAccess, self.devInfo, self.updateStatus)
        self.yoMultiOutlet.initNode()
        if self.yoMultiOutlet.online:
            time.sleep(2)
            logging.debug('multiOutlet past initNode')
            self.ports = self.yoMultiOutlet.getMultiOutStates()
            self.nbrOutlets = self.yoMultiOutlet.nbrOutlets
            self.nbrUsb = self.yoMultiOutlet.nbrUsb
            #states = self.yoMultiOutlet.getMultiOutletstate()
            delays = self.yoMultiOutlet.refreshDelays()
            logging.debug('init data {}, {}'.format(self.nbrOutlets, delays))
            self.subOutlet = {}
            self.subUsb = {}
            self.subOutletAdr ={}
            self.subUsbAdr = {}
            self.node.setDriver('GV8', 1, True, True)
            for port in range(0,self.yoMultiOutlet.nbrOutlets):
                try:
                    logging.debug('Adding sub outlet : {}'.format(port))
                    self.subOutletAdr[port] = self.address+'s'+str(port)
                    self.subOutlet[port] = udiYoSubOutlet(self.poly, self.address, self.subOutletAdr[port], 'SubOutlet-'+str(port+1),port,self.yoMultiOutlet)
                    self.poly.addNode(self.subOutlet[port])
                    self.wait_for_node_done()
                                    
                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subOutletAdr[port], e))
            for usb in range(0, self.yoMultiOutlet.nbrUsb):
                        
                try:
                    self.subUsbAdr[usb] = self.address+'u'+str(usb)
                    self.subUsb[usb] = udiYoSubUSB(self.poly, self.address,self.subUsbAdr[usb] , 'USB Port-'+str(usb),usb, self.yoMultiOutlet)
                    self.poly.addNode(self.subUsb[usb])
                    self.wait_for_node_done()
                    self.usbExists = True
                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subUsbAdr[usb], e))
            self.node.setDriver('ST', 1, True, True)
            self.subNodesReady = True
            self.createdNodes = self.poly.getNodes()
            logging.info('udiYoMultiOutlet - finished creating sub nodes')
            #logging.debug(self.subnodeAdr)
            logging.debug(self.createdNodes)
    
            self.yoMultiOutlet.refreshMultiOutlet()
            logging.debug('Finished  MultiOutlet start')
        else:
            logging.info('MultiOulet is not online')
            self.ports = 0
            self.nbrOutlets = 0
            self.node.setDriver('ST', 0, True, True)


    '''
    def controlUsb(self, controlCmd):
        logging.debug('controlDevice')
    '''

    '''
    def controlOutlet(self, port, controlCmd):
        logging.debug('controlOutlet')
        if 'switch' in controlCmd:
            self.subOutletUpdates(port, controlCmd['switch'])
        elif 'delayOn' in controlCmd:
            logging.debug('setting On delay')
        elif 'delayOff' in controlCmd:
            logging.debug('setting Off delay')
        else:
            logging.error ('Unknown command')
    '''

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    '''
    def subOutletUpdates(self, port, state):
        logging.info('subOutletUpdates')
        
        portList = []
        portList.append(port+self.nbrUsb)
        self.yoMultiOutlet.setMultiOutPortState(portList, state)


    def usbUpdates(self, port, state):
        logging.info('usbUpdates not implemented')
        portList = []
        portList.append(port) 
        self.yoMultiOutlet.setMultiOutUsbState(portList, state)

    '''

    def stop (self):
        logging.info('Stop udiYoMultiOutlet ')
        self.node.setDriver('ST', 0, True, True)
        self.yoMultiOutlet.shut_down()


    def updateStatus(self, data):
        

        logging.debug('updateStatus - udiYoMultiOutlet')
        
        self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)

        if self.yoMultiOutlet.online:
            self.yoMultiOutlet.updateCallbackStatus(data)

            logging.debug('updateCallbackStatus - udiYoMultiOutlet')
            logging.debug(data)
            self.nbrOutlets = self.yoMultiOutlet.nbrOutlets
            logging.debug('nbr ports {} , online {}'.format(self.nbrOutlets, self.yoMultiOutlet.online ))
            logging.debug('udiYoMultiOutlet - nbrOutlets: {}'.format(self.nbrOutlets))
            self.delaysActive = False
            outletStates =  self.yoMultiOutlet.getMultiOutStates()
            logging.debug('outlet states: {}'.format (outletStates))
            logging.debug(outletStates)
            if self.subNodesReady and self.yoMultiOutlet.online:
                for outlet in range(0,self.yoMultiOutlet.nbrOutlets):
                    portName = 'port'+str(outlet)

                    if outletStates[portName]['state'] == 'open':
                        state = 1
                    elif outletStates[portName]['state'] == 'closed':
                        state = 0
                    else:
                        state = 99
                    if 'delays'in outletStates[portName]:
                        if 'on' in outletStates[portName]['delays']:
                            onDelay = outletStates[portName]['delays']['on']
                        else:
                            onDelay = 0
                        if 'off' in outletStates[portName]['delays']:
                            offDelay = outletStates[portName]['delays']['off']
                        else:
                            offDelay = 0
                    #else:
                    #    onDelay = 0
                    #    offDelay = 0
                    logging.debug('Updating subnode : {} {}'.format(portName, state))
                    self.subOutlet[outlet].updateOutNode(state, onDelay, offDelay)
                for usb in range(0,self.yoMultiOutlet.nbrUsb):       
                    logging.debug('Updating USB - {}'.format(usb))
                    usbName = 'usb'+str(usb)
                    if outletStates[usbName]['state'] == 'open':
                        state = 1
                    elif outletStates[usbName]['state'] == 'closed':
                        state = 0
                    else:
                        state = 99
                    self.subUsb[usb].updateUsbNode(state)
        else:
            logging.info( '{} - not on line'.format(self.nodeName))



    # Need to use shortPoll
    def pollDelays(self):
        if self.delaysActive and self.yoMultiOutlet.online: 
            delays =  self.yoMultiOutlet.refreshDelays()
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
                self.suboutlet[port].updateOutNode(state, onDelay, offDelay )
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




