#!/usr/bin/env python3
import requests
import time
import json
import psutil
import sys
import math

from yolink_logging import BUSY, OFFLINE

from  datetime import datetime
try:
    import udi_interface
    logging = udi_interface.LOGGER
    #logging = getlogger('yolink_init_V4')
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
from queue import Queue, Empty
from threading import Thread, Event, Lock
DEBUG = False

SENSITIVE_LOG_KEYS = {
    'access_token',
    'refresh_token',
    'token',
    'authorization',
    'client_secret',
    'secret_key',
    'password',
    'secid',
    'uaid',
}


def _mask_secret(value, keep=4):
    text = str(value)
    if len(text) <= keep:
        return '*' * len(text)
    return f"***{text[-keep:]}"


def _redact_log_value(value):
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_LOG_KEYS:
                redacted[key] = _mask_secret(item)
            else:
                redacted[key] = _redact_log_value(item)
        return redacted

    if isinstance(value, list):
        return [_redact_log_value(item) for item in value]

    return value


def _response_log_summary(response):
    summary = {
        'ok': response.ok,
        'status_code': response.status_code,
    }
    try:
        summary['body'] = _redact_log_value(response.json())
    except ValueError:
        summary['body'] = '<non-json response>'
    return summary


def _summarize_device_list(device_list):
    devices = []
    for device in device_list:
        if not isinstance(device, dict):
            continue
        devices.append({
            'deviceId': device.get('deviceId'),
            'name': device.get('name'),
            'type': device.get('type'),
            'modelName': device.get('modelName'),
            'parentDeviceId': device.get('parentDeviceId'),
            'serviceZone': device.get('serviceZone'),
        })
    return {'count': len(devices), 'devices': devices}


class YoLinkInitPAC(object):
    def __init__(yoAccess, ID, secret, tokenURL='https://api.yosmart.com/open/yolink/token' , apiURL='https://api.yosmart.com/open/yolink/v2/api', mqttURL= 'api.yosmart.com', mqttPort = 8003, home_id = None):
        yoAccess.RETRY_STEP = 5
        yoAccess.homeID  = home_id
        yoAccess.disconnect_occured = False 
        yoAccess.tokenLock = Lock()
        yoAccess.fileLock = Lock()
        yoAccess.TimeTableLock = Lock()
        yoAccess.processing_access = Lock()
        yoAccess.retryLock = Lock()
        yoAccess.publishQueue = Queue()
        yoAccess.finishQueue = Queue()
        yoAccess.retryQueue = Queue()
        yoAccess.retryIndex = {}
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
        yoAccess.apiv2URL = apiURL
        yoAccess.mqttURL = mqttURL
        yoAccess.mqttPort = mqttPort
        yoAccess.connectedToBroker = False
        yoAccess.loopRunning = False
        yoAccess.uaID = ID
        yoAccess.secID = secret
        if home_id is None:
            yoAccess.access_mode = ['cloud']
            yoAccess.local = False
        else:
            yoAccess.access_mode = ['local']
            yoAccess.local = True
            yoAccess.local_client_id = ID 
            yoAccess.local_client_secret = secret
            yoAccess.local_URL = ''
            yoAccess.local_port_str = ':1080'
            yoAccess.local_client_id = ID
            yoAccess.local_client_secret = secret
        yoAccess.tokenExpTime = 0
        yoAccess.timeExpMarging = 3600 # 1 hour - most devices report once per hour
        yoAccess.lastTransferTime = int(time.time())
        yoAccess.lastPublishTime_ns = 0  # tracks last MQTT publish time (ns) for inter-publish spacing
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
        yoAccess.mqtt_str = ''
        yoAccess.QoS = 1
        yoAccess.keepAlive = 60
        yoAccess.MAX_RETRY = 5


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
            #while not yoAccess.refresh_token():
            #    time.sleep(35) # Wait 35 sec and try again - 35 sec ensures less than 10 attemps in 5min - API restriction
            #    logging.info('Trying to obtain new Token - Network/YoLink connection may be down')
            #logging.info('Retrieving YoLink API info')
            time.sleep(1)
            logging.debug(
                'Start info: home_id=%s mqtt=%s:%s keepalive=%s token_present=%s',
                yoAccess.homeID,
                yoAccess.mqttURL,
                yoAccess.mqttPort,
                yoAccess.keepAlive,
                yoAccess.token is not None,
            )
            if 'cloud' in yoAccess.access_mode:
                while not yoAccess.refresh_token():
                    time.sleep(35) # Wait 35 sec and try again - 35 sec ensures less than 10 attemps in 5min - API restriction
                    logging.log(OFFLINE, 'Trying to obtain new token - network or YoLink connection may be down')
                logging.info('Retrieving YoLink API info')
                time.sleep(1)
                yoAccess.mqtt_str = 'yl-home/'
                logging.debug(
                    'cloud mode topic_prefix=%s token=%s',
                    yoAccess.mqtt_str,
                    _redact_log_value(yoAccess.token),
                )
                if yoAccess.token != None:
                    yoAccess.retrieve_homeID()                    
                    yoAccess.retrieve_device_list()
            else:
                yoAccess.mqtt_str = 'ylsubnet/'   
            logging.debug(f'initialize MQTT {yoAccess.homeID}' )
            #try:
            yoAccess.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, yoAccess.homeID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            #except Exception as e:
            #    logging.debug('Using non pG3x code {e}')
            #    yoAccess.client = mqtt.Client(yoAccess.homeID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            logging.debug(
                'MQTT info: home_id=%s mqtt=%s:%s keepalive=%s token=%s',
                yoAccess.homeID,
                yoAccess.mqttURL,
                yoAccess.mqttPort,
                yoAccess.keepAlive,
                _redact_log_value(yoAccess.token),
            )
            yoAccess.client.on_connect = yoAccess.on_connect
            yoAccess.client.on_message = yoAccess.on_message
            yoAccess.client.on_subscribe = yoAccess.on_subscribe
            yoAccess.client.on_disconnect = yoAccess.on_disconnect
            yoAccess.client.on_publish = yoAccess.on_publish
            #logging.debug('finish subscribing ')

            while not yoAccess.connect_to_broker():
                time.sleep(2)
            yoAccess.stop_queues = False    
            yoAccess.start_retry_queue()
  
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
        logging.debug(f'{yoAccess.access_mode} check_connection: port {port}')
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
        logging.debug('Device list summary: %s', _summarize_device_list(yoAccess.deviceList))
        return(yoAccess.deviceList)

    '''
    #@measure_time
    def request_new_token(yoAccess):
        logging.debug('yoAccess Token exists : {}'.format(yoAccess.token != None))
        now = int(time.time())
        if yoAccess.token == None:
            try:
                now = int(time.time())
                yoAccess.time_tracking('global')
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
                logging.error('Exception occcured during request_new_token : {}'.format(e))
                return(False)
        else:
            yoAccess.refresh_token()  
            return(True) # use existing Token 
    '''

    #@measure_time
    def token_needs_refresh(yoAccess):
        if yoAccess.token is None:
            return True

        expiration_time = yoAccess.token.get('expirationTime')
        if expiration_time is None:
            return True

        now = int(time.time())
        return now >= (expiration_time - yoAccess.timeExpMarging)

    #@measure_time
    def refresh_token(yoAccess):
        
        try:
            logging.info(f'{yoAccess.access_mode} Refreshing token; token_present={yoAccess.token is not None}')
            now = int(time.time())
            
            if yoAccess.token != None:
                if now < yoAccess.token.get('expirationTime', 0):
                    yoAccess.time_tracking('global')
                    response = requests.post( yoAccess.tokenURL,
                        data={"grant_type": "refresh_token",
                            "client_id" :  yoAccess.uaID,
                            "refresh_token":yoAccess.token['refresh_token'], 
                            }, timeout= 5
                    )
                else:
                    yoAccess.time_tracking('global')
                    response = requests.post( yoAccess.tokenURL,
                        data={"grant_type": "client_credentials",
                            "client_id" : yoAccess.uaID,
                            "client_secret" : yoAccess.secID }, timeout= 5
                )
                logging.debug('Refresh response: %s', _response_log_summary(response))
                if response.ok:
                    token_data = response.json()
                    if 'access_token' not in token_data:
                        logging.error(f'Auth failed from YoLink API: {token_data}')
                        return False
                    yoAccess.token = token_data
                    yoAccess.token['expirationTime'] = int(yoAccess.token['expires_in']) + now
                    return True
                else:
                    logging.error('Was not able to refresh token')
                    return(False)
            else:
                yoAccess.time_tracking('global')
                response = requests.post( yoAccess.tokenURL,
                    data={"grant_type": "client_credentials",
                        "client_id" : yoAccess.uaID,
                        "client_secret" : yoAccess.secID }, timeout= 5
                )
                logging.debug('Refresh response: %s', _response_log_summary(response))
                if response.ok:
                    token_data = response.json()
                    if 'access_token' not in token_data:
                        logging.error(f'Auth failed from YoLink API: {token_data}')
                        return False
                    yoAccess.token = token_data
                    yoAccess.token['expirationTime'] = int(yoAccess.token['expires_in']) + now
                    return True
                else:
                    logging.error('Was not able to refresh token')
                    return False



        except Exception as e:
            logging.error(f'Exception occcured during refresh_token {yoAccess.access_mode} : {e}')
            #return(yoAccess.request_new_token())

   


    #@measure_time
    def get_access_token(yoAccess):
        yoAccess.tokenLock.acquire()
        #now = int(time.time())
        if yoAccess.token == None:
            yoAccess.refresh_token()
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
            logging.debug(f' {yoAccess.access_mode} retrieve_device_list')
            data= {}
            data['method'] = 'Home.getDeviceList'
            data['time'] = str(int(time.time_ns()/1e6))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ yoAccess.token['access_token']
            yoAccess.time_tracking('global')
            r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1, timeout=5) 
            info = r.json()
            logging.debug('retrieve_device_list summary: %s', _summarize_device_list(info.get('data', {}).get('devices', [])))
            
            if 'cloud' in yoAccess.access_mode:
                yoAccess.deviceList = info['data']['devices']
            elif 'local' in yoAccess.access_mode:
                yoAccess.deviceList = info['data']['devices']
            logging.debug('%s device list summary: %s', yoAccess.access_mode, _summarize_device_list(yoAccess.deviceList))
                       
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

            yoAccess.time_tracking('global')
            r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1, timeout=5) 
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
    #def getDeviceList (yoAccess):
    #    return(yoAccess.deviceList)

    #@measure_time
    def shut_down(yoAccess):
        try:
            yoAccess.disconnect = True
            if yoAccess.client:
                yoAccess.STOP.set()
                yoAccess.client.disconnect()
                yoAccess.client.loop_stop()
                yoAccess.stop_queues = True
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
            logging.info(f"{yoAccess.access_mode} Connecting to broker...")
            while yoAccess.token_needs_refresh() and not yoAccess.refresh_token():
                time.sleep(35) # Wait 35 sec and try again (35sec ensure less than 10 attempts in 5 min)
                logging.log(OFFLINE, 'Trying to obtain new token - network or YoLink connection may be down')
            logging.info('Retrieving YoLink API info')
            #yoAccess.retrieve_device_list()
            #yoAccess.retrieve_homeID()
            time.sleep(1)
            logging.debug(
                'Connect info: mode=%s mqtt=%s:%s keepalive=%s token=%s',
                yoAccess.access_mode,
                yoAccess.mqttURL,
                yoAccess.mqttPort,
                yoAccess.keepAlive,
                _redact_log_value(yoAccess.token),
            )
            if 'cloud' in yoAccess.access_mode:
                logging.debug('cloud connect using access token')
                yoAccess.client.username_pw_set(username=yoAccess.token['access_token'], password=None)
            elif 'local' in yoAccess.access_mode:
                logging.debug('local connect using configured client credentials')
                yoAccess.client.username_pw_set(username=yoAccess.local_client_id, password=yoAccess.local_client_secret)

            logging.debug(
                'Connect 2 info: mqtt=%s:%s keepalive=%s token=%s',
                yoAccess.mqttURL,
                yoAccess.mqttPort,
                yoAccess.keepAlive,
                _redact_log_value(yoAccess.token),
            )
            temp = yoAccess.client.connect(yoAccess.mqttURL, yoAccess.mqttPort, keepalive= yoAccess.keepAlive)
            logging.debug(f'yoAccess.client.connect: {temp}' )  

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
            logging.error(f'Exception {yoAccess.access_mode}  - connect_to_broker: {e}')
            #if yoAccess.token == None:
            #    yoAccess.request_new_token()
            #else:
            #    yoAccess.refresh_token()
            return(False)

    #@measure_time
    def _classify_callback_route(yoAccess, payload):
        schedule_actions = {
            'getSchedules', 'setSchedules',
            'getLeakSchedules', 'setLeakSchedules',
            'getValveSchedules', 'setValveSchedules',
        }

        if not isinstance(payload, dict):
            return('default')

        for key in ['method', 'event']:
            value = payload.get(key)
            if isinstance(value, str):
                action = value.split('.')[-1]
                if action in schedule_actions:
                    return('schedule')

        return('default')

    def _get_callback_entries(yoAccess, deviceId):
        if deviceId not in yoAccess.mqttList:
            return([])

        callback_entries = yoAccess.mqttList[deviceId].get('callbacks', [])
        normalized_entries = []

        for entry in callback_entries:
            if callable(entry):
                normalized_entries.append({'callback': entry, 'route_filter': 'default'})
            elif isinstance(entry, dict) and callable(entry.get('callback')):
                normalized_entries.append({
                    'callback': entry['callback'],
                    'route_filter': entry.get('route_filter', 'default'),
                })

        if len(normalized_entries) == 0:
            tempCallback = yoAccess.mqttList[deviceId].get('callback')
            if callable(tempCallback):
                normalized_entries.append({'callback': tempCallback, 'route_filter': 'default'})

        return(normalized_entries)

    def subscribe_mqtt(yoAccess, deviceId, callback, route_filter='default') -> bool:

        logging.info(f'{yoAccess.access_mode} Subscribing deviceId {deviceId} to MQTT {yoAccess.mqtt_str}+{ yoAccess.homeID}')
        topicReq = yoAccess.mqtt_str +yoAccess.homeID+'/'+ deviceId +'/request'
        topicResp = yoAccess.mqtt_str +yoAccess.homeID+'/'+ deviceId +'/response'
        topicReport = yoAccess.mqtt_str+ yoAccess.homeID+'/'+ deviceId +'/report'
        #topicReportAll = 'yl-home/'+yoAccess.homeID+'/+/report'
        logging.debug('Subscribing to topics: {} {} {}'.format(topicReq, topicResp, topicReport))

        if not deviceId in yoAccess.mqttList :
            # Do NOT subscribe to the device request topic to avoid receiving our own published requests.
            # Subscribe only to responses and reports from the device.
            yoAccess.client.subscribe(topicResp, yoAccess.QoS)
            yoAccess.client.subscribe(topicReport,  yoAccess.QoS)

            yoAccess.mqttList[deviceId] = { 'callback': callback,
                                            'callbacks': [{'callback': callback, 'route_filter': route_filter}],
                                            'request': topicReq,
                                            'response': topicResp,
                                            'report': topicReport,
                                            'subscribed': True
                                            }
            time.sleep(1)
        else:
            callback_list = yoAccess.mqttList[deviceId].setdefault('callbacks', [])
            callback_exists = False
            for entry in callback_list:
                if isinstance(entry, dict):
                    if entry.get('callback') == callback and entry.get('route_filter', 'default') == route_filter:
                        callback_exists = True
                        break
                elif entry == callback and route_filter == 'default':
                    callback_exists = True
                    break

            if not callback_exists:
                callback_list.append({'callback': callback, 'route_filter': route_filter})
            if 'callback' not in yoAccess.mqttList[deviceId] and len(callback_list) > 0:
                first_entry = callback_list[0]
                if isinstance(first_entry, dict):
                    yoAccess.mqttList[deviceId]['callback'] = first_entry.get('callback')
                else:
                    yoAccess.mqttList[deviceId]['callback'] = first_entry
        return(True)

    #@measure_time
    def update_mqtt_subscription (yoAccess, deviceId):
        logging.info(f'{yoAccess.access_mode} update_mqtt_subscription {deviceId}')
        topicReq = yoAccess.mqtt_str +yoAccess.homeID+'/'+ deviceId +'/request'
        topicResp = yoAccess.mqtt_str +yoAccess.homeID+'/'+ deviceId +'/response'
        topicReport = yoAccess.mqtt_str +yoAccess.homeID+'/'+ deviceId +'/report'
        #topicReportAll = yoAccess.mqtt_str +yoAccess.homeID+'/+/report'
        logging.debug('update_mqtt_subscription to topics: {} {} {}'.format(topicReq, topicResp, topicReport))

        if  deviceId in yoAccess.mqttList :
            logging.debug('unsubscribe {}'.format(deviceId))
            # Do not unsubscribe/subscribe to request topic (we don't subscribe to it).
            yoAccess.client.unsubscribe(yoAccess.mqttList[deviceId]['response'] )
            yoAccess.client.unsubscribe(yoAccess.mqttList[deviceId]['report'] )
            
            logging.debug('re-subscribe {}'.format(deviceId))
            yoAccess.client.subscribe(topicResp, yoAccess.QoS)
            yoAccess.client.subscribe(topicReport, yoAccess.QoS)
            yoAccess.mqttList[deviceId]['request'] =  topicReq
            yoAccess.mqttList[deviceId]['response'] = topicResp
            yoAccess.mqttList[deviceId]['report'] = topicReport
        #logging.debug('mqtt.list:{}.'.format(yoAccess.mqttList))


    def send_to_callback(yoAccess, deviceId, payload):
        if deviceId in yoAccess.mqttList:
            payload_route = yoAccess._classify_callback_route(payload)
            callback_entries = yoAccess._get_callback_entries(deviceId)

            matched_callbacks = []
            for entry in callback_entries:
                route_filter = entry.get('route_filter', 'default')
                if route_filter in ['all', payload_route]:
                    matched_callbacks.append(entry['callback'])

            if len(matched_callbacks) == 0 and payload_route != 'default':
                for entry in callback_entries:
                    if entry.get('route_filter', 'default') == 'default':
                        matched_callbacks.append(entry['callback'])

            for tempCallback in matched_callbacks:
                try:
                    tempCallback(payload)
                except Exception as e:
                    logging.error('Callback failed for {}: {}'.format(deviceId, e), exc_info=True)
        else:
            logging.error('Unsupported device in send_to_callback: {}'.format(deviceId))

#@measure_time
    def process_message(yoAccess):
        try:
            #yoAccess.messageLock.acquire()
            msg = yoAccess.messageQueue.get(timeout = 10) 
            #logging.debug(f'{yoAccess.access_mode} Received message - Q size={yoAccess.messageQueue.qsize()}')
            payload = json.loads(msg.payload.decode("utf-8"))
            #logging.debug('process_message : {}'.format(payload))
            
            deviceId = 'unknown'
            if 'targetDevice' in payload:
                deviceId = payload['targetDevice']
            elif 'deviceId' in payload:
                deviceId = payload['deviceId']
            else:
                logging.debug('Unknow device in payload : {}'.format(payload))

            logging.debug(
                '%s process_message for %s: payload=%s topic=%s',
                yoAccess.access_mode,
                deviceId,
                _redact_log_value(payload),
                msg.topic,
            )
            

            if deviceId not in yoAccess.mqttList:
                logging.error('Unsupported device: {}'.format(deviceId))
                return
                
            #if payload['msgid'] in yoAccess.pendingDict:
            #    yoAccess.pendingDict.pop(payload['msgid'] )
            if  msg.topic == yoAccess.mqttList[deviceId]['report']: 
                logging.debug('processing report: ')   
                yoAccess.send_to_callback(deviceId, payload)
                # Remove device from retry queue if event received from device (when device comes back on-line )
                yoAccess._clean_retry_queue(payload['deviceId'], payload['event'])#####
                if yoAccess.debug:
                        fileData= {}
                        fileData['type'] = 'EVENT'
                        fileData['data'] = payload 
                        yoAccess.fileQueue.put(fileData)
                        event_fileThread = Thread(target = yoAccess.save_packet_info )
                        event_fileThread.start()
                        logging.debug('event_fileThread - starting')


            elif msg.topic == yoAccess.mqttList[deviceId]['response']:
                return_msg={'code': None, 'msgid': None}
                if 'msgid' in payload:
                    return_msg['msgid'] = payload['msgid']
                if 'code' in payload:                           
                    return_msg['code'] = payload['code']                        
                logging.debug('finishQueue PUT: {}'.format(return_msg))
                if 'method' in payload: # only put commands in finish queue - no need to add events as they are generated by device and not node commands
                    return_msg['method'] = payload['method']
                    yoAccess.finishQueue.put(return_msg)
                    logging.debug(f'finishQueue PUT size: {yoAccess.finishQueue.qsize()}') 

                logging.debug('processing response: ')
                if 'code' in payload and payload['code'] == '000000':
                    yoAccess.send_to_callback(deviceId, payload)
                elif 'code' in payload and payload['code'] in ['000201', '020104' ]:
                    log_level = OFFLINE if payload['code'] == '000201' else BUSY
                    logging.log(log_level, 'Error code {} received for message {} - initiating retry'.format(payload['code'], payload.get('msgid', 'N/A')))
                else:
                    logging.error('Non-000000 code {} '.format(payload['desc']))
                    yoAccess.send_to_callback(deviceId, payload)
                if yoAccess.debug:
                    fileData= {}
                    fileData['type'] = 'RESP'
                    fileData['data'] = payload 
                    yoAccess.fileQueue.put(fileData)
                    resp_fileThread = Thread(target = yoAccess.save_packet_info )
                    resp_fileThread.start()
                    
                    logging.debug('resp_fileThread - starting')
                    
            elif msg.topic == yoAccess.mqttList[deviceId]['request']:
                logging.debug('processing request - no action: ')                   
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
                logging.error('Topic not matching: {} '.format(msg.topic))
                if yoAccess.debug:
                    fileData= {}
                    fileData['type'] = 'MISC'
                    fileData['data'] = payload
                    yoAccess.fileQueue.put(fileData)   
                    misc_fileThread = Thread(target = yoAccess.save_packet_info )
                    misc_fileThread.start()
                    logging.debug('misc_fileThread - starting')                                     
            #else:
            #    logging.error('Unsupported device: {}'.format(deviceId))
            #yoAccess.messageLock.release()
        except Empty: # Ensure this is imported
            logging.debug('message processing timeout - queue empty')
            pass
        except Exception as e:
            logging.error(f'process_message error: {e}', exc_info=True)
            #pass
            #yoAccess.messageLock.release()

    '''
    #@measure_time
    def process_messageORG(yoAccess):
        try:
            #yoAccess.messageLock.acquire()
            msg = yoAccess.messageQueue.get(timeout = 60) 
            logging.debug(f'{yoAccess.access_mode} Received message - Q size={yoAccess.messageQueue.qsize()}')
            payload = json.loads(msg.payload.decode("utf-8"))
            #logging.debug('process_message : {}'.format(payload))
            
            deviceId = 'unknown'
            if 'targetDevice' in payload:
                deviceId = payload['targetDevice']
            elif 'deviceId' in payload:
                deviceId = payload['deviceId']
            else:
                logging.debug('Unknow device in payload : {}'.format(payload))

            logging.debug(f'{yoAccess.access_mode} process_message for {deviceId}: {payload} {msg.topic}')
            

            if deviceId in yoAccess.mqttList:

                tempCallback = yoAccess.mqttList[deviceId]['callback']
                
                #if payload['msgid'] in yoAccess.pendingDict:
                #    yoAccess.pendingDict.pop(payload['msgid'] )
                if  msg.topic == yoAccess.mqttList[deviceId]['report']: 
                    logging.debug('processing report')   
                    tempCallback(payload)
                    # Remove device from retry queue if event received from device (when device comes back on-line )
                    yoAccess._clean_retry_queue(payload['deviceId'], payload['event'])#####
                    if yoAccess.debug:
                            fileData= {}
                            fileData['type'] = 'EVENT'
                            fileData['data'] = payload 
                            yoAccess.fileQueue.put(fileData)
                            event_fileThread = Thread(target = yoAccess.save_packet_info )
                            event_fileThread.start()
                            logging.debug('event_fileThread - starting')


                elif msg.topic == yoAccess.mqttList[deviceId]['response']:
                    return_msg={'code': None, 'msgid': None}
                    if 'msgid' in payload:
                        return_msg['msgid'] = payload['msgid']
                    if 'code' in payload:                           
                        return_msg['code'] = payload['code']                        
                    logging.debug('finishQueue PUT: {}'.format(return_msg))
                    if 'method' in payload: # only put commands in finish queue - no need to add events as they are generated by device and not node commands
                        return_msg['method'] = payload['method']
                        yoAccess.finishQueue.put(return_msg)
                        logging.debug(f'finishQueue PUT size: {yoAccess.finishQueue.qsize()}') 

                    logging.debug('processing response:')
                    if 'code' in payload and payload['code'] == '000000':
                        tempCallback(payload)
                    else:
                        logging.error('Non-000000 code {}'.format(payload['desc']))
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
                    logging.debug('processing request - no action:')                   
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
                    logging.error('Topic not matching: {}'.format(msg.topic))
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
    '''

    #@measure_time
    def on_message(yoAccess, client, userdata, msg):
        """
        Callback for broker published events
        """
        logging.debug(
            '%s on_message: %s',
            yoAccess.access_mode,
            _redact_log_value(json.loads(msg.payload.decode("utf-8"))),
        )
        yoAccess.messageQueue.put(msg)
        #qsize = yoAccess.messageQueue.qsize()
        #logging.debug('Message received and put in queue (size : {})'.format(qsize))
        logging.debug('Creating thread to handle the received messages')

        t = Thread(target = yoAccess.process_message)
        t.start()
        #threads = []
        #for idx in range(0, qsize):
        #    threads.append(Thread(target = yoAccess.process_message ))
        #  [t.start() for t in threads]
        #[t.join() for t in threads]
        logging.debug('on_message threads starting')

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
            logging.debug(f'{yoAccess.access_mode} on_connect - Connected with result code {rc}')
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
                    logging.error(f'Authentication error {rc} - Token no longer valid - Need to reconnect ')
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
                    logging.error(f'Authentication error {rc} - Token no longer valid - Need to reconnect ')
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
                    logging.error(f'Authentication error {rc} - check credentials and try again  ')




            else:
                logging.error('Broker connection failed with result code {}'.format(rc))
                yoAccess.client.disconnect()
                yoAccess.connectedToBroker = False
                yoAccess.online = False
         
        except Exception as e:
            logging.error(f'Exception {yoAccess.access_mode} -  on_connect: {e}')       

    #@measure_time
    def on_disconnect(yoAccess, client, userdata,rc=0):
        logging.debug(f'{yoAccess.access_mode} Disconnect - stop loop')
        #yoAccess.connectedToBroker = False
        yoAccess.disconnect_occured = True
        if yoAccess.disconnect:
            logging.debug('Disconnect - stop loop')
            yoAccess.client.loop_stop()
            
        else:
            logging.log(OFFLINE, 'Unintentional disconnect - Reacquiring connection')

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
                logging.error(f'Exception occcured during on_ disconnect : {e}')
                if yoAccess:
                    yoAccess.refresh_token()
                else:
                    logging.error('Lost credential info - need to restart node server')

    #@measure_time
    def on_subscribe(yoAccess, client, userdata, mID, granted_QoS):     

        logging.debug(f'{yoAccess.access_mode} on_subscribe {client} {userdata} {mID} {granted_QoS}')
        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('Granted QoS: ' +  str(granted_QoS))
        #logging.debug('\n')

    #@measure_time
    def on_publish(yoAccess, client, userdata, mID):
        logging.debug(f'{yoAccess.access_mode} on_publish {client} {userdata} {mID}')

        #logging.debug('client = ' + str(client))
        #logging.debug('userdata = ' + str(userdata))
        #logging.debug('mID = '+str(mID))
        #logging.debug('\n')


    #@measure_time
    def publish_data(yoAccess, data):
        logging.debug(
            '%s Publish Data to Queue: %s',
            yoAccess.access_mode,
            json.dumps(_redact_log_value(data), indent=4, separators=(",", ": ")),
        )
        sleeping = False
        while not yoAccess.connectedToBroker:
            logging.debug('Connection to Broker not established - waiting')
            time.sleep(1)       
            sleeping = True
        if sleeping:
            time.sleep(2) # give some time to settle after connection established

        yoAccess.publishQueue.put(data, timeout = 5)
        
        publishThread = Thread(target = yoAccess.transfer_data )
        publishThread.start()
        logging.debug(f'{yoAccess.access_mode} publishThread - starting')
        #while not yoAccess.publishQueue.empty():
        #    time.sleep(0.1)
        #    yoAccess.publishQueue.put(data, timeout = 5)
        #    publishThread = Thread(target = yoAccess.transfer_data )
        #    publishThread.start()
        #logging.debug('publishThread - starting')
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
            #logging.debug('time_track_going in: {}, {}, {}'.format(t_now, dev_id, yoAccess.time_tracking_dict))
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
            if t_delay > 0:
                logging.debug('Adding {} delay to t_now {}  =  {} to TimeTrack - dev delay={}, all_delay={}, dev2dev={}'.format(t_delay, t_now, t_now + t_delay, t_dev_delay, t_all_delay, t_dev_2_dev))
            yoAccess.time_tracking_dict[dev_id].append(t_now + t_delay)
            yoAccess.TimeTableLock.release()
            #logging.debug('TimeTrack after: time {} dev: {} delay: {} -  {}'.format(t_now, dev_id, int(math.ceil(t_delay/1000)), yoAccess.time_tracking_dict))
            return(t_delay / 1000.0)  # return fractional seconds (not ceiling) to avoid rounding 188ms up to 1s
            #return(int(math.ceil(t_delay/1000)), int(math.ceil(t_all_delay)), int(math.ceil(t_all_delay)))
        except Exception as e:
            logging.error(f' Exception Timetrack : {e}')
            yoAccess.TimeTableLock.release()
        #yoAccess.time_tracking_dict[dev_id].append(time)

    def start_retry_queue(yoAccess, ):
        logging.debug('Starting Retry Queue checking')
        retryThread = Thread(target = yoAccess.check_retry_queue )
        retryThread.start()

    def _retry_key(yoAccess, data):
        try:
            return(data['targetDevice'], data['method'])
        except Exception:
            return(None)

    def _enqueue_retry(yoAccess, data):
        """Add/merge retry item by (targetDevice, method) to avoid duplicates."""
        key = yoAccess._retry_key(data)
        if key is None:
            logging.error('Cannot enqueue retry - missing targetDevice/method: {}'.format(data))
            return(False)

        try:
            yoAccess.retryLock.acquire()
            if key in yoAccess.retryIndex:
                existing = yoAccess.retryIndex[key]
                merged_retry = max(existing.get('retry', 0), data.get('retry', 0))
                merged_last = max(existing.get('last_retry_time', 0), data.get('last_retry_time', 0))
                existing.update(data)
                existing['retry'] = merged_retry
                existing['last_retry_time'] = merged_last
                return(False)

            yoAccess.retryIndex[key] = data
            yoAccess.retryQueue.put(data, timeout = 5)
            return(True)
        finally:
            yoAccess.retryLock.release()

    def check_retry_queue(yoAccess):
        '''check_retry_queue'''
        while not yoAccess.stop_queues:
            temp_list = []
            try:    
                if not yoAccess.retryQueue.empty():
                    #logging.debug(f'{yoAccess.access_mode} - Checking retry - queue size {yoAccess.retryQueue.qsize()}  ')                
                    while not yoAccess.retryQueue.empty():
                        temp_list.append(yoAccess.retryQueue.get(timeout = 5))
                    yoAccess.retryLock.acquire()
                    yoAccess.retryIndex = {}
                    yoAccess.retryLock.release()
                    logging.debug(f'temp_retry_list {temp_list}')
                    time_now = int(time.time())
                    selected_data_list = []
                    pending_data_list = []
                    for retry_data in temp_list:
                        #selected_data = None ###
                        if 'retry' in retry_data:
                            retry_fact = min(retry_data['retry'], 12) # max 12 retries (2^12 > 1 hour)
                        else:
                            retry_fact = 0
                            retry_data['retry'] = retry_fact
                        delay = min(yoAccess.RETRY_STEP + 2**retry_fact, 3600) #double delay every iteration until 1 hour (3600 sec)
                        #logging.debug(f'{yoAccess.access_mode} delay {delay}')
                        #logging.debug(f"{yoAccess.access_mode} retry if negative { int(retry_data['last_retry_time']/1000+delay) - time_now}")
                        logging.debug('{} - target device - {} - delay {}'.format( yoAccess.access_mode, retry_data['targetDevice'], delay ))
                                                
                        if int(retry_data['last_retry_time']/1000+delay) - time_now < 0:
                            selected_data_list.append(retry_data)
                        else:
                            pending_data_list.append(retry_data)

                    for retry_data in pending_data_list:
                        yoAccess._enqueue_retry(retry_data)

                    if selected_data_list: # found data the needs to retried  
                        seen_keys = set()
                        for retry_data in selected_data_list:
                            key = yoAccess._retry_key(retry_data)
                            if key in seen_keys:
                                continue
                            seen_keys.add(key)
                            retry_attempt = retry_data.get('retry', 0) + 1
                            logging.info(
                                '%s retrying %s for %s (attempt %s)',
                                yoAccess.access_mode,
                                retry_data.get('method'),
                                retry_data.get('targetDevice'),
                                retry_attempt,
                            )
                            logging.debug(f'{yoAccess.access_mode} ADDING RETRY TO PUBLISH QUEUE {retry_data}')
                            yoAccess.publish_data(retry_data) # place selected_data in publishQueue
                            time.sleep(2) # give some time to process the publish before waiting for response
                    logging.debug(f'{yoAccess.access_mode} temp_retry_list {list (yoAccess.retryQueue.queue)}')

                time.sleep(10)   
            except Exception as e:
                logging.error('Exception check_retry_queue - {}'.format(e))
                for temp in temp_list: # restore what was processed until now
                    yoAccess._enqueue_retry(temp)
                time.sleep(5) 
                pass


    '''
    def _pick_next_retry(yoAccess):
          try:
            temp_list = []
            while not yoAccess.retryQueue.empty():
                temp_list.append(yoAccess.retryQueue.get(timeout = 5))
            first = 0
            for tmp_data in temp_list:
                if 'retry' in tmp_data:
                    retry_mult = tmp_data['retry']
                else:
                    retry_mult = 1
                if 'time' in tmp_data:
                    if first >= int(tmp_data['time'])*retry_mult*yoAccess.RETRY_STEP:
                        logging.debug(f'')


        except Exception as e:
            logging.error(f'Exception - _pick_next_retry {e}')
 
    '''
    #@measure_time
    def _clean_retry_queue(yoAccess, deviceId, method):

        try:
            temp_list = []
            while not yoAccess.retryQueue.empty():
                data = yoAccess.retryQueue.get(timeout = 5)
                if data['targetDevice'] == deviceId and data['method'] == method:                    
                    logging.debug('Removing {} from retry queue as publish was successful'.format(data))                    
                else:
                    temp_list.append(data)

            yoAccess.retryLock.acquire()
            yoAccess.retryIndex = {}
            yoAccess.retryLock.release()

            for data in temp_list:
                yoAccess._enqueue_retry(data)
        except Exception as e:
            logging.error('Exception _clean_retry_queue - {}'.format(e))
    
    #@measure_time
    def transfer_data(yoAccess):
        '''transfer_data'''
        yoAccess.lastTransferTime = int(time.time())
        
        try:
            yoAccess.processing_access.acquire()
            #while yoAccess.publishQueue.qsize() != 0:
            data = yoAccess.publishQueue.get(timeout = 10)
            logging.debug( 'transfer_data - data from publishQueue: {} - size {}'.format(data, yoAccess.publishQueue.qsize()))
            deviceId = data['targetDevice']
            method = data['method']
            #logging.debug('mqttList : {}'.format(yoAccess.mqttList))
            if deviceId in yoAccess.mqttList:
                logging.debug( 'Starting publish_data:')
                ### check if publish list is full

                # enforce minimum 210ms between any two consecutive publishes before rate-limit check
                min_gap_ns = 210_000_000  # 210 ms in nanoseconds
                since_last_ns = time.time_ns() - yoAccess.lastPublishTime_ns
                if since_last_ns < min_gap_ns:
                    time.sleep((min_gap_ns - since_last_ns) / 1e9)

                #all_delay, dev_delay =  yoAccess.time_tracking(timeNow_ms, deviceId)
                delay_s =  yoAccess.time_tracking(deviceId)
                #logging.debug( 'Needed delay: {} - {}'.format(delay, timeNow_s))
                if delay_s > 0: # some delay needed
                    logging.info('Delaying call by {}sec due to too many calls'.format(delay_s))
                    time.sleep(delay_s)
                    # As this is multi threaded we can just sleep  - if another call is ready and can go though is will so in a differnt thread
                yoAccess.lastPublishTime_ns = time.time_ns()
                data['time'] = str(int(time.time_ns()/1e6))  # update time to actual packet time (to include delays)
                message_id = data['time'] 
                dataStr = str(json.dumps(data))
                #yoAccess.tmpData[deviceId] = dataStr
                yoAccess.lastDataPacket[deviceId] = data

                logging.debug( 'publish_data: {} - {}'.format(yoAccess.mqttList[deviceId]['request'], json.dumps(data, indent=4, separators=(",", ": "))))
                result = yoAccess.client.publish(yoAccess.mqttList[deviceId]['request'], dataStr, yoAccess.QoS)
                # Do not clear retry entries yet: wait for a confirmed successful response.
                # Cleaning here can race with check_retry_queue and remove the only pending retry
                # for a command that never receives a response.
                
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
            time.sleep(0.1) # give some time to process the publish before waiting for response
            logging.debug(f'waiting for response to be received - message_id {message_id} - finishQueue GET size  {yoAccess.finishQueue.qsize()} {list(yoAccess.finishQueue.queue)}' )
            message= yoAccess.finishQueue.get(timeout = 10)
            logging.debug(f'finishQueue GET {message} size {yoAccess.finishQueue.qsize()}')
            completed_message_id = message['msgid']
            msg_code = message['code']
            logging.debug(f'transfer_data - response received message_id {message_id} completed_message_id {completed_message_id} finishQueue size {yoAccess.finishQueue.qsize()}')
            logging.debug(f'retry queue {list (yoAccess.retryQueue.queue) }')
            while message_id != completed_message_id :
                message = yoAccess.finishQueue.get(timeout = 10)
                completed_message_id = message['msgid']
                msg_code = message['code']
                logging.debug(f'while loop {message} {completed_message_id} {msg_code} size {completed_message_id} finishQueue size {yoAccess.finishQueue.qsize()}')
                logging.debug(f'transfer_data - response received message_id {message_id} completed_message_id {completed_message_id} finishQueue size {yoAccess.finishQueue.qsize()}')
            yoAccess.processing_access.release()
            if msg_code in ['000201', '020104']: # device off line or busy 
                log_level = OFFLINE if msg_code == '000201' else BUSY
                logging.log(log_level, 'Error code {} received for message {} - initiating retry'.format(msg_code, data))
                if 'retry' in data:
                    data['retry']= data['retry']+1
                    data['last_retry_time'] = int(data['time'])
                else:
                    data['retry'] = 0 # starting retry
                    data['last_retry_time'] = int(data['time'])
                yoAccess._enqueue_retry(data)
            elif msg_code in ['000000'] :
                if data is None: 
                    logging.log(BUSY, 'No data received - device not ready - initiating retry'.format( data))
                    data['retry'] = 0 # starting retry
                    data['last_retry_time'] = int(data['time'])
                    yoAccess._enqueue_retry(data)
                elif 'retry' in data and len(data) == 1:
                    data['retry']= data['retry']+1
                    data['last_retry_time'] = int(data['time'])
                    yoAccess._enqueue_retry(data)
                else:
                    yoAccess._clean_retry_queue(deviceId, method) # remove pending retries for this call 
                '''
                if not yoAccess.publishQueue.empty():
                    logging.debug('publishQueue not empty - checking if newer entries exists')
                    publish_list = list (yoAccess.publishQueue.queue) # put retry at front of queue
                    for Q_data in publish_list:
                        if Q_data['targetDevice'] == data['targetDevice']:
                            logging.debug('Newer command found for device {} - cancelling retry of {}'.format(data['targetDevice'], data))
                            return(True) # newer command exists - do not retry                
                if 'retry' in data:
                    data['retry'] = data['retry'] + 1
                else:  
                    data['retry'] = 1


                if data['retry'] <= yoAccess.MAX_RETRY: # stop after MAX_RETRY attempts
                    logging.debug('Retrying command - retry {}'.format(data['retry']))
                    logging.debug('Issuing Retry command: {}'.format(data))
                    time.sleep(5*data['retry'])
                    logging.debug('publishQueue before retry: {}'.format(list(yoAccess.publishQueue.queue)))
                    if not yoAccess.publishQueue.empty():
                        logging.debug('publishQueue not empty - checking if newer entries exists')
                        publish_list = list (yoAccess.publishQueue.queue) # put retry at front of queue
                        for Q_data in publish_list:
                            if Q_data['targetDevice'] == data['targetDevice']:
                                logging.debug('Newer command found for device {} - cancelling retry of {}'.format(data['targetDevice'], data))
                                return(True) # newer command exists - do not retry

                    data['time'] = str(int(time.time_ns()/1e6)) #update time to actual packet time
                    yoAccess.publish_data(data) # retry
                else:
                    logging.error('Max retries reached - giving up on command {}'.format(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))))
                '''
        except Exception as e:
            logging.warning('Exception No new data to publish - {}'.format(e))
            yoAccess.processing_access.release()
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

    def set_water_unit(yoAccess, unit):
        yoAccess.water_unit = unit

    def get_water_unit(yoAccess):
        return(yoAccess.water_unit)  

    def set_debug(yoAccess, debug):
        yoAccess.debug = debug


