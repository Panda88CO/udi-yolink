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
from yolinkMultiOutletV3 import YoLinkMultiOut
import re

#assigned_addresses
class udiYoSubOutlet(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key
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
        self.last_state = 99
        self.timer_cleared = True
        self.timer_update = 5
        self.timer_expires = 0
        self.address = address
        self.name = name
        self.node = None
        self.portState = 0
        logging.debug('udiYoSubOutlet - init - port {}'.format(self.port))
        self.n_queue = [] 
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.offDelay = 0
        self.onDelay = 0


        self.poly.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = polyglot.getNode(self.address)
        
        time.sleep(1)

        


    def start (self):
        logging.debug('udiYoSubOutlet - start')
        while 5 != len(self.drivers):
            logging.debug('Waiting for node {} to get created'.format(self.name))
            time.sleep(1)
        while self.node == None:
            logging.debug('Waiting for node {} to get created'.format(self.name))
            time.sleep(1)

        self.my_setDriver('ST', 1)
        self.my_setDriver('GV4', self.port)
        try:
            state = self.yolink.getMultiOutPortState(self.port)
            #self.my_setDriver('ST', 1) 
            if state.upper() == 'ON' or  state.upper() == 'OPEN':
                self.my_setDriver('GV0', 1) 
                self.portState = 1
            else:
                self.my_setDriver('GV0', 0) 
                self.portState = 0
        except Exception as e:
            logging.debug('Exception: {}'.format(e))
            self.my_setDriver('ST', 0) 

    def stop (self):
        logging.debug('udiYoSubOutlet - stop')
        self.my_setDriver('ST', 0)
       
    def checkOnline(self):
        pass

    def checkDataUpdate(self):
        pass

    def updateOutNode(self, outletstate, onDelay, offDelay):
        logging.debug('udiYoSubOutlet - updateOutNode: state={} onD={} offD={}'.format(outletstate, onDelay, offDelay))
        if outletstate == 1:
            self.portState = 1
            self.my_setDriver('GV0', 1)
            #if self.last_state != outletstate:
            #    self.node.reportCmd('DON')
            self.my_setDriver('ST', 1) 
        elif outletstate == 0:
            self.portState = 0
            self.my_setDriver('GV0', 0)
            #if self.last_state != outletstate:
            #    self.node.reportCmd('DOF')
            self.my_setDriver('ST', 1)        
        else:
            self.portState = 99
            self.my_setDriver('GV0', 99)
            #self.my_setDriver('ST', 0) 
        self.last_state = outletstate
        self.my_setDriver('GV1', onDelay)
        self.my_setDriver('GV2', offDelay)
        #logging.debug('Timer info : {} '. format(time.time() - self.timer_expires))
        if time.time() >= self.timer_expires - self.timer_update and self.timer_expires != 0:
            self.my_setDriver('GV1', 0)
            self.my_setDriver('GV2', 0)

    def updateLastTime(self):
        pass
      
    def updateDelayCountdown(self, timeRemaining):
        logging.debug('udiYoSubOutlet updateDelayCountDown: port: {} delays: {}'.format(self.port, timeRemaining))
        max_delay = 0
        for delayInfo in range(0, len(timeRemaining)):

            if 'ch' in timeRemaining[delayInfo]:
                if timeRemaining[delayInfo]['ch'] == self.port:
                    if 'on' in timeRemaining[delayInfo]:
                        self.my_setDriver('GV1', timeRemaining[delayInfo]['on'])
                        if max_delay < timeRemaining[delayInfo]['on']:
                            max_delay = timeRemaining[delayInfo]['on']
                    if 'off' in timeRemaining[delayInfo]:
                        self.my_setDriver('GV2', timeRemaining[delayInfo]['off'])
                        if max_delay < timeRemaining[delayInfo]['off']:
                            max_delay = timeRemaining[delayInfo]['off']
        self.timer_expires = time.time()+max_delay
   
   
    def set_port_on(self, command = None):
        logging.info('udiYoSubOutlet set_port_on')
        self.yolink.setMultiOutState(self.port, 'ON')
        self.my_setDriver('GV0',1 )
        #self.node.reportCmd('DON')
        self.portState = 1

    def set_port_off(self, command = None):
        logging.info('udiYoSubOutlet set_port_off')
        self.yolink.setMultiOutState(self.port, 'OFF')
        self.my_setDriver('GV0',0 )
        #self.node.reportCmd('DOF')
        self.portState = 0

    def switchControl(self, command):
        logging.info('udiYoSubOutlet switchControl')

        ctrl = int(command.get('value'))     
        if ctrl == 0:
            self.yolink.setMultiOutState(self.port, 'OFF')
            self.my_setDriver('GV0',0 )
            self.node.reportCmd('DOF')
            self.portState = 0        
        elif ctrl == 1:
            self.yolink.setMultiOutState(self.port, 'ON')
            self.my_setDriver('GV0',1 )
            self.node.reportCmd('DON')
            self.portState = 1

        elif ctrl == 2: #Toggle            
            if self.portState == 1 :
                self.yolink.setMultiOutState(self.port, 'OFF')
                self.my_setDriver('GV0',0 )
                self.node.reportCmd('DOF')
                self.portState = 0
            elif self.portState == 0:
                self.yolink.setMultiOutState(self.port, 'ON')
                self.my_setDriver('GV0',1 )
                self.node.reportCmd('DON')
                self.portState = 1
        
        #elif ctrl == 3: #Fast OFF
        #    self.yolink.setMultiOutState(self.port, 'OFF')
        #    self.my_setDriver('GV0',0 )
        #    self.node.reportCmd('DOF')
        #    self.portState = 0
        #                
        #elif ctrl == 4: # Fast ON
        #    self.yolink.setMultiOutState(self.port, 'ON')
        #    self.my_setDriver('GV0',1 )
        #    self.node.reportCmd('DFON')
        #    self.portState = 1
        
        elif ctrl == 5: # Delay sets delays
            logging.info('udiYoSubOutlet set Delays Executed: {} {}'.format(self.onDelay, self.offDelay))
            #self.yolink.setMultiOutDelay(self.port, self.onDelay, self.offDelay)
            self.my_setDriver('GV1', self.onDelay * 60)
            self.my_setDriver('GV2', self.offDelay * 60 )
            self.yolink.setMultiOutDelayList([{'ch':self.port, 'on':self.onDelay, 'off':self.offDelay}]) 

            #Unknown remains unknown

    def program_delays(self, command):
        logging.info('udiYoOutlet program_delays {}'.format(command))
        query = command.get("query")
        self.onDelay = int(query.get("ondelay.uom44"))
        self.offDelay = int(query.get("offdelay.uom44"))
        self.my_setDriver('GV1', self.onDelay * 60)
        self.my_setDriver('GV2', self.offDelay * 60 )
        self.yoMultiOutlet.setDelayList([{'on':self.onDelay, 'off':self.offDelay}]) 
    
        
    def prepOnDelay(self, command ):
        logging.info('udiYoSubOutlet setOnDelay Executed')
        self.onDelay =int(command.get('value'))
        logging.info('udiYoSubOutlet prepOnDelay Executed {}'.format( self.onDelay ))
        #self.yolink.setMultiOutDelayList([{'ch':self.port, 'on':self.onDelay}]  )
        #self.my_setDriver('GV1', self.onDelay * 60)


        

    def prepOffDelay(self, command):
        logging.info('udiYoSubOutlet setOffDelay Executed')
        self.offDelay =int(command.get('value'))
        logging.info('udiYoSubOutlet prepOffDelay Executed {}'.format( self.offDelay ))
        #self.yolink.setMultiOutDelayList([{'ch':self.port, 'off':self.offDelay }]  )
        #self.my_setDriver('GV2', self.offDelay * 60 )
  

    def update(self, command = None):
        logging.info('udiYoSubOutlet Update Executed')
        self.yolink.refreshDevice()

    commands = {
                'SWCTRL'   : switchControl, 
                #'ONDELAY'  : prepOnDelay,
                #'OFFDELAY' : prepOffDelay,
                'DELAY_CTRL'    : program_delays, 
                'UPDATE'   : update,
                'QUERY'    : update,
                'DON'      : set_port_on,
                'DOF'      : set_port_off,
                }


class udiYoSubUSB(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key
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
        self.last_state = 99
        self.address = address
        self.portState = -1
        self.name = name
        self.node = None
        #self.port = port
        logging.debug('udiYoSubUSB - init - port {}'.format(self.usbPort))
        self.n_queue = []
        polyglot.subscribe(polyglot.START, self.start, self.address)
        polyglot.subscribe(polyglot.STOP, self.stop)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
       

        # start processing events and create add our controller node
        self.poly.ready()
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = polyglot.getNode(self.address)
        #time.sleep(1)
        




    def start (self):
        logging.debug('udiYoSubUSB {} - start'.format(self.name))
        while 2 != len(self.drivers):
            logging.debug('Waiting for node {} to get created'.format(self.name))
            time.sleep(1)


        #self.my_setDriver('ST', 1)
        try:
            state = self.yolink.getMultiOutUsbState(self.usbPort)
            if state.upper() == 'ON' or  state.upper() == 'OPEN':
                self.my_setDriver('GV0', 1) 
                self.portState = 1
            else:
                self.my_setDriver('GV0', 0) 
                self.portState = 0

    
        except Exception as e:
            logging.debug('Exception: {}'.format(e))
            #self.my_setDriver('ST', 0)

    def stop (self):
        logging.info('udiYoSubUSB - stop')
        self.my_setDriver('ST', 0) 
    
    def checkOnline(self):
        pass

    def checkDataUpdate(self):
        pass

    def updateLastTime(self):
        pass

    def updateUsbNode(self, gv0):
        logging.info('udiYoSubUSB - updateUsbNode: {}'.format(gv0))
        self.my_setDriver('GV0', gv0)
        self.my_setDriver('ST', 1)
        #if self.last_state != gv0:
        #    if 1 == gv0:
        #        self.node.reportCmd('DON')
        #    elif 0 == gv0:
        #        self.node.reportCmd('DOF')
        self.my_setDriver('GV0', gv0)
        self.last_state = gv0
        self.portState = gv0
        

    def usbControl(self, command):
        logging.info('udiYoSubUSB - usbControl')

        ctrl = int(command.get('value'))     
        if ctrl == 1:
            self.yolink.setUsbState(self.usbPort, 'ON')
            self.my_setDriver('GV0', 1)
            self.node.reportCmd('DON')
            self.portState = 1
        elif ctrl == 0:
            self.yolink.setUsbState(self.usbPort, 'OFF')
            self.my_setDriver('GV0', 0)
            self.node.reportCmd('DOF')  
            self.portState = 0    
        elif ctrl == 2:
            if self.portState == 1:
                self.yolink.setUsbState(self.usbPort, 'OFF')
                self.my_setDriver('GV0', 0)
                self.node.reportCmd('DOF')  
                self.portState = 0
            elif self.portState == 0:
                self.yolink.setUsbState(self.usbPort, 'ON')
                self.my_setDriver('GV0', 1)
                self.node.reportCmd('DON')
                self.portState = 1

  
    def usb_on(self, command = None ):
        logging.info('udiYoSubUSB - usb_on')
        self.yolink.setUsbState(self.usbPort, 'ON')
        self.my_setDriver('GV0', 1)
        #self.node.reportCmd('DON')
        self.portState = 1

    def usb_off(self, command = None):
        logging.info('udiYoSubUSB - usb_off')
        self.yolink.setUsbState(self.usbPort, 'OFF')
        self.my_setDriver('GV0', 0)
        #self.node.reportCmd('DOF')  
        self.portState = 0    

    def update(self, command = None):
        logging.info('Update Status Executed')
        self.yolink.getMultiOutStates()

    commands = {
                 'USBCTRL': usbControl, 
                 'UPDATE' : update,
                 'QUERY'  : update, 
                 'DON'    : usb_on,
                 'DOF'    : usb_off,
                }

class udiYoMultiOutlet(udi_interface.Node):
    from  udiYolinkLib import my_setDriver, prep_schedule, activate_schedule, update_schedule_data, node_queue, wait_for_node_done, mask2key
    id = 'yomultiout'

    '''
       drivers = [
            'ST' = online
            ]
    ''' 
    drivers = [

            {'driver': 'GV12', 'value': 99, 'uom': 25}, #Output
            {'driver': 'GV13', 'value': 0, 'uom': 25}, #Schedule index/no
            {'driver': 'GV14', 'value': 99, 'uom': 25}, # Active
            {'driver': 'GV15', 'value': 99, 'uom': 25}, #start Hour
            {'driver': 'GV16', 'value': 99, 'uom': 25}, #start Min  
            {'driver': 'GV21', 'value': 99, 'uom': 25}, #start Min              
            {'driver': 'GV17', 'value': 99, 'uom': 25}, #stop Hour                                              
            {'driver': 'GV18', 'value': 99, 'uom': 25}, #stop Min
            {'driver': 'GV22', 'value': 99, 'uom': 25}, #start Min              
            {'driver': 'GV19', 'value': 0, 'uom': 25}, #days
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV20', 'value': 0, 'uom': 25},
             {'driver': 'TIME', 'value' :int(time.time()), 'uom': 151},            
            ]
    
    def  __init__(self, polyglot, primary, address, name, yoAccess, deviceInfo):
        super().__init__( polyglot, primary, address, name)   
        #super(YoLinkSW, self).__init__( csName, csid, csseckey, devInfo,  self.updateStatus, )
        
        logging.debug('MultiOutlet Node INIT')
 
        self.nodeName = address
        self.yoAccess = yoAccess
        self.delaysActive = False
        if 'YS6802' in deviceInfo['modelName']:
            self.nbrOutlets = 2
            self.nbrUsb = 0
        elif 'YS6801' in deviceInfo['modelName']:
            self.nbrOutlets = 4
            self.nbrUsb = 1
        else:
            logging.error('Unsupported device : {}'.format(deviceInfo['modelName']))
        self.ports =self.nbrOutlets + self.nbrUsb
        self.timer_update = 5
        self.devInfo =  deviceInfo
        self.yoMultiOutlet = None
        self.node_ready = False
        self.subUsb = []
        self.subOutlet = []
        self.schedule_setected = 0
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
        self.poly.addNode(self, conn_status = None, rename = True)
        self.wait_for_node_done()
        self.node = self.poly.getNode(address)
        self.adr_list = []
        self.adr_list.append(address)

        self.node_fully_config = False
        self.node_ready = True
        self.schedule_selected = 0

    def start(self):
        #self.node_fully_config = False
        #self.usbExists = True
        logging.debug('start - udiYoMultiOutlet: {}'.format(self.devInfo['name']))
        self.my_setDriver('ST', 0)
        self.yoMultiOutlet  = YoLinkMultiOut(self.yoAccess, self.devInfo, self.updateStatus)
        self.yoMultiOutlet.nbrOutlets = self.nbrOutlets
        self.yoMultiOutlet.nbrUsb = self.nbrUsb
        
        #self.my_setDriver('ST', 1)
        #time.sleep(1)
        #self.yoMultiOutlet.initNode()
        #time.sleep(3)
        #if not self.yoMultiOutlet.online:
        #    logging.warning('Device {} not on-line -  Cannot determine number of outlets and USBs'.format(self.devInfo['name']))
        #    self.ports = 0
        #    self.nbrOutlets = 0
        #    self.my_setDriver('ST', 0)
        #    #self.node_fully_config = False

        #logging.debug('before start {} {}'.format(self.yoMultiOutlet.nbrOutlets, self.node_fully_config ))
        if self.yoMultiOutlet.nbrOutlets == 0 and not self.yoMultiOutlet.online:
            logging.debug(' No config yet {} {}'.format(self.yoMultiOutlet.nbrOutlets, self.yoMultiOutlet.online))
            self.my_setDriver('GV20', 2)
        else:
            self.yoMultiOutlet.delayTimerCallback (self.updateDelayCountdown, self.timer_update)
            time.sleep(2)
            logging.debug('multiOutlet past initNode')
            #self.ports = self.yoMultiOutlet.getMultiOutStates()
            #self.nbrOutlets = self.yoMultiOutlet.nbrOutlets
            #self.nbrUsb = self.yoMultiOutlet.nbrUsb
            #states = self.yoMultiOutlet.getMultiOutletstate()
            delays = self.yoMultiOutlet.refreshDelays()
            logging.debug('init data: outlets: {}, USB {}, delays{}'.format(self.nbrOutlets, self.nbrUsb, delays))
            self.subOutlet = {}
            self.subUsb = {}
            self.subOutletAdr ={}
            self.subUsbAdr = {}
            self.outletName = 'outlet'
            self.usbName = 'usb'
            #self.my_setDriver('ST', 1)
            logging.debug('Checking/creating  Outlets  {}'.format(self.nbrOutlets))
            for port in range(0,self.nbrOutlets):
                try:
                    #logging.debug('Adding sub outlet : {}'.format(port))
                    self.subOutletAdr[port] =  self.address[3:14]+'_o' + str(port)
                    logging.debug('Adding Power outlet : {} {} {} {}'.format( self.address, self.subOutletAdr[port], 'Outlet-'+str(port+1), port))
                    self.subOutlet[port] = udiYoSubOutlet(self.poly, self.address, self.subOutletAdr[port], 'Outlet-'+str(port+1),port, self.yoMultiOutlet)
                    self.adr_list.append(self.subOutletAdr[port])
                    time.sleep(1) # ensure not too close calls for the different outlets
                                    
                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subOutletAdr[port], e))
            logging.debug('Checking/creating  USB  {}'.format(self.yoMultiOutlet.nbrUsb))
            for usb in range(0, self.nbrUsb): 
                try:
                    self.subUsbAdr[usb] = self.address[3:14]+'_u'+str(usb)
                    logging.debug('Adding USB outlet : {} {} {} {}'.format( self.address, self.subUsbAdr[usb] , 'USB-'+str(usb), usb))
                    self.subUsb[usb] = udiYoSubUSB(self.poly, self.address, self.subUsbAdr[usb] , 'USB-'+str(usb),usb, self.yoMultiOutlet)
                    self.adr_list.append(self.subUsbAdr[usb])  
                    time.sleep(1) # ensure not too close calls for the different usb ports (there is currently only 1)
                    self.usbExists = True

                except Exception as e:
                    logging.error('Failed to create {}: {}'.format(self.subUsbAdr[usb], e))
            
            self.node_fully_config = True
            logging.info('udiYoMultiOutlet - finished creating sub nodes - {} '.format(self.node_fully_config ))

            #logging.debug(self.subnodeAdr)
        time.sleep(1)
        self.yoMultiOutlet.initNode()
        time.sleep(3)
        self.yoMultiOutlet.refreshMultiOutlet()
        self.yoMultiOutlet.refreshSchedules()
        self.node_ready = True
        logging.debug('Finished  MultiOutlet start')





    def updateDelayCountdown(self, timeRemaining):
        logging.debug('updateDelayCountdown - time: {}'.format(timeRemaining))
        for outlet in range(0,self.nbrOutlets):
            self.subOutlet[outlet].updateDelayCountdown(timeRemaining)


    def stop (self):
        logging.info('Stop udiYoMultiOutlet ')
        self.my_setDriver('ST', 0)
        self.yoMultiOutlet.shut_down()

    def checkOnline(self):
        self.yoMultiOutlet.refreshDevice() 



    def checkDataUpdate(self):
        if self.yoMultiOutlet.data_updated():
            self.updateData()

    def updateData(self):
        outletStates =  self.yoMultiOutlet.getMultiOutStates()

        if self.node_fully_config:
            self.my_setDriver('ST',1)
            self.my_setDriver('TIME', self.yoMultiOutlet.getLastUpdateTime(), 151)

            for outlet in range(0,self.nbrOutlets):
                portName = 'port'+str(outlet)
                state = 99
                if self.yoMultiOutlet.online:   
                    if portName in outletStates:
                        if 'state' in outletStates[portName]:
                            if outletStates[portName]['state'] == 'open':
                                state = 1
                            elif outletStates[portName]['state'] == 'closed':
                                state = 0
                    else:
                        logging.error(f'PortName {portName} not in outletState  {outletStates}')
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
        else:

            self.my_setDriver('ST',0)
            self.my_setDriver('GV20', 2)

        if not self.yoMultiOutlet.online:
            logging.error( '{} - not on line'.format(self.nodeName))
            #self.my_setDriver('ST', 0)
            self.my_setDriver('GV20', 2)
        else:
            self.my_setDriver('ST', 1)
            if self.yoMultiOutlet.suspended:
                self.my_setDriver('GV20', 1)
            else:
                self.my_setDriver('GV20', 0)
            
        sch_info = self.yoMultiOutlet.getScheduleInfo(self.schedule_selected)
        self.update_schedule_data(sch_info, self.schedule_selected)
            




    def updateStatus(self, data):
        
        logging.debug('updateStatus - udiYoMultiOutlet: {}'.format(self.devInfo['name']))
        #self.yoMultiOutlet.online =  self.yoMultiOutlet.checkOnlineStatus(data)
        #if self.yoMultiOutlet.online:
        self.yoMultiOutlet.updateStatus(data)
        self.updateData()

        logging.debug( 'updateStatus data: {} {}'.format(self.node_fully_config, self.yoMultiOutlet.nbrOutlets ))
        if not self.node_fully_config: # Device was never initialized
            logging.debug('Node server not fully configured yet')
            self.node_ready = True
            #self.yoMultiOutlet.refreshDevice()
            time.sleep(10.1)
            self.start()
            time.sleep(3)




    def lookup_schedule(self, command):
        logging.info('udiYoMultiOutlet lookup_schedule {}'.format(command))
        self.schedule_selected = int(command.get('value'))
        self.yoMultiOutlet.refreshSchedules()

    def define_schedule(self, command):
        logging.info('udiYoSwitch define_schedule {}'.format(command))
        query = command.get("query")
        self.schedule_selected, params = self.prep_schedule(query)
        self.yoMultiOutlet.setSchedule(self.schedule_selected, params)


    def control_schedule(self, command):
        logging.info('udiYoSwitch control_schedule {}'.format(command))       
        query = command.get("query")
        self.activated, self.schedule_selected = self.activate_schedule(query)
        self.yoMultiOutlet.activateSchedule(self.schedule_selected, self.activated)
        

    def update(self, command = None):
        logging.info('udiYoMultiOutlet Update Executed')
        self.yoMultiOutlet.refreshMultiOutlet()
        #self.yoMultiOutlet.refreshSchedules()     


    commands = {
                'UPDATE'        : update,
                'QUERY'         : update,
                'LOOKUP_SCH'    : lookup_schedule,
                'DEFINE_SCH'    : define_schedule,
                'CTRL_SCH'      : control_schedule,
                }




