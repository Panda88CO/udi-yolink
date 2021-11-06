
import time
import threading
import logging
from  datetime import datetime
from dateutil.tz import *



logging.basicConfig(level=logging.DEBUG)

import paho.mqtt.client as mqtt
from queue import Queue
from yolink_mqtt_client import YoLinkMQTTClient

"""
Object representation for YoLink MQTT Client
"""
class YoLinkMQTTDevice(object):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback):
        #super().__init__( yolink_URL, csid, csseckey, deviceInfo)
        #self.callback = callback
        #self.build_device_api_request_data()
        #self.enable_device_api()
        #{"deviceId": "d88b4c1603007966", "deviceUDID": "75addd8e21394d769b85bc292c553275", "name": "YoLink Hub", "token": "118347ae-d7dc-49da-976b-16fae28d8444", "type": "Hub"}
        self.deviceInfo = deviceInfo
        self.deviceId = self.deviceInfo['deviceId']
        self.delayList = []

        self.yolinkMQTTclient = YoLinkMQTTClient(csName, csid, csseckey, mqtt_URL, mqtt_port,  self.deviceId , callback )

        self.yolink_URL = yolink_URL
        self.mqtt_url = mqtt_URL

        self.daysOfWeek = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        self.type = ''
        
        
        self.maxSchedules = 6
        self.methodList = []
        self.eventList = []
        self.lastUpdate = 'lastTime'
        self.lastMessage = 'lastMessage'
        self.dOnline = 'online'
        self.dData = 'data'
        self.dState= 'state'
        self.dSchedule = 'schedules'
        self.dDelays = 'delays' 
        self.messageTime = 'time'
        self.forceStop = False


        
        self.dataAPI = {
                        'lastTime':str(int(time.time()*1000))
                        ,'lastMessage':{}
                        ,'online':None
                        ,'data':{ 'state':{} }
                        }
   
        self.eventQueue = Queue()
        self.mutex = threading.Lock()
        self.timezoneOffsetSec = self.timezoneOffsetSec()
        self.yolinkMQTTclient.connect_to_broker()
        #self.loopTimeSec = updateTimeSec
    
        #self.updateInterval = 3
        self.messagePending = False

   
    def deviceError(self, data):
        logging.debug(self.type+' - deviceError')
        self.dataAPI[self.dOnline] = False
        # may need to add more error handling 

    def refreshDevice(self):
        logging.debug(self.type+' - refreshDevice')
        if 'getState' in self.methodList:
            methodStr = self.type+'.getState'
            #logging.debug(methodStr)  
            data = {}
            data['time'] = str(int(time.time())*1000)
            data['method'] = methodStr
            data["targetDevice"] =  self.deviceInfo['deviceId']
            data["token"]= self.deviceInfo['token']
            self.yolinkMQTTclient.publish_data(data)
            #time.sleep(2)
              
    def setDevice(self,  data):
        logging.debug(self.type+' - setDevice')
        if 'setState' in self.methodList:
            methodStr = self.type+'.setState'
            data['time'] = str(int(time.time())*1000)
            data['method'] = methodStr
            data["targetDevice"] =  self.deviceInfo['deviceId']
            data["token"]= self.deviceInfo['token']
            self.yolinkMQTTclient.publish_data(data)
            return(True)
        else:
            return(False)

    def getValue(self, key):
        logging.debug(self.type+' - getValue')
        attempts = 1
        while key not in self.dataAPI[self.dData] and attempts <3:
            time.sleep(1)
            attempts = attempts + 1
        if key in self.dataAPI[self.dData]:
            return(self.dataAPI[self.dData][key])
        else:
            return('NA')

    def refreshDelays(self):
        logging.debug(self.type+' - refreshDelays')
        self.refreshDevice()
        return(self.getDelays())


    def setDelay(self, delayList):
        logging.debug(self.type+' - setDelay')
        data = {}
        data['params'] = {}
        if len(delayList) == 0:  
            data['params']['delayOn'] = 0
            data['params']['delayOff'] = 0
        elif len(delayList) == 1:
            for key in delayList[0]:
                if key.lower() == 'delayon' or key.lower() == 'on' :
                    data['params']['delayOn'] = delayList[0][key]
                elif key.lower() == 'delayoff'or key.lower() == 'off' :
                    data['params']['delayOff'] = delayList[0][key] 
                else:
                    logging.debug('Wrong parameter passed - must be overwritten to support multi devices  : ' + str(key))
        else:
            logging.debug('Must overwrite to support multi devices for now')
            return(False)
        data['time'] = str(int(time.time())*1000)
        data['method'] = self.type+'.setDelay'
        data["targetDevice"] =  self.deviceInfo['deviceId']
        data["token"]= self.deviceInfo['token'] 
        self.yolinkMQTTclient.publish_data( data)
        return(True)


    def refreshSchedules(self):
        logging.debug(self.type+' - refreshSchedules')
        if 'getSchedules' in self.methodList:
            data= {}
            methodStr = self.type+'.getSchedules'
            data['time'] = str(int(time.time())*1000)
            data['method'] = methodStr
            data["targetDevice"] =  self.deviceInfo['deviceId']
            data["token"]= self.deviceInfo['token']
            self.yolinkMQTTclient.publish_data( data)
            time.sleep(1)
 
    def getSchedules(self):
        nbrSchedules  = len(self.dataAPI[self.dData][self.dSchedule])
        temp = {}
        for schedule in range(0,nbrSchedules):
            temp[schedule] = {}
            for key in self.dataAPI[self.dData][self.dSchedule][str(schedule)]:
                if key == 'week':
                    days = self.maskToDays(self.dataAPI[self.dData][self.dSchedule][str(schedule)][key])
                    temp[schedule][key]= days
                elif key == 'isValid':
                     temp[schedule]['isActive']=self.dataAPI[self.dData][self.dSchedule][str(schedule)][key]
                elif self.dataAPI[self.dData][self.dSchedule][str(schedule)][key] == '25:0':
                    temp[schedule][key] = 'DISABLED'
                else:
                     temp[schedule][key] = self.dataAPI[self.dData][self.dSchedule][str(schedule)][key]
        return(temp)

    def refreshFWversion(self):
        logging.debug(self.type+' - refreshFWversion - Not supported yet')
        #return(self.refreshDevice('Manipulator.getVersion', self.updateStatus))

   



















    def daysToMask (self, dayList):
        daysValue = 0 
        i = 0
        for day in self.daysOfWeek:
            if day in dayList:
                daysValue = daysValue + pow(2,i)
            i = i+1
        return(daysValue)

    def maskToDays(self, daysValue):
        daysList = []
        for i in range(0,7):
            mask = pow(2,i)
            if (daysValue & mask) != 0 :
                daysList.append(self.daysOfWeek[i])
        return(daysList)

    def updateNbrPorts(self, data):
        if 'delays' in data['data']:
            self.dataAPI['nbrPorts'] = len(data['data']['delays'])  
        return(self.dataAPI['nbrPorts'])

    def getNbrPorts(self):
        if 'nbrPorts' in self.dataAPI:
            return(self.dataAPI['nbrPorts'] )
        else:
            return (0)

    def setOnline(self, data):
        if 'online' in data[self.dData]:
            self.dataAPI[self.dOnline] = data[self.dData][self.dOnline]
        else:
            self.dataAPI[self.dOnline] = True

    def setNbrPorts(self, data):
        if not 'nbrPorts' in self.dataAPI:
            if 'delays' in data['data']:
                self.nbrPorts  = len(data['data']['delays'])
                self.dataAPI['nbrPorts'] = self.nbrPorts 
            else:
                self.dataAPI['nbrPorts'] = -1 # to handle case where event happens before first poll - will be updated right after this

    def updateLoraInfo(self, data):
        if self.dState in data[self.dData]:
            if 'loraInfo' in data[self.dData][self.dState]:
                self.dataAPI[self.dData][self.dState]['loraInfo']= data[self.dData]['loraInfo']

    def updateMessageInfo(self, data):
        self.dataAPI[self.lastUpdate] = data[self.messageTime]
        self.dataAPI[self.lastMessage] = data

    def updateMultiStatusData (self, data):
        self.setOnline(data)
        self.setNbrPorts(data)
        self.updateLoraInfo(data)
        if 'method' in data:
            #for key in range(0, self.nbrPorts):
            self.dataAPI[self.dData][self.dState] = data[self.dData][self.dState][0:self.nbrPorts]
                
            if 'delays'in data[self.dData]:
                self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dDelays]
                    #self.dataAPI[self.dData][self.dDelays]=[]
                    #test = data[self.dData][self.dDelays][key]
                    #self.dataAPI[self.dData][self.dDelays][key] = test
        else: #event
            self.dataAPI[self.dData][self.dState] = data[self.dData][self.dState][0:self.nbrPorts]
            if 'delays'in data[self.dData]:
                self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dDelays]                 
        self.updateMessageInfo(data)


    def updateStatusData  (self, data):
        if 'online' in data[self.dData]:
            self.dataAPI[self.dOnline] = data[self.dData][self.dOnline]
        else:
            self.dataAPI[self.dOnline] = True
        if 'method' in data:
            if self.dState in data[self.dData]:
                if type(data[self.dData][self.dState]) is dict:
                    for key in data[self.dData][self.dState]:
                        if key == 'delay':
                             self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dState][self.dDelays]
                        else:
                            self.dataAPI[self.dData][self.dState][key] = data[self.dData][self.dState][key]
                elif  type(data[self.dData][self.dState]) == list:
                    self.dataAPI[self.dData][self.dState] = data[self.dData][self.dState][0:self.nbrPorts]
                    if 'delays'in data[self.dData]:
                        self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dDelays]
                else:
                    for key in data[self.dData]:
                        if key == 'delay':
                             self.dataAPI[self.dData][self.dDelays] = data[self.dData][key]
                        else:
                             self.dataAPI[self.dData][self.dState][key] = data[self.dData][key]
        else: #event
            for key in data[self.dData]:
                self.dataAPI[self.dData][self.dState][key] = data[self.dData][key]
        self.updateLoraInfo(data)
        self.updateMessageInfo(data)

    def updateScheduleStatus(self, data):
        self.setOnline(data)
        self.setNbrPorts(data)
        self.updateLoraInfo(data)
        self.dataAPI[self.dData][self.dSchedule] = data[self.dData]
        self.dataAPI[self.lastMessage] = data

    def updateDelayStatus(self, data):
        self.setOnline(data)
        self.setNbrPorts(data)
        self.updateLoraInfo(data)
        if 'delays'in data[self.dData]:
            self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dDelays]
 
        self.updateMessageInfo(data)

    def updateFWStatus(self, data):
        # Need to have it workign forst - not sure what return struture will look lik
        #self.dataAPI['data']['state']['state'].append( data['data'])
        self.dataAPI['state']['lastTime'] = data['time']
        self.dataAPI['lastMessage'] = data      

    def eventPending(self):
        return( not self.eventQueue.empty())
    
    def extractEventData(self):
        if not self.eventQueue.empty():
            return(self.eventQueue.get())
        else:
            return(None)
           
    def getInfoAPI (self):
        return(self.dataAPI)

    def sensorOnline(self):
        return(self.dataAPI['online'] )       

    def getLastUpdate (self):
        return(self.dataAPI[self.lastUpdate])

    def refreshState(self):
        logging.debug(str(self.type)+ ' - refreshState')
        #devStr = str(self.type)+'.getSate'
        self.refreshDevice()
        #time.sleep(2)
   
    def getState(self):
        logging.debug('Manituplator - getState')
        return(self.dataAPI[self.dData][self.dState][self.dState])

    def getDelays(self):
        logging.debug(str(self.type)+ ' - getDelays')
        self.refreshDevice()
        time.sleep(2)
        if self.dDelays in self.dataAPI:
            return(self.dataAPI[self.dDelays])
        else:
            return(None)



        return(self.dataAPI[self.dData][self.dDelays])

    def updateGarageCtrlStatus(self, data):
        self.dataAPI[self.dData][self.dState] = data['data']
        self.dataAPI[self.lastUpdate] = data[self.messageTime]
        self.dataAPI[self.lastMessage] = data
  
    def timezoneOffsetSec(self):
        local = tzlocal()
        tnow = datetime.now()
        tnow = tnow.replace(tzinfo = local)
        utctnow = tnow.astimezone(tzutc())
        tnowStr = str(tnow)
        
        pos = tnowStr.rfind('+')
        if pos > 0:
            tnowStr = tnowStr[0:pos]
        else:
            pos = tnowStr.rfind('-')
            tnowStr = tnowStr[0:pos]
        utctnowStr = str(utctnow)
        pos = utctnowStr.rfind('+')
        if pos > 0:
            utctnowStr = utctnowStr[0:pos]
        else:
            pos = utctnowStr.rfind('-')
            utctnowStr = utctnowStr[0:pos]

        tnow = datetime.strptime(tnowStr,  '%Y-%m-%d %H:%M:%S.%f')
        utctnow = datetime.strptime(utctnowStr,  '%Y-%m-%d %H:%M:%S.%f')
        diff = utctnow - tnow
        return (diff.total_seconds())
    '''
    def setDelay(self, delayList):

        logging.debug('setManipulatorDelay')
        data = {}
        data['params'] = {} 
        if 'delayOn' in delayList or 'ON' in delayList:
            data['params']['delayOn'] = delayList['delayOn']
        else:
            data['params']['delayOn'] = 0
        if 'delayOff' in delayList  or 'OFF' in delayList:
            data['params']['delayOff'] = delayList['delayOff']   
        else:
            data['params']['delayOff'] = 0
        return(self.setDevice( data ))
    '''

    def resetSchedules(self):
        logging.debug('resetSchedules')
        self.scheduleList = {}

    def activateSchedules(self, index, Activated):
        logging.debug('activateSchedules')
        if index in self. scheduleList:
            if Activated:
                self.scheduleList[index]['isValid'] = 'Enabled'
            else:
                self.scheduleList[index]['isValid'] = 'Disabled'
            return(True)
        else:
            return(False)

    def addSchedule(self, schedule):
        logging.debug('addSchedule')
        if 'days' and ('onTime' or 'offTime') and 'isValid' in schedule:    
            index = 0
            while  index in self.scheduleList:
                index=index+1
            if index < self.maxSchedules:
                self.scheduleList[index] = schedule
                return(index)
        return(-1)
            
    def deleteSchedule(self, index):
        logging.debug('addSchedule')       
        if index in self.scheduleList:
            self.scheduleList.pop(1)
            return(True)
        else:
            return(False)

    def transferSchedules(self):
        logging.debug('transferSchedules - does not seem to work yet')
        data = {}

        for index in self.scheduleList:
            data[index] = {}
            data[index]['index'] = index
            if self.scheduleList[index]['isValid'] == 'Enabled':
                data[index]['isValid'] = True
            else:
                data[index]['isValid'] = False
            if 'onTime' in self.scheduleList[index]:
                data[index]['on'] = self.scheduleList[index]['onTime']
            else:
                data[index]['on'] = '25:0'
            if 'offTime' in self.scheduleList[index]:
                data[index]['off'] = self.scheduleList[index]['offTime'] 
            else:
                data[index]['off'] = '25:0'
            data[index]['week'] = self.daysToMask(self.scheduleList[index]['days'])

        return(self.setDevice( 'Manipulator.setSchedules', data, self.updateStatus))