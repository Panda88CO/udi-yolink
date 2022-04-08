#!/usr/bin/env python3


import requests
import time
import json
import os
from threading import Lock
from  datetime import datetime
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

countdownTimerUpdateInterval_G = 10
#from yolink_mqtt_clientV3 import YoLinkMQTTClient
import paho.mqtt.client as mqtt
DEBUG = True


class YoLinkInitPAC(object):
    def __init__(yoAccess, uaID, secID, tokenURL='https://api.yosmart.com/open/yolink/token', pacURL = 'https://api.yosmart.com/open/yolink/v2/api' , mqttURL= 'api.yosmart.com', mqttPort = 8003):
       
        yoAccess.lock = Lock()
        yoAccess.tokenURL = tokenURL
        yoAccess.apiv2URL = pacURL
        yoAccess.mqttURL = mqttURL
        yoAccess.mqttPort = mqttPort
        yoAccess.uaID = uaID
        yoAccess.secID = secID
        yoAccess.apiType = 'UAC'
        yoAccess.tokenExpTime = 0
        yoAccess.timeExpMarging = 3600 # 1 hour - most devices report once per hour
        #yoAccess.timeExpMarging = 7170 #min for testing 

        yoAccess.lastDataPacket = {}
        yoAccess.mqttList = {}


        yoAccess.token = None
        while not yoAccess.request_new_token( ):
            time.sleep(60)
            logging.info('Waiting to acquire access token')
        logging.info('Retrieving YoLink API info')
        yoAccess.retrieve_device_list()
        yoAccess.retrieve_homeID()

        yoAccess.retryNbr = 0
        yoAccess.disconnect = False

        logging.info('Connecting to YoLink MQTT server')

        #if yoAccess.client == None:    
        try:
            logging.debug('initialize MQTT' )
            yoAccess.client = mqtt.Client(yoAccess.homeID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            yoAccess.client.on_connect = yoAccess.on_connect
            yoAccess.client.on_message = yoAccess.on_message
            yoAccess.client.on_subscribe = yoAccess.on_subscribe
            yoAccess.client.on_disconnect = yoAccess.on_disconnect
            yoAccess.client.on_publish = yoAccess.on_publish
            #logging.debug('finish subscribing ')
            yoAccess.connect_to_broker()
        except Exception as E:
            logging.error('Exception - init- MQTT: {}'.format(E))

        yoAccess.messagePending = False


    def request_new_token(yoAccess):
        try:
            now = int(time.time())
            response = requests.post( yoAccess.tokenURL,
                    data={"grant_type": "client_credentials",
                        "client_id" : yoAccess.uaID,
                        "client_secret" : yoAccess.secID },
                )
            
            temp = response.json()
            yoAccess.token = temp
            yoAccess.token['expirationTime'] = int(yoAccess.token['expires_in'] + now )
            return(True)

        except Exception as e:
            logging.debug('Exeption occcured during request_new_token : {}'.format(e))
            return(False)

    def refresh_token(yoAccess):
        try:
            logging.info('Refershing Token ')
            now = int(time.time())
            response = requests.post( yoAccess.tokenURL,
                data={"grant_type": "refresh_token",
                    "client_id" :  yoAccess.uaID,
                    "refresh_token":yoAccess.token['refresh_token'],
                    }
            )
            temp =  response.json()
            yoAccess.token = temp
            yoAccess.token['expirationTime'] = int(yoAccess.token['expires_in'] + now )
            return(True)

        except Exception as e:
            logging.debug('Exeption occcured during refresh_token : {}'.format(e))
            return(yoAccess.request_new_token())

    def get_access_token(yoAccess):
        yoAccess.lock.acquire()
        now = int(time.time())
        if yoAccess.token == None:
            yoAccess.request_new_token()
        #if now > yoAccess.token['expirationTime']  - yoAccess.timeExpMarging :
        #    if now > yoAccess.token['expirationTime']: #we loast the token
        #        yoAccess.request_new_token()
        #    else:
        #        yoAccess.refresh_token()
        yoAccess.lock.release()
        #return(yoAccess.token['access_token'])
                
    def is_token_expired (yoAccess, accessToken):
        return(accessToken == yoAccess.token['access_token'])
        

    def retrieve_device_list(yoAccess):
        try:
            data= {}
            data['method'] = 'Home.getDeviceList'
            data['time'] = str(int(time.time()*1000))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ yoAccess.token['access_token']
            r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
            info = r.json()
            #logging.debug(str(info))
            yoAccess.deviceList = info['data']['devices']
        except Exception as e:
            logging.error('Exception  -  retrieve_device_list : {}'.format(e))             


    def retrieve_homeID(yoAccess):
        try:
            data= {}
            data['method'] = 'Home.getGeneralInfo'
            data['time'] = str(int(time.time()*1000))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ yoAccess.token['access_token']

            r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
            homeId = r.json()
            #logging.debug(homeId)
            yoAccess.homeID = homeId['data']['id']

        except Exception as e:
            logging.error('Exception  - retrieve_homeID: {}'.format(e))            

    def getDeviceList (yoAccess):
        return(yoAccess.deviceList)


    def shut_down(yoAccess):
        yoAccess.client.loop_stop()

    ########################################
    # MQTT stuff
    ########################################

    def connect_to_broker(yoAccess):
        """
        Connect to MQTT broker
        """
        yoAccess.get_access_token()
        yoAccess.client.loop_stop()
        yoAccess.client.disconnect()
        try: 
            logging.info("Connecting to broker...")
            yoAccess.client.username_pw_set(username=yoAccess.token['access_token'], password=None)
            #time.sleep(1)
            yoAccess.client.connect(yoAccess.mqttURL, yoAccess.mqttPort, keepalive= 16000) #devices report every 4 hours or earlier
            #time.sleep(3)
            yoAccess.client.loop_start()
            #time.sleep(1)
        except Exception as e:
            logging.error('Exception  - connect_to_broker: {}'.format(e))

    def subscribe_mqtt(yoAccess, deviceId, callback):
        logging.info('Subscribing deviceId {} to MQTT'.format(deviceId))
        topicReq = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/request'
        topicResp = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/response'
        topicReport = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/report'
        #topicReportAll = 'yl-home/'+yoAccess.homeID+'/+/report'
        
        if not deviceId in yoAccess.mqttList :
            yoAccess.client.subscribe(topicReq)
            yoAccess.client.subscribe(topicResp)
            yoAccess.client.subscribe(topicReport)

            yoAccess.mqttList[deviceId] = { 'callback': callback, 
                                            'request': topicReq,
                                            'response': topicResp,
                                            'report': topicReport,
                                            'subscribed': True
                                            }
            #logging.debug('subscribe_mqtt: {}'.format(yoAccess.mqttList))
            time.sleep(2)



    def on_message(yoAccess, client, userdata, msg):
        """
        Callback for broker published events
        """
        #logging.debug('on_message')
        #logging.debug(client)
        #logging.debug(userdata)
        #logging.debug(msg)
        logging.debug('on message in topic {}, payload{}: '.format(msg.topic, msg.payload))
        
        payload = json.loads(msg.payload.decode("utf-8"))
        deviceId = 'unknown'
        #try:
        if 'targetDevice' in payload:
            deviceId = payload['targetDevice']
        elif 'deviceId' in payload:
            deviceId = payload['deviceId']
        else:
            logging.debug('Unknow device in payload : {}'.format(payload))
            return(False)
        if DEBUG:
            dataTemp = str(json.dumps(payload))
        logging.debug('on_message for {}: {} {}'.format(deviceId, msg.topic, payload))

        if deviceId in yoAccess.mqttList:
            tempCallback = yoAccess.mqttList[deviceId]['callback']
            if  msg.topic == yoAccess.mqttList[deviceId]['report']:                    
                tempCallback(payload)
                if DEBUG:
                    yoAccess.savePacket(msg.topic, dataTemp, 'EVENT')
            elif msg.topic == yoAccess.mqttList[deviceId]['response']:

                    if payload['code'] == '000000':
                       tempCallback(payload)
                    else:
                        logging.error('NON 000000 code {}: {}'.format(payload['desc'], payload))
                        tempCallback(payload)
                        #time.sleep(2)
                        #yoAccess.publish_data(yoAccess.lastDataPacket[deviceId])
                    if DEBUG:
                        yoAccess.savePacket(msg.topic, dataTemp, 'RESP')
            elif msg.topic == yoAccess.mqttList[deviceId]['request']:

                    if DEBUG:
                        yoAccess.savePacket(msg.topic, dataTemp, 'REQ')
            else:
                logging.error('Topic not mathing:' + msg.topic + '  ' + str(json.dumps(payload)))
        else:
            logging.error('Unsupported device: {}'.format(deviceId))
        #except Exception as e:
        #    logging.error('Exception - on_message for {} {}: {}'.format(deviceId, payload, e))
        #    logging.error ('Error data: {}'.format(payload))
   
    def on_connect(yoAccess, client, userdata, flags, rc):
        """
        Callback for connection to broker
        """
        logging.debug("Connected with result code %s" % rc)
        #logging.debug( client,  userdata, flags)
        try:

            if (rc == 0):
                logging.info(" Successfully connected to broker {} ".format(yoAccess.mqttURL))
            else:
                logging.debug("Broker connection failed with result code {}".format(rc))
                os.exit(2)
            time.sleep(1)
            #logging.debug('Subsribe: ' + yoAccess.topicResp + ', '+yoAccess.topicReport+', '+ yoAccess.topicReportAll )

        except Exception as E:
            logging.error('Exception  -  on_connect: ' + str(E))       


    def on_disconnect(yoAccess, client, userdata,rc=0):
        logging.debug('Disconnect - stop loop')
        if yoAccess.disconnect:
            logging.debug('Disconnect - stop loop')
            yoAccess.client.loop_stop()
        else:
            logging.debug('Unintentional disconnect - Reacquiring connection')
            try:
                
                #yoAccess.accessToken = yoAccess.yoAccess.get_access_token() 
                yoAccess.client.loop_stop()
                yoAccess.client.disconnect()
                #time.sleep(1)
                while not yoAccess.request_new_token():
                    time.sleep(60)
                    logging.info('Trying to acquire new token')
                #time.sleep(1)
                #yoAccess.accessToken = yoAccess.get_access_token()
                yoAccess.connect_to_broker()
                for deviceId in yoAccess.mqttList:
                    yoAccess.client.subscribe(yoAccess.mqttList[deviceId]['request'])
                    yoAccess.client.subscribe(yoAccess.mqttList[deviceId]['response'])
                    yoAccess.client.subscribe(yoAccess.mqttList[deviceId]['report'])
            except Exception as e:
                logging.error('Exeption occcured during on_ disconnect : {}'.format(e))
                if yoAccess:
                   yoAccess.request_new_token()
                else:
                    logging.error('Lost credential info - need to restart node server')

    def on_subscribe(yoAccess, client, userdata, mID, granted_QOS):
        logging.debug('on_subscribe')
        #logging.debug('on_subscribe called')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('Granted QoS: ' +  str(granted_QOS))
        #logging.debug('\n')

    def on_publish(yoAccess, client, userdata, mID):
        logging.debug('on_publish')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('\n')

    def publish_data(yoAccess, data):
        max_retries = 3
        #logging.debug('publish_data: {}'.format(data))
        #yoAccess.lastDataPacket = data
        #token = yoAccess.get_access_token()
        #logging.debug ('publish data - tokens identical  : {}'.format(yoAccess.accessToken == token))
        #if yoAccess.accessToken == token:
        try:
            
            #yoAccess.lastDataPacket = data
            dataStr = str(json.dumps(data))
            deviceId = data['targetDevice']
            #dataTempStr = str(dataTemp)
            yoAccess.lastDataPacket[deviceId] = data
            logging.debug( 'publish_data: {} - {}'.format(yoAccess.mqttList[deviceId]['request'], dataStr))
            logging.debug('mqtt list : {}'.format(yoAccess.mqttList))
            if deviceId in yoAccess.mqttList:
                logging.debug( 'publish_data: {} - {}'.format(yoAccess.mqttList[deviceId]['request'], dataStr))
                result = yoAccess.client.publish(yoAccess.mqttList[deviceId]['request'], dataStr)
            else:
                logging.error('device {} not in mqtt list'.format(deviceId))
            logging.debug('publish result: {}'.format(result.rc))
            if result.rc != 0:
                attempts = 0 
                if result.rc == 4: #try to renew token
                    yoAccess.get_access_token() 
                    yoAccess.client.loop_stop()
                    yoAccess.client.disconnect()
                    yoAccess.connect_to_broker()
                while attempts < max_retries and result.rc != 0:
                    time.sleep(1)
                    result = yoAccess.client.publish(yoAccess.mqttList[deviceId]['request'], dataStr)
                    if result.rc != 0:
                        attempts = attempts + 1
                        logging.info('Device {} not fonund - retrying '.format(deviceId))
                        

        except Exception as e:
            logging.error('Exception  - publish_data: {}'.format(e))
        '''
        else: # token was renewed - we need to reconnect to the broker
            logging.info('access token renewed')
            yoAccess.accessToken = token 
            yoAccess.client.loop_stop()
            yoAccess.client.disconnect()
            yoAccess.connect_to_broker()
            try:
                dataTemp = str(json.dumps(data))
                deviceId = dataTemp['data']['targetDevice']
                if deviceId in yoAccess.mqttList:
                    result = yoAccess.client.publish(yoAccess.mqttList[deviceId]['request'], dataTemp)
                    #result = yoAccess.client.publish(yoAccess.topicReq, dataTemp)
                else:
                    logging.debug('Device not subscribed: {}'.format(dataTemp))
                if result.rc == 0:
                    time.sleep(2) 
            except Exception as E:
                logging.error('Exception  - publish_data: ' + str(E))
        '''


    def savePacket(yoAccess, msg, data, fileType):
        yoAccess.lock.acquire()
        if fileType == 'REQ':
            f = open('TXpackets.txt', 'a')
        elif fileType == 'RESP':
            f = open('RXpackets.txt', 'a')
        elif fileType == 'EVENT':  
            f = open('EVENTpackets.txt', 'a')
        else:
            f = open('MISCpackets.txt', 'a')
        #jsonStr  = json.dumps(dataTemp, sort_keys=True, indent=4, separators=(',', ': '))
        f.write('{} - {}\n'.format( datetime.datatime.now(), msg))
        f.write(data)
        f.write('\n\n')
        #json.dump(jsonStr, f)
        f.close()
        yoAccess.lock.release()








class YoLinkInitCSID(object):
    def __init__(yoAccess,  csName, csid, csSeckey, yoAccess_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003 ):
        yoAccess.csName = csName
        yoAccess.csid = csid
        yoAccess.cssSeckey = csSeckey
        yoAccess.apiType = 'CSID'