#!/usr/bin/env python3


import requests
import time
import json
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)



class YoLinkDevicesPAC(object):
    def __init__(yoAccess, uaID, secID, tokenURL='https://api.yosmart.com/open/yoAccess/token', pacURL = 'https://api.yosmart.com/open/yoAccess/v2/api' ):
       
        yoAccess.tokenURL = tokenURL
        yoAccess.apiv2URL = pacURL
        yoAccess.uaID = uaID
        yoAccess.secID = secID
        yoAccess.timeMargin = 600
        yoAccess.tokenExpTime = 0
        yoAccess.token = None
        yoAccess.get_access_token()
        yoAccess.retrieveDeviceList()
        yoAccess.retrieveHouseID()
        
    '''
    def get_access_token(yoAccess, uaId, secret_key, url="https://api.yosmart.com/open/yoAccess/token"):
        response = requests.post(
            url,
            data={"grant_type": "client_credentials"},
            auth=(uaId, secret_key),
        )
        return response.json()

    def get_access_token(yoAccess, client_id, client_secret):
        response = requests.post(
            yoAccess.tokenURL,
            data={"grant_type": "client_credentials",
                "client_id" : client_id,
                "client_secret" :client_secret},
        )
        temp = response.json()
        yoAccess.tokenExpTime = int(time.time()) + temp['expires_in']
        yoAccess.accessToken = temp['access_token']
        yoAccess.refreshToken = temp['refresh_token']
    '''

    def request_new_token(yoAccess):
        now = time()
        response = requests.post(
                yoAccess.tokenURL,
                data={"grant_type": "client_credentials",
                    "client_id" : yoAccess.uaID,
                    "client_secret" : yoAccess.secID },
            )
        temp = response.json()
        temp['expirationTime'] = temp['expires_in'] - now
        return(temp)


    def refresh_token(yoAccess, client_id, token):
        logging.info('Refershing Token ')
        response = requests.post(
            yoAccess.tokenURL,
            data={"grant_type": "refresh_token",
                "client_id" : client_id,
                "refresh_token":yoAccess.refreshToken,
                }
        )
        return( response.json())
        #yoAccess.tokenExpTime = str(int(time.time())) + temp['expires_in']
        #yoAccess.accessToken = temp['access_token']
        #yoAccess.refreshToken = temp['refresh_token']  

        
    def get_access_token(yoAccess):
        now = int(time())
        if yoAccess.token == None:
            yoAccess.token = yoAccess.request_new_token()

        if now >= yoAccess.tokenExpTime - yoAccess.timeMargin:
            yoAccess.refresh_token()   
        
        return (yoAccess.token['access_token'])
        #response = requests.post(
        #    yoAccess.tokenURL,
        #    data={"grant_type": "client_credentials",
        #        "client_id" : yoAccess.uaID,
        #        "client_secret" : yoAccess.secID },
        #)
        #temp = response.json()
    
        #yoAccess.tokenExpTime = int(time.time()) + temp['expires_in']
        #yoAccess.accessToken = temp['access_token']
        #yoAccess.refreshToken = temp['refresh_token']




    def retrieveDeviceList(yoAccess):
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


    def retrieveHouseID(yoAccess):
        data= {}
        data['method'] = 'Home.getGeneralInfo'
        data['time'] = str(int(time.time()*1000))
        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['Authorization'] = 'Bearer '+yoAccess.accessToken

        r = requests.post(yoAccess.apiv2URL, data=json.dumps(data), headers=headers1) 
        houseId = r.json()
        logging.debug(houseId)
        yoAccess.houseID = houseId['data']['id']

    def getDeviceList (yoAccess):
        return(yoAccess.deviceList)
