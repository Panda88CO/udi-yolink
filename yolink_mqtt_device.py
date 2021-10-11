import hashlib
import json
import os
import sys
import time
import threading
import paho.mqtt.client as mqtt
import logging

from queue import Queue
from yolink_mqtt_class import YoLinkMQTTDevice
logging.basicConfig(level=logging.DEBUG)

#from yolink_mqtt_client import YoLinkMQTTClient
"""
Object representation for YoLink MQTT device
"""
class YoLinkMultiOutlet(YoLinkMQTTDevice):

    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        startTime = str(int(time.time()*1000))
        self.multiOutlet = {
                             'nbrPorts': -1
                            ,'state':{'lastTime':startTime}
                            ,'schedules':{'lastTime':startTime}
                            ,'delays':{'lastTime':startTime}
                            ,'status':{'lastTime':startTime} 
                            }
        self.daysOfWeek = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        self.delayList = []
        self.scheduleList = []

        self.connect_to_broker()
        dataOK = self.refreshMultiOutletState() # needed to get number of ports on device
        dataOK = self.refreshMultiOutletSchedule()
     
    def getMultiOutLetState (self):
        return(self.multiOutlet['state'])

    def getMultiOutLetSchedules (self):
        return(self.multiOutlet['schedules'])  

    def getMultiOutLetDelays (self):
        return(self.multiOutlet['delays'])  

    def getMultiOutLetStatus (self):
        return(self.multiOutlet['status'])

    def getgetMultiOutLetAll(self):  
        return(self.multiOutlet)

    def updateStatus(self, data):
        logging.debug('updateStatus')
        if 'method' in  data:
            logging.debug('method')
            if data['code'] == '000000':
                if  data['method'] == 'MultiOutlet.getState':
                    #logging.debug('getState')
                    self.multiOutlet['nbrPorts'] = len(data['data']['delays'])
                    if int(data['time']) > int(self.multiOutlet['state']['lastTime']):
                        for active in range(self.multiOutlet['nbrPorts']):
                            activePort = data['data']['delays'][active]['ch']
                            onDelay = data['data']['delays'][active]['on']
                            offDelay = data['data']['delays'][active]['off']
                            if not activePort in self.multiOutlet['delays']:
                                self.multiOutlet['delays'][activePort] = {}
                            self.multiOutlet['delays'][activePort]['ON DELAY'] = onDelay
                            self.multiOutlet['delays'][activePort]['OFF DELAY'] = offDelay
                        self.multiOutlet['delays']['lastTime'] = str(data['time'])

                        self.multiOutlet['status']['timeZone'] = data['data']['tz']
                        self.multiOutlet['status']['FWvers'] = data['data']['version']
                        self.multiOutlet['status']['signaldB'] = data['data']['loraInfo']['signal']
                        self.multiOutlet['status']['lastTime'] = str(data['time'])
                if ( data['method'] == 'MultiOutlet.setState' or  data['method'] == 'MultiOutlet.getState'):
                    if int(data['time']) > int(self.multiOutlet['state']['lastTime']):
                        for port in range(self.multiOutlet['nbrPorts']):
                            if data['data']['state'][port] == 'open':
                                self.multiOutlet['state'][port] = 'ON'
                            elif data['data']['state'][port] == 'closed':
                                self.multiOutlet['state'][port] = 'OFF'
                            else:
                                self.multiOutlet['state'][port] = 'UNKNOWN'
                        self.multiOutlet['state']['lastTime'] = data['time']
                if  data['method'] == 'MultiOutlet.getSchedules':
                    if int(data['time']) > int(self.multiOutlet['schedules']['lastTime']):
                        for scheduleNbr in data['data']:
                             for item in data['data'][scheduleNbr]:
                                if scheduleNbr not in  self.multiOutlet['schedules']:
                                    self.multiOutlet['schedules'][scheduleNbr] = {}
                                if item == 'isValid':
                                     self.multiOutlet['schedules'][scheduleNbr]['Enabled']= data['data'][scheduleNbr][item]
                                elif item == 'ch':
                                     self.multiOutlet['schedules'][scheduleNbr]['port']= data['data'][scheduleNbr][item]
                                elif item == 'week':
                                    temp = []
                                    if 'days' not in self.multiOutlet['schedules'][scheduleNbr]:
                                        self.multiOutlet['schedules'][scheduleNbr]['days'] = []
                                    for i in range(0,6):
                                        mask = pow(2,i)
                                        if (data['data'][scheduleNbr][item]  & mask) != 0 :
                                             self.multiOutlet['schedules'][scheduleNbr]['days'].append(self.daysOfWeek[i])
                                elif item == 'index':
                                    continue # do nothing
                                else:    
                                    self.multiOutlet['schedules'][scheduleNbr][item]= data['data'][scheduleNbr][item]
                        self.multiOutlet['schedules']['lastTime'] = data['time']
                if  data['method'] == 'MultiOutlet.getVersion':
                    if int(data['time']) > int(self.multiOutlet['status']['lastTime']):
                        
                        #for item in data['data']:


                        self.multiOutlet['status']['version'] = data['version']                             
                        self.multiOutlet['status']['lastTime'] = data['time']
            else:
                #data['method'] == 'MultiOutlet.getState' and data['code'] == '000000':
                logging.debug('Not supported yet' )

        elif 'event' in data:
            logging.debug('StatusChange')
            if data['event'] == 'MultiOutlet.StatusChange':
                if int(data['time']) > int(self.multiOutlet['state']['lastTime']):
                    for port in range(len(data['data']['state'])):
                        if data['data']['state'][port] == 'open':
                            self.multiOutlet['state'][port] = 'ON'
                        elif data['data']['state'][port] == 'closed':
                            self.multiOutlet['state'][port] = 'OFF'
                        else:
                            self.multiOutlet['state'][port] = 'UNKNOWN'
                    self.multiOutlet['state']['lastTime'] = data['time']
        else:
            logging.error('unsupported data')

    def refreshMultiOutletState(self):
        logging.debug('refreshMultiOutletState')
        data={}
        data['method'] = 'MultiOutlet.getState'
        data['time'] = str(int(time.time())*1000)
        self.publish_data(data)
        time.sleep(2)
        rxdata = self.getData(data["time"])
        dataOK = False

        if 'code' in  rxdata:
            if rxdata['code'] == '000000':
                dataOK = True
            self.updateStatus(rxdata) 
        return(dataOK)

    def setMultiOutletState(self, portList, value):
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
        data["method"] = 'MultiOutlet.setState'
        data["time"] = str(int(time.time())*1000)
        data["params"] = {}
        data["params"]["chs"] =  port
        data["params"]['state'] = state

        self.publish_data(data)
        time.sleep(2)
        dataOK, rxdata = self.getData(data['time'])
        if dataOK:
            self.updateStatus(rxdata)
            #messagetime = rxdata['time']
        while self.eventMessagePending():
            msgId= self.getEventMsgId()
            dataOK,  rxdata = self.getData(msgId)
            if dataOK:
                self.updateStatus(rxdata)
        return(dataOK)
   
    def refreshMultiOutletSchedule(self):
        logging.debug('getMultiOutletSchedule')
        data={}
        data['method'] = 'MultiOutlet.getSchedules'
        data['time'] = str(int(time.time())*1000)
        self.publish_data(data)
        time.sleep(2)
       
        dataOK,  rxdata = self.getData(data["time"])
        if dataOK:
            self.updateStatus(rxdata)
        while self.eventMessagePending():
            msgId= self.getEventMsgId()
            dataOK,  rxdata = self.getData(msgId)
            if dataOK:
                self.updateStatus(rxdata)
        return(dataOK)

    def setMultiOutletSchedule(self, scheduleList):
        logging.debug('setMultiOutletSchedule - not currently supported')
        data={}
        data["method"] = 'MultiOutlet.setSchedules'
        data["time"] = str(int(time.time())*1000)
        data["params"] = {}
        #data["params"]["chs"] =  port
        #data["params"]['state'] = state

        self.publish_data(data)
        time.sleep(2)
        dataOK, rxdata = self.getData(data['time'])
        if dataOK:
            self.updateStatus(rxdata)
            #messagetime = rxdata['time']
        while self.eventMessagePending():
            msgId= self.getEventMsgId()
            dataOK,  rxdata = self.getData(msgId)
            if dataOK:
                self.updateStatus(rxdata)
        return(dataOK)

    def resetDelayList (self):
        self.delayList = []

    def appedMultiOutletDelay(self, delay):
        nbrDelays = len(self.delayList)
        self

    def setMultiOutletDelay(self, delayList):
        logging.debug('setMultiOutletDelay - not currently supported')
        data={}
        data["method"] = 'MultiOutlet.setDelay'
        data["time"] = str(int(time.time())*1000)
        data["params"] = []
        nbrDelays = len(delayList)
        data["params"]["delays"] = {}
        if nbrDelays > 0:
            for delayNbr in delayList:
                data["params"]["delays"][delayNbr]={}
                data["params"]["delays"][delayNbr]['ch'] = delayList[delayNbr]['port']
                data["params"]['delays'][delayNbr]['on'] = delayList[delayNbr]['OnDelay']
                data["params"]['delays'][delayNbr]['off'] = delayList[delayNbr]['OffDelay']
        self.publish_data(data)
        time.sleep(2)
        dataOK, rxdata = self.getData(data['time'])
        if dataOK:
            self.updateStatus(rxdata)
            #messagetime = rxdata['time']
        while self.eventMessagePending():
            msgId= self.getEventMsgId()
            dataOK,  rxdata = self.getData(msgId)
            if dataOK:
                self.updateStatus(rxdata)
        return(dataOK)

    def refreshMultiOutletVersion(self):
        logging.debug('getMultiOutletVersion - not currently supported ')
        data={}
        data['method'] = 'MultiOutlet.getVersion'
        data['time'] = str(int(time.time())*1000)
        self.publish_data(data)
        time.sleep(2)
       
        dataOK,  rxdata = self.getData(data["time"])
        if dataOK:
            self.updateStatus(rxdata)
        while self.eventMessagePending():
            eventData = self.getEventData()
            self.updateStatus(eventData)
        return(dataOK)


    def startUpgrade(self):
        logging.debug('startUpgrade - not currently supported')
    '''
    def checkStatusChanges(self):
        logging.debug('checkStatusChanges')
    '''


class YoLinkTHsensor(YoLinkMQTTDevice):

    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num):
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        startTime = str(int(time.time()*1000))
        self.THSensor = {'lastTime':startTime}
        
        self.connect_to_broker()
        MonitorT = threading.Thread(target = self.eventMonitorThread)
        self.mutex = threading.Lock()
        self.forceStop = False

    def eventMonitorThread (self, updateInterval = 3):
        time.sleep(5)
        while not self.forceStop:
            while self.eventMessagePending():
                msgId= self.getEventMsgId()
                dataOK,  rxdata = self.getData(msgId)
                if dataOK:
                    self.mutex.acquire()
                    self.updateStatus(rxdata)
                    self.mutex.release()
        time.sleep(updateInterval)    


    def refreshTHsensor(self):
        logging.debug('refreshTHsensor')
        data={}
        data['method'] = 'THSensor.getState'
        data['time'] = str(int(time.time())*1000)
        self.publish_data(data)
        time.sleep(2)
        rxdata = self.getData(data["time"])
        if rxdata[0]:
             # data structure seems to indicate more than 1 sensor but even only returns 1 and no way to identify origen
            self.mutex.acquire()
            self.updateStatus(rxdata[1])
            self.mutex.release()
        return(rxdata[0])

    def updateStatus(self, data):
        logging.debug('updateStatus')  
        if 'method' in  data:
            if  (data['method'] == 'THSensor.getState' and  data['code'] == '000000'):
                if int(data['time']) > int(self.THSensor['lastTime']):
                    self.THSensor['online'] = data['data']['online']
                        
                    self.THSensor['tempC'] = data['data']['state']['temperature']
                    self.THSensor['tempCorrectionC'] = data['data']['state']['tempCorrection']
                    self.THSensor['tempLimitMinC'] = data['data']['state']['tempLimit']['min']
                    self.THSensor['tempLimitMaxC'] = data['data']['state']['tempLimit']['max']

                    self.THSensor['humidity'] = data['data']['state']['humidity']
                    self.THSensor['humidityCorrection'] = data['data']['state']['humidityCorrection']
                    self.THSensor['humidityLimitMin'] = data['data']['state']['humidityLimit']['min']
                    self.THSensor['humidityLimitMax'] = data['data']['state']['humidityLimit']['max']

                    self.THSensor['alertInterval'] = data['data']['state']['interval']
                    self.THSensor['battery'] = data['data']['state']['battery']
                    self.THSensor['state'] = data['data']['state']['state']
                    self.THSensor['FWvers'] = data['data']['state']['version']
                    
                    self.THSensor['alamrs'] = {}
                    self.THSensor['alamrs']['battery'] =  data['data']['state']['alarm']['lowBattery']
                    self.THSensor['alamrs']['lowTemp'] =  data['data']['state']['alarm']['lowTemp']
                    self.THSensor['alamrs']['highTemp'] =  data['data']['state']['alarm']['highTemp']
                    self.THSensor['alamrs']['lowHumidity'] =  data['data']['state']['alarm']['lowHumidity']
                    self.THSensor['alamrs']['highHumidity'] =  data['data']['state']['alarm']['highHumidity']
                    self.THSensor['lastTime'] = str(data['time'])
        elif 'event' in data:
            if int(data['time']) > int(self.THSensor['lastTime']):
                self.THSensor['online'] = True
                    
                self.THSensor['tempC'] = data['data']['temperature']
                self.THSensor['tempCorrectionC'] = data['data']['temperatureCorrection']
                self.THSensor['tempLimitMinC'] = data['data']['tempLimit']['min']
                self.THSensor['tempLimitMaxC'] = data['data']['tempLimit']['max']

                self.THSensor['humidity'] = data['data']['humidity']
                self.THSensor['humidityCorrection'] = data['data']['humidityCorrection']
                self.THSensor['humidityLimitMin'] = data['data']['humidityLimit']['min']
                self.THSensor['humidityLimitMax'] = data['data']['humidityLimit']['max']

                self.THSensor['alertInterval'] = data['data']['interval']
                self.THSensor['battery'] = data['data']['battery']
                self.THSensor['state'] = data['data']['state']
                self.THSensor['FWvers'] = data['data']['version']
                
                self.THSensor['alamrs'] = {}
                self.THSensor['alamrs']['battery'] =  data['data']['alarm']['lowBattery']
                self.THSensor['alamrs']['lowTemp'] =  data['data']['alarm']['lowTemp']
                self.THSensor['alamrs']['highTemp'] =  data['data']['alarm']['highTemp']
                self.THSensor['alamrs']['lowHumidity'] =  data['data']['alarm']['lowHumidity']
                self.THSensor['alamrs']['highHumidity'] =  data['data']['alarm']['highHumidity']

                self.THSensor['signaldB'] =  data['data']['loraInfo']['signal']           
                self.THSensor['lastTime'] = str(data['time'])    
        else:
            logging.error('unsupported data')

    '''
    def checkStatusChanges(self):
        logging.debug('checkStatusChanges')
        return(self.eventMessagePending())
    '''