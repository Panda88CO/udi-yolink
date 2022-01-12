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
        yoAccess.get_access_token(yoAccess.uaID,  yoAccess.secID )
        yoAccess.retrieve_device_list()
        yoAccess.retrieve_homeID()
        yoAccess.tokenExpTime = 0
        yoAccess.timeExpMarging = 600 #10min

    #def get_access_token(yoAccess, uaId, secret_key, url="https://api.yosmart.com/open/yolink/token"):
    #    currentTime = int(time.time())
    #    if currentTime > yoAccess.tokenExpTime - yoAccess.timeExpMarging :
    #        response = requests.post(
    #            url,
    #            data={"grant_type": "client_credentials"},
    #            auth=(uaId, secret_key),
    #        )
    #   return response.json()

    def get_access_token(yoAccess):
        yoAccess.lock.acquire()
        currentTime = int(time.time())
        if currentTime > yoAccess.tokenExpTime - yoAccess.timeExpMarging :
            if currentTime > yoAccess.tokenExpTime: #we loast the token
                response = requests.post(
                    yoAccess.tokenURL,
                    data={  "grant_type": "client_credentials",
                            "client_id" : yoAccess.uaID,
                            "client_secret" : yoAccess.secID,
                        }
                    )
                temp = response.json()
                yoAccess.tokenExpTime = int(time.time()) + temp['expires_in']
                yoAccess.accessToken = temp['access_token']
                yoAccess.refreshToken = temp['refresh_token']
            else:
                yoAccess.refresh_token()
        yoAccess.lock.release()
                

    def refresh_token(yoAccess):
        response = requests.post(
            yoAccess.tokenURL,
            data={"grant_type": "refresh_token",
                    "client_id" : yoAccess.uaID,
                    "refresh_token":yoAccess.refreshToken,
                }
            )
        temp = response.json()
        yoAccess.tokenExpTime = int(time.time()) + temp['expires_in']
        yoAccess.accessToken = temp['access_token']
        yoAccess.refreshToken = temp['refresh_token']  

    def is_token_expired (yoAccess, accessToken):
        return(accessToken == yoAccess.accessToken)
        


    def retrieve_device_list(yoAccess):
        data= {}
        data['method'] = 'Home.getDeviceList'
        data['time'] = str(int(time.time()*1000))
        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['Authorization'] = 'Bearer '+ yoAccess.accessToken
        r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
        info = r.json()
        #logging.debug(str(info))
        yoAccess.deviceList = info['data']['devices']


    def retrieve_homeID(yoAccess):
        data= {}
        data['method'] = 'Home.getGeneralInfo'
        data['time'] = str(int(time.time()*1000))
        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['Authorization'] = 'Bearer '+ yoAccess.accessToken

        r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
        homeId = r.json()
        logging.debug(homeId)
        yoAccess.homeID = homeId['data']['id']

    def getDeviceList (yoAccess):
        return(yoAccess.deviceList)




class YoLinkInitCSID(object):
    def __init__(yoAccess,  csName, csid, csSeckey, yoAccess_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003 ):
        yoAccess.csName = csName
        yoAccess.csid = csid
        yoAccess.cssSeckey = csSeckey
        yoAccess.apiType = 'CSID'