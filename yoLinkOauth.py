#!/usr/bin/env python3


import requests
import time
import json
from requests_oauthlib import OAuth2Session
import hashlib


class YoLinkDevices(object):
    def __init__(yolink, clientId, client_secKey, tokenURL='https://api.yosmart.com/open/yolink/token', pacURL = 'https://api.yosmart.com/open/yolink/v2/api' ):
        yolink.redirect_uri = 'https://127.0.0.1/blablabla'
        yolink.authorization_base_url = "https://api.yosmart.com/oauth/v2/authorization.htm"
        yolink.token_url = "https://api.yosmart.com/oauth/v2/getAccessToken.api"
        yolink.yolinkURL =  'https://api.yosmart.com/openApi' 
        
        #yolink.client_id = '60dd7fa7960d177187c82039'
        yolink.client_id = clientId

        #yolink.client_secret = '3f68536b695a435d8a1a376fc8254e70'
        yolink.client_secret = client_secKey
        yolink.yolinkOauth = OAuth2Session(yolink.client_id, redirect_uri=yolink.redirect_uri,scope=["create"])
        #authorization_url, state = self.yolinkOauth.authorization_url(authorization_base_url)
       
        #token = yolink.yolinkOauth.fetch_token(yolink.token_url, client_secret=yolink.client_secret, authorization_response=yolink.redirect_response)
       
     

       
       
    def getAuthURL(yolink):
        authorization_url, state = yolink.yolinkOauth.authorization_url(yolink.authorization_base_url)
        return(authorization_url)
       
    def getToken(yolink, client_Sec, redirectResp) :   
        return(yolink.yolinkOauth.fetch_token(yolink.token_url, client_secret=client_Sec, authorization_response=redirectResp))

    '''
    def get_access_token(yolink, uaId, secret_key, url="https://api.yosmart.com/open/yolink/token"):
        response = requests.post(
            url,
            data={"grant_type": "client_credentials"},
            auth=(uaId, secret_key),
        )
        return response.json()
    '''

    def getDeviceList (yolink, token, client_id, client_sec):
        data = {}
        data["method"] = 'Manage.syncAccountDevice'
        data["time"] = str(int(time.time()*1000))
        data["params"] = {'accessToken': token['access_token']}
        dataTemp = str(json.dumps(data))

        headers1 = {}
        headers1['Content-type'] = 'application/json'
        headers1['ktt-ys-brand'] = 'yolink'
        headers1['YS-CSID'] = client_id

        # MD5(data + csseckey)

        cskey =  dataTemp +  client_sec
        cskeyUTF8 = cskey.encode('utf-8')
        hash = hashlib.md5(cskeyUTF8)
        hashKey = hash.hexdigest()
        headers1['ys-sec'] = hashKey
        #headersTemp = json.dumps(headers1)

        #print("Header:{0} Data:{1}\n".format(headersTemp, dataTemp))
        r = requests.post(yolink.yolinkURL, data=json.dumps(data), headers=headers1) 
        info = r.json()

        return(info)
