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
class YoLinkMQTTClientV2(object):

    def __init__(yolink, UaID, houseID, mqtt_url, mqtt_port, deviceId, callback ):
        yolink.callback = callback
        yolink.UaID = UaID
        yolink.houseID = houseID
        yolink.uniqueID = deviceId
        #yolink.uniqueID = str(csName+'_'+ yolink.uniqueID )    
        yolink.topicReq = houseID+'/'+ yolink.uniqueID +'/request'
        yolink.topicResp = houseID+'/'+ yolink.uniqueID +'/response'
        yolink.topicReport = houseID+'/'+ yolink.uniqueID +'/report'
        yolink.topicReportAll = houseID+'/report'

        yolink.mqtt_port = int(mqtt_port)
        #yolink.topic = topic
        yolink.mqtt_url = mqtt_url
      
        #yolink.device_hash = device_hash
        yolink.deviceId = deviceId
        try:
            print('initialize MQTT' )
            yolink.client = mqtt.Client(yolink.uniqueID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            yolink.client.on_connect = yolink.on_connect
            yolink.client.on_message = yolink.on_message
            yolink.client.on_subscribe = yolink.on_subscribe
            yolink.client.on_disconnect = yolink.on_disconnect
            print('finish subscribing ')
        except Exception as E:
            logging.error('Exception  - -init-: ' + str(E))
        yolink.messagePending = False
        logging.debug(yolink.deviceId)
        #yolink.client.tls_set()

    
    def connect_to_broker(yolink):
        """
        Connect to MQTT broker
        """
        try: 
            logging.info("Connecting to broker...")
            yolink.client.username_pw_set(username=yolink.UaID, password=None)
            yolink.client.connect(yolink.mqtt_url, yolink.mqtt_port, 30)
            #time.sleep(3)
            logging.debug ('connect:')
            yolink.client.loop_start()
            #yolink.client.loop_forever()
            #logging.debug('loop started')
            time.sleep(1)
        except Exception as E:
            logging.error('Exception  - connect_to_broker: ' + str(E))


    def on_message(yolink, client, userdata, msg):
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
        if msg.topic == yolink.topicReportAll or msg.topic == yolink.topicReport:
            if payload['deviceId'] == yolink.deviceId :
                #yolink.eventQueue.put(payload['msgid'])
                #yolink.dataQueue.put(payload)
                logging.debug (payload)
                yolink.callback(payload)
                logging.debug(' device reporting')
            else:
                logging.debug ('\n report on differnt device : ' + msg.topic)
                logging.debug (payload)
                logging.debug('\n')
        elif msg.topic == yolink.topicResp:
                #yolink.dataQueue.put(payload)
                logging.debug (payload)
                yolink.callback(payload)
                #print('Device response:')
                #print(payload)
        elif msg.topic == yolink.topicReq:
                logging.debug('publishing request' )
                logging.debug (payload)
                yolink.callback(payload) # is this needed????
                logging.debug('device publishing')
                logging.debug(payload)
        else:
            logging.debug(msg.topic,  yolink.topicReport, yolink.topicReportAll )
        
        if DEBUG:
            f = open('packets.txt', 'a')
            jsonStr  = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(jsonStr)
            f.write('\n\n')
            #json.dump(jsonStr, f)
            f.close()



        #logging.debug("Event:{0} Device:{1} State:{2}".format(event, yolink.device_hash[deviceId].get_name(), state))
   
    def on_connect(yolink, client, userdata, flags, rc):
        """
        Callback for connection to broker
        """
        logging.debug("Connected with result code %s" % rc)
        #logging.debug( client,  userdata, flags)
        try:

            if (rc == 0):
                logging.debug("Successfully connected to broker %s" % yolink.mqtt_url)
                test1 = yolink.client.subscribe(yolink.topicResp)
                #logging.debug(test1)
                test2 = yolink.client.subscribe(yolink.topicReport)
                #logging.debug(test2)
                test3 = yolink.client.subscribe(yolink.topicReportAll)
                #logging.debug(test3)

            else:
                logging.debug("Connection with result code %s" % rc);
                sys.exit(2)
            time.sleep(1)
            logging.debug('Subsribe: ' + yolink.topicResp + ', '+yolink.topicReport+', '+ yolink.topicReportAll )

        except Exception as E:
            logging.error('Exception  -  on_connect: ' + str(E))       
    
    def on_disconnect(yolink, client, userdata,rc=0):
        logging.debug('Disconnect - stop loop')
        yolink.client.loop_stop()

    def on_subscribe(yolink, client, userdata, mID, granted_QOS):
        logging.debug('on_subscribe')
        #logging.debug('on_subscribe called')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('Granted QoS: ' +  str(granted_QOS))
        #logging.debug('\n')

    def on_publish(yolink, client, userdata, mID):
        logging.debug('on_publish')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('\n')

    def publish_data(yolink, data):
        logging.debug('publish_data: ')
        logging.debug(data)
        try:
            dataTemp = str(json.dumps(data))
            result = yolink.client.publish(yolink.topicReq, dataTemp)
            if result.rc == 0:
                time.sleep(2) 
        except Exception as E:
            logging.error('Exception  - publish_data: ' + str(E))


    def shut_down(yolink):
        yolink.client.loop_stop()
    