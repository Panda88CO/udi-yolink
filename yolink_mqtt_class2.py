
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
 

        self.yolinkMQTTclient = YoLinkMQTTClient(csName, csid, csseckey, mqtt_URL, mqtt_port,  self.deviceId , callback )

        self.yolink_URL = yolink_URL
        self.mqtt_url = mqtt_URL

        self.daysOfWeek = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        
        self.lastUpdate = 'lastTime'
        self.lastMessage = 'lastMessage'
        self.dOnline = 'online'
        self.dData = 'data'
        self.dState= 'state'
        self.dSchedule = 'schedules'
        self.dDelays = 'delays' #may not be needed
        self.messageTime = 'time'
        self.forceStop = False
        
        self.dataAPI = {
                        'lastTime':str(int(time.time()*1000))
                        ,'lastMessage':{}
                        ,'online':None
                        ,'data':{ 'state':{} }
                        }
   
        #self.dataQueue = Queue()
        self.eventQueue = Queue()
        self.mutex = threading.Lock()
        self.timezoneOffsetSec = self.timezoneOffsetSec()
        self.yolinkMQTTclient.connect_to_broker()
        #self.loopTimeSec = updateTimeSec
    
        #self.updateInterval = 3
        self.messagePending = False

   
    def refreshDevice(self, methodStr, callback):
        logging.debug(methodStr)  
        data = {}
        data['time'] = str(int(time.time())*1000)
        data['method'] = methodStr
        data["targetDevice"] =  self.deviceInfo['deviceId']
        data["token"]= self.deviceInfo['token']
        self.yolinkMQTTclient.publish_data(data)
        #self.updateData(callback)
      
            
    def setDevice(self, methodStr, data, callback):
        data['time'] = str(int(time.time())*1000)
        data['method'] = methodStr
        data["targetDevice"] =  self.deviceInfo['deviceId']
        data["token"]= self.deviceInfo['token']
        self.yolinkMQTTclient.publish_data( data)
        #self.updateData(callback)

    def getValue(self, data, key):
        attempts = 1
        while key not in data and attempts <3:
            time.sleep(1)
            attempts = attempts + 1
        if key in data:
            return(data[key])
        else:
            return('NA')

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
        for i in range(0,6):
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
        self.dataAPI[self.dData][self.dState]['loraInfo']= data[self.dData]['loraInfo']

    def updateMessageInfo(self, data):
        self.dataAPI[self.lastUpdate] = data[self.messageTime]
        self.dataAPI[self.lastMessage] = data

    def updateMultiIOStatusData (self, data):
        self.setOnline(data)
        self.setNbrPorts(data)
        self.updateLoraInfo(data)
        if 'method' in data:
            for key in range(0, self.nbrPorts):
                self.dataAPI[self.dData][self.dState][key] = data[self.dData][self.dState][key]
                if 'delays'in data[self.dData]:
                    self.dataAPI[self.dData][self.dDelays]=[]
                    test = data[self.dData][self.dDelays][key]
                    self.dataAPI[self.dData][self.dDelays][key] = test
        else: #event
            for key in range(0, self.nbrPorts):
                    self.dataAPI[self.dData][self.dState][key] = data[self.dData][self.dState][key]
        self.updateMessageInfo(data)



        
    def updateStatusData  (self, data):
        if 'online' in data[self.dData]:
            self.dataAPI[self.dOnline] = data[self.dData][self.dOnline]
        else:
            self.dataAPI[self.dOnline] = True
        if 'method' in data:
            
            for key in data[self.dData][self.dState]:
                self.dataAPI[self.dData][self.dState][key] = data[self.dData][self.dState][key]
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
        self.updateMessageInfo(data)

    def updateDelayStatus(self, data):
        self.setOnline(data)
        self.setNbrPorts(data)
        self.updateLoraInfo(data)

        for key in range(0, self.nbrPorts):
            self.dataAPI[self.dData][self.dDelays]=[]
            if 'delays'in data[self.dData]:
                self.dataAPI[self.dData][self.dDelays][key] = data[self.dData][self.dDelays][key]
 
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

    def getState(self):
        return(self.dataAPI[self.dData][self.dState]['state'])
        
    def getInfoValue(self, key):
        if key in self.dataAPI[self.dData][self.dState]:
            return(self.dataAPI[self.dData][self.dState][key])
        else:
            return(None)

    def sensorOnline(self):
        return(self.dataAPI['online'] )       

    def getLastUpdate (self):
        return(self.dataAPI[self.lastUpdate])
    
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