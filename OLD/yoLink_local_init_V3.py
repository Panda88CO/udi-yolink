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


#import paho.mqtt.client as mqtt
from queue import Queue
from threading import Thread, Event, Lock
DEBUG = False


class YoLinkInitLocal(object):
    def __init__(self, client_id, client_secret, local_ip,  localPort = 1080):
        self.disconnect_occured = False 
        #self.tokenLock = Lock()
        #self.fileLock = Lock()
        #self.TimeTableLock = Lock()
        #self.publishQueue = Queue()
        #self.delayQueue = Queue()
        #self.messageQueue = Queue()
        #self.fileQueue = Queue()
        #self.timeQueue = Queue()
        #self.MAX_MESSAGES = 100  # number of messages per self.MAX_TIME
        #self.MAX_TIME = 30      # Time Window
        #self.time_tracking_dict = {} # structure to track time so we do not violate yolink publishing requirements
        #self.debug = False
        #self.pendingDict = {}
        #self.pending_messages = 0
        #self.time_since_last_message_RX = 0
        #self.tokenURL = tokenURL
        #self.apiv2URL = pacURL
        #self.mqttURL = mqttURL
        #self.mqttPort = mqttPort

        #self.connectedToBroker = False
        #self.loopRunning = False
        #self.uaID = uaID
        #self.secID = secID
        self.apiType = 'LOCAL'
        self.tokenExpTime = 0
        self.timeExpMarging = 3600 # 1 hour - most devices report once per hour
        self.lastTransferTime = int(time.time())

        self.local_URL = ''
        self.local_port = ':' + str(localPort)
        self.local_client_id = client_id
        self.local_client_secret = client_secret
        self.local_ip = local_ip
        self.local_token = None
                
        #self.timeExpMarging = 7170 #min for testing 
        self.tmpData = {}
        self.lastDataPacket = {}
        #self.mqttList = {}
        self.TtsMessages = {}
        self.nbrTTS = 0
        self.temp_unit = 0
        self.online = False
        self.deviceList = []
        self.token = None
        
        self.QoS = 1
        self.keepAlive = 60


        self.unassigned_nodes = []

        self.initializeLocalAccess(self.local_client_id, self.local_client_secret, self.local_ip)
        self.refreshLocalAccess()
        self.get_local_device_list()
        logging.debug(f'Local device list {self.deviceList}')


        '''
        try:
            #while not self.request_new_token( ):
            #    time.sleep(60)
            #    logging.info('Waiting to acquire access token')
           
            #self.retrieve_device_list()
            #self.retrieve_homeID()

            self.retryNbr = 0
            self.disconnect = False
            self.STOP = Event()

            #self.messageThread = Thread(target = self.process_message )
            #self.publishThread = Thread(target = self.transfer_data )
            #self.fileThread =  Thread(target = self.save_packet_info )
            #self.connectionMonitorThread = Thread(target = self.connection_monitor)

            #self.messageThread.start()
            #self.publishThread.start()
            #self.fileThread.start()
            

            logging.info('Connecting to YoLink MQTT server')
            while not self.refresh_token():
                time.sleep(35) # Wait 35 sec and try again - 35 sec ensures less than 10 attemps in 5min - API restriction
                logging.info('Trying to obtain new Token - Network/YoLink connection may be down')
            logging.info('Retrieving YoLink API info')
            time.sleep(1)
            if self.token != None:
                self.retrieve_homeID()
            #if self.client == None:    
      
            #logging.debug('initialize MQTT' )
            try:
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.homeID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
            except Exception as e:
                logging.error(f'Using non pG3x code {e}')
                self.client = mqtt.Client(self.homeID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")

            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            #logging.debug('finish subscribing ')

            while not self.connect_to_broker():
                time.sleep(2)
            
            #self.connectionMonitorThread.start()
            
            #logging.debug('Connectoin Established: {}'.format(self.check_connection( self.mqttPort )))
            
        except Exception as E:
            logging.error('Exception - init- MQTT: {}'.format(E))

        self.messagePending = False
        '''

    ############################
    #  Local ACCESS FUNCTIONS

    def initializeLocalAccess(self, client_id, client_secret, local_ip):
        logging.debug(f'initializeLocalAccess {client_id} {client_secret} {local_ip}')
        self.local_client_id = client_id
        self.local_client_secret = client_secret
        self.local_URL = 'http://'+local_ip+self.local_port
        response = requests.post(self.local_URL+'/open/yolink/token', 
                                 data={ "grant_type": "client_credentials",
                                        "client_id" :  self.local_client_id ,
                                        "client_secret":self.local_client_secret }, timeout= 5)
        if response.ok:
            temp = response.json()
            logging.debug('Local yoAccess Token : {}'.format(temp))
        
        if 'state' not in temp:
            self.local_token = temp
            self.local_token['expirationTime'] = int(self.local_token['expires_in'] + int(time.time()) )
            logging.debug('Local yoAccess Token : {}'.format(self.local_token ))
        else:
            if temp['state'] != 'error':
                logging.error('Authentication error')


    def refreshLocalAccess(self):
        
        try:
            logging.info('Refreshing Local Token ')
            now = int(time.time())
            if self.token != None:
                if now < self.local_token['expirationTime']:
                    response = requests.post( self.local_URL+'/open/yolink/token',
                        data={"grant_type": "refresh_token",
                            "client_id" :  self.local_client_id,
                            "refresh_token":self.local_token['refresh_token'], 
                            }, timeout= 5
                    )
                else:
                    response = requests.post( self.local_URL+'/open/yolink/token',
                                 data={ "grant_type": "client_credentials",
                                        "client_id" :  self.local_client_id ,
                                        "client_secret":self.local_client_secret }, timeout= 5)
                if response.ok:
                    if response.ok:
                        self.local_token =  response.json()
                        self.local_token['expirationTime'] = int(self.local_token['expires_in']) + now
                        return(True)
                    else:
                        logging.error('Was not able to refresh token')
                        return(False)
                else:
                    response = requests.post( self.local_URL+'/open/yolink/token',
                            data={"grant_type": "refresh_token",
                                "client_id" :  self.local_client_id,
                                "refresh_token":self.local_token['refresh_token'], 
                                }, timeout= 5
                        )
                    if response.ok:
                        self.local_token =  response.json()
                        self.local_token['expirationTime'] = int(self.local_token['expires_in']) + now
                        return(True)
                    else:
                        logging.error('Was not able to refresh token')
                        return(False)       

        except Exception as e:
            logging.debug('Exeption occcured during refresh_token : {}'.format(e))
            #return(self.request_new_token())

    def get_local_device_list(self):
        try:
            logging.debug('retrieve_device_list')
            data= {}
            data['method'] = 'Home.getDeviceList'
            data['time'] = str(int(time.time_ns()/1e6))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ self.local_token['access_token']
            r = requests.post(self.local_URL+'/open/yolink/v2/api', data=json.dumps(data), headers=headers1, timeout=5) 
            info = r.json()
            self.deviceList = info['data']['devices']
            logging.debug('yoAccess.deviceList : {}'.format(self.deviceList))
        except Exception as e:
            logging.error(f'Exception  -  retrieve_device_list : {e}')             


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
    def check_connection(self, port):
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
    def getDeviceList(self):
        logging.debug(f'Device list: {self.deviceList}')
        return(self.deviceList)

    '''
    #@measure_time
    def request_new_token(self):
        logging.debug('self Token exists : {}'.format(self.token != None))
        now = int(time.time())
        if self.token == None:
            try:
                now = int(time.time())
                response = requests.post( self.tokenURL,
                        data={"grant_type": "client_credentials",
                            "client_id" : self.uaID,
                            "client_secret" : self.secID },
                    )
                if response.ok:
                    temp = response.json()
                    logging.debug('yoAccess Token : {}'.format(temp))
                else:
                    logging.error('Error occured obtaining token - check credentials')
                    return(False)
                if 'state' not in temp:
                    self.token = temp
                    self.token['expirationTime'] = int(self.token['expires_in'] + now )
                    #logging.debug('yoAccess Token : {}'.format(self.token ))
                else:
                    if temp['state'] != 'error':
                        logging.error('Authentication error')
                return(True)

            except Exception as e:
                logging.error('Exeption occcured during request_new_token : {}'.format(e))
                return(False)
        else:
            self.refresh_token()  
            return(True) # use existing Token 
    '''

    #@measure_time
    '''
    def refresh_token(self):
        
        try:
            logging.info('Refreshing Token ')
            now = int(time.time())
            if self.token != None:
                if now < self.token['expirationTime']:
                    response = requests.post( self.tokenURL,
                        data={"grant_type": "refresh_token",
                            "client_id" :  self.uaID,
                            "refresh_token":self.token['refresh_token'], 
                            }, timeout= 5
                    )
                else:
                    response = requests.post( self.tokenURL,
                        data={"grant_type": "client_credentials",
                            "client_id" : self.uaID,
                            "client_secret" : self.secID }, timeout= 5
                )
                if response.ok:
                    self.token =  response.json()
                    self.token['expirationTime'] = int(self.token['expires_in']) + now
                    return(True)
                else:
                    logging.error('Was not able to refresh token')
                    return(False)
            else:
                response = requests.post( self.tokenURL,
                    data={"grant_type": "client_credentials",
                        "client_id" : self.uaID,
                        "client_secret" : self.secID }, timeout= 5
                )
                if response.ok:
                    self.token =  response.json()
                    self.token['expirationTime'] = int(self.token['expires_in']) + now
                    return(True)
                else:
                    logging.error('Was not able to refresh token')
                    return(False)       



        except Exception as e:
            logging.debug('Exeption occcured during refresh_token : {}'.format(e))
            #return(self.request_new_token())

    #@measure_time
    def get_access_token(self):
        self.tokenLock.acquire()
        #now = int(time.time())
        if self.token == None:
            self.refresh_token()
        #if now > self.token['expirationTime']  - self.timeExpMarging :
        #    self.refresh_token()
        #    if now > self.token['expirationTime']: #we lost the token
        #        self.request_new_token()
        #    else:
        self.tokenLock.release() 

    #@measure_time                
    def is_token_expired (self, accessToken):
        return(accessToken == self.token['access_token'])
    '''
    #@measure_time
    def retrieve_device_list(self):
        try:
            logging.debug('retrieve_device_list')
            data= {}
            data['method'] = 'Home.getDeviceList'
            data['time'] = str(int(time.time_ns()/1e6))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ self.local_token['access_token']
            r = requests.post(self.local_URL, data=json.dumps(data), headers=headers1, timeout=5) 
            info = r.json()
            deviceList = info['data']['devices']
            logging.debug(f'self.deviceList : {deviceList}')
            return (deviceList)

        except Exception as e:
            logging.error('Exception  -  retrieve_device_list : {}'.format(e))             
            return (None)
    #@measure_time
    def retrieve_homeID(self):
        try:
            data= {}
            data['method'] = 'Home.getGeneralInfo'
            data['time'] = str(int(time.time_ns()/1e6))
            headers1 = {}
            headers1['Content-type'] = 'application/json'
            headers1['Authorization'] = 'Bearer '+ self.local_token['access_token']

            r = requests.post(self.local_URL, data=json.dumps(data), headers=headers1, timeout=5) 
            logging.debug('Obtaining  homeID : {}'.format(r.ok))
            if r.ok:
                homeId = r.json()
                self.homeID = homeId['data']['id']
            else:
                self.homeID = None
                logging.error('Failed ot obtain HomeID')
        except Exception as e:
            logging.error('Exception  - retrieve_homeID: {}'.format(e))    

    def setState(self, state):
        logging.debug(self.type+' - setState')
        #if 'setState'  in self.methodList:          
        #    if state.lower() not in self.stateList:
        #        logging.error('Unknows state passed')
        #        return(False)
        if state.lower() == 'on':
            state = 'open'
        if state.lower() == 'off':
            state = 'closed'
        data = {}
        data['params'] = {}
        data['params']['state'] = state.lower()
        self.type = 'Switch'
        return(self.setDevice( data))
        #else:
        #    return(False)
   
    def setDevice(self,  data):
        logging.debug(self.type+' - setDevice')
        worked = False
        #if 'setState' in self.methodList:
        methodStr = self.type+'.setState'
        #    worked = True
        #elif 'toggle' in self.methodList:
        #    methodStr = self.type+'.toggle'
        #    worked = True
        #elif 'setAttributes' in self.methodList:
        #    methodStr = self.type+'.setAttributes'
        #    worked = True               
        #data['time'] = str(int(time.time_ns()//1e6))# we assign time just before publish
        data['method'] = methodStr
        data["targetDevice"] =  self.deviceInfo['deviceId']
        data["token"]= self.deviceInfo['token']
        logging.debug(self.type+' - setDevice -data {}'.format(data))
        if worked:
            self._callApi('POST', '')
            #while  not self.yoAccess.publish_data( data) and attempt <= maxAttempts:
            #    time.sleep(10.1) # we can only try 6 timer per minute per device 
            #    attempt = attempt + 1
            #self.yoAccess.publish_data(data)
            return(True)
        else:
            return(False)
   
    #@measure_time
    #def getDeviceList (self):
    #    return(self.deviceList)

    #@measure_time
    def shut_down(self):
        try:
            self.disconnect = True
            #if self.client:
            #    self.STOP.set()
                #self.client.disconnect()
                #self.client.loop_stop()
        except Exception as E:
            logging.error('Shut down exception {}'.format(E))
