import hashlib
import json
import os
import sys
import time
import threading
import paho.mqtt.client as mqtt
import logging
import datetime
import pytz

from queue import Queue
from yolink_mqtt_class1 import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

#from yolink_mqtt_client import YoLinkMQTTClient
"""
Object representation for YoLink MQTT device
"""
class YoLinkMultiOutlet(YoLinkMQTTDevice):

    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec = 3):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        startTime = str(int(time.time()*1000))
        self.dataAPI = {
                        'lastTime':startTime
                        ,'lastMessage':{}
                        ,'nbrPorts': -1
                        ,'data':{   'state':{}
                                    ,'schedules': {}
                                }

                        }


       
        self.delayList = []
        self.scheduleList = []

        self.connect_to_broker()
        self.loopTimeSec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimeSec  )
        time.sleep(2)

        self.refreshMultiOutput() # needed to get number of ports on device
        self.refreshSchedules()
        self.refreshFWversion()


    def getStateValue (self):
        temp = self.dataAPI['data']['state']['state']
        temp = temp[0:self.dataAPI['nbrPorts']]
        for port in range(len(temp)):
            if temp[port] == 'closed':
                temp[port] = 'OFF'
            elif temp[port] == 'open':
                temp[port] = 'ON'
            else:
                temp[port] = '??'
                
        return(temp)

    def getSchedules (self):
        return(self.dataAPI['data']['schedules'])  

    def getDelays (self):
        return(self.dataAPI['data']['state']['delays'])  


    '''
    def getInfoAPI(self):  
        return(self.dataAPI)
    '''
    def updateStatus(self, data):
        if 'method' in  data:
            if  (data['method'] == 'MultiOutlet.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):

                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delays'])

                    self.dataAPI['data']['state'] = data['data']
            elif  (data['method'] == 'MultiOutlet.setState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['data']['state']['state'] = data['data']['state']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
                   
            elif  (data['method'] == 'MultiOutlet.setDelay' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    self.dataAPI['data']['state']['delays']=data['data']['delays']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']

            elif  (data['method'] == 'MultiOutlet.getSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):  
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['data']['schedules'] = data['data']
            elif  (data['method'] == 'MultiOutlet.setSchedules' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):  
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['data']['schedules'] = data['data']

            elif  (data['method'] == 'MultiOutlet.getVersion' and  data['code'] == '000000'):
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    # Need to have it workign forst - not sure what return struture will look lik
                    #self.dataAPI['data']['state']['state'].append( data['data'])
                    self.dataAPI['state']['lastTime'] = data['time']
                    self.dataAPI['lastMessage'] = data
            else:
                logging.debug('Unsupported Method passed' + str(json(data)))
        elif 'event' in data:
            if data['event'] == 'MultiOutlet.StatusChange':
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['data']['state']['state'] = data['data']['state']
                    self.dataAPI['data']['state']['loraInfo']= data['data']['loraInfo']
            elif data['event'] == 'MultiOutlet.Report':
                if int(data['time']) > int(self.dataAPI['lastTime']):
                    self.dataAPI['lastMessage'] = data
                    self.dataAPI['lastTime'] = data['time']
                    self.dataAPI['nbrPorts'] = len(data['data']['delays'])
                    self.dataAPI['data']['state'] = data['data']
                    
            else :
                logging.debug('Unsupported Event passed' + str(json(data)))
                                        

    def refreshMultiOutput(self):
        return(self.refreshDevice('MultiOutlet.getState', self.updateStatus))


    def setState(self, portList, value):
        logging.debug('setMultiOutletState')
        # portlist a a listof ports being changed port range 0-7
        # vaue is state that need to change 2 (ON/OFF)
        port = 0
        for i in portList:
            port = port + pow(2, i)
        if value.upper() == 'ON':
            state = 'open'
        elif value.upper() == 'OFF':
            state = 'closed'
        else:
            logging.error('Unknows state passed')
        data={}
        data["params"] = {}
        data["params"]["chs"] =  port
        data["params"]['state'] = state

        return(self.setDevice( 'MultiOutlet.setState', data, self.updateStatus))


    def refreshSchedules(self):
        return(self.refreshDevice('MultiOutlet.getSchedules', self.updateStatus))
 
    
    def resetScheduleList(self):
        self.scheduleList = []

    def setSchedule(self, scheduleList):
        logging.debug('setMultiOutletSchedule - not currently supported')
       
        data = {}
        data["params"] = {}
        data["params"]["chs"] =  scheduleList
        #data["params"]['state'] = state
        return(self.setDevice('MultiOutlet.setSchedules', data, self.updateStatus))


    def resetDelayList (self):
        self.delayList = []

    def appedDelay(self, delay):
        nbrDelays = len(self.delayList)
        self

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


