#!/usr/bin/env python3


import requests
import hashlib
import time
import json


client_id = '60dd7fa7960d177187c82039'
client_secret = '3f68536b695a435d8a1a376fc8254e70'
yolinkURL =  'https://api.yosmart.com/openApi' 
yolinkV2URL =  'https://api.yosmart.com/open/yolink/v2/api' 
tokenURL = "https://api.yosmart.com/open/yolink/token"
UaID = "ua_D78FFCACB1A8465ABE5279E68E201E7B"
SecID = "sec_v1_Tuqy3L7UqL/t/R3P5xpcBQ=="




def get_access_token(url, client_id, client_secret):
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    return response.json()


'''
client_id = ''
client_secret = ''
yolinkURL =  'https://api.yosmart.com/openApi' 
tokenURL = "https://api.yosmart.com/open/yolink/token"
UaID = ''
SecID = ''
'''

token = get_access_token(tokenURL, UaID, SecID)
data= {}
data['method'] = 'Home.getDeviceList'
data['time'] = str(int(time.time()*1000))
#data['params'] = {'accessToken': token['access_token']}
#data['params']={'Authorization': token['access_token']}
#data['params'] = {'bearerToken': token['access_token']}
#data['Authorization'] = token['access_token']
dataTemp = str(json.dumps(data))

headers1 = {}
headers1['Content-type'] = 'application/json'
headers1['Authorization'] = 'Bearer '+token['access_token']
#headers1['token_type'] = 'bearer'
#headers1['ktt-ys-brand'] = 'yolink'
#headers1['YS-CSID'] = client_id
'''
cskey =  dataTemp +  client_secret
cskeyUTF8 = cskey.encode('utf-8')
hash = hashlib.md5(cskeyUTF8)
hashKey = hash.hexdigest()
headers1['ys-sec'] = hashKey
headersTemp = json.dumps(headers1)
'''

#print("Header:{0} Data:{1}\n".format(headersTemp, dataTemp))
r = requests.post(yolinkV2URL, data=json.dumps(data), headers=headers1) 
info = r.json()
print(info)

f = open('devicesNew.json', 'w')
json.dump(info, f)
f.close()

'''
import requests
import time
import json

def get_access_token(url, client_id, client_secret):
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    return response.json()['access_token']

def post_command(url, method, token):
    commandData = {}
    commandData['method'] = method
    commandData['time'] = str(int(time.time()*1000))

    commandHeaders = {}
    commandHeaders['Content-type'] = 'application/json'
    commandHeaders['Authorization'] = 'Bearer ' + token

    print("Headers: {0}\nData: {1}\n".format(json.dumps(commandHeaders), json.dumps(commandData)))
    response = requests.post(
        url,
        data=json.dumps(commandData),
        headers=commandHeaders
    )
    return response.json()

#yolinkV2URL =  'https://api.yosmart.com/open/yolink/v2/api' 
#tokenURL = "https://api.yosmart.com/open/yolink/token"
#UaID = 'ua_**********'
#SecID = 'sec_v1_*********'

token = get_access_token(tokenURL, UaID, SecID)
responseData = post_command(yolinkV2URL, 'Home.getDeviceList', token)
print(responseData) 
'''