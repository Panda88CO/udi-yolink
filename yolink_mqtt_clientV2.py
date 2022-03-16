#import hashlib
import json
#import sys
import time
import datetime
import os
from threading import Lock
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
    
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

import paho.mqtt.client as mqtt

DEBUG = False
"""
Object representation for YoLink MQTT Client
"""
class YoLinkMQTTClient(object):

    def __init__(yolink, yoAccess,  deviceInfo, callback ):
        yolink.lock = Lock()
        yolink.callback = callback
        yolink.yoAccess = yoAccess
        yolink.deviceInfo = deviceInfo
        yolink.homeID = yoAccess.homeID
        yolink.deviceId = deviceInfo['deviceId']
        yolink.uniqueID = yolink.deviceId#+str(int(time.time()))
        yolink.accessToken = yoAccess.get_access_token()
 
        yolink.topicReq = 'yl-home/'+yolink.homeID+'/'+ yolink.uniqueID +'/request'
        yolink.topicResp = 'yl-home/'+yolink.homeID+'/'+ yolink.uniqueID +'/response'
        yolink.topicReport = 'yl-home/'+yolink.homeID+'/'+ yolink.uniqueID +'/report'
        yolink.topicReportAll = 'yl-home/'+yolink.homeID+'/+/report'

        yolink.mqttPort = int(yoAccess.mqttPort)
        yolink.mqttURL = yoAccess.mqttURL
        yolink.retryNbr = 0
        yolink.disconnect = False
        #yolink.lastDataPacket = {}
  
        try:
            logging.debug('initialize MQTT' )
            yolink.client = mqtt.Client(yolink.uniqueID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            yolink.client.on_connect = yolink.on_connect
            yolink.client.on_message = yolink.on_message
            yolink.client.on_subscribe = yolink.on_subscribe
            yolink.client.on_disconnect = yolink.on_disconnect
            logging.debug('finish subscribing ')
        except Exception as E:
            logging.error('Exception  - -init-: ' + str(E))
        yolink.messagePending = False
        #logging.debug(yolink.deviceId)
        #yolink.client.tls_set()

    
    def connect_to_broker(yolink):
        """
        Connect to MQTT broker
        """
        yolink.accessToken  = yolink.yoAccess.get_access_token()
        yolink.client.loop_stop()
        yolink.client.disconnect()
        try: 
            logging.info("Connecting to broker...")

            yolink.client.username_pw_set(username=yolink.accessToken, password=None)
            time.sleep(1)
            yolink.client.connect(yolink.mqttURL, yolink.mqttPort, 30)
            #time.sleep(3)

            yolink.client.loop_start()
            time.sleep(1)
        except Exception as E:
            logging.error('Exception  - connect_to_broker: ' + str(E))


    def on_message(yolink, client, userdata, msg):
        """
        Callback for broker published events
        """
        maxRetry = 2
        #logging.debug('on_message')
        #logging.debug(client)
        #logging.debug(userdata)
        #logging.debug(msg)
        #logging.debug(msg.topic, msg.payload)
        
        payload = json.loads(msg.payload.decode("utf-8"))
        if DEBUG:
            dataTemp = str(json.dumps(payload))
        logging.debug('on_message: {}\n {}'.format(msg.topic, payload))


        if  msg.topic == yolink.topicReport:
            if payload['deviceId'] == yolink.deviceId :
                yolink.callback(payload)

            if DEBUG:
                yolink.savePacket(msg.topic, dataTemp, 'EVENT')
        elif msg.topic == yolink.topicResp:

                if payload['code'] == '000000':
                    yolink.retryNbr = 0
                    yolink.callback(payload)
                else:
                    yolink.retryNbr += 1
                    if yolink.retryNbr <= maxRetry:
                        yolink.callback(payload)
                        time.sleep(2)
                        yolink.publish_data(yolink.lastDataPacket)
                    else:
                        yolink.retryNbr = 0
                        yolink.callback(payload)
                if DEBUG:
                    yolink.savePacket(msg.topic, dataTemp, 'RESP')
        elif msg.topic == yolink.topicReq:

                if DEBUG:
                    yolink.savePacket(msg.topic, dataTemp, 'REQ')
        else:
            logging.error('Topic not mathing:' + msg.topic + '  ' + str(json.dumps(payload)))

        
   
    def on_connect(yolink, client, userdata, flags, rc):
        """
        Callback for connection to broker
        """
        logging.debug("Connected with result code %s" % rc)
        #logging.debug( client,  userdata, flags)
        try:

            if (rc == 0):
                logging.debug("{} - Successfully connected to broker {} ".format(yolink.deviceInfo['name'], yolink.mqttURL))
                yolink.client.subscribe(yolink.topicResp)
                yolink.client.subscribe(yolink.topicReq)
                yolink.client.subscribe(yolink.topicReport)
                #yolink.client.subscribe(yolink.topicReportAll)

                #yolink.client.subscribe('yl-home/'+yolink.homeID+'/+/report')
            else:
                logging.debug("Connection with result code {}".format(rc))
                os.exit(2)
            time.sleep(1)
            #logging.debug('Subsribe: ' + yolink.topicResp + ', '+yolink.topicReport+', '+ yolink.topicReportAll )

        except Exception as E:
            logging.error('Exception  -  on_connect: ' + str(E))       
    
    def on_disconnect(yolink, client, userdata,rc=0):
        logging.debug('Disconnect - stop loop')
        if yolink.disconnect:
            logging.debug('Disconnect - stop loop')
            yolink.client.loop_stop()
        else:
            try:
                logging.debug('Unintentional disconnect - Reacquiring connection')
                #yolink.accessToken = yolink.yoAccess.get_access_token() 
                yolink.client.loop_stop()
                yolink.client.disconnect()
                time.sleep(1)
                while not yolink.yoAccess.request_new_token():
                    time.sleep(60)
                    logging.info('Trying to acquire new token')
                time.sleep(1)
                yolink.accessToken = yolink.yoAccess.get_access_token()
                yolink.connect_to_broker()
            except Exception as e:
                logging.error('Exeption occcured during on_ disconnect : {}'.format(e))
                if yolink.yoAccess:
                    yolink.yoAccess.request_new_token()
                else:
                    logging.error('Lost credential info - need to restart node server')

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
        max_retries = 3
        #logging.debug('publish_data: {}'.format(data))
        #yolink.lastDataPacket = data
        token = yolink.yoAccess.get_access_token()
        logging.debug ('publish data - tokens : {} {} {}'.format(yolink.accessToken == token,yolink.accessToken, token  ))
        if yolink.accessToken == token:
            try:
                
                yolink.lastDataPacket = data
                dataTemp = str(json.dumps(data))    
                result = yolink.client.publish(yolink.topicReq, dataTemp)

                #logging.debug('publish result: {}'.format(result.rc))
                if result.rc != 0:
                    attempts = 0 
                    if result.rc == 4: #try to renew token
                        yolink.accessToken = yolink.yoAccess.get_access_token() 
                        yolink.client.loop_stop()
                        yolink.client.disconnect()
                        yolink.connect_to_broker()
                    while attempts < max_retries and result.rc != 0:
                        time.sleep(1)
                        result = yolink.client.publish(yolink.topicReq, dataTemp)
                        if result.rc != 0:
                            attempts = attempts + 1
                            logging.info('Device not fonund - retrying ')
                            

            except Exception as e:
                logging.error('Exception  - publish_data: {}'.format(e))

        else: # token was renewed - we need to reconnect to the broker
            logging.info('access token renewed')
            yolink.accessToken = token 
            yolink.client.loop_stop()
            yolink.client.disconnect()
            yolink.connect_to_broker()
            try:
                dataTemp = str(json.dumps(data))
                result = yolink.client.publish(yolink.topicReq, dataTemp)
                if result.rc == 0:
                    time.sleep(2) 
            except Exception as E:
                logging.error('Exception  - publish_data: ' + str(E))
            


    def savePacket(yolink, msg, data, fileType):
        yolink.lock.acquire()
        if fileType == 'REQ':
            f = open('TXpackets.txt', 'a')
        elif fileType == 'RESP':
            f = open('RXpackets.txt', 'a')
        elif fileType == 'EVENT':  
            f = open('EVENTpackets.txt', 'a')
        else:
            f = open('MISCpackets.txt', 'a')
        #jsonStr  = json.dumps(dataTemp, sort_keys=True, indent=4, separators=(',', ': '))
        f.write('{} - {}\n'.format( datetime.datetime.now(), msg))
        f.write(data)
        f.write('\n\n')
        #json.dump(jsonStr, f)
        f.close()
        yolink.lock.release()

    def shut_down(yolink):
        yolink.client.loop_stop()
