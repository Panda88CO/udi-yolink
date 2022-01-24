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
    def __init__(yolink, uaID, secID, tokenURL='https://api.yosmart.com/open/yolink/token', pacURL = 'https://api.yosmart.com/open/yolink/v2/api' ):
       
        yolink.tokenURL = tokenURL
        yolink.apiv2URL = pacURL
        yolink.uaID = uaID
        yolink.secID = secID
        yolink.get_access_token(yolink.uaID,  yolink.secID )
        yolink.retrieveDeviceList()
        yolink.retrieveHouseID()
        

    def get_access_token(yolink, uaId, secret_key, url="https://api.yosmart.com/open/yolink/token"):
        response = requests.post(
            url,
            data={"grant_type": "client_credentials"},
            auth=(uaId, secret_key),
        )
        return response.json()

    def get_access_token(yolink, client_id, client_secret):
        response = requests.post(
            yolink.tokenURL,
            data={"grant_type": "client_credentials",
                "client_id" : client_id,
                "client_secret" :client_secret},
        )
        temp = response.json()
        yolink.tokenExpTime = int(time.time()) + temp['expires_in']
        yolink.accessToken = temp['access_token']
        yolink.refreshToken = temp['refresh_token']


    def refresh_token(yolink, client_id, token):
        response = requests.post(
            yolink.tokenURL,
            data={"grant_type": "refresh_token",
                "client_id" : client_id,
                "refresh_token":yolink.refreshToken,
                }
        )
        temp = response.json()
        yolink.tokenExpTime = str(int(time.time())) + temp['expires_in']
        yolink.accessToken = temp['access_token']
        yolink.refreshToken = temp['refresh_token']  


    def retrieveDeviceList(yolink):
        data= {}
        data['method'] = 'Home.getDeviceList'
        data['time'] = str(int(time.time()*1000))
        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['Authorization'] = 'Bearer '+ yolink.accessToken
        r = requests.post(yolink.apiv2URL, data=json.dumps(data), headers=headers1) 
        info = r.json()
        #logging.debug(str(info))
        yolink.deviceList = info['data']['devices']


    def retrieveHouseID(yolink):
        data= {}
        data['method'] = 'Home.getGeneralInfo'
        data['time'] = str(int(time.time()*1000))
        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['Authorization'] = 'Bearer '+yolink.accessToken

        r = requests.post(yolink.apiv2URL, data=json.dumps(data), headers=headers1) 
        houseId = r.json()
        logging.debug(houseId)
        yolink.houseID = houseId['data']['id']

    def getDeviceList (yolink):
        return(yolink.deviceList)
