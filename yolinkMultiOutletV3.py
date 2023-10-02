import json
#from os import ONDELAY
import time
import re

from yolink_mqtt_classV3 import YoLinkMQTTDevice
from yolink_delay_timer import CountdownTimer
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
        yolink.yoAccess = yoAccess
        yolink.maxSchedules = 6
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdates'   ]
        yolink.eventList = ['StatusChange', 'Report']
        yolink.type = 'MultiOutlet'
        yolink.MQTT_class = 'c'
        yolink.last_set_data = None
        yolink.attempt = 0
        yolink.MultiOutletName = 'MultiOutletEvent'
        yolink.eventTime = 'Time'
        yolink.delayUpdateInt = 15
        yolink.nbrOutlets = 0
        yolink.nbrUsb = 0
        #yolink.timerCallback = callback
        yolink.extDelayTimer = CountdownTimer()
        #yolink.extDelayTimer.timerCallback(callback)

        #time.sleep(1)

    '''
    def initNode(yolink):
        logging.debug('MultiOutlet initNode - {}'.format(yolink.deviceInfo['name']))
        
        yolink.initDevice()
        time.sleep(2)
        #time.sleep(2)
        
       
        #temp = yolink.getInfoAPI()
        #yolink.refreshMultiOutlet() # needed to get number of ports on device
        #yolink.refreshDevice()
        #yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            logging.info('MultiOutlet init - Nbr Outlets : {}'.format(yolink.nbrOutlets))
            logging.info('MultiOutlet init - Nbr USB : {}'.format(yolink.nbrUsb))
        else:
            logging.info ('MultiOutlet not online')
        #yolink.refreshSchedules()
        #yolink.refreshFWversion()

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
            portNbr = yolink.extractStrNbr(i)
            if portNbr < yolink.nbrUsb and portNbr >= 0 :
                port = port + pow(2, portNbr)
            else:
                logging.error('wrong port number (range 0- '+str(yolink.nbrPorts)+'): ' + str(i))
                return(False)
        if value.lower() == 'on' or value.lower() == 'open':
            state = 'open'
        elif value.lower() == 'off' or value.lower() == 'closed' :
            state = 'closed'
        else:
            logging.error('Unknows state passed')
            status = False
        if status:
            data={}
            data["params"] = {}
            data["params"]["chs"] =  port
            data["params"]['state'] = state
            yolink.last_set_data = data
            yolink.setDevice(  data)
        return(status)
    

    def data_updated(yolink):
        tmp = yolink.lastUpdate()
        if ( tmp > yolink.lastUpdateTime):
            yolink.lastUpdateTime = tmp 
            logging.debug('{} - Data Updated'.format(yolink.type))
            return(True)
        else:
            return(False)


    def setUsbState (yolink, port, state):
        logging.info('usbSetState')
     
        if yolink.nbrUsb > 0:
            portList = []
            portList.append(yolink.extractStrNbr(port))
            yolink.setMultiOutUsbState(portList, state)
        else:
            logging.error('No USB port on device')



    def setMultiOutPortState(yolink, portList, value ):
        logging.debug( yolink.type+'- setMultiOutletState')
        # portlist a a listof ports being changed port range 0-7
        # value is state that need to change 2 (ON/OFF)
        status = True
        port = 0
        for i in portList:            
            portNbr = yolink.extractStrNbr(i)
            portNbr = portNbr + yolink.nbrUsb  # Ports start after USB control ports
            if portNbr <= yolink.nbrPorts and portNbr >= 0 :
                port = port + pow(2, portNbr)
            else:
                logging.error('wrong port number (range 0 - '+str(yolink.nbrPorts)+'): ' + str(i))
                return(False)
        if value.lower() == 'on' or value.lower() == 'open':
            state = 'open'
        elif value.lower() == 'off' or value.lower() == 'closed' :
            state = 'closed'
        else:
            logging.error('Unknows state passed')
            status = False
        if status:
            data={}
            data["params"] = {}
            data["params"]["chs"] =  port
            data["params"]['state'] = state
            yolink.last_set_data = data
            yolink.setDevice( data)
        return(status)

    def setMultiOutState ( yolink, port, state):
        logging.info('outletSetState')
        portList = []
        portList.append(str(yolink.extractStrNbr(port))) # port is 0 based
        yolink.setMultiOutPortState(portList, state)


    def setMultiOutDelayList (yolink, delayList):

        logging.info('outletSetDelayList')
        data = {}
        delTemp = []
        data['params'] = {}
        data['params']['delays'] = []
        for delays in range(0,len(delayList)):  
            temp = {}
            for key in delayList[delays]:               
                if key.lower() == 'ch' or key.lower() == 'port':
                    ch = int(delayList[delays][key])
                    temp['ch'] = ch
                    #dTemp['ch'] = ch
                if key.lower() == 'on' or key.lower() == 'ondelay' or key.lower() == 'delayon':
                    onDelay = int(delayList[delays][key])
                    temp['on'] =  onDelay
                    #dTemp['on'] = onDelay
                if key.lower() == 'off' or key.lower() == 'offdelay' or key.lower() == 'delayoff':
                    offDelay = int(delayList[delays][key])
                    temp['off'] = offDelay
                    #dTemp['off'] = offDelay
            logging.debug('temp delayList: {}'.format(temp))
            if 'ch' in temp and len(temp)>1:
                data['params']['delays'].append(temp)
                delTemp.append(temp)
        logging.debug('Sending delay data: {}'.format( data['params']['delays']))
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.last_set_data = data
        yolink.send_data( data)
        #yolink.writeDelayData(data)
        yolink.extDelayTimer.addDelays(delTemp)
        yolink.online = yolink.dataAPI[yolink.dOnline]


    def setMultiOutDelay (yolink, port, onDelay, offDelay):
        logging.info('outletSetDelay')
        data = {}
        data['params'] = {}
        data['params']['delays'] = []
        portNbr = yolink.extractStrNbr(port)
        delaySpec = {'ch':portNbr+yolink.nbrUsb, 'on':onDelay, 'off':offDelay}       
        
        logging.debug('Sending delay data: {}'.format(delaySpec))
        data['params']['delays'].append(delaySpec)
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.last_set_data = data
        yolink.send_data( data)
        #yolink.writeDelayData(data)
        yolink.extDelayTimer.addDelays([{'ch':portNbr+yolink.nbrUsb, 'on':onDelay, 'off':offDelay}] )
        yolink.online = yolink.dataAPI[yolink.dOnline]

    def setMultiOutOnDelay (yolink, port, onDelay):
        logging.info('outletSetDelay')
        data = {}
        data['params'] = {}
        data['params']['delays'] = []
        portNbr = yolink.extractStrNbr(port)
        delaySpec = {'ch':portNbr+yolink.nbrUsb, 'on':onDelay}       
        
        logging.debug('Sending delay data: {}'.format(delaySpec))
        data['params']['delays'].append(delaySpec)
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.last_set_data = data
        yolink.send_data( data)
        #yolink.writeDelayData(data)
        yolink.extDelayTimer.addDelays([{'ch':portNbr+yolink.nbrUsb, 'on':onDelay}] )
        yolink.online = yolink.dataAPI[yolink.dOnline]
    
    def setMultiOutOffDelay (yolink, port, offDelay):
        logging.info('outletSetDelay')
        data = {}
        data['params'] = {}
        data['params']['delays'] = []
        portNbr = yolink.extractStrNbr(port)
        delaySpec = {'ch':portNbr+yolink.nbrUsb, 'off':offDelay}       
        
        logging.debug('Sending delay data: {}'.format(delaySpec))
        data['params']['delays'].append(delaySpec)
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
        yolink.last_set_data = data
        yolink.send_data( data)
        #yolink.writeDelayData(data)
        yolink.extDelayTimer.addDelays([{'ch':portNbr+yolink.nbrUsb, 'off':offDelay}] )
        yolink.online = yolink.dataAPI[yolink.dOnline]

    def retry_send_data(yolink):
        logging.debug('retrying to send data')
        yolink.send_data(yolink.last_set_data)

    def getMultiOutStates(yolink):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        states= {}
        temp = yolink.getInfoAPI()
        logging.debug(temp)

        for usb in range (0,yolink.nbrUsb):
                states['usb'+str(usb)]= {'state':temp['data']['state'][usb]}
        delays = yolink.extDelayTimer.timeRemaining()      
        for outlet in range(0, yolink.nbrOutlets):      
            state = temp['data']['state'][outlet + yolink.nbrUsb]
            found = False
            for indx in range(0, len(delays)):
                if delays[indx]['ch'] == outlet:
                    found = True
                   
                    if 'on' in delays[indx]:
                        onDelay = int(delays[indx]['on']/60)
                    else:
                        onDelay = 0
                    if 'off' in delays[indx]:
                        offDelay = int(delays[indx]['off']/60) 
                    else:
                        offDelay = 0 
            if not found:
                onDelay = 0
                offDelay = 0
            states['port'+str(outlet)]= {'state':state, 'delays':{'on':onDelay, 'off':offDelay}}
        return(states)


    def getMultiOutPortState(yolink, portStr):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        port = yolink.extractStrNbr(portStr)
        port = port + yolink.nbrUsb
        temp = yolink.getInfoAPI()
        temp = temp['data'] # Need to look at include USB in API
        #logging.debug('getMultiOutletPortState  {} {} {}'.format(port,temp['state'], temp ))
        if port < len(temp['state'])-yolink.nbrUsb:
            return(temp['state'][port])
        else:
            return('unknown')
        
    def getMultiOutUsbState(yolink, usbStr):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        usb = yolink.extractStrNbr(usbStr)
        temp = yolink.getInfoAPI()
        temp = temp['data'] # Need to look at include USB in API
        #logging.debug('getMultiOutletPortState  {} {} {}'.format(port,temp['state'], temp ))
        if yolink.nbrUsb > 0 and usb < yolink.nbrUsb:
            return(temp['state'][usb])
        else:
            return('unknown')

    '''
    def setMultiDelay(yolink,  delayList):
        atttempt = 1
        maxAttempts = 3
        logging.debug(yolink.type+' - setDelay')
        #port = port + yolink.nbrUsb
        data = {}
        data['params'] = {}
        data['params']['delays'] = []
        if len(delayList) >= 1:
            for delayNbr in range(0,len(delayList)):
                for key in delayList[delayNbr]:
                    if key.lower() == 'delayon' or key.lower() == 'on' :
                        data['params']['delays'][delayNbr]['on'] = delayList[delayNbr][key]
                    elif key.lower() == 'delay'or key.lower() == 'off' :
                        data['params']['delays'][delayNbr]['off'] = delayList[delayNbr][key] 
                    elif key.lower == 'CH':
                        data['params']['delays'][delayNbr]['ch'] = delayList[delayNbr][key] 
                    else:
                        logging.debug('Wrong parameter passed - must be overwritten to support multi devices  : ' + str(key))
        else:
            logging.debug('Empty list provided ')

            return(False, yolink.dataAPI[yolink.dOnline])
        data['time'] = str(int(time.time_ns()//1e6))
        data['method'] = yolink.type+'.setDelay'
        data["targetDevice"] =  yolink.deviceInfo['deviceId']
        data["token"]= yolink.deviceInfo['token'] 
         yolink.last_set_data = data
        yolink.send_data( data)
        yolink.online = yolink.dataAPI[yolink.dOnline]
        return(True)

    def getMultiOutletData(yolink):
        logging.debug(yolink.type+' - getMultiOutletData')
    
    def updateStatus(self, data):
        self.updateCallbackStatus(data, False)
        # add sub node updates 
    '''
    def updateStatus(yolink, data):
        yolink.updateCallbackStatus(data, False)
        '''

        max_attemps = 3
        if yolink.device_connected(data):
            logging.debug('yolink.device_connected(data) {} '.format(data))
            yolink.updateCallbackStatus(data, False)
            yolink.attempt = 0
        else:
            logging.error('{} - updateStatus - device appears not connected - retrying'.format(yolink.type))
            yolink.attempts = yolink.attempts + 1
            if yolink.attempts < max_attemps:
                logging.error('{} - updateStatus - device appears not connected - retrying'.format(yolink.type))
                time.sleep(1)
                yolink.send_data( yolink.last_set_data) #Try again
                #yolink.setState(yolink.temp_set_state) 
            else:
                logging.error('{} - updateStatus - device appears not connected - giving up after {} attempts'.format(yolink.type, yolink.attempts ))                
                yolink.updateCallbackStatus(data, False)
                yolink.attempts = 0
        '''

        
    def get_nbr_attempts (yolink):
        return(yolink.attempt)

    '''
    def refreshFWversion(yolink):
        logging.debug('refreshFWversion - not currently supported')
        #return(yolink.refreshDevice('MultiOutlet.getVersion',  yolink.updateStatus))

    def startUpgrade(yolink):
        logging.debug('startUpgrade - not currently supported')
    
    def checkStatusChanges(yolink):
        logging.debug('checkStatusChanges')

    def resetDelayList (yolink):
        yolink.delayList = []
    '''

    '''
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
    '''
    def shut_down(yolink):
        yolink.diconnect = True
        yolink.yolinkMQTTclient.shut_down()
    '''
class YoLinkMultiOutlet(YoLinkMultiOut):

    def __init__(yolink, yoAccess, deviceInfo):
        super().__init__(  yoAccess, deviceInfo, yolink.updateStatus)
        yolink.initNode()
        if yolink.online:
            logging.info('MultiOutlet init - Nbr Outlets : {}'.format(yolink.nbrOutlets))
            logging.info('MultiOutlet init - Nbr USB : {}'.format(yolink.nbrUsb))
        else:
            logging.info ('MultiOutlet not online')   


    def updateStatus(self, data):
        self.updateCallbackStatus(data, True)