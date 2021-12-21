import json
import time


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
        yolink.online = yolink.getOnlineStatus()
        if yolink.online:
            yolink.nbrPorts = yolink.getNbrPorts()
            logging.debug('MultiOutlt init - Nbr ports: {}'.format(yolink.nbrPorts))
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
    

    def setMultiOutletState(yolink, portList, value ):
        logging.debug( yolink.type+'- setMultiOutletState')
        # portlist a a listof ports being changed port range 0-7
        # value is state that need to change 2 (ON/OFF)
        status = True
        port = 0
        for i in portList:
            if i <= yolink.nbrPorts and i >= 0 :
                port = port + pow(2, i)
            else:
                logging.error('wrong port number (range 0- '+str(yolink.nbrPorts)+'): ' + str(i))
                status = False
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
            yolink.setDevice( 'MultiOutlet.setState', data, yolink.updateStatus)
        return(status)
    
    def getMultiOutletStates(yolink):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        temp = yolink.getInfoAPI()
        #yolink.nbrPorts, yolink.online = yolink.getNbrPorts()
        states= {}
        logging.debug('getMultiOutletState - temp = {}'.format(temp))
        for port in range(0,yolink.nbrPorts):
            if 'delays' in temp['data']:
                delay = None
                for ch in  temp['data']['delays']:
                         if ch['ch'] == port + yolink.nbrUsb: ###
                            delay = ch
                   
                states['port'+str(port)]= {'state':temp['data']['state'][port+ yolink.nbrUsb], 'delays':delay}
        #print(states)
        for usb in range (0,yolink.nbrUsb):
                states['usb'+str(usb)]= {'state':temp['data']['state'][port+ yolink.nbrUsb]}
        return(states)

    def getMultiOutletPortState(yolink, port):
        logging.debug(yolink.type+' - getMultiOutletState')
        #yolink.refreshMultiOutlet()
        temp = yolink.getInfoAPI()
        temp = temp['lastMessage']['data'] # Need to look at include USB in API
        #logging.debug('getMultiOutletPortState  {} {} {}'.format(port,temp['state'], temp ))
        if yolink.online and port < len(temp['state']):
            return(temp['state'][port])
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