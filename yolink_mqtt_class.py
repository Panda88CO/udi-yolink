import hashlib
import json
import os
import sys
import time
import threading
import logging
from  datetime import datetime
from dateutil.tz import *



logging.basicConfig(level=logging.DEBUG)

import paho.mqtt.client as mqtt
#from logger import getLogger
#log = getLogger(__name__)
from queue import Queue
from yolink_devices import YoLinkDevice
#from yolink_mqtt_device import YoLinkMQTTClient
"""
Object representation for YoLink MQTT Client
"""
class YoLinkMQTTDevice(YoLinkDevice):
    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num):
        super().__init__( yolink_URL, csid, csseckey, serial_num)
        self.uniqueID = serial_num[0:10]
        self.clientId = str(csName+'_'+ self.uniqueID )     
        self.build_device_api_request_data()
        self.enable_device_api()
        self.csid = csid
        self.csseckey = csseckey
        self.topicReq = csName+'/'+ self.uniqueID +'/request'
        self.topicResp = csName+'/'+ self.uniqueID +'/response'
        self.topicReport = csName+'/'+ self.uniqueID +'/report'
        self.topicReportAll = csName+'/report'
        self.yolink_URL = yolink_URL
        self.mqtt_url = mqtt_URL
        self.daysOfWeek = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        self.mqtt_port = int(mqtt_port)
        self.targetId = self.get_id()



        self.forceStop = False

   
        self.dataQueue = Queue()
        self.eventQueue = Queue()
        self.mutex = threading.Lock()
        self.timezoneOffsetSec = self.timezoneOffsetSec()
       
       
        self.client = mqtt.Client(self.clientId,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_disconnect = self.on_disconnect
        self.updateInterval = 3
        self.messagePending = False

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

    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        logging.info("Connecting to broker...")
        self.client.username_pw_set(username=self.csid, password=hashlib.md5(self.csseckey.encode('utf-8')).hexdigest())
        self.client.connect(self.mqtt_url, self.mqtt_port, 30)
        logging.debug ('connect:')
        self.client.loop_start()
        #self.client.loop_forever()
        #logging.debug('loop started')
        time.sleep(1)
     
    def on_message(self, client, userdata, msg):
        """
        Callback for broker published events
        """
        logging.debug('on_message')
        #logging.debug(client)
        #logging.debug(userdata)
        #logging.debug(msg)
        #logging.debug(msg.topic, msg.payload)
        
        payload = json.loads(msg.payload.decode("utf-8"))
        if msg.topic == self.topicReportAll or msg.topic == self.topicReport:
            if payload['deviceId'] == self.targetId:
                #self.eventQueue.put(payload['msgid'])
                self.dataQueue.put(payload)
            else:
                logging.debug ('\n report on differnt device : ' + msg.topic)
                logging.debug (payload)
                logging.debug('\n')
        elif msg.topic == self.topicResp:
                self.dataQueue.put(payload)
        elif msg.topic == self.topicReq:
                logging.debug('publishing request' )
                logging.debug (payload)
        else:
            logging.debug(msg.topic,  self.topicReport, self.topicReportAll )
        #logging.debug("Event:{0} Device:{1} State:{2}".format(event, self.device_hash[deviceId].get_name(), state))
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for connection to broker
        """
        logging.debug("Connected with result code %s" % rc)
        #logging.debug( client,  userdata, flags)

        if (rc == 0):
            logging.debug("Successfully connected to broker %s" % self.mqtt_url)

        else:
            logging.debug("Connection with result code %s" % rc);
            sys.exit(2)
        time.sleep(1)
        logging.debug('Subsribe: ' + self.topicResp + ', '+self.topicReport+', '+ self.topicReportAll )
        test1 = self.client.subscribe(self.topicResp)
        #logging.debug(test1)
        test2 = self.client.subscribe(self.topicReport)
        #logging.debug(test2)
        test3 = self.client.subscribe(self.topicReportAll)
        #logging.debug(test3)

    def on_disconnect(self, client, userdata,rc=0):
        logging.debug('Disconnect - stop loop')
        self.client.loop_stop()

    def on_subscribe(self, client, userdata, mID, granted_QOS):
        logging.debug('on_subscribe')
        logging.debug('on_subscribe called')
        logging.debug('client = ' + str(client))
        logging.debug('userdata = ' + str(userdata))
        logging.debug('mID = '+str(mID))
        logging.debug('Granted QoS: ' +  str(granted_QOS))
        logging.debug('\n')

    def on_publish(self, client, userdata, mID):
        logging.debug('on_publish')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        logging.debug('mID = '+str(mID))
        #logging.debug('\n')


    def publish_data(self, data, callback):
        logging.debug('publish_data: ' + data['method'])
        dataTemp = str(json.dumps(data))
        test = self.client.publish(self.topicReq, dataTemp)
        if test.rc == 0:
            time.sleep(2)
            self.updateData(callback)
        
                
    def shurt_down(self):
        self.client.loop_stop()

    def getData(self):
        #expirationTime = int(time.time()*1000-60*60*1000) # 1 hour in milisec
        if not(self.dataQueue.empty()):
            temp = self.dataQueue.get()
            if 'event' in temp:
                dataOK = True
            if 'method' in temp:
                dataOK = temp['code'] == '000000'
            return(dataOK, temp)
        else:
            return(False, None)
    
    def eventMessagePending(self):
        logging.debug('getEventData')
        return(not self.eventQueue.empty())

    def getEventMsgId(self):
        logging.debug('getEventMsgId')
        temp = (self.eventQueue.get())
        return(temp)

    def monitorLoop(self, callback, updateInterval):
        Monitor = threading.Thread(target = self.eventMonitorThread, args = (callback, updateInterval ))
        Monitor.start()
        

    def eventMonitorThread (self, callback, updateInterval):
        time.sleep(5)
        while not self.forceStop:
            time.sleep(updateInterval) 
            while not self.dataQueue.empty():
                self.updateData(callback)
                logging.debug('eventMonitorThread GET DATA')  
            
            logging.debug('eventMonitorThread')  

    def updateData(self, callback):
        self.mutex.acquire()
        dataOK,  rxdata = self.getData()
        if dataOK:
            callback(rxdata)
        self.mutex.release()

    def refreshDevice(self, methodStr, callback):
        logging.debug(methodStr)  
        data = {}

        data['time'] = str(int(time.time())*1000)
        data['method'] = methodStr
        data["targetDevice"] =  self.get_id()
        data["token"]= self.get_token()
        self.publish_data(data, callback)
      
            
    def setDevice(self, methodStr, data, callback):
        
        data['time'] = str(int(time.time())*1000)
        data['method'] = methodStr
        data["targetDevice"] =  self.get_id()
        data["token"]= self.get_token()
        self.publish_data(  data, callback)

    def getValue(self, data, key):
        attempts = 1
        while key not in data and attempts <3:
            time.sleep(1)
            attempts = attempts + 1
        if key in data:
            return(data[key])
        else:
            return('NA')