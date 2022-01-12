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



class YoLinkInitPAC(object):
    def __init__(yo_mqtt, uaID, secID, tokenURL='https://api.yosmart.com/open/yolink/token', pacURL = 'https://api.yosmart.com/open/yolink/v2/api' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003):
       
        yo_mqtt.tokenURL = tokenURL
        yo_mqtt.apiv2URL = pacURL
        yo_mqtt.mqttURL = mqtt_URL
        yo_mqtt.mqttPort = mqtt_port
        yo_mqtt.uaID = uaID
        yo_mqtt.secID = secID
        yo_mqtt.apiType = 'UAC'
        yo_mqtt.get_access_token(yo_mqtt.uaID,  yo_mqtt.secID )
        yo_mqtt.retrieve_device_list()
        yo_mqtt.retrieve_homeID()
        

    def get_access_token(yo_mqtt, uaId, secret_key, url="https://api.yosmart.com/open/yolink/token"):
        response = requests.post(
            url,
            data={"grant_type": "client_credentials"},
            auth=(uaId, secret_key),
        )
        return response.json()

    def get_access_token(yo_mqtt, client_id, client_secret):
        response = requests.post(
            yo_mqtt.tokenURL,
            data={"grant_type": "client_credentials",
                "client_id" : client_id,
                "client_secret" :client_secret},
        )
        temp = response.json()
        yo_mqtt.tokenExpTime = str(int(time.time())) + temp['expires_in']
        yo_mqtt.accessToken = temp['access_token']
        yo_mqtt.refreshToken = temp['refresh_token']


    def refresh_token(yo_mqtt, client_id, token):
        response = requests.post(
            yo_mqtt.tokenURL,
            data={"grant_type": "refresh_token",
                "client_id" : client_id,
                "refresh_token":yo_mqtt.refreshToken,
                }
        )
        temp = response.json()
        yo_mqtt.tokenExpTime = str(int(time.time())) + temp['expires_in']
        yo_mqtt.accessToken = temp['access_token']
        yo_mqtt.refreshToken = temp['refresh_token']  

    def is_token_expired (yo_mqtt, accessToken):
        return(accessToken == yo_mqtt.accessToken)
        


    def retrieve_device_list(yo_mqtt):
        data= {}
        data['method'] = 'Home.getDeviceList'
        data['time'] = str(int(time.time()*1000))
        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['Authorization'] = 'Bearer '+ yo_mqtt.accessToken
        r = requests.post(yo_mqtt.apiv2URL, data=json.dumps(data), headers=headers1) 
        info = r.json()
        #logging.debug(str(info))
        yo_mqtt.deviceList = info['data']['devices']


    def retrieve_homeID(yo_mqtt):
        data= {}
        data['method'] = 'Home.getGeneralInfo'
        data['time'] = str(int(time.time()*1000))
        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['Authorization'] = 'Bearer '+yo_mqtt.accessToken

        r = requests.post(yo_mqtt.apiv2URL, data=json.dumps(data), headers=headers1) 
        homeId = r.json()
        logging.debug(homeId)
        yo_mqtt.houseID = homeId['data']['id']

    def getDeviceList (yo_mqtt):
        return(yo_mqtt.deviceList)




class YoLinkInitCSID(object):
    def __init__(yo_mqtt,  csName, csid, csSeckey, yo_mqtt_URL ='https://api.yosmart.com/openApi' , mqtt_URL= 'api.yosmart.com', mqtt_port = 8003 ):
        yo_mqtt.csName = csName
        yo_mqtt.csid = csid
        yo_mqtt.cssSeckey = csSeckey
        yo_mqtt.apiType = 'CSID'