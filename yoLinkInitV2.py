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
DEBUG = True


class YoLinkInitPAC(object):
    def __init__(yoAccess, uaID, secID, tokenURL='https://api.yosmart.com/open/yolink/token', pacURL = 'https://api.yosmart.com/open/yolink/v2/api' , mqttURL= 'api.yosmart.com', mqttPort = 8003):
        yoAccess.disconnect_occured = False 
        yoAccess.tokenLock = Lock()
        yoAccess.messageLock = Lock()
        yoAccess.publishQueue = Queue()
        yoAccess.messageQueue = Queue()
        yoAccess.fileQueue = Queue()
        #yoAccess.pendingDict = {}
        yoAccess.pending_messages = 0
        yoAccess.time_since_last_message_RX = 0
        yoAccess.tokenURL = tokenURL
        yoAccess.apiv2URL = pacURL
        yoAccess.mqttURL = mqttURL
        yoAccess.mqttPort = mqttPort
        yoAccess.connectedToBroker = False
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
        
        #yoAccess.TSSfile = 'TSSmessages.json'
        #yoAccess.readTssFile()

        yoAccess.token = None
        try:
            while not yoAccess.request_new_token( ):
                time.sleep(60)
                logging.info('Waiting to acquire access token')
            logging.info('Retrieving YoLink API info')
            yoAccess.retrieve_device_list()
            yoAccess.retrieve_homeID()

            yoAccess.retryNbr = 0
            yoAccess.disconnect = False
            yoAccess.STOP = Event()

            logging.info('Connecting to YoLink MQTT server')

            #if yoAccess.client == None:    
      
            #logging.debug('initialize MQTT' )
            yoAccess.client = mqtt.Client(yoAccess.homeID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            yoAccess.client.on_connect = yoAccess.on_connect
            yoAccess.client.on_message = yoAccess.on_message
            yoAccess.client.on_subscribe = yoAccess.on_subscribe
            yoAccess.client.on_disconnect = yoAccess.on_disconnect
            yoAccess.client.on_publish = yoAccess.on_publish
            #logging.debug('finish subscribing ')
            
            yoAccess.messageThread = Thread(target = yoAccess.process_message )
            yoAccess.publishThread = Thread(target = yoAccess.transfer_data )
            yoAccess.fileThread =  Thread(target = yoAccess.save_packet_info )
            #yoAccess.connectionMonitorThread = Thread(target = yoAccess.connection_monitor)

            yoAccess.messageThread.start()
            yoAccess.publishThread.start()
            yoAccess.fileThread.start()
            yoAccess.connect_to_broker()
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
        logging.debug('yoAccess Token : {}'.format(yoAccess.token ))
        if yoAccess.token == None:
            try:
                now = int(time.time())
                response = requests.post( yoAccess.tokenURL,
                        data={"grant_type": "client_credentials",
                            "client_id" : yoAccess.uaID,
                            "client_secret" : yoAccess.secID },
                    )
                
                temp = response.json()
                #logging.debug('yoAccess Token : {}'.format(temp))
                if 'state' not in temp:
                    yoAccess.token = temp
                    yoAccess.token['expirationTime'] = int(yoAccess.token['expires_in'] + now )
                    #logging.debug('yoAccess Token : {}'.format(yoAccess.token ))
                else:
                    if temp['state'] != 'error':
                        logging.error('Authentication error')
                return(True)

            except Exception as e:
                logging.debug('Exeption occcured during request_new_token : {}'.format(e))
                return(False)
        else:

            return(True) # use existing Token 

    def refresh_token(yoAccess):
        
        try:
            logging.info('Refreshing Token ')
            now = int(time.time())
            #if yoAccess.token == None:
            response = requests.post( yoAccess.tokenURL,
                data={"grant_type": "refresh_token",
                    "client_id" :  yoAccess.uaID,
                    "refresh_token":yoAccess.token['refresh_token'],
                    }
            )
            yoAccess.token =  response.json()
            yoAccess.token['expirationTime'] = int(yoAccess.token['expires_in']) + now 

            #if temp['access_token'] != yoAccess.token['access_token'] :
            #    yoAccess.token = temp
            #    yoAccess.client.username_pw_set(username=yoAccess.token['access_token'], password=None)
            #    #need to check if device tokens change with new access token
            return(True)

        except Exception as e:
            logging.debug('Exeption occcured during refresh_token : {}'.format(e))
            return(yoAccess.request_new_token())

    def get_access_token(yoAccess):
        yoAccess.tokenLock.acquire()
        now = int(time.time())
        if yoAccess.token == None:
            yoAccess.request_new_token()
        if now > yoAccess.token['expirationTime']  - yoAccess.timeExpMarging :
            yoAccess.refresh_token()
        #    if now > yoAccess.token['expirationTime']: #we lost the token
        #        yoAccess.request_new_token()
        #    else:
        yoAccess.tokenLock.release() 

                
    def is_token_expired (yoAccess, accessToken):
        return(accessToken == yoAccess.token['access_token'])
        

    def retrieve_device_list(yoAccess):
        try:
            data= {}
            data['method'] = 'Home.getDeviceList'
            data['time'] = str(int(time.time_ns()//1e6))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ yoAccess.token['access_token']
            r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
            info = r.json()
            yoAccess.deviceList = info['data']['devices']
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
            homeId = r.json()
            yoAccess.homeID = homeId['data']['id']

        except Exception as e:
            logging.error('Exception  - retrieve_homeID: {}'.format(e))            

    def getDeviceList (yoAccess):
        return(yoAccess.deviceList)


    def shut_down(yoAccess):
        
        yoAccess.STOP.set()
        yoAccess.disconnect = True
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
            yoAccess.get_access_token()
                   
            yoAccess.client.username_pw_set(username=yoAccess.token['access_token'], password=None)
            yoAccess.client.connect(yoAccess.mqttURL, yoAccess.mqttPort, keepalive= 30) # ping server every 30 sec
            yoAccess.connectedToBroker = True
            time.sleep(5)              
            yoAccess.client.loop_start()

            #yoAccess.client.will_set()

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
            time.sleep(3)

    def process_message(yoAccess):

        while not yoAccess.STOP.is_set():
            try:
                #yoAccess.messageLock.acquire()
                msg = yoAccess.messageQueue.get(timeout = 10) 
                logging.debug('Received message - Q size={}'.format(yoAccess.messageQueue.qsize()))
                payload = json.loads(msg.payload.decode("utf-8"))
                deviceId = 'unknown'

                if 'targetDevice' in payload:
                    deviceId = payload['targetDevice']
                elif 'deviceId' in payload:
                    deviceId = payload['deviceId']
                else:
                    logging.debug('Unknow device in payload : {}'.format(payload))

                logging.debug('process_message for {}: {} {}'.format(deviceId, msg.topic, payload))
                #DEBUG = logging.root.level <= logging.DEBUG
                if deviceId in yoAccess.mqttList:

                    tempCallback = yoAccess.mqttList[deviceId]['callback']
                    
                    #if payload['msgid'] in yoAccess.pendingDict:
                    #    yoAccess.pendingDict.pop(payload['msgid'] )
                    #    logging.debug('POP {} yoAccess.pendingDict {}:{}'.format(payload['msgid'] ,len(yoAccess.pendingDict), yoAccess.pendingDict))
                    if  msg.topic == yoAccess.mqttList[deviceId]['report']:                    
                        tempCallback(payload)
                        if DEBUG:
                                fileData= {}
                                fileData['type'] = 'EVENT'
                                fileData['data'] = payload 
                                yoAccess.fileQueue.put(fileData)

                    elif msg.topic == yoAccess.mqttList[deviceId]['response']:
                        if payload['code'] == '000000':
                            tempCallback(payload)
                        else:
                            logging.error('Non-000000 code {}: {}'.format(payload['desc'], str(json.dumps(payload))))
                            tempCallback(payload)
                        if DEBUG:
                            fileData= {}
                            fileData['type'] = 'RESP'
                            fileData['data'] = payload 
                            yoAccess.fileQueue.put(fileData)
                            
                    elif msg.topic == yoAccess.mqttList[deviceId]['request']:
                        #transmitted message
                        if DEBUG:
                            fileData= {}
                            fileData['type'] = 'REQ'
                            fileData['data'] = payload
                            yoAccess.fileQueue.put(fileData)

                    else:
                        logging.error('Topic not mathing:' + msg.topic + '  ' + str(json.dumps(payload)))
                        if DEBUG:
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
        yoAccess.messageQueue.put(msg)
        logging.debug('Message: {}'.format(json.loads(msg.payload.decode("utf-8"))) )
        logging.debug('Message received and put in queue (size : {})'.format(yoAccess.messageQueue.qsize()))

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
            logging.debug('on_connect -Connected with result code {}'.format(rc))

            if (rc == 0):
                yoAccess.online = True
                logging.info('Successfully connected to broker {} '.format(yoAccess.mqttURL))
                if not yoAccess.connectedToBroker:
                    logging.debug('Re-subscribing devices after after disconnect')
                    for deviceId in yoAccess.mqttList:
                        yoAccess.client.subscribe(yoAccess.mqttList[deviceId]['request'],2)
                        yoAccess.client.subscribe(yoAccess.mqttList[deviceId]['response'],2)
                        yoAccess.client.subscribe(yoAccess.mqttList[deviceId]['report'],2)
                    yoAccess.connectedToBroker = True
                    #yoAccess.clean_up_pending_Dict()
                    time.sleep(5)
            elif (rc >= 5):
                logging.error('Authentication error 5 - check credentials and try again  ')
                if yoAccess.connectedToBroker: # Already connected - need to disconnect before reconnecting
                    #yoAccess.client.reconnect()
                    #yoAccess.client.loop_stop()
                    yoAccess.get_access_token()                  
                    time.sleep(2)
                    #yoAccess.connectedToBroker = False
                netid = yoAccess.check_connection(yoAccess.mqttPort)
                logging.debug('netid = {}'.format(netid))
                if None == netid:
                    restart = True
                    yoAccess.connectedToBroker = False
                else:
                    restart = False
                if restart:
                    logging.info('Connection lost - disconnecting to force reconnect')
                    
                    #yoAccess.disconnect = False
                    yoAccess.client.loop_stop()
                    yoAccess.client.disconnect()
                    yoAccess.connectedToBroker = False
                else:
                    logging.debug('Connection status = {}'.format(netid.status))
                yoAccess.online = False
            else:
                logging.error('Broker connection failed with result code {}'.format(rc))
                yoAccess.connectedToBroker = True
                yoAccess.online = False
                #yoAccess.connect_to_broker()
                #os.exit(2)
            #time.sleep(1)
            #logging.debug('Subsribe: ' + yoAccess.topicResp + ', '+yoAccess.topicReport+', '+ yoAccess.topicReportAll )

        except Exception as E:
            logging.error('Exception  -  on_connect: ' + str(E))       


    def on_disconnect(yoAccess, client, userdata,rc=0):
        logging.debug('Disconnect - stop loop')
        yoAccess.connectedToBroker = False
        yoAccess.disconnect_occured = True
        if yoAccess.disconnect:
            logging.debug('Disconnect - stop loop')
            yoAccess.client.loop_stop()
            
        else:
            logging.debug('Unintentional disconnect - Reacquiring connection')

            try:
                #netid = yoAccess.check_connection(yoAccess.mqttPort)
                #if None == netid:
                #    restart = True
                #elif netid.status.__contains__('ESTABLISHED'):
                #    restart = False
                #else:
                #    restart = False
                if not yoAccess.connectedToBroker:
                    #yoAccess.client.loop_stop() 
                    #yoAccess.client.disconnect()     
                    yoAccess.get_access_token()               
                    time.sleep(2)
                    #yoAccess.connectedToBroker = False
                    yoAccess.token = None
                    yoAccess.connect_to_broker()
                    yoAccess.connectedToBroker = True
                yoAccess.online = False
                time.sleep(3)   

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
                    #yoAccess.pendingDict[data['time']] = data
                    #logging.debug('PUT yoAccess.pendingDict {}'.format(len(yoAccess.pendingDict)))
                    #logging.debug('publish result: {}'.format(result.rc))

                # should not be needed - on_message should pick it up
                else:
                    logging.error('device {} not in mqtt list'.format(deviceId))

                    return (False)
                
                #if DEBUG:
                #    fileData = {}
                #    fileData['type'] = 'REQ'
                #    fileData['data'] = data
                #    yoAccess.fileQueue.put(fileData)
                
                if result.rc != 0:
                    logging.error('Error {} during publishing {}'.format(result.rc, data))
                    #errorCount = errorCount + 1
                    if result.rc == 4 or result.rc == 3: #off line
                        logging.debug('rc = {}'.format(result.rc))
                        yoAccess.online = False
                        #yoAccess.client.reconnect() # is this the right strategy 

                        #logging.debug( 'publish_data: {} - {}'.format(yoAccess.mqttList[deviceId]['request'], dataStr))
                        #result = yoAccess.client.publish(yoAccess.mqttList[deviceId]['request'], dataStr)

                else:
                    yoAccess.lastTransferTime = time.time()
                    yoAccess.online = True
            except Exception as e:
                #logging.debug('Data  Queue looping {}'.format(e))
                # Check if no activity for a while - 
                if yoAccess.lastTransferTime + yoAccess.timeExpMarging + 900 <= time.time():
                    logging.info('No Activity in {} sec - trying to reacquire token'.format(time.time() - yoAccess.lastTransferTime))
                    yoAccess.get_access_token() 
                    yoAccess.client.username_pw_set(username=yoAccess.token['access_token'], password=None)
                    yoAccess.client.reconnect()
                    #yoAccess.client.loop_stop()
                    #yoAccess.client.disconnect()
                    #yoAccess.connect_to_broker()
                    yoAccess.lastTransferTime = time.time()
                    time.sleep(60)

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

class YoLinkInitCSID(object):
    def __init__(yoAccess,  csName, csid, csSeckey, yoAccess_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003 ):
        yoAccess.csName = csName
        yoAccess.csid = csid
        yoAccess.cssSeckey = csSeckey
        yoAccess.apiType = 'CSID'