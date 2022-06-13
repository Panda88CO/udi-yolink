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
    logging.basicConfig(level=logging.INFO)

#import sys
import time
from yolinkMultiOutletV2 import YoLinkMultiOut
import re


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
        portStr = re.findall('[0-9]+', str(port))
        self.port  = int(portStr.pop())
        #self.port = int(port )
        logging.debug('udiYoSubOutlet - init - port {}'.format(self.port))
    
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []   


        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = polyglot.getNode(address)
        time.sleep(1)
        self.node.setDriver('ST', 1, True, True)
        self.node.setDriver('GV4', self.port, True, True)
        
    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()


    def start (self):
        logging.debug('udiYoSubOutlet - start')

        try:
            state = self.yolink.getMultiOutPortState(self.port)
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
       
    def checkOnline(self):
        pass


    def updateOutNode(self, outletstate, onDelay, offDelay):
        logging.debug('udiYoSubOutlet - updateOutNode: state={} onD={} offD={}'.format(outletstate, onDelay, offDelay))
        if outletstate == 1:
            self.node.setDriver('GV0', 1, True, True)
            self.node.reportCmd('DON')
        elif outletstate == 0:
            self.node.setDriver('GV0', 0, True, True)
            self.node.reportCmd('DOF')        
        else:
            self.node.setDriver('GV0', 99, True, True)

        self.node.setDriver('GV1', onDelay, True, False)
        self.node.setDriver('GV2', offDelay, True, False)

      
    def updateDelayCountdown(self, timeRemaining):
        logging.debug('udiYoSubOutlet updateDelayCountDown: port: {} delays: {}'.format(self.port, timeRemaining))
        #ch = self.port - 1 # 0 based vs 1 based 
        for delayInfo in range(0, len(timeRemaining)):

            if 'ch' in timeRemaining[delayInfo]:
                
                if timeRemaining[delayInfo]['ch'] == (self.port):
                    #logging.debug('debug port: {} timeRemain: {} '.format(self.port, timeRemaining[delayInfo] ))
                    if 'on' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV1', timeRemaining[delayInfo]['on'], True, True)
                    if 'off' in timeRemaining[delayInfo]:
                        self.node.setDriver('GV2', timeRemaining[delayInfo]['off'], True, True)
                #logging.debug('display update {}'.format(timeRemaining))

    def switchControl(self, command):
        logging.info('udiYoSubOutlet switchControl')
        state = int(command.get('value'))  
        #logging.debug('switchControl port: {}, state: {}'.format(self.port, state))   
        if state == 1:
            self.yolink.setMultiOutState(self.port, 'ON')

        else:
            self.yolink.setMultiOutState(self.port, 'OFF')
        self.node.setDriver('GV0', state, True, True)

        
    def setOnDelay(self, command ):
        logging.info('udiYoSubOutlet setOnDelay Executed')
        self.onDelay =int(command.get('value'))
        self.yolink.setMultiOutDelayList([{'ch':self.port, 'on':self.onDelay}]  )
        self.node.setDriver('GV1', self.onDelay * 60, True, True)


        

    def setOffDelay(self, command):
        logging.info('udiYoSubOutlet setOffDelay Executed')
        self.offDelay =int(command.get('value'))
        self.yolink.setMultiOutDelayList([{'ch':self.port, 'off':self.offDelay }]  )
        self.node.setDriver('GV2', self.offDelay * 60 , True, True)
  

    def update(self, command = None):
        logging.info('udiYoSubOutlet Update Executed')
        self.yolink.refreshDevice()

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
        
        portStr = re.findall('[0-9]+', str(usbPort))
        self.usbPort = int(portStr.pop())


        #self.port = port
        logging.debug('udiYoSubUSB - init - port {}'.format(self.usbPort))

        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.n_queue = []

        # start processing events and create add our controller node
        self.poly.ready()
        self.poly.addNode(self)
        self.wait_for_node_done()
        self.node = polyglot.getNode(address)
        time.sleep(1)
        self.node.setDriver('ST', 1, True, True)


    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()




    def start (self):
        logging.debug('udiYoSubUSB - start')
        try:
            state = self.yolink.getMultiOutUsbState(self.usbPort)
            if state.upper() == 'ON' or  state.upper() == 'OPEN':
                self.node.setDriver('GV0', 1, True, True) 
                self.portState = 1
            else:
                self.node.setDriver('GV0', 0, True, True) 
                self.portState = 0
    
        except Exception as e:
            logging.debug('Exception: {}'.format(e))

    def stop (self):
        logging.info('udiYoSubUSB - stop')
        self.node.setDriver('ST', 0, True, True) 
    
    def checkOnline(self):
        pass

    def updateUsbNode(self, gv0):
        logging.info('udiYoSubUSB - updateUsbNode: {}'.format(gv0))
        self.node.setDriver('GV0', gv0, True, True)

    def usbControl(self, command):
        logging.info('udiYoSubUSB - usbControl')

        state = int(command.get('value'))     
        if state == 1:
            self.yolink.setUsbState(self.usbPort, 'ON')
            self.node.setDriver('GV0', 1, True, True)
            self.node.reportCmd('DON')
        elif state == 0:
            self.yolink.setUsbState(self.usbPort, 'OFF')
            self.node.setDriver('GV0', 0, True, True)
            self.node.reportCmd('DOF')      
        else:
            self.node.setDriver('GV0', 99, True, True)
  



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
        self.nbrOutlets = -1
        self.nbrUsb = -1
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
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def start(self):
        self.subNodesReady = False
        self.usbExists = True
        logging.debug('start - udiYoMultiOutlet: {}'.format(self.devInfo['name']))
        self.yoMultiOutlet  = YoLinkMultiOut(self.yoAccess, self.devInfo, self.updateStatus)
        time.sleep(1)
        self.yoMultiOutlet.initNode()

        if not self.yoMultiOutlet.online:
            logging.warning('Device {} not on-line -  Cannot determine number of outlets and USBs'.format(self.devInfo['name']))
            self.ports = 0
            self.nbrOutlets = 0

        else:
            self.node.setDriver('ST', 1, True, True)
            self.yoMultiOutlet.delayTimerCallback (self.updateDelayCountdown, 5)
            time.sleep(2)
            logging.debug('multiOutlet past initNode')
            self.ports = self.yoMultiOutlet.getMultiOutStates()
            self.nbrOutlets = self.yoMultiOutlet.nbrOutlets
            self.nbrUsb = self.yoMultiOutlet.nbrUsb
            #states = self.yoMultiOutlet.getMultiOutletstate()
            delays = self.yoMultiOutlet.refreshDelays()
            logging.debug('init data: outlets: {}, USB {}, delays{}'.format(self.nbrOutlets, self.nbrUsb, delays))
            self.subOutlet = {}
            self.subUsb = {}
            self.subOutletAdr ={}
            self.subUsbAdr = {}
            self.outletName = 'outlet'
            self.usbName = 'usb'
            self.node.setDriver('GV8', 1, True, True)
            for port in range(0,self.yoMultiOutlet.nbrOutlets):
                try:
                    #logging.debug('Adding sub outlet : {}'.format(port))
                    self.subOutletAdr[port] =  self.address[0:11]+'_o' + str(port)
                    logging.debug('Adding outlet : {} {} {} {}'.format( self.address, self.subOutletAdr[port], 'Outlet-'+str(port+1), port))
                    self.subOutlet[port] = udiYoSubOutlet(self.poly, self.address, self.subOutletAdr[port], 'Outlet-'+str(port+1),port, self.yoMultiOutlet)
                    self.poly.addNode(self.subOutlet[port])
                    self.wait_for_node_done()
                                    
                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subOutletAdr[port], e))
            for usb in range(0, self.yoMultiOutlet.nbrUsb):
                        
                try:
                    self.subUsbAdr[usb] = self.address[0:11]+'_u'+str(usb)
                    logging.debug('Adding outlet : {} {} {} {}'.format( self.address, self.subUsbAdr[usb] , 'USB-'+str(usb), usb))
                    self.subUsb[usb] = udiYoSubUSB(self.poly, self.address, self.subUsbAdr[usb] , 'USB-'+str(usb),usb, self.yoMultiOutlet)
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
            #logging.debug(self.createdNodes)
    
            self.yoMultiOutlet.refreshMultiOutlet()
            #logging.debug('Finished  MultiOutlet start')



    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def updateDelayCountdown(self, timeRemaining):
        logging.debug('updateDelayCountdown - time: {}'.format(timeRemaining))
        for outlet in range(0,self.nbrOutlets):
            self.subOutlet[outlet].updateDelayCountdown(timeRemaining)


    def stop (self):
        logging.info('Stop udiYoMultiOutlet ')
        self.node.setDriver('ST', 0, True, True)
        self.yoMultiOutlet.shut_down()
        if self.node:
            self.poly.delNode(self.node.address)

    def checkOnline(self):
        self.yoMultiOutlet.refreshDevice() 

    def updateStatus(self, data):
        
        logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.devInfo['name']))
        
        self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)

        if self.yoMultiOutlet.online:
            if self.ports == 0: # Device was never initialized
                self.start()
            self.yoMultiOutlet.updateCallbackStatus(data)
            #logging.debug('updateCallbackStatus - udiYoMultiOutlet')
            #logging.debug(data)
            #logging.debug('nbr ports {} , online {}'.format(self.nbrOutlets, self.yoMultiOutlet.online ))
            #logging.debug('udiYoMultiOutlet - nbrOutlets: {}'.format(self.nbrOutlets))
            self.delaysActive = False
            outletStates =  self.yoMultiOutlet.getMultiOutStates()

            if self.subNodesReady:
                for outlet in range(0,self.nbrOutlets):
                    portName = 'port'+str(outlet)
                    if self.yoMultiOutlet.online:
                        if outletStates[portName]['state'] == 'open':
                            state = 1
                        elif outletStates[portName]['state'] == 'closed':
                            state = 0
                    else:
                        state = 99
                    if 'delays'in outletStates[portName] and self.yoMultiOutlet.online:
                        if 'on' in outletStates[portName]['delays']:
                            onDelay = outletStates[portName]['delays']['on']*60
                        else:
                            onDelay = 0
                        if 'off' in outletStates[portName]['delays']:
                            offDelay = outletStates[portName]['delays']['off']*60
                        else:
                            offDelay = 0
                    else:
                        onDelay = 0
                        offDelay = 0
                    logging.debug('Updating subnode {}: {} {} {}'.format(outlet, state, onDelay, offDelay))
                    self.subOutlet[outlet].updateOutNode(state, onDelay, offDelay)
                for usb in range(0,self.nbrUsb):       
                    usbName = 'usb'+str(usb)
                    if self.yoMultiOutlet.online:
                        if outletStates[usbName]['state'] == 'open':
                            state = 1
                        elif outletStates[usbName]['state'] == 'closed':
                            state = 0
                    else:
                        state = 99
                    self.subUsb[usb].updateUsbNode(state)
            if not self.yoMultiOutlet.online:
                logging.error( '{} - not on line'.format(self.nodeName))
  





    def update(self, command = None):
        logging.info('udiYoMultiOutlet Update Executed')
        self.yoMultiOutlet.refreshMultiOutlet()
        #self.yoMultiOutlet.refreshSchedules()     


    commands = {
                'UPDATE': update                        

                }




