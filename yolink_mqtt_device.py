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
        self.connect_to_broker()
        self.multiOutlet = { 'lastTime':int(time.time*1000)
                            ,'state':{}
                            ,'schedule':{}
                            ,'delays':{}
                            ,'status':{} 
                            }

        data = self.getOutletState()
        data = self.getOutletSchedule()
     

    def updateStatus(self, data):
        logging.debug('updateStatus')
        if 'method' in  data:
            logging.debug('method')
            if ( data['method'] == 'MultiOutlet.setState' or  data['method'] == 'MultiOutlet.getState') and data['code'] == '000000':
                for port in range(len(data['data']['state'])):
                    if data['data']['state'][port] == 'open':
                        self.multiOutlet['state'][port] = 'ON'
                    elif data['data']['state'][port] == 'closed':
                        self.multiOutlet['state'][port] = 'OFF'
                    else:
                        self.multiOutlet['state'][port] = 'UNKNOWN'

            else:
                #data['method'] == 'MultiOutlet.getState' and data['code'] == '000000':
                logging.debug('Not supported yet' )

        elif 'event' in data:
            logging.debug('StatusChange')
            if data['event'] == 'MultiOutlet.StatusChange':
                for port in range(len(data['data']['state'])):
                    if data['data']['state'][port] == 'open':
                        self.multiOutlet['state'][port] = 'ON'
                    elif data['data']['state'][port] == 'closed':
                        self.multiOutlet['state'][port] = 'OFF'
                    else:
                        self.multiOutlet['state'][port] = 'UNKNOWN'

        else:
            logging.error('unsupported data')

    def getOutletState(self):
        logging.debug('getOutletState')
        data={}
        data["method"] = 'MultiOutlet.getState'
        data["time"] = str(int(time.time())*1000)
        self.publish_data(data)
        time.sleep(2)
        rxdata = self.request_data()
        messagetime = 0
        dataOK = False
        for result in range(len(rxdata)):
            if 'code' in  rxdata[result]:
                print(rxdata[result]['code'] == '000000' ,  rxdata[result]['method'] == data['method'])
                if rxdata[result]['code'] == '000000' and rxdata[result]['method'] == data['method']:
                    dataOK = True
            if int(rxdata[result]['time']) > messagetime:
                self.updateStatus(rxdata[result]) 
                messagetime = rxdata[result]['time']

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
        rxdata = self.request_data()
        dataOK = False
        messagetime = 0
        for result in range(len(rxdata)):
            if 'code' in  rxdata[result]:
                if rxdata[result]['code'] == '000000' and  rxdata[result]['msgid']== data['time'] and rxdata[result]['method'] == data['method']:
                    dataOK = True
            if int(rxdata[result]['time']) > messagetime:
                self.updateStatus(rxdata[result])
                messagetime = rxdata[result]['time']

        return(dataOK)

    
    def getOutletSchedule(self):
        print('getOutletSchedule')
    
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