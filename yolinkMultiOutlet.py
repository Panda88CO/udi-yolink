import json
import time
import re

from yolink_mqtt_class import YoLinkMQTTDevice
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class YoLinkMultiOut(YoLinkMQTTDevice):
    def __init__(yolink, csName, csid, csseckey, deviceInfo, callback, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback)
        yolink.maxSchedules = 6
        yolink.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdates'   ]
        yolink.eventList = ['StatusChange', 'Report']
        yolink.type = 'MultiOutlet'
        yolink.MultiOutletName = 'MultiOutletEvent'
        yolink.eventTime = 'Time'
        time.sleep(2)


    def initNode(yolink):
        logging.debug('MultiOutlet initNode')
        yolink.refreshMultiOutlet() # needed to get number of ports on device
       
        time.sleep(2)
        
        yolink.initDevice()
        temp = yolink.getInfoAPI()
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            logging.info('MultiOutlet init - Nbr Outlets : {}'.format(yolink.nbrOutlets))
            logging.info('MultiOutlet init - Nbr USB : {}'.format(yolink.nbrUsb))
    
           
        else:
            logging.error ('MultiOutlet not online')
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
            yolink.setDevice( data)
        return(status)
    
    def getMultiOutStates(yolink):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        states= {}
        temp = yolink.getInfoAPI()
        if yolink.online:
            for outlet in temp['data']['delays']:
                port = outlet['ch']-yolink.nbrUsb
                states['port'+str(port)]= {'state':temp['data']['state'][port], 'delays':outlet}
            #print(states)
            for usb in range (0,yolink.nbrUsb):
                    states['usb'+str(usb)]= {'state':temp['data']['state'][usb]}
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

    def __init__(yolink, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, deviceInfo, yolink.updateStatus, yolink_URL, mqtt_URL, mqtt_port)
        yolink.initNode()

    def updateStatus(self, data):
        self.updateCallbackStatus(data, True)