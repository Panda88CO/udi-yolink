import hashlib
import json
import sys
import time
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

import paho.mqtt.client as mqtt
#from logger import getLogger
#log = getLogger(__name__)
DEBUG = True
"""
Object representation for YoLink MQTT Client
"""
class YoLinkMQTTClient(object):

    def __init__(self, csName, csid, csseckey, mqtt_url, mqtt_port, deviceId, callback ):
        self.callback = callback
        self.csid = csid
        self.csseckey = csseckey
        self.uniqueID = deviceId
        self.uniqueID = str(csName+'_'+ self.uniqueID )    
        self.topicReq = csName+'/'+ self.uniqueID +'/request'
        self.topicResp = csName+'/'+ self.uniqueID +'/response'
        self.topicReport = csName+'/'+ self.uniqueID +'/report'
        self.topicReportAll = csName+'/report'

        self.mqtt_port = int(mqtt_port)

        self.csid = csid
        self.csseckey = csseckey
        #self.topic = topic
        self.mqtt_url = mqtt_url
      
        #self.device_hash = device_hash
        self.deviceId = deviceId
        try:
            print('initialize MQTT' )
            self.client = mqtt.Client(self.uniqueID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
            self.client.on_disconnect = self.on_disconnect
            print('finish subscribing ')
        except Exception as E:
            logging.error('Exception  - -init-: ' + str(E))
        self.messagePending = False
        logging.debug(self.deviceId)
        #self.client.tls_set()

    
    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        try: 
            logging.info("Connecting to broker...")
            self.client.username_pw_set(username=self.csid, password=hashlib.md5(self.csseckey.encode('utf-8')).hexdigest())
            self.client.connect(self.mqtt_url, self.mqtt_port, 30)
            #time.sleep(3)
            logging.debug ('connect:')
            self.client.loop_start()
            #self.client.loop_forever()
            #logging.debug('loop started')
            time.sleep(1)
        except Exception as E:
            logging.error('Exception  - connect_to_broker: ' + str(E))


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
        logging.debug('on_message')
        logging.debug(payload)
        if msg.topic == self.topicReportAll or msg.topic == self.topicReport:
            if payload['deviceId'] == self.deviceId :
                #self.eventQueue.put(payload['msgid'])
                #self.dataQueue.put(payload)
                logging.debug (payload)
                self.callback(payload)
                logging.debug(' device reporting')
            else:
                logging.debug ('\n report on differnt device : ' + msg.topic)
                logging.debug (payload)
                logging.debug('\n')
        elif msg.topic == self.topicResp:
                #self.dataQueue.put(payload)
                logging.debug (payload)
                self.callback(payload)
                #print('Device response:')
                #print(payload)
        elif msg.topic == self.topicReq:
                logging.debug('publishing request' )
                logging.debug (payload)
                self.callback(payload) # is this needed????
                logging.debug('device publishing')
                logging.debug(payload)
        else:
            logging.debug(msg.topic,  self.topicReport, self.topicReportAll )
        
        if DEBUG:
            f = open('packets.txt', 'a')
            jsonStr  = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(jsonStr)
            f.write('\n\n')
            #json.dump(jsonStr, f)
            f.close()



        #logging.debug("Event:{0} Device:{1} State:{2}".format(event, self.device_hash[deviceId].get_name(), state))
   
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for connection to broker
        """
        logging.debug("Connected with result code %s" % rc)
        #logging.debug( client,  userdata, flags)
        try:

            if (rc == 0):
                logging.debug("Successfully connected to broker %s" % self.mqtt_url)
                test1 = self.client.subscribe(self.topicResp)
                #logging.debug(test1)
                test2 = self.client.subscribe(self.topicReport)
                #logging.debug(test2)
                test3 = self.client.subscribe(self.topicReportAll)
                #logging.debug(test3)

            else:
                logging.debug("Connection with result code %s" % rc);
                sys.exit(2)
            time.sleep(1)
            logging.debug('Subsribe: ' + self.topicResp + ', '+self.topicReport+', '+ self.topicReportAll )

        except Exception as E:
            logging.error('Exception  -  on_connect: ' + str(E))       
    
    def on_disconnect(self, client, userdata,rc=0):
        logging.debug('Disconnect - stop loop')
        self.client.loop_stop()

    def on_subscribe(self, client, userdata, mID, granted_QOS):
        logging.debug('on_subscribe')
        #logging.debug('on_subscribe called')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('Granted QoS: ' +  str(granted_QOS))
        #logging.debug('\n')

    def on_publish(self, client, userdata, mID):
        logging.debug('on_publish')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('\n')

    def publish_data(self, data):
        logging.debug('publish_data: ')
        logging.debug(data)
        try:
            dataTemp = str(json.dumps(data))
            result = self.client.publish(self.topicReq, dataTemp)
            if result.rc == 0:
                time.sleep(2) 
        except Exception as E:
            logging.error('Exception  - publish_data: ' + str(E))


    def shut_down(self):
        self.client.loop_stop()
    