import hashlib
import json
import os
import sys
import time

import paho.mqtt.client as mqtt
#from logger import getLogger
#log = getLogger(__name__)

"""
Object representation for YoLink MQTT Client
"""
class YoLinkMQTTClient(object):

    def __init__(self, csid, csseckey, topic, mqtt_url, mqtt_port, device_hash, client_id=os.getpid()):
        self.csid = csid
        self.csseckey = csseckey
        self.topic = topic
        self.mqtt_url = mqtt_url
        self.mqtt_port = int(mqtt_port)
        self.device_hash = device_hash

        self.client = mqtt.Client(client_id=str('Panda88_' + str(client_id)),  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe

        print(client_id)
        #self.client.tls_set()

    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        print("Connecting to broker...")

        #print(hashlib.md5(self.csseckey.encode('utf-8')).hexdigest())
        self.client.username_pw_set(username=self.csid, password=hashlib.md5(self.csseckey.encode('utf-8')).hexdigest())

        self.client.connect(self.mqtt_url, self.mqtt_port, 10)
        #time.sleep(5)
        print ('connect:')
        self.client.loop_start()
        #
        # self.client.loop_forever()
        print('loop started')


        time.sleep(1)
        #self.client.loop_stop()

    def on_message(self, client, userdata, msg):
        """
        Callback for broker published events
        """
        print('on_message')
        print(msg)
        print(msg.topic, msg.payload)

        payload = json.loads(msg.payload.decode("utf-8"))
        print(payload)
    
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
        print('Subsribe: '  + self.topic)
        test = self.client.subscribe(self.topic)
        print(self.topic+ ' = ' +str(test))


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


    def publish_data(self, topic, data):
        #topic1 = csName + '/1/request'
        print('Publish: '+ topic + ' ' + data)
        test = self.client.publish(topic, data)
        print(test)
        
    def shurt_down(self):
        self.client.loop_stop()

    def subscribe_data(self, topic):
        print('Subscribe: ' + topic)
        test = self.client.subscribe(topic)
        print(topic +' = ' + str(test))