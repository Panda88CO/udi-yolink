import hashlib
import json
import os
import sys
import time

import logging
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
        self.mqtt_port = int(mqtt_port)
        self.targetId = self.get_id()

   
        self.dataQueue = Queue()
        self.eventQueue = Queue()
        self.data= {}
        #self.eventData = {}
        self.client = mqtt.Client(self.clientId,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_disconnect = self.on_disconnect

        self.messagePending = False


      
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
                self.eventQueue.put(payload['msgid'])
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
        '''
        
        if payload['deviceId'] == self.targetId:
            self.dataQueue.put(payload)

        logging.debug(payload)
        test = self.dataQueue.put(payload)
        logging.debug (test)
        res = self.dataQueue.get(payload)
        logging.debug (res)
        test = self.dataQueue.put(payload)
        logging.debug (test)    
        #logging.debug('data Queue' )
        #logging.debug(self.dataQueue)

        #event = payload['event']
        #deviceId = payload['deviceId']
        #state = payload['data']['state']
        '''
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


    def publish_data(self, data):
        #topic1 = csName + '/1/request'
        #logging.debug('Publish: '+ self.topicReq + ' ' + data)
        data["targetDevice"] =  self.get_id()
        data["token"]= self.get_token()
        dataTemp = str(json.dumps(data))


        test = self.client.publish(self.topicReq, dataTemp)
        logging.debug(test)
        
    def shurt_down(self):
        self.client.loop_stop()

    def getData(self, messageId):
        expirationTime = time.time()*1000-60*60*1000 # 1 hour in milisec
        while not self.dataQueue.empty():
            temp = (self.dataQueue.get())
            msgId = temp['msgid']
            self.data[msgId] = temp
        for id in self.data: # remove too old data
            if expirationTime > int(msgId):
                del self.data[id]
        if messageId in self.data:
            temp = self.data[messageId]
            del self.data[messageId]
            dataOK = (temp['code'] == '000000')
            return(dataOK, temp)
        else:
            return(None)
    
    def eventMessagePending(self):
        logging.debug('getEventData')
        return(not self.eventQueue.empty())

    def getEventMsgId(self):
        logging.debug('getEventMsgId')
        temp = (self.eventQueue.get())
        return(temp)

    