#!/usr/bin/env python3
import requests
import time
import json
import psutil
import sys
import math

from  datetime import datetime
try:
    import udi_interface
    logging = udi_interface.LOGGER
    #logging = getlogger('yolink_init_V2')
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    #root = logging.getLogger()
    #root.setLevel(logging.DEBUG)
    #handler = logging.StreamHandler(sys.stdout)
    #handler.setLevel(logging.DEBUG)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #handler.setFormatter(formatter)
    #root.addHandler(handler)

countdownTimerUpdateInterval_G = 10


import paho.mqtt.client as mqtt
from queue import Queue
from threading import Thread, Event, Lock
DEBUG = False


class YoLinkInitPAC(object):
    def __init__(yoAccess, uaID, secID, tokenURL='https://api.yosmart.com/open/yolink/token', pacURL = 'https://api.yosmart.com/open/yolink/v2/api' , mqttURL= 'api.yosmart.com', mqttPort = 8003):
        yoAccess.disconnect_occured = False 
        yoAccess.tokenLock = Lock()
        yoAccess.fileLock = Lock()
        yoAccess.TimeTableLock = Lock()
        yoAccess.publishQueue = Queue()
        #yoAccess.delayQueue = Queue()
        yoAccess.messageQueue = Queue()
        yoAccess.fileQueue = Queue()
        #yoAccess.timeQueue = Queue()
        yoAccess.MAX_MESSAGES = 100  # number of messages per yoAccess.MAX_TIME
        yoAccess.MAX_TIME = 30      # Time Window
        yoAccess.time_tracking_dict = {} # structure to track time so we do not violate yolink publishing requirements
        yoAccess.debug = False
        #yoAccess.pendingDict = {}
        yoAccess.pending_messages = 0
        yoAccess.time_since_last_message_RX = 0
        yoAccess.tokenURL = tokenURL
        yoAccess.apiv2URL = pacURL
        yoAccess.mqttURL = mqttURL
        yoAccess.mqttPort = mqttPort
        yoAccess.connectedToBroker = False
        yoAccess.loopRunning = False
        yoAccess.uaID = uaID
        yoAccess.secID = secID
        yoAccess.apiType = 'UAC'
        yoAccess.tokenExpTime = 0
        yoAccess.timeExpMarging = 3600 # 1 hour - most devices report once per hour
        yoAccess.lastTransferTime = int(time.time())
        #yoAccess.timeExpMarging = 7170 #min for testing 
        yoAccess.tmpData = {}
        yoAccess.lastDataPacket = {}
        yoAccess.mqttList = {}
        yoAccess.TtsMessages = {}
        yoAccess.nbrTTS = 0
        yoAccess.temp_unit = 0
        yoAccess.online = False
        yoAccess.deviceList = []
        yoAccess.token = None
        
        yoAccess.QoS = 1
        yoAccess.keepAlive = 60


        yoAccess.unassigned_nodes = []
        try:
            #while not yoAccess.request_new_token( ):
            #    time.sleep(60)
            #    logging.info('Waiting to acquire access token')
           
            #yoAccess.retrieve_device_list()
            #yoAccess.retrieve_homeID()

            yoAccess.retryNbr = 0
            yoAccess.disconnect = False
            yoAccess.STOP = Event()

            #yoAccess.messageThread = Thread(target = yoAccess.process_message )
            #yoAccess.publishThread = Thread(target = yoAccess.transfer_data )
            #yoAccess.fileThread =  Thread(target = yoAccess.save_packet_info )
            #yoAccess.connectionMonitorThread = Thread(target = yoAccess.connection_monitor)

            #yoAccess.messageThread.start()
            #yoAccess.publishThread.start()
            #yoAccess.fileThread.start()
            

            logging.info('Connecting to YoLink MQTT server')
            while not yoAccess.request_new_token():
                time.sleep(35) # Wait 35 sec and try again - 35 sec ensures less than 10 attemps in 5min - API restriction
                logging.info('Trying to obtain new Token - Network/YoLink connection may be down')
            logging.info('Retrieving YoLink API info')
            time.sleep(1)
            if yoAccess.token != None:
                yoAccess.retrieve_homeID()
            #if yoAccess.client == None:    
      
            #logging.debug('initialize MQTT' )
            yoAccess.client = mqtt.Client(yoAccess.homeID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            yoAccess.client.on_connect = yoAccess.on_connect
            yoAccess.client.on_message = yoAccess.on_message
            yoAccess.client.on_subscribe = yoAccess.on_subscribe
            yoAccess.client.on_disconnect = yoAccess.on_disconnect
            yoAccess.client.on_publish = yoAccess.on_publish
            #logging.debug('finish subscribing ')

            while not yoAccess.connect_to_broker():
                time.sleep(2)
            
            #yoAccess.connectionMonitorThread.start()
            
            #logging.debug('Connectoin Established: {}'.format(yoAccess.check_connection( yoAccess.mqttPort )))
            
        except Exception as E:
            logging.error('Exception - init- MQTT: {}'.format(E))

        yoAccess.messagePending = False

    #######################################
    #check if connected to YoLink Cloud server
    def measure_time(func):                                                                                                   
                                                                                                                          
        def wrapper(*arg):                                                                                                      
            t = time.time()                                                                                                     
            res = func(*arg)                                                                                                    
            logging.debug ("Function took " + str(time.time()-t) + " seconds to run")                                                    
            return res                                                                                                          
        return wrapper                                                                                                                

    #@measure_time
    def check_connection(yoAccess, port):
        logging.debug( 'check_connection: port {}'.format(port))
        connectons = psutil.net_connections()
        #logging.debug('connections: {}'.format(connectons))
        for netid in connectons:
            raddr = netid.raddr
            if len (raddr) > 0:
                if  port == raddr.port:
                    logging.debug('found : {} {}'.format(raddr.port, netid.status ))
                    return(netid)
        else:

            return(None)


    #####################################
    #@measure_time
    def getDeviceList(yoAccess):
        return(yoAccess.deviceList)


    #@measure_time
    def request_new_token(yoAccess):
        logging.debug('yoAccess Token exists : {}'.format(yoAccess.token != None))
        now = int(time.time())
        if yoAccess.token == None:
            try:
                now = int(time.time())
                response = requests.post( yoAccess.tokenURL,
                        data={"grant_type": "client_credentials",
                            "client_id" : yoAccess.uaID,
                            "client_secret" : yoAccess.secID },
                    )
                if response.ok:
                    temp = response.json()
                    logging.debug('yoAccess Token : {}'.format(temp))
                else:
                    logging.error('Error occured obtaining token - check credentials')
                    return(False)
                if 'state' not in temp:
                    yoAccess.token = temp
                    yoAccess.token['expirationTime'] = int(yoAccess.token['expires_in'] + now )
                    #logging.debug('yoAccess Token : {}'.format(yoAccess.token ))
                else:
                    if temp['state'] != 'error':
                        logging.error('Authentication error')
                return(True)

            except Exception as e:
                logging.error('Exeption occcured during request_new_token : {}'.format(e))
                return(False)
        else:
            #yoAccess.refresh_token()  Need to consider 
            return(True) # use existing Token 

    #@measure_time
    def refresh_token(yoAccess):
        
        try:
            logging.info('Refreshing Token ')
            now = int(time.time())
            if yoAccess.token != None:
                if now < yoAccess.token['expirationTime']:
                    response = requests.post( yoAccess.tokenURL,
                        data={"grant_type": "refresh_token",
                            "client_id" :  yoAccess.uaID,
                            "refresh_token":yoAccess.token['refresh_token'],
                            }
                    )
                else:
                    response = requests.post( yoAccess.tokenURL,
                        data={"grant_type": "client_credentials",
                            "client_id" : yoAccess.uaID,
                            "client_secret" : yoAccess.secID },
                    )
                if response.ok:
                    yoAccess.token =  response.json()
                    yoAccess.token['expirationTime'] = int(yoAccess.token['expires_in']) + now
                    return(True)
                else:
                    logging.error('Was not able to refresh token')
                    return(False)
            else:
                return(yoAccess.request_new_token())


        except Exception as e:
            logging.debug('Exeption occcured during refresh_token : {}'.format(e))
            return(yoAccess.request_new_token())

    #@measure_time
    def get_access_token(yoAccess):
        yoAccess.tokenLock.acquire()
        #now = int(time.time())
        if yoAccess.token == None:
            yoAccess.request_new_token()
        #if now > yoAccess.token['expirationTime']  - yoAccess.timeExpMarging :
        #    yoAccess.refresh_token()
        #    if now > yoAccess.token['expirationTime']: #we lost the token
        #        yoAccess.request_new_token()
        #    else:
        yoAccess.tokenLock.release() 

    #@measure_time                
    def is_token_expired (yoAccess, accessToken):
        return(accessToken == yoAccess.token['access_token'])
        
    #@measure_time
    def retrieve_device_list(yoAccess):
        try:
            logging.debug('retrieve_device_list')
            data= {}
            data['method'] = 'Home.getDeviceList'
            data['time'] = str(int(time.time_ns()/1e6))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ yoAccess.token['access_token']
            r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
            info = r.json()
            yoAccess.deviceList = info['data']['devices']
            logging.debug('device_list : {}'.format(yoAccess.deviceList))
        except Exception as e:
            logging.error('Exception  -  retrieve_device_list : {}'.format(e))             

    #@measure_time
    def retrieve_homeID(yoAccess):
        try:
            data= {}
            data['method'] = 'Home.getGeneralInfo'
            data['time'] = str(int(time.time_ns()/1e6))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ yoAccess.token['access_token']

            r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
            logging.debug('Obtaining  homeID : {}'.format(r.ok))
            if r.ok:
                homeId = r.json()
                yoAccess.homeID = homeId['data']['id']
            else:
                yoAccess.homeID = None
                logging.error('Failed ot obtain HomeID')
        except Exception as e:
            logging.error('Exception  - retrieve_homeID: {}'.format(e))    

    #@measure_time
    def getDeviceList (yoAccess):
        return(yoAccess.deviceList)

    #@measure_time
    def shut_down(yoAccess):
        try:
            yoAccess.disconnect = True
            if yoAccess.client:
                yoAccess.STOP.set()
                yoAccess.client.disconnect()
                yoAccess.client.loop_stop()
        except Exception as E:
            logging.error('Shut down exception {}'.format(E))
            
    ########################################
    # MQTT stuff
    ########################################

    #@measure_time
    def connect_to_broker(yoAccess):
        """
        Connect to MQTT broker
        """
        try: 
            logging.info("Connecting to broker...")
            while not yoAccess.request_new_token():
                time.sleep(35) # Wait 35 sec and try again (35sec ensure less than 10 attempts in 5 min)
                logging.info('Trying to obtain new Token - Network/YoLink connection may be down')
            logging.info('Retrieving YoLink API info')
            yoAccess.retrieve_device_list()
            #yoAccess.retrieve_homeID()
            time.sleep(1)
            yoAccess.client.username_pw_set(username=yoAccess.token['access_token'], password=None)
            logging.debug('yoAccess.client.connect: {}'.format(yoAccess.client.connect(yoAccess.mqttURL, yoAccess.mqttPort, keepalive= yoAccess.keepAlive))) # ping server every 30 sec
                
            yoAccess.client.loop_start()
            time.sleep(2)
            yoAccess.connectedToBroker = True   
            yoAccess.loopRunning = True 
            logging.debug(yoAccess.mqttList)
            for deviceId in yoAccess.mqttList:
                yoAccess.update_mqtt_subscription(deviceId)
                logging.debug('Updating {} in mqttList'.format(deviceId))
            #yoAccess.client.will_set()
            return(True)

        except Exception as e:
            logging.error('Exception  - connect_to_broker: {}'.format(e))
            #if yoAccess.token == None:
            #    yoAccess.request_new_token()
            #else:
            #    yoAccess.refresh_token()
            return(False)

    #@measure_time
    def subscribe_mqtt(yoAccess, deviceId, callback):
        logging.info('Subscribing deviceId {} to MQTT'.format(deviceId))
        topicReq = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/request'
        topicResp = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/response'
        topicReport = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/report'
        #topicReportAll = 'yl-home/'+yoAccess.homeID+'/+/report'
        
        if not deviceId in yoAccess.mqttList :
            yoAccess.client.subscribe(topicReq, yoAccess.QoS)
            yoAccess.client.subscribe(topicResp, yoAccess.QoS)
            yoAccess.client.subscribe(topicReport,  yoAccess.QoS)

            yoAccess.mqttList[deviceId] = { 'callback': callback, 
                                            'request': topicReq,
                                            'response': topicResp,
                                            'report': topicReport,
                                            'subscribed': True
                                            }
            time.sleep(1)

    #@measure_time
    def update_mqtt_subscription (yoAccess, deviceId):
        logging.info('update_mqtt_subscription {} '.format(deviceId))
        topicReq = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/request'
        topicResp = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/response'
        topicReport = 'yl-home/'+yoAccess.homeID+'/'+ deviceId +'/report'
        #topicReportAll = 'yl-home/'+yoAccess.homeID+'/+/report'
        
        if  deviceId in yoAccess.mqttList :
            logging.debug('unsubscribe {}'.format(deviceId))
            yoAccess.client.unsubscribe(yoAccess.mqttList[deviceId]['request'] )
            yoAccess.client.unsubscribe(yoAccess.mqttList[deviceId]['response'] )
            yoAccess.client.unsubscribe(yoAccess.mqttList[deviceId]['report'] )
            
            logging.debug('re-subscribe {}'.format(deviceId))
            yoAccess.client.subscribe(topicReq, yoAccess.QoS)
            yoAccess.client.subscribe(topicResp, yoAccess.QoS)
            yoAccess.client.subscribe(topicReport, yoAccess.QoS)
            yoAccess.mqttList[deviceId]['request'] =  topicReq
            yoAccess.mqttList[deviceId]['response'] = topicResp
            yoAccess.mqttList[deviceId]['report'] = topicReport
        #logging.debug('mqtt.list:{}.'.format(yoAccess.mqttList))

    #@measure_time
    def process_message(yoAccess):
        try:
            #yoAccess.messageLock.acquire()
            msg = yoAccess.messageQueue.get(timeout = 10) 
            logging.debug('Received message - Q size={}'.format(yoAccess.messageQueue.qsize()))
            payload = json.loads(msg.payload.decode("utf-8"))
            logging.debug('process_message : {}'.format(payload))
            
            deviceId = 'unknown'
            if 'targetDevice' in payload:
                deviceId = payload['targetDevice']
            elif 'deviceId' in payload:
                deviceId = payload['deviceId']
            else:
                logging.debug('Unknow device in payload : {}'.format(payload))

            logging.debug('process_message for {}: {} {}'.format(deviceId, payload, msg.topic))
            

            if deviceId in yoAccess.mqttList:

                tempCallback = yoAccess.mqttList[deviceId]['callback']
                
                #if payload['msgid'] in yoAccess.pendingDict:
                #    yoAccess.pendingDict.pop(payload['msgid'] )
                if  msg.topic == yoAccess.mqttList[deviceId]['report']: 
                    logging.debug('porcessing report: {}'.format(payload))                   
                    tempCallback(payload)
                    if yoAccess.debug:
                            fileData= {}
                            fileData['type'] = 'EVENT'
                            fileData['data'] = payload 
                            yoAccess.fileQueue.put(fileData)
                            event_fileThread = Thread(target = yoAccess.save_packet_info )
                            event_fileThread.start()
                            logging.debug('event_fileThread - starting')


                elif msg.topic == yoAccess.mqttList[deviceId]['response']:
                    logging.debug('porcessing response: {}'.format(payload))                   

                    if payload['code'] == '000000':
                        tempCallback(payload)
                    else:
                        logging.error('Non-000000 code {} : {}'.format(payload['desc'], str(json.dumps(payload))))
                        tempCallback(payload)
                    if yoAccess.debug:
                        fileData= {}
                        fileData['type'] = 'RESP'
                        fileData['data'] = payload 
                        yoAccess.fileQueue.put(fileData)
                        resp_fileThread = Thread(target = yoAccess.save_packet_info )
                        resp_fileThread.start()
                        logging.debug('resp_fileThread - starting')
                        
                elif msg.topic == yoAccess.mqttList[deviceId]['request']:
                    logging.debug('porcessing request - no action: {}'.format(payload))                   
                    #transmitted message
                    if yoAccess.debug:
                        fileData= {}
                        fileData['type'] = 'REQ'
                        fileData['data'] = payload
                        yoAccess.fileQueue.put(fileData)
                        req_fileThread = Thread(target = yoAccess.save_packet_info )
                        req_fileThread.start()
                        logging.debug('req_fileThread - starting')

                else:
                    logging.error('Topic not mathing:' + msg.topic + '  ' + str(json.dumps(payload)))
                    if yoAccess.debug:
                        fileData= {}
                        fileData['type'] = 'MISC'
                        fileData['data'] = payload
                        yoAccess.fileQueue.put(fileData)   
                        misc_fileThread = Thread(target = yoAccess.save_packet_info )
                        misc_fileThread.start()
                        logging.debug('misc_fileThread - starting')                                     
            else:
                logging.error('Unsupported device: {}'.format(deviceId))
            #yoAccess.messageLock.release()

        except Exception as e:
            logging.debug('message processing timeout - no new commands') 
            pass
            #yoAccess.messageLock.release()

    #@measure_time
    def on_message(yoAccess, client, userdata, msg):
        """
        Callback for broker published events
        """
        logging.debug('on_message: {}'.format(json.loads(msg.payload.decode("utf-8"))) )
        yoAccess.messageQueue.put(msg)
        qsize = yoAccess.messageQueue.qsize()
        logging.debug('Message received and put in queue (size : {})'.format(qsize))
        logging.debug('Creating threads to handle the received messages')
        threads = []
        for idx in range(0, qsize):
            threads.append(Thread(target = yoAccess.process_message ))
        [t.start() for t in threads]
        #[t.join() for t in threads]
        logging.debug('{} on_message threads starting'.format(qsize))

    #def obtain_connection (yoAccess):
    #    if not yoAccess.connectedToBroker:    
    #        yoAccess.client.disconnect()          
    #        logging.debug('Waiting to (re)establish connection to broker')
    #        yoAccess.client.connect(yoAccess.mqttURL, yoAccess.mqttPort, keepalive= 30) # ping server every 30 sec                    
    #        time.sleep(5)

    #@measure_time
    def on_connect(yoAccess, client, userdata, flags, rc):
        """
        Callback for connection to broker
        """
        netstate = []
        try:
            logging.debug('on_connect - Connected with result code {}'.format(rc))
            #// Possible values for client.state()
            #define MQTT_CONNECTION_TIMEOUT     -4
            #define MQTT_CONNECTION_LOST        -3
            #define MQTT_CONNECT_FAILED         -2
            #define MQTT_DISCONNECTED           -1
            #define MQTT_CONNECTED               0
            #define MQTT_CONNECT_BAD_PROTOCOL    1
            #define MQTT_CONNECT_BAD_CLIENT_ID   2
            #define MQTT_CONNECT_UNAVAILABLE     3
            #define MQTT_CONNECT_BAD_CREDENTIALS 4
            #define MQTT_CONNECT_UNAUTHORIZED    5

            if (rc == 0):
                yoAccess.online = True
                logging.info('Successfully connected to broker {} '.format(yoAccess.mqttURL))
                logging.debug('Re-subscribing devices after after disconnect')
                for deviceId in yoAccess.mqttList:
                    yoAccess.update_mqtt_subscription(deviceId)
                yoAccess.connectedToBroker = True

            elif (rc == 2):
                if yoAccess.connectedToBroker: # Already connected - need to disconnect before reconnecting
                    logging.error('Authentication error 2 - Token no longer valid - Need to reconnect ')
                    #netid = yoAccess.check_connection(yoAccess.mqttPort)
                    #logging.debug('netid = {}'.format(netid))
                    yoAccess.connectedToBroker = False
                    yoAccess.disconnect = True
                    yoAccess.client.disconnect()
                    yoAccess.refresh_token()
                    time.sleep(2)
                    yoAccess.connect_to_broker()

            elif (rc >= 4):
                if yoAccess.connectedToBroker: # Already connected - need to disconnect before reconnecting
                    logging.error('Authentication error {rc} - Token no longer valid - Need to reconnect ')
                    netid = yoAccess.check_connection(yoAccess.mqttPort)
                    logging.debug('netid = {}'.format(netid))

                    if None == netid: # no communication to brooker possible 
                        yoAccess.connectedToBroker = False
                        yoAccess.disconnect = True
                        yoAccess.client.disconnect()
                        time.sleep(2)
                        yoAccess.token = None
                        yoAccess.connect_to_broker()
                    else: # still connected - needs new token - disconnect should automatically reconnect
                        yoAccess.connectedToBroker = False
                        yoAccess.client.disconnect()

                else:
                    logging.error('Authentication error {rc}} - check credentials and try again  ')




            else:
                logging.error('Broker connection failed with result code {}'.format(rc))
                yoAccess.client.disconnect()
                yoAccess.connectedToBroker = False
                yoAccess.online = False
         
        except Exception as e:
            logging.error('Exception  -  on_connect: ' + str(e))       

    #@measure_time
    def on_disconnect(yoAccess, client, userdata,rc=0):
        logging.debug('Disconnect - stop loop')
        #yoAccess.connectedToBroker = False
        yoAccess.disconnect_occured = True
        if yoAccess.disconnect:
            logging.debug('Disconnect - stop loop')
            yoAccess.client.loop_stop()
            
        else:
            logging.error('Unintentional disconnect - Reacquiring connection')

            try:
                netid = yoAccess.check_connection(yoAccess.mqttPort)
                if None == netid:      
                    yoAccess.connectedToBroker = False
                elif netid.status.__contains__('ESTABLISHED'):
                    yoAccess.connectedToBroker = True
                else:
                    yoAccess.connectedToBroker = False
                logging.debug('on_disconnect - connectedToBroker = {}'.format(yoAccess.connectedToBroker))
                if not yoAccess.connectedToBroker:

                    logging.debug('on_disconnect - restarting broker')
                    #yoAccess.client.loop_stop() 
                    yoAccess.client.disconnect()  # seems it is needed to disconnect to not have API add up connections
                    time.sleep(2) 
                    yoAccess.token = None
                    yoAccess.connect_to_broker()
                    yoAccess.connectedToBroker = True
                yoAccess.online = False
                #time.sleep(3)   


            except Exception as e:
                logging.error('Exeption occcured during on_ disconnect : {}'.format(e))
                if yoAccess:
                    yoAccess.request_new_token()
                else:
                    logging.error('Lost credential info - need to restart node server')

    #@measure_time
    def on_subscribe(yoAccess, client, userdata, mID, granted_QoS):        
        logging.debug('on_subscribe')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('Granted QoS: ' +  str(granted_QoS))
        #logging.debug('\n')

    #@measure_time
    def on_publish(yoAccess, client, userdata, mID):
        logging.debug('on_publish')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('\n')


    #@measure_time
    def publish_data(yoAccess, data):
        logging.debug( 'Publish Data to Queue: {}'.format(data))
        while not yoAccess.connectedToBroker:
            logging.debug('Connection to Broker not established - waiting')
            time.sleep(1)       

        yoAccess.publishQueue.put(data, timeout = 5)
        
        publishThread = Thread(target = yoAccess.transfer_data )
        publishThread.start()
        logging.debug('publishThread - starting')
        return(True)

    #@measure_time
    def set_api_limits(yoAccess, api_calls, api_dev_calls):
        ''''''
        yoAccess.nbr_api_calls = api_calls
        yoAccess.nbr_api_dev_calls = api_dev_calls


    #@measure_time
    def time_tracking(yoAccess, dev_id):
        '''time_track_publish'''
        ''' make 100 overall calls per 5 min and 6 per dev per min and 200ms between calls'''
        try:
            yoAccess.TimeTableLock.acquire()
            if dev_id not in yoAccess.time_tracking_dict:
                yoAccess.time_tracking_dict[dev_id] = []
                #logging.debug('Adding timetrack for {}'.format(dev_id))            
            t_now = int(time.time_ns()/1e6)
            logging.debug('time_track_going in: {}, {}, {}'.format(t_now, dev_id, yoAccess.time_tracking_dict))
            max_dev_id = 5 # commands per dev_time_limit to same dev (add margin)
            max_dev_all = 99 # commands per call_time_limit to same dev (add margin)
            dev_time_limit = 60000 # 1 min =  60 sec = 60000 ms
            call_time_limit = 300000 # 5min = 300 sec = 300000 ms
            dev_to_dev_limit = 200 # min 200ms between calls to same dev
            total_dev_calls = 0
            total_dev_id_calls = 0
            t_oldest = t_now
            t_oldest_dev = t_now
            t_previous_dev = 0
            t_dev_2_dev = 0
            t_call = t_now

            #t_now = int(time.time_ns()/1e6)
            #logging.debug('time_tracking 0 - {}'.format(yoAccess.time_tracking_dict))
            discard_list = {}
            #remove data older than time_limit
            for dev in yoAccess.time_tracking_dict:
                for call_nbr  in range(0,len(yoAccess.time_tracking_dict[dev])):
                    t_call = yoAccess.time_tracking_dict[dev][call_nbr]
                    if t_call  < (t_now - call_time_limit): # more than 1 min ago
                        discard_list[t_call] = dev
            for tim in discard_list:
                yoAccess.time_tracking_dict[discard_list[tim]].remove(tim)
            # find oldest data in dict and for devices of the dev
            #logging.debug('time_track AFTER >1MIN REMOVAL: {}'.format(yoAccess.time_tracking_dict))
            for dev in yoAccess.time_tracking_dict:
                #logging.debug('time_tracking 1 - {} - {}'.format(dev, len(yoAccess.time_tracking_dict[dev])))
                for call_nbr  in range(0,len(yoAccess.time_tracking_dict[dev])):
                    #logging.debug('time_tracking 1.5 - {}'.format(t_call))
                    total_dev_calls = total_dev_calls + 1
                    t_call = yoAccess.time_tracking_dict[dev][call_nbr]
                    #logging.debug('Loop info : {} - {} - {} '.format(dev, call_nbr, (t_now - t_call)))  
                    if t_call < t_oldest:
                        t_oldest = t_call
                    #logging.debug('After cleanup {} {} {} - {}'.format(t_call, t_oldest, t_old_dev_tmp, yoAccess.time_tracking_dict ))
                    #logging.debug('devs {} {} {}'.format(dev==dev_id, dev, dev_id))
                    if dev == dev_id: # check if max_dev_id is in play
                        if t_call >= (t_now - dev_time_limit): # call is less than 1 min old
                            total_dev_id_calls = total_dev_id_calls + 1
                            #logging.debug('time_tracking2 - dev found')
                            #yoAccess.time_tracking_dict[dev].append(t_now)
                            if t_call < t_oldest_dev: # only test for selected dev_id
                                t_oldest_dev = t_call
                            if t_call > t_previous_dev:
                                t_previous_dev = t_call

            if total_dev_calls <= max_dev_all:
                t_all_delay = 0
            else:
                t_all_delay = call_time_limit - (t_now - t_oldest )
            
            if (t_now - t_previous_dev) <= dev_to_dev_limit:
                #time.sleep((dev_to_dev_limit + 10 -(t_now - t_previous_dev))/1000) # calls to same device must be min dev_to_dev_limit (200ms) apart
                #t_dev_2_dev = dev_to_dev_limit) # sleep 200ms + 100 ms margin - Seems calculating the limit is not accurate enough
                t_dev_2_dev = (dev_to_dev_limit + 100 -(t_now - t_previous_dev))
                #logging.debug('Sleeping {}ms due to too close dev calls '.format(t_now - t_previous_dev))
                #logging.debug('Sleeping {}s due to too close dev calls '.format(dev_to_dev_limit/1000))
            if total_dev_id_calls <= max_dev_id:
                t_dev_delay = 0
            else:
                t_dev_delay = dev_time_limit  - (t_now- t_oldest_dev)
            #logging.debug('total_calls = {}, total_dev_calls = {}'.format(total_dev_calls, total_dev_id_calls))
            t_delay = max(t_all_delay,t_dev_delay, t_dev_2_dev, 0 )
            logging.debug('Adding {} delay to t_now {}  =  {} to TimeTrack - dev delay={}, all_delay={}, dev2dev={}'.format(t_delay, t_now, t_now + t_delay, t_dev_delay, t_all_delay, t_dev_2_dev))
            yoAccess.time_tracking_dict[dev_id].append(t_now + t_delay)
            yoAccess.TimeTableLock.release()
            logging.debug('TimeTrack after: time {} dev: {} delay: {} -  {}'.format(t_now, dev_id, int(math.ceil(t_delay/1000)), yoAccess.time_tracking_dict))
            return(int(math.ceil(t_delay/1000)))
            #return(int(math.ceil(t_delay/1000)), int(math.ceil(t_all_delay)), int(math.ceil(t_all_delay)))
        except Exception as e:
            logging.debug(' Exception Timetrack : {}'.format(e))
            yoAccess.TimeTableLock.release()
        #yoAccess.time_tracking_dict[dev_id].append(time)

    #@measure_time
    def transfer_data(yoAccess):
        '''transfer_data'''
        yoAccess.lastTransferTime = int(time.time())
        
        try:
            data = yoAccess.publishQueue.get(timeout = 10)

            deviceId = data['targetDevice']

            #logging.debug('mqttList : {}'.format(yoAccess.mqttList))
            if deviceId in yoAccess.mqttList:
                logging.debug( 'Starting publish_data:')
                ### check if publish list is full
                
                #all_delay, dev_delay =  yoAccess.time_tracking(timeNow_ms, deviceId)
                delay_s =  yoAccess.time_tracking(deviceId)
                #logging.debug( 'Needed delay: {} - {}'.format(delay, timeNow_s))
                if delay_s > 0: # some delay needed
                    logging.info('Delaying call by {}sec due to too many calls'.format(delay_s))
                    time.sleep(delay_s)
                    # As this is multi threaded we can just sleep  - if another call is ready and can go though is will so in a differnt thread    
                data['time'] = str(int(time.time_ns()/1e6))  # update time to actual packet time (to include delays)
                dataStr = str(json.dumps(data))
                yoAccess.tmpData[deviceId] = dataStr
                yoAccess.lastDataPacket[deviceId] = data

                logging.debug( 'publish_data: {} - {}'.format(yoAccess.mqttList[deviceId]['request'], dataStr))
                result = yoAccess.client.publish(yoAccess.mqttList[deviceId]['request'], dataStr, yoAccess.QoS)
            else:
                logging.error('device {} not in mqtt list'.format(deviceId))
                return (False)
            
            if result.rc != 0:
                logging.error('Error {} during publishing {}'.format(result.rc, data))
                #errorCount = errorCount + 1
                if result.rc == 3: #off line
                    logging.debug('rc = {}'.format(result.rc))
                    yoAccess.online = False
                if result.rc == 4 : #off line
                    logging.debug('rc = {}'.format(result.rc))
                    yoAccess.online = False
                    yoAccess.client.reconnect() # is this the right strategy 
            else:
                yoAccess.lastTransferTime = int(time.time())
                yoAccess.online = True
        except Exception as e:
            pass # go wait again unless stop is called

    #@measure_time
    def save_packet_info(yoAccess):
        yoAccess.fileLock.acquire()
        try:
            data = yoAccess.fileQueue.get(timeout = 10)
            if 'targetDevice' in data['data']:
                deviceId = data['data']['targetDevice']
            elif 'deviceId' in data['data']:
                deviceId = data['data']['deviceId']
            if data['type'].upper() == 'REQ':
                f = open('TXpackets.txt', 'a')
            elif data['type'].upper() == 'RESP':
                f = open('RXpackets.txt', 'a')
            elif data['type'].upper() == 'EVENT':  
                f = open('EVENTpackets.txt', 'a')
            else:
                f = open('MISCpackets.txt', 'a')
            #jsonStr  = json.dumps(dataTemp, sort_keys=True, indent=4, separators=(',', ': '))
            f.write('{} - {}:  '.format( datetime.now(),deviceId))
            f.write(str(json.dumps(data['data'])))
            f.write('\n\n')
            #json.dump(jsonStr, f)
            f.close()
            time.sleep(0.2)
        
        except Exception as e:
            # logging.debug('File Queue looping {}'.format(e))
            pass # go wait again unless stop is called
        yoAccess.fileLock.release()

    #@measure_time
    def system_online(yoAccess):
        return(yoAccess.online)


################
#   Misc stuff
###############
    #@measure_time
    def set_temp_unit(yoAccess, unit):
        yoAccess.temp_unit = unit

    def get_temp_unit(yoAccess):
        return(yoAccess.temp_unit)

    def set_debug(yoAccess, debug):
        yoAccess.debug = debug


class YoLinkInitCSID(object):
    def __init__(yoAccess,  csName, csid, csSeckey, yoAccess_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003 ):
        yoAccess.csName = csName
        yoAccess.csid = csid
        yoAccess.cssSeckey = csSeckey
        yoAccess.apiType = 'CSID'