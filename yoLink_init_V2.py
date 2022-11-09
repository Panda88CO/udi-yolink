#!/usr/bin/env python3
import requests
import time
import json
import psutil

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


import paho.mqtt.client as mqtt
from queue import Queue
from threading import Thread, Event
DEBUG = False


class YoLinkInitPAC(object):
    def __init__(yoAccess, uaID, secID, tokenURL='https://api.yosmart.com/open/yolink/token', pacURL = 'https://api.yosmart.com/open/yolink/v2/api' , mqttURL= 'api.yosmart.com', mqttPort = 8003):
        yoAccess.disconnect_occured = False 
        yoAccess.tokenLock = Lock()
        yoAccess.messageLock = Lock()
        yoAccess.publishQueue = Queue()
        yoAccess.messageQueue = Queue()
        yoAccess.debug = True
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
        yoAccess.lastTransferTime = time.time()
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
        try:
            #while not yoAccess.request_new_token( ):
            #    time.sleep(60)
            #    logging.info('Waiting to acquire access token')
           
            #yoAccess.retrieve_device_list()
            #yoAccess.retrieve_homeID()

            yoAccess.retryNbr = 0
            yoAccess.disconnect = False
            yoAccess.STOP = Event()

            yoAccess.messageThread = Thread(target = yoAccess.process_message )
            yoAccess.publishThread = Thread(target = yoAccess.transfer_data )
            yoAccess.fileThread =  Thread(target = yoAccess.save_packet_info )
            #yoAccess.connectionMonitorThread = Thread(target = yoAccess.connection_monitor)

            yoAccess.messageThread.start()
            yoAccess.publishThread.start()
            yoAccess.fileThread.start()
            

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

    def getDeviceList(yoAccess):
        return(yoAccess.deviceList)

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
            return(True) # use existing Token 

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

    def get_access_token(yoAccess):
        yoAccess.tokenLock.acquire()
        now = int(time.time())
        if yoAccess.token == None:
            yoAccess.request_new_token()
        #if now > yoAccess.token['expirationTime']  - yoAccess.timeExpMarging :
        #    yoAccess.refresh_token()
        #    if now > yoAccess.token['expirationTime']: #we lost the token
        #        yoAccess.request_new_token()
        #    else:
        yoAccess.tokenLock.release() 

                
    def is_token_expired (yoAccess, accessToken):
        return(accessToken == yoAccess.token['access_token'])
        

    def retrieve_device_list(yoAccess):
        try:
            logging.debug('retrieve_device_list')
            data= {}
            data['method'] = 'Home.getDeviceList'
            data['time'] = str(int(time.time_ns()//1e6))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ yoAccess.token['access_token']
            r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
            info = r.json()
            yoAccess.deviceList = info['data']['devices']
            logging.debug('device_list : {}'.format(yoAccess.deviceList))
        except Exception as e:
            logging.error('Exception  -  retrieve_device_list : {}'.format(e))             


    def retrieve_homeID(yoAccess):
        try:
            data= {}
            data['method'] = 'Home.getGeneralInfo'
            data['time'] = str(int(time.time_ns()//1e6))
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

    def getDeviceList (yoAccess):
        return(yoAccess.deviceList)


    def shut_down(yoAccess):

        yoAccess.disconnect = True
        if yoAccess.client:
            yoAccess.STOP.set()
            yoAccess.client.disconnect()
            yoAccess.client.loop_stop()
        
    ########################################
    # MQTT stuff
    ########################################

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
            logging.debug('yoAccess.client.connect: {}'.format(yoAccess.client.connect(yoAccess.mqttURL, yoAccess.mqttPort, keepalive= 30))) # ping server every 30 sec
                
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
            return(False)

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
            time.sleep(1)


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
            yoAccess.client.subscribe(topicReq,2)
            yoAccess.client.subscribe(topicResp,2)
            yoAccess.client.subscribe(topicReport,2)
            yoAccess.mqttList[deviceId]['request'] =  topicReq
            yoAccess.mqttList[deviceId]['response'] = topicResp
            yoAccess.mqttList[deviceId]['report'] = topicReport
        #logging.debug('mqtt.list:{}.'.format(yoAccess.mqttList))

    def process_message(yoAccess):

        while not yoAccess.STOP.is_set():
            try:
                #yoAccess.messageLock.acquire()
                msg = yoAccess.messageQueue.get(timeout = 10) 
                logging.debug('Received message - Q size={}'.format(yoAccess.messageQueue.qsize()))
                payload = json.loads(msg.payload.decode("utf-8"))
                #logging.debug('process_message : {}'.format(payload))
                
                deviceId = 'unknown'
                if 'targetDevice' in payload:
                    deviceId = payload['targetDevice']
                elif 'deviceId' in payload:
                    deviceId = payload['deviceId']
                else:
                    logging.debug('Unknow device in payload : {}'.format(payload))

                logging.debug('process_message for {}: {} {}'.format(deviceId, payload, msg.topic))
                #yoAccess.debug = logging.root.level <= logging.DEBUG
                if deviceId in yoAccess.mqttList:

                    tempCallback = yoAccess.mqttList[deviceId]['callback']
                    
                    #if payload['msgid'] in yoAccess.pendingDict:
                    #    yoAccess.pendingDict.pop(payload['msgid'] )
                    #    logging.debug('POP {} yoAccess.pendingDict {}:{}'.format(payload['msgid'] ,len(yoAccess.pendingDict), yoAccess.pendingDict))
                    if  msg.topic == yoAccess.mqttList[deviceId]['report']:                    
                        tempCallback(payload)
                        if yoAccess.debug:
                                fileData= {}
                                fileData['type'] = 'EVENT'
                                fileData['data'] = payload 
                                yoAccess.fileQueue.put(fileData)

                    elif msg.topic == yoAccess.mqttList[deviceId]['response']:
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
                            
                    elif msg.topic == yoAccess.mqttList[deviceId]['request']:
                        #transmitted message
                        if yoAccess.debug:
                            fileData= {}
                            fileData['type'] = 'REQ'
                            fileData['data'] = payload
                            yoAccess.fileQueue.put(fileData)

                    else:
                        logging.error('Topic not mathing:' + msg.topic + '  ' + str(json.dumps(payload)))
                        if yoAccess.debug:
                            fileData= {}
                            fileData['type'] = 'MISC'
                            fileData['data'] = payload
                            yoAccess.fileQueue.put(fileData)                
                else:
                    logging.error('Unsupported device: {}'.format(deviceId))
                #yoAccess.messageLock.release()

            except Exception as e:
                pass
                #logging.error('message processing timeout - no new commands') 
                #yoAccess.messageLock.release()

    def on_message(yoAccess, client, userdata, msg):
        """
        Callback for broker published events
        """
        logging.debug('Message: {}'.format(json.loads(msg.payload.decode("utf-8"))) )
        logging.debug('Message received and put in queue (size : {})'.format(yoAccess.messageQueue.qsize()))

        yoAccess.messageQueue.put(msg)


    #def obtain_connection (yoAccess):
    #    if not yoAccess.connectedToBroker:    
    #        yoAccess.client.disconnect()          
    #        logging.debug('Waiting to (re)establish connection to broker')
    #        yoAccess.client.connect(yoAccess.mqttURL, yoAccess.mqttPort, keepalive= 30) # ping server every 30 sec                    
    #        time.sleep(5)

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
                    logging.error('Authentication error 5 - Token no longer valid - Need to reconnect ')
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
                    logging.error('Authentication error 5 - check credentials and try again  ')




            else:
                logging.error('Broker connection failed with result code {}'.format(rc))
                yoAccess.client.disconnect()
                yoAccess.connectedToBroker = False
                yoAccess.online = False
         
        except Exception as e:
            logging.error('Exception  -  on_connect: ' + str(e))       


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

    def on_subscribe(yoAccess, client, userdata, mID, granted_QOS):        
        logging.debug('on_subscribe')
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


    def transfer_data(yoAccess):
        errorCount = 0
        yoAccess.lastTransferTime = time.time()
        while not yoAccess.STOP.is_set():
            try:
                data = yoAccess.publishQueue.get(timeout = 10) 
                #DEBUG = logging.getEffectiveLevel() == logging.DEBUG
                deviceId = data['targetDevice']
                dataStr = str(json.dumps(data))
                yoAccess.tmpData[deviceId] = dataStr
                yoAccess.lastDataPacket[deviceId] = data
                if deviceId in yoAccess.mqttList:
                    logging.debug( 'publish_data: {} - {}'.format(yoAccess.mqttList[deviceId]['request'], dataStr))
                    result = yoAccess.client.publish(yoAccess.mqttList[deviceId]['request'], dataStr, 2)
                else:
                    logging.error('device {} not in mqtt list'.format(deviceId))
                    return (False)
                
                if result.rc != 0:
                    logging.error('Error {} during publishing {}'.format(result.rc, data))
                    #errorCount = errorCount + 1
                    if result.rc == 4 or result.rc == 3: #off line
                        logging.debug('rc = {}'.format(result.rc))
                        yoAccess.online = False
                        #yoAccess.client.reconnect() # is this the right strategy 
                else:
                    yoAccess.lastTransferTime = time.time()
                    yoAccess.online = True
            except Exception as e:
                pass # go wait again unless stop is called


    def save_packet_info(yoAccess):
        while not yoAccess.STOP.is_set():
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

    def system_online(yoAccess):
        return(yoAccess.online)


################
#   Misc stuff
###############
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