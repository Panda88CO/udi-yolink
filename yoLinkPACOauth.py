#!/usr/bin/env python3


import requests
import time
import json




class YoLinkDevices(object):
    def __init__(yolink, uaId, secKey, tokenURL='https://api.yosmart.com/open/yolink/token', pacURL = 'https://api.yosmart.com/open/yolink/v2/api' ):
        yolink.token = yolink.get_access_token(uaId, secKey, tokenURL )
        data= {}
        data['method'] = 'Home.getDeviceList'
        data['time'] = str(int(time.time()*1000))
        #dataTemp = str(json.dumps(data))
        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['Authorization'] = 'Bearer '+ yolink.token['access_token']
        r = requests.post(pacURL, data=json.dumps(data), headers=headers1) 
        info = r.json()
        print(str(info))
        yolink.deviceList = info['data']['devices']
        

    def get_access_token(yolink, uaId, secret_key, url="https://api.yosmart.com/open/yolink/token"):
        response = requests.post(
            url,
            data={"grant_type": "client_credentials"},
            auth=(uaId, secret_key),
        )
        return response.json()


    def getDeviceList (yolink):
        return(yolink.deviceList)
