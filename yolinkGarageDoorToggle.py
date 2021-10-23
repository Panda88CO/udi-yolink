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



class YoLinkGarageDoorToggle(YoLinkMQTTDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num, updateTimeSec):
        logging.debug('toggleGarageDoorCtrl Init') 
        super().__init__(  csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num)
        self.methodList = ['GarageDoor.toggle' ]
        self.eventList = ['GarageDoor.Report']
        self.ToggleName = 'GarageEvent'
        self.eventTime = 'Time'


        self.connect_to_broker()
        self.loopTimesec = updateTimeSec
        self.monitorLoop(self.updateStatus, self.loopTimesec  )
        time.sleep(2)
        

    def toggleGarageDoorToggle(self):
        logging.debug('toggleGarageDoorCtrl') 
        data={}
        return(self.setDevice( 'GarageDoor.toggle', data, self.updateStatus))

    def updateStatus(self, data):
        logging.debug(' YoLinkGarageDoorCtrl updateStatus')  
        #special case 
        if 'method' in  data:
            if  (data['method'] in self.methodList and  data['code'] == '000000'):
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateGarageCtrlStatus(data)

        elif 'event' in data: # not sure events exits
            if data['event'] in self.eventList:
                if int(data['time']) > int(self.getLastUpdate()):
                    self.updateStatusData(data)
                    eventData = {}
                    eventData[self.ToggleName] = self.getState()
                    eventData[self.eventTime] = self.data[self.messageTime]
                    self.ToggleEventQueue.put(eventData)
        else:
            logging.error('unsupported data: ' + str(json(data)))



