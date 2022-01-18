import json
import time
import re

from yolink_mqtt_classV2 import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class YoLinkMultiOut(YoLinkMQTTDevice):
    def __init__(yolink, yoAccess,  deviceInfo, callback):
        super().__init__(  yoAccess, deviceInfo, callback)
        yolink.maxSchedules = 6
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdates'   ]
        yolink.eventList = ['StatusChange', 'Report']
        yolink.type = 'MultiOutlet'
        yolink.MultiOutletName = 'MultiOutletEvent'
        yolink.eventTime = 'Time'
        time.sleep(2)


    def initNode(yolink):
        logging.debug('MultiOutlet initNode')
        yolink.initDevice()
       
        time.sleep(2)
        
       
        #temp = yolink.getInfoAPI()
        #yolink.refreshMultiOutlet() # needed to get number of ports on device
        #yolink.refreshDevice()
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            logging.info('MultiOutlet init - Nbr Outlets : {}'.format(yolink.nbrOutlets))
            logging.info('MultiOutlet init - Nbr USB : {}'.format(yolink.nbrUsb))
            
    
           
        else:
            logging.info ('MultiOutlet not online')
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()

    '''
    def getSchedules (yolink):
        return(yolink.dataAPI['data']['schedules'])  

    def getDelays (yolink):
        return(yolink.dataAPI['data']['delays'])  
    '''

                                

    def refreshMultiOutlet(yolink):
        return(yolink.refreshDevice())
    
    def setMultiOutUsbState(yolink, portList, value ):
        logging.debug( yolink.type+'- setMultiOutletState')
        # portlist a a listof ports being changed port range 0-7
        # value is state that need to change 2 (ON/OFF)
        status = True
        port = 0
        for i in portList:
            portStr = re.findall('[0-9]+', i)
            portNbr = int(portStr.pop())
            if portNbr < yolink.nbrUsb and portNbr >= 0 :
                port = port + pow(2, portNbr)
            else:
                logging.error('wrong port number (range 0- '+str(yolink.nbrPorts)+'): ' + str(i))
                return(False)
        if value.upper() == 'ON' or value.upper() == 'OPEN':
            state = 'open'
        elif value.upper() == 'OFF' or value.upper() == 'CLOSED' :
            state = 'closed'
        else:
            logging.error('Unknows state passed')
            status = False
        if status:
            data={}
            data["params"] = {}
            data["params"]["chs"] =  port
            data["params"]['state'] = state
            yolink.setDevice(  data)
        return(status)
    

    def usbSetState (yolink, port, state):
        logging.info('usbSetState')
        if yolink.online:
            if yolink.nbrUsb > 0:
                portList = []
                portList.append(port+yolink.nbrUsb)
                yolink.setMultiOutPortState(portList, state)
            else:
                logging.error('No USB port on device')
        else:
            logging.error('Device not online') 


    def outletSetState ( yolink, port, state):
        logging.info('outletSetState')
        if yolink.online:
            portList = []
            portList.append(int(port)+yolink.nbrUsb)
            yolink.setMultiOutPortState(portList, state)
        else:
            logging.error('Device not online') 

    def outletSetDelayList (yolink, delayList):
        logging.info('outletSetDelayList')
        data = {}
        data['params'] = {}
        data['params']['delays'] = []
        if yolink.online:
            data = {}
            data['params'] = {}
            data['params']['delays'] = []
            for delays in range(0,len(delayList)):
                for key in delayList[delays]:
                    onDelay = 0
                    offDelay = 0      
                    if key.lower() == 'ch' or key.lower() == 'port':
                        ch = int(delayList[delays][key]) + yolink.nbrUsb 
                    if key.lower() == 'on' or key.lower() == 'onDelay':
                        onDelay = int(delayList[delays][key])
                    if key.lower() == 'off' or key.lower() == 'offDelay':
                        offDelay = int(delayList[delays][key])
                data['params']['delays'].append( {'ch':ch, 'on':onDelay, 'off':offDelay } )
            logging.debug('Sending delay data: {}'.format( data['params']['delays']))
            data['time'] = str(int(time.time())*1000)
            data['method'] = yolink.type+'.setDelay'
            data["targetDevice"] =  yolink.deviceInfo['deviceId']
            data["token"]= yolink.deviceInfo['token'] 
            yolink.yolinkMQTTclient.publish_data( data)
            yolink.online = yolink.dataAPI[yolink.dOnline]
        else:
            logging.error('Device not online') 

    def outletSetDelay (yolink, port, onDelay=0, offDelay=0):
        logging.info('outletSetDelay')
        if yolink.online:
            data = {}
            data['params'] = {}
            data['params']['delays'] = []
            portStr = re.findall('[0-9]+', port)
            portNbr = int(portStr.pop())
            delaySpec = {'ch':portNbr+yolink.nbrUsb, 'on':onDelay, 'off':offDelay}       
            logging.debug('Sending delay data: {}'.format(delaySpec))
            data['params']['delays'].append(delaySpec)
            data['time'] = str(int(time.time())*1000)
            data['method'] = yolink.type+'.setDelay'
            data["targetDevice"] =  yolink.deviceInfo['deviceId']
            data["token"]= yolink.deviceInfo['token'] 
            yolink.yolinkMQTTclient.publish_data( data)
            yolink.online = yolink.dataAPI[yolink.dOnline]
        else:
            logging.error('Device not online') 

    def setMultiOutPortState(yolink, portList, value ):
        logging.debug( yolink.type+'- setMultiOutletState')
        # portlist a a listof ports being changed port range 0-7
        # value is state that need to change 2 (ON/OFF)
        status = True
        port = 0
        for i in portList:            
            portStr = re.findall('[0-9]+', i)
            portNbr = int(portStr.pop())
            portNbr = portNbr + yolink.nbrUsb  # Ports start after USB control ports
            if portNbr <= yolink.nbrPorts and portNbr >= 0 :
                port = port + pow(2, portNbr)
            else:
                logging.error('wrong port number (range 0 - '+str(yolink.nbrPorts)+'): ' + str(i))
                return(False)
        if value.upper() == 'ON' or value.upper() == 'OPEN':
            state = 'open'
        elif value.upper() == 'OFF' or value.upper() == 'CLOSED' :
            state = 'closed'
        else:
            logging.error('Unknows state passed')
            status = False
        if status:
            data={}
            data["params"] = {}
            data["params"]["chs"] =  port
            data["params"]['state'] = state
            yolink.setDevice( data)
        return(status)
    
    def getMultiOutStates(yolink):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        states= {}
        temp = yolink.getInfoAPI()
        logging.debug(temp)
        if yolink.online:
            for usb in range (0,yolink.nbrUsb):
                    states['usb'+str(usb)]= {'state':temp['data']['state'][usb]}
            if temp['data']['delays'] != None:
                for outlet in temp['data']['delays']:
                    port = outlet['ch']-yolink.nbrUsb
                    states['port'+str(port)]= {'state':temp['data']['state'][port], 'delays':outlet}
            #print(states)
            else:
                portNbr = 0
                for port in range(yolink.nbrUsb,yolink.nbrOutlets):
                    states['port'+str(portNbr)]= {'state':temp['data']['state'][port]}
                    portNbr = portNbr + 1

        return(states)


    def getMultiOutPortState(yolink, portStr):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        tmpStr = re.findall('[0-9]+', portStr)
        port = int(tmpStr.pop())
        port = port + yolink.nbrUsb
        temp = yolink.getInfoAPI()
        temp = temp['data'] # Need to look at include USB in API
        #logging.debug('getMultiOutletPortState  {} {} {}'.format(port,temp['state'], temp ))
        if yolink.online and port < len(temp['state'])-yolink.nbrUsb:
            return(temp['state'][port])
        else:
            return('unknown')
        
    def getMultiOutUsbState(yolink, usbStr):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        tmpStr = re.findall('[0-9]+', usbStr)
        usb = int(tmpStr.pop())
        temp = yolink.getInfoAPI()
        temp = temp['data'] # Need to look at include USB in API
        #logging.debug('getMultiOutletPortState  {} {} {}'.format(port,temp['state'], temp ))
        if yolink.online and yolink.nbrUsb > 0 and usb < yolink.nbrUsb:
            return(temp['state'][usb])
        else:
            return('unknown')


    def setMultiDelay(yolink,  delayList):
        logging.debug(yolink.type+' - setDelay')
        #port = port + yolink.nbrUsb
        data = {}
        if len(delayList) >= 1:
            for delayNbr in range(0,len(delayList)):
                for key in delayList:
                    if key.lower() == 'delayon' or key.lower() == 'on' :
                        data['params']['delays'][delayNbr]['on'] = delayList[delayNbr][key]
                    elif key.lower() == 'delayoff'or key.lower() == 'off' :
                        data['params']['delays'][delayNbr]['off'] = delayList[delayNbr][key] 
                    elif key.lower == 'ch':
                        data['params']['delays'][delayNbr]['ch'] = delayList[delayNbr][key] 
                    else:
                        logging.debug('Wrong parameter passed - must be overwritten to support multi devices  : ' + str(key))
        else:
            logging.debug('Empty list provided ')
            return(False, yolink.dataAPI[yolink.dOnline])
        data['time'] = str(int(time.time())*1000)
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.yolinkMQTTclient.publish_data( data)
        yolink.online = yolink.dataAPI[yolink.dOnline]
        return(True)


    '''
    def getMultiOutletData(yolink):
        logging.debug(yolink.type+' - getMultiOutletData')
    '''
    def updateStatus(self, data):
        self.updateCallbackStatus(data, False)
        # add sub node updates 
    '''
    def refreshFWversion(yolink):
        logging.debug('refreshFWversion - not currently supported')
        #return(yolink.refreshDevice('MultiOutlet.getVersion',  yolink.updateStatus))

    def startUpgrade(yolink):
        logging.debug('startUpgrade - not currently supported')
    
    def checkStatusChanges(yolink):
        logging.debug('checkStatusChanges')
    '''

    '''
    def resetDelayList (yolink):
        yolink.delayList = []

    def appendDelay(yolink, delay):
        # to remove a delay program it to 0 
        try:
            invalid = False
            if 'port' in delay  and 'OnDelay' in delay and 'OffDelay' in delay:
                if delay['port'] <0 and delay['port'] >= yolink.nbrPorts:
                    invalid = True
                if 'OnDelay' in delay:
                    if delay['OnDelay'] < 0:
                        invalid = True
                if 'OffDelay' in delay:
                    if delay['OffDelay'] < 0:
                        invalid = True
            elif  'OnDelay' in delay and 'OffDelay' in delay:
                if 'OnDelay' in delay:
                    if delay['OnDelay'] < 0:
                        invalid = True
                if 'OffDelay' in delay:
                    if delay['OffDelay'] < 0:
                        invalid = True
                delay['port'] = 1 #use channel 1 for non-multi port devices
            else:
                logging.debug('Missing or wrong input parameters: ' + str(delay))
            if not invalid:
                yolink.delayList.append(delay)
            return(invalid)
        except logging.exception as E:
            logging.debug('Exception appendDelay : ' + str(E))

    def prepareDelayData(yolink):
        data={}
        data['params'] = {}
        nbrDelays = len(yolink.delayList)
        data["params"]["delays"] = []
        if nbrDelays > 0:
            for delayNbr in range (0,nbrDelays):
                #temp = yolink.delayList[delayNbr]
                temp = {}
                temp['ch'] = yolink.delayList[delayNbr]['port']
                temp['on'] = yolink.delayList[delayNbr]['OnDelay']
                temp['off'] = yolink.delayList[delayNbr]['OffDelay']
                
                data["params"]["delays"].append(temp)
                #temp['on'] = tmp['OnDelay']
                #temp['off'] = tmp['OffDelay']
                #data["params"]["delays"].append(temp)
        return(data)
    '''

class YoLinkMultiOutlet(YoLinkMultiOut):

    def __init__(yolink, yoAccess, deviceInfo):
        super().__init__(  yoAccess, deviceInfo, yolink.updateStatus)
        yolink.initNode()

    def updateStatus(self, data):
        self.updateCallbackStatus(data, True)