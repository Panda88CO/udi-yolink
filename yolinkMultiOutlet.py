import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkMultiOutlet(YoLinkMQTTDevice):

    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        self.maxSchedules = 6
        self.methodList = ['getState', 'setState', 'setDelay', 'getSchedules', 'setSchedules', 'getUpdates'   ]
        self.eventList = ['StatusChange', 'Report']
        self.type = 'MultiOutlet'
        self.ManipulatorName = 'MultiOutletEvent'
        self.eventTime = 'Time'
        time.sleep(3)
        self.refreshMultiOutlet() # needed to get number of ports on device
        self.nbrPorts  = self.getNbrPorts()  
        self.refreshSchedules()
        self.refreshFWversion()


    def getSchedules (self):
        return(self.dataAPI['data']['schedules'])  

    def getDelays (self):
        return(self.dataAPI['data']['delays'])  


    def updateStatus(self, data):
        if 'method' in  data:
            if  (data['method'] == 'MultiOutlet.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateMultiStatusData(data)             
            elif  (data['method'] == 'MultiOutlet.setState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateMultiStatusData(data)                                       
            elif  (data['method'] == 'MultiOutlet.setDelay' and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateDelayStatus(data)
            elif  (data['method'] == 'MultiOutlet.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateScheduleStatus(data)
            elif  (data['method'] == 'MultiOutlet.setSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()): 
                    self.updateScheduleStatus(data)
            elif  (data['method'] == 'MultiOutlet.getVersion' and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateFWStatus(data)

            else:
                logging.debug('Unsupported Method passed' + str(json.dumps(data)))
        elif 'event' in data:
            if data['event'] == 'MultiOutlet.StatusChange':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateMultiStatusData(data)    

            elif data['event'] == 'MultiOutlet.Report':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateMultiStatusData(data)  

            else :
                logging.debug('Unsupported Event passed' + str(json(data)))
                                        

    def refreshMultiOutlet(self):
        return(self.refreshDevice('MultiOutlet.getState', self.updateStatus))


    def setMultiOutletState(self, portList, value ):
        logging.debug('setMultiOutletState')
        # portlist a a listof ports being changed port range 0-7
        # vaue is state that need to change 2 (ON/OFF)
        status = True
        port = 0
        for i in portList:
            if i <= self.nbrPorts and i >= 0 :
                port = port + pow(2, i)
            else:
                logging.error('wrong port number (range 0- '+str(self.nbrPorts)+'): ' + str(i))
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
            self.setDevice( 'MultiOutlet.setState', data, self.updateStatus)
        return(status)


    def refreshSchedules(self):
        return(self.refreshDevice('MultiOutlet.getSchedules', self.updateScheduleStatus))
 
    
    def resetScheduleList(self):
        self.scheduleList = []

    def setSchedule(self, scheduleList):
        logging.debug('setMultiOutletSchedule - not currently supported')
       
        data = {}
        data["params"] = {}
        data["params"]["chs"] =  scheduleList
        #data["params"]['state'] = state
        #return(self.setDevice('MultiOutlet.setSchedules', data, self.updateScheduleStatus))


    def getMultiOutletState(self):
        self.refreshMultiOutlet()
        temp = self.getInfoAPI()
        states= {}
        for port in range(0,self.nbrPorts):
            if 'delays' in temp['data']:
                delay = None
                for ch in  temp['data']['delays']:
                    if ch['ch'] == port:
                        delay = ch
                states['port'+str(port)]= {'state':temp['data']['state'][port], 'delays':delay}
        #print(states)
        return(states)


    #def removeDelay(self, delay):

    
    def setDelay(self):
        logging.debug('setMultiOutletDelay ')
        data = self.prepareDelayData()
        return(self.setDevice('MultiOutlet.setDelay', data, self.updateStatus))


    def refreshFWversion(self):
        logging.debug('refreshFWversion - not currently supported')
        #return(self.refreshDevice('MultiOutlet.getVersion',  self.updateStatus))

    def startUpgrade(self):
        logging.debug('startUpgrade - not currently supported')
    '''
    def checkStatusChanges(self):
        logging.debug('checkStatusChanges')
    '''


    def resetDelayList (self):
        self.delayList = []

    def appendDelay(self, delay):
        # to remove a delay program it to 0 
        try:
            invalid = False
            if 'port' in delay  and 'OnDelay' in delay and 'OffDelay' in delay:
                if delay['port'] <0 and delay['port'] >= self.nbrPorts:
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
                self.delayList.append(delay)
            return(invalid)
        except logging.exception as E:
            logging.debug('Exception appendDelay : ' + str(E))

    def prepareDelayData(self):
        data={}
        data['params'] = {}
        nbrDelays = len(self.delayList)
        data["params"]["delays"] = []
        if nbrDelays > 0:
            for delayNbr in range (0,nbrDelays):
                #temp = self.delayList[delayNbr]
                temp = {}
                temp['ch'] = self.delayList[delayNbr]['port']
                temp['on'] = self.delayList[delayNbr]['OnDelay']
                temp['off'] = self.delayList[delayNbr]['OffDelay']
                
                data["params"]["delays"].append(temp)
                #temp['on'] = tmp['OnDelay']
                #temp['off'] = tmp['OffDelay']
                #data["params"]["delays"].append(temp)
        return(data)