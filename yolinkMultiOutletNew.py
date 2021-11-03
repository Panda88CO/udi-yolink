import json
import time
import logging

from yolink_mqtt_class2 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)


class YoLinkMultiOutlet(YoLinkMQTTDevice):

    def __init__(self, csName, csid, csseckey, deviceInfo, yolink_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, self.updateStatus)
        self.maxSchedules = 6
        self.methodList = ['MultiOutlet.getState', 'MultiOutlet.setState', 'MultiOutlet.setDelay', 'MultiOutlet.getSchedules', 'MultiOutlet.setSchedules'   ]
        self.eventList = ['MultiOutlet.StatusChange', 'MultiOutlet.Report']
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


    '''
    def getInfoAPI(self):  
        return(self.dataAPI)
    '''
    def updateStatus(self, data):
        if 'method' in  data:
            if  (data['method'] == 'MultiOutlet.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    #self.nbrPorts  = self.updateNbrPorts(data)
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateMultiStatusData(data)             
            elif  (data['method'] == 'MultiOutlet.setState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
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
                logging.debug('Unsupported Method passed' + str(json(data)))
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
        return(self.setDevice('MultiOutlet.setSchedules', data, self.updateScheduleStatus))


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


    def resetDelayList (self):
        self.delayList = []

    def appendDelay(self, delay):
        nbrDelays = len(self.delayList)
        #self

    def setDelay(self, delayList):
        logging.debug('setMultiOutletDelay - not currently supported')
        data={}
        nbrDelays = len(delayList)
        data["params"]["delays"] = {}
        if nbrDelays > 0:
            for delayNbr in delayList:
                data["params"]["delays"][delayNbr]={}
                data["params"]["delays"][delayNbr]['ch'] = delayList[delayNbr]['port']
                data["params"]['delays'][delayNbr]['on'] = delayList[delayNbr]['OnDelay']
                data["params"]['delays'][delayNbr]['off'] = delayList[delayNbr]['OffDelay']
        
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


