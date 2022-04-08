#!/usr/bin/env python3


import requests
import time
import json
from threading import Lock
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

countdownTimerUpdateInterval_G = 10
from OLD.yolink_mqtt_clientV3 import YoLinkMQTTClient


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
        yoAccess.token = None
        while not yoAccess.request_new_token( ):
            time.sleep(60)
            logging.info('Waiting to acquire access token')
        yoAccess.retrieve_device_list()
        yoAccess.retrieve_homeID()

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
        return(yoAccess.token['access_token'])
                
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




class YoLinkInitCSID(object):
    def __init__(yoAccess,  csName, csid, csSeckey, yoAccess_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003 ):
        yoAccess.csName = csName
        yoAccess.csid = csid
        yoAccess.cssSeckey = csSeckey
        yoAccess.apiType = 'CSID'