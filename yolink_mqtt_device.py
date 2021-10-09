import hashlib
import json
import os
import sys
import time

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
                            ,'schedule':{'lastTime':startTime}
                            ,'delays':{'lastTime':startTime}
                            ,'status':{'lastTime':startTime} 
                            }
        self.connect_to_broker()
        dataOK = self.refreshOutletState() # needed to get number of ports on device
        dataOK = self.refreshOutletSchedule()
        self.daysOfWeek = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']

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
                     if int(data['time']) > int(self.multiOutlet['schedule']['lastTime']):
                         for scheduleNbr in data['data']:
                             for index in data['data'][scheduleNbr]:
                                if index not in  self.multiOutlet['schedule']:
                                    self.multiOutlet['schedule'][scheduleNbr] = {}
                                if index == 'isValid':
                                     self.multiOutlet['schedule'][scheduleNbr]['Enabled']= data['data'][scheduleNbr][index]
                                elif index == 'ch':
                                     self.multiOutlet['schedule'][scheduleNbr]['port']= data['data'][scheduleNbr][index]
                                elif index == 'week':
                                    temp = []
                                    if 'days' not in self.multiOutlet['schedule'][scheduleNbr]:
                                        self.multiOutlet['schedule'][scheduleNbr]['days'] = []
                                    for i in range(0,6):
                                        mask = pow(2,i)
                                        if (data['data'][scheduleNbr][index]  & mask) != 0 :
                                             self.multiOutlet['schedule'][scheduleNbr]['days'].append(self.daysOfWeek[i])
                                elif index == 'index':
                                    continue # do nothing
                                else:    
                                    self.multiOutlet['schedule'][scheduleNbr][index]= data['data'][scheduleNbr][index]

                
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

    def refreshOutletState(self):
        logging.debug('getOutletState')
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

    def setOutletState(self, portList, value):
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
            messagetime = rxdata['time']
        while self.eventMessagePending():
            eventData = self.getEventData()
            self.updateStatus(eventData)
        return(dataOK)

    
    def refreshOutletSchedule(self):
        print('getOutletSchedule')
        data={}
        data['method'] = 'MultiOutlet.getSchedules'
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

    def setOutletSchedule(self):
        print('setOutletSchedule')

    def setOutletDelay(self):
        print('setOutletDelay')

    def getOutletVersion(self):
        print('getOutletVersion')

    def startUpgrade(self):
        print('startUpgrade')

    def checkStatusChanges(self):
        print('checkStatusChanges')

