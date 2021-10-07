import hashlib
import json
import os
import sys
import time

import paho.mqtt.client as mqtt
#from logger import getLogger
#log = getLogger(__name__)
from queue import Queue
from yolink_devices import YoLinkDevice
from yolink_mqtt_client import YoLinkMQTTClient
"""
Object representation for YoLink MQTT Client
"""
class YoLinkMQTTDevice(YoLinkDevice):

    def __init__(self, csName, csid, csseckey, yolink_URL, mqtt_URL, mqtt_port, serial_num):
        super().__init__( yolink_URL, csid, csseckey, serial_num)
        self.uniqueID = serial_num[0:10]
        self.clientId = str(csName+'_'+ self.uniqueID )     
        #YoLinkMQTTClient.__init__(self,  csid, csseckey, mqtt_URL, mqtt_port, self.clientId )
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

        #self.device_hash = device_hash
        self.dataQueue = Queue()
        self.client = mqtt.Client(self.clientId,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_disconnect = self.on_disconnect

        #print(client_id)
        #self.client.tls_set()

      
    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        print("Connecting to broker...")

        #print(hashlib.md5(self.csseckey.encode('utf-8')).hexdigest())
        self.client.username_pw_set(username=self.csid, password=hashlib.md5(self.csseckey.encode('utf-8')).hexdigest())

        self.client.connect(self.mqtt_url, self.mqtt_port, 30)
        #time.sleep(5)
        print ('connect:')
        self.client.loop_start()
        #
        #self.client.loop_forever()
        #print('loop started')
        time.sleep(1)
        #self.client.loop_stop()

    def on_message(self, client, userdata, msg):
        """
        Callback for broker published events
        """
        print('on_message')
        print(client)
        print(userdata)
        print(msg)
        print(msg.topic, msg.payload)


        payload = json.loads(msg.payload.decode("utf-8"))
        print(payload)
        test = self.dataQueue.put(payload)
        print (test)
        res = self.dataQueue.get(payload)
        print (res)
        test = self.dataQueue.put(payload)
        print (test)    
        #print('data Queue' )
        #print(self.dataQueue)

        #event = payload['event']
        #deviceId = payload['deviceId']
        #state = payload['data']['state']

        #print("Event:{0} Device:{1} State:{2}".format(event, self.device_hash[deviceId].get_name(), state))
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for connection to broker
        """
        print("Connected with result code %s" % rc)
        print( client,  userdata, flags)

        if (rc == 0):
            print("Successfully connected to broker %s" % self.mqtt_url)

        else:
            print("Connection with result code %s" % rc);
            sys.exit(2)
        time.sleep(1)
        print('Subsribe: ' + self.topicResp + ', '+self.topicReport+', '+ self.topicReportAll )
        test1 = self.client.subscribe(self.topicResp)
        print(test1)
        test2 = self.client.subscribe(self.topicReport)
        print(test2)
        test3 = self.client.subscribe(self.topicReportAll)
        print(test3)

    def on_disconnect(self, client, userdata,rc=0):
        print('Disconnect - stop loop')
        self.client.loop_stop()

    def on_subscribe(self, client, userdata, mID, granted_QOS):
        print()
        print('on_subscribe called')
        print('client = ' + str(client))
        print('userdata = ' + str(userdata))
        print('mID = '+str(mID))
        print('Granted QoS: ' +  str(granted_QOS))
        print('\n')

    def on_publish(self, client, userdata, mID):
        print('on_publish')
        print('client = ' + str(client))
        print('userdata = ' + str(userdata))
        print('mID = '+str(mID))
        print('\n')


    def publish_data(self, data):
        #topic1 = csName + '/1/request'
        print('Publish: '+ self.topicReq + ' ' + data)
        test = self.client.publish(self.topicReq, data)
        print(test)
        
    def shurt_down(self):
        self.client.loop_stop()

    def request_data(self):
        while not self.dataQueue.empty():
            print('QUEUE data: \n')
            print( self.dataQueue.get())

    