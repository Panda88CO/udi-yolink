
import time
import json
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
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, deviceInfo, callback ):
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
        self.eventSupport = False # Support adding to EventQueue

        
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
    def shut_down(self):
        self.yolinkMQTTclient.shut_down()
   
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
            print ('refreshDevice')
            self.yolinkMQTTclient.publish_data(data)
            time.sleep(2)
              
    def setDevice(self,  data):
        logging.debug(self.type+' - setDevice')
        worked = False
        if 'setState' in self.methodList:
            methodStr = self.type+'.setState'
            worked = True
        elif 'toggle' in self.methodList:
            methodStr = self.type+'.toggle'
            worked = True
        data['time'] = str(int(time.time())*1000)
        data['method'] = methodStr
        data["targetDevice"] =  self.deviceInfo['deviceId']
        data["token"]= self.deviceInfo['token']
        if worked:
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

    def updateStatusData(self, data): 
        if 'online' in data[self.dData]:
            self.dataAPI[self.dOnline] = data[self.dData][self.dOnline]
        else:
            self.dataAPI[self.dOnline] = True
        if 'method' in data:
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

    def updateDelayData(self, data):
        if 'online' in data[self.dData]:
            self.dataAPI[self.dOnline] = data[self.dData][self.dOnline]
        else:
            self.dataAPI[self.dOnline] = True
        if 'event' in data:
            tmp =  {}
            for key in data[self.dData]:
                if key == 'delayOn':
                    tmp['on'] = data[self.dData][key]
                elif key == 'delayOff':
                    tmp['off'] = data[self.dData][key] 
                else:
                    tmp[key] =  data[self.dData][key] 
            self.dataAPI[self.dData][self.dDelays]= tmp
        self.updateLoraInfo(data)
        self.updateMessageInfo(data)

    def updateCallbackStatus(self, data, eventSupport = False):
        print(self.type+' - updateCallbackStatus')
        logging.debug(self.type+' - updateCallbackStatus')
        if 'method' in  data:
            if data['code'] == '000000':
                if  (data['method'] == self.type +'.getState' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)       
                elif  (data['method'] == self.type +'.setState' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateStatusData(data)                          
                elif  (data['method'] == self.type +'.setDelay' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateDelayData(data)       
                elif  (data['method'] == self.type +'.getSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateScheduleStatus(data)
                elif  (data['method'] == self.type +'.setSchedules' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateScheduleStatus(data)
                elif  (data['method'] == self.type +'.getVersion' and  data['code'] == '000000'):
                    if int(data['time']) > int(self.getLastUpdate()):
                        self.updateFWStatus(data)
                else:
                    logging.debug('Unsupported Method passed' + str(json.dumps(data)))     
            else:
                self.deviceError(data)
        elif 'event' in data:
            if data['event'] == self.type +'.StatusChange' :
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)              
            elif data['event'] == self.type +'.Report':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)  
            elif data['event'] == self.type +'.getState':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)  
            elif data['event'] == self.type +'.setState':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)                      
            elif data['event'] == self.type +'.getSchedules':
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateScheduleStatus(data)   
            elif data['event'] == self.type +'.Alert':         
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateScheduleStatus(data)  
            elif data['event'] == self.type +'.setDelay':         
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateDelayData(data)                    
            else:
                logging.debug('Unsupported Event passed - trying anyway' )
                print(data)
                logging.debug(data)
                try:
                    if int(data['time']) > int(self.getLastUpdate()):
                        if data['event'].find('chedule') >= 0 :
                            self.updateScheduleStatus(data)    
                        elif data['event'].find('ersion') >= 0 :
                            self.updateFWStatus(data)
                        else:
                            self.updateStatusData(data)   
                except logging.exception as E:
                    logging.debug('Unsupported event detected: ' + str(E))
            if eventSupport:
                self.eventQueue.put(data['event']) 
        else:
            logging.debug('updateStatus: Unsupported packet type: ' +  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))



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

    def resetScheduleList(self):
        self.scheduleList = []


    def prepareScheduleData(self):
        logging.debug(self.type + '- prepareScheduleData')
        nbrSchedules = len(self.scheduleList)
        if nbrSchedules <= self.maxSchedules:
            tmpData = {}
            for schedule in range (0, nbrSchedules):
                tmpData[schedule] = {}

                tmpData[schedule]['isValid'] = self.scheduleList[schedule]['isValid']
                tmpData[schedule]['index'] = self.scheduleList[schedule]['index']
                if 'on' in self.scheduleList[schedule]:
                    tmpData[schedule]['on'] = self.scheduleList[schedule]['on']
                else:
                    tmpData[schedule]['on'] = '25:0'
                if 'off' in self.scheduleList[schedule]:
                    tmpData[schedule]['off'] = self.scheduleList[schedule]['off']
                else:
                    tmpData[schedule]['off'] = '25:0'
                tmpData[schedule]['week'] = self.daysToMask(self.scheduleList[schedule]['week'])
            return(tmpData)
        else:
            logging.error('More than '+str(self.maxSchedules)+' defined')
            return(None)
        
    def refreshSchedules(self):
        logging.debug(self.type + '- refreshSchedules')

        if 'getSchedules' in self.methodList:
            methodStr = self.type+'.getSchedules'
            #logging.debug(methodStr)  
            data = {}
            data['time'] = str(int(time.time())*1000)
            data['method'] = methodStr
            data["targetDevice"] =  self.deviceInfo['deviceId']
            data["token"]= self.deviceInfo['token']
            self.yolinkMQTTclient.publish_data(data)
            

    def getSchedules(self):
        logging.debug(self.type + '- getSchedules')
        self.refreshSchedules()
        nbrSchedules  = len(self.dataAPI[self.dData][self.dSchedule])
        temp = {}
        self.scheduleList = []
        for schedule in range(0,nbrSchedules):
            temp[schedule] = {}
            for key in self.dataAPI[self.dData][self.dSchedule][str(schedule)]:
                if key == 'week':
                    days = self.maskToDays(self.dataAPI[self.dData][self.dSchedule][str(schedule)][key])
                    temp[schedule][key]= days
                elif self.dataAPI[self.dData][self.dSchedule][str(schedule)][key] == '25:0':
                    #temp[schedule].pop(key)
                    pass
                else:
                    temp[schedule][key] = self.dataAPI[self.dData][self.dSchedule][str(schedule)][key]
            temp[schedule]['index'] = schedule   
            self.scheduleList.append(temp[schedule])
        return(temp)



    def setSchedules(self):
        logging.debug(self.type + '- setSchedule')
        data = self.prepareScheduleData()        
        
        data['time'] = str(int(time.time())*1000)
        data['method'] = self.type+'.setSchedules'
        data["targetDevice"] =  self.deviceInfo['deviceId']
        data["token"]= self.deviceInfo['token']
        self.yolinkMQTTclient.publish_data(data)
        time.sleep(1)

    
    def activateSchedules(self, index, Activate):
        logging.debug(self.type + 'activateSchedules')
        for schedule  in self.scheduleList:
            if schedule['index'] == index:        
                self.scheduleList[index]['isValid'] = Activate
                return(True)
        else:
            return(False)

    def addSchedule(self, schedule):
        logging.debug(self.type + 'addSchedule')
        tmp = schedule
        if 'week' and ('on' or 'off') and 'isValid' in schedule:    
            indexList = []
            for sch in self.scheduleList:
                indexList.append(sch['index'])
            index = 0
            while index in indexList and index <self.maxSchedules:
                index = index+ 1
            if index < self.maxSchedules:
                tmp['index'] = index
                self.scheduleList.append(tmp)
            return(index)
        return(-1)
            
    def deleteSchedule(self, index):
        logging.debug(self.type + 'addSchedule')       
        sch = 0 
       
        while sch < len(self.scheduleList):
            if self.scheduleList[sch]['index'] == index:
                self.scheduleList.pop(sch)
                return(True)
            else:
                sch = sch + 1
        return(False)

    
    def resetSchedules(self):
        logging.debug(self.type + 'resetSchedules')
        self.scheduleList = {}


    '''
    def transferSchedules(yolink):
        logging.debug(self.type + 'transferSchedules - does not seem to work yet')
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
    '''

    '''
 
    def refreshFWversion(yolink):
        logging.debug(self.type+' - refreshFWversion - Not supported yet')
        #return(self.refreshDevice('Manipulator.getVersion', self.updateStatus))

   '''


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
    '''
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
    '''

    def updateStatusData  (self, data):
        logging.debug(self.type + 'updateStatusData')
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
                  
                    if 'delays'in data[self.dData]:
                        self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dDelays]
                        self.nbrPorts = len( self.dataAPI[self.dData][self.dDelays])
                    else:
                        self.nbrPorts = 1
                    self.dataAPI['nbrPorts'] = self.nbrPorts     
                    self.dataAPI[self.dData][self.dState] = data[self.dData][self.dState][0:self.nbrPorts]
                else:
                    for key in data[self.dData]:
                        if key == 'delay':
                             self.dataAPI[self.dData][self.dDelays] = data[self.dData][key]
                        else:
                             self.dataAPI[self.dData][self.dState][key] = data[self.dData][key]
            else:
                pass # no data and state         
        else: #event
            if type(data[self.dData][self.dState]) is dict:
                for key in data[self.dData][self.dState]:
                    if key == 'delay':
                            self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dState][self.dDelays]
                    else:
                        self.dataAPI[self.dData][self.dState][key] = data[self.dData][self.dState][key]
            elif  type(data[self.dData][self.dState]) == list:           
                if 'delays'in data[self.dData]:
                    self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dDelays]
                else:
                    self.dataAPI[self.dData][self.dDelays] = None
                self.dataAPI[self.dData][self.dState] = data[self.dData][self.dState][0:self.nbrPorts]
            else:
                for key in data[self.dData]:
                    self.dataAPI[self.dData][self.dState][key] = data[self.dData][key]
        self.updateLoraInfo(data)
        self.updateMessageInfo(data)
    
    def updateScheduleStatus(self, data):
        logging.debug(self.type + 'updateScheduleStatus')
        self.setOnline(data)
        self.setNbrPorts(data)
        self.updateLoraInfo(data)
        self.dataAPI[self.dData][self.dSchedule] = data[self.dData]
        self.dataAPI[self.lastMessage] = data

    def updateDelayStatus(self, data):
        logging.debug(self.type + 'updateDelayStatus')
        self.setOnline(data)
        self.setNbrPorts(data)
        self.updateLoraInfo(data)
        if 'delays'in data[self.dData]:
            self.dataAPI[self.dData][self.dDelays] = data[self.dData][self.dDelays]
 
        self.updateMessageInfo(data)


    def updateFWStatus(self, data):
        logging.debug(self.type + 'updateFWStatus - not working ??')
        # Need to have it workign forst - not sure what return struture will look lik
        #self.dataAPI['data']['state']['state'].append( data['data'])
        self.dataAPI['state']['lastTime'] = data['time']
        self.dataAPI['lastMessage'] = data      
    
    def eventPending(self):
        return( not self.eventQueue.empty())
    
    def getEvent(self):
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
        logging.debug(self.type +' - getState')
        return(self.dataAPI[self.dData][self.dState][self.dState])

    def getData(self):
        logging.debug(self.type +' - getDAta')
        return(self.dataAPI[self.dData][self.dState])

    def refreshDelays(self):
        logging.debug(str(self.type)+ ' - refreshDelays')
        self.refreshDevice()
        time.sleep(2)
        return(self.getDelays())

    def getDelays(self):
        logging.debug(str(self.type)+ ' - getDelays')
        if self.dDelays in self.dataAPI[self.dData]:
            return(self.dataAPI[self.dData][self.dDelays])
        else:
            return(None)
    
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