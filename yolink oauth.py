#!/usr/bin/env python3

#import argparse
#import os
#import sys
#import yaml as yaml
import hashlib
import time
import json
import requests
import threading
#from logger import getLogger

from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

headers = {}
data = {}

yolinkURL =  'https://api.yosmart.com/openApi' 
import logging
logging.basicConfig(level=logging.DEBUG)
#creds
client_id = '' #csID
client_secret = ' # CSSseckey
redirect_uri="https://127.0.0.1/yolink"

#oauth endpoints
authorization_base_url = "https://api.yosmart.com/oauth/v2/authorization.htm"
token_url = "https://api.yosmart.com/oauth/v2/getAccessToken.api"

from requests_oauthlib import OAuth2Session
yolink = OAuth2Session(client_id,redirect_uri=redirect_uri,scope=["create"])

#redirect
authorization_url, state = yolink.authorization_url(authorization_base_url)
print ("go", authorization_url)

#get
redirect_response = input('Paste the full redirect URL here:')
#fetch
token = yolink.fetch_token(token_url, client_secret=client_secret, authorization_response=redirect_response)



data["method"] = 'Manage.syncAccountDevice'
data["time"] = str(int(time.time()*1000))
data["params"] = {'accessToken': token['access_token']}
dataTemp = str(json.dumps(data))

headers1 = {}
headers1['Content-type'] = 'application/json'
headers1['ktt-ys-brand'] = 'yolink'
headers1['YS-CSID'] = client_id

# MD5(data + csseckey)

cskey =  dataTemp +  client_secret
cskeyUTF8 = cskey.encode('utf-8')
hash = hashlib.md5(cskeyUTF8)
hashKey = hash.hexdigest()
headers1['ys-sec'] = hashKey
headersTemp = json.dumps(headers1)

#print("Header:{0} Data:{1}\n".format(headersTemp, dataTemp))
r = requests.post(yolinkURL, data=json.dumps(data), headers=headers1) 
info = r.json()

print(str(info)+'\n')
f = open('devices.json', 'w')
json.dump(info, f)
f.close()


