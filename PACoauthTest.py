#!/usr/bin/env python3


import requests
import hashlib
import time
import json
import sys
#from  yolink_mqtt_clientV2 import YoLinkMQTTClientV2
import paho.mqtt.client as mqtt

client_id = '60dd7fa7960d177187c82039'
client_secret = '3f68536b695a435d8a1a376fc8254e70'
yolinkURL =  'https://api.yosmart.com/openApi' 
yolinkV2URL =  'https://api.yosmart.com/open/yolink/v2/api' 
tokenURL = "https://api.yosmart.com/open/yolink/token"
UaID = "ua_93BF42449446432EA43E49887492C3FC"
SecID = "sec_v1_2IQ13RYyyvxMBpPK3POF0A=="


def get_access_token(url, client_id, client_secret):
    response = requests.post(
        url,
        data={"grant_type": "client_credentials",
               "client_id" : client_id,
               "client_secret" :client_secret},
        #auth=(client_id, client_secret),
    )
    return response.json()


def refresh_token(url, client_id, token):
    response = requests.post(
        url,
        data={"grant_type": "refresh_token",
             "client_id" : client_id,
             "refresh_token":token['refresh_token'],
            }
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
def on_connect(yolink, client, userdata, flags, rc):
    """
    Callback for connection to broker
    """
    #logging.debug("Connected with result code %s" % rc)
    #logging.debug( client,  userdata, flags)
    try:

        if (rc == 0):
            #logging.debug("Successfully connected to broker %s" % yolink.mqtt_url)
            test1 = client.subscribe(topicResp)
            #logging.debug(test1)
            test2 = client.subscribe(topicReport)
            #logging.debug(test2)
            test3 = client.subscribe(topicReportAll)
            #logging.debug(test3)

        else:
            #logging.debug("Connection with result code %s" % rc);
            sys.exit(2)
        time.sleep(1)
        #logging.debug('Subsribe: ' + yolink.topicResp + ', '+yolink.topicReport+', '+ yolink.topicReportAll )

    except Exception as E:
        print('Exception  -  on_connect: ' + str(E))    


token = get_access_token(tokenURL, UaID, SecID)
#time.sleep(2)
#token1 = refresh_token(tokenURL, UaID, token)

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

f = open('devicesPAC.json', 'w')
json.dump(info, f)
f.close()


data= {}
data['method'] = 'Home.getGeneralInfo'
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
houseId = r.json()
print(houseId)

UaID = client_id
houseID = houseId['data']['id']

uniqueID = info['data']['devices'][15]['deviceId']
#yolink.uniqueID = str(csName+'_'+ yolink.uniqueID )    
topicReq = houseID+'/'+ uniqueID +'/request'
topicResp = houseID+'/'+ uniqueID +'/response'
topicReport = houseID+'/'+ uniqueID +'/report'
topicReportAll = houseID+'/report'


client = mqtt.Client(uniqueID,  clean_session=True, userdata=None,  protocol=mqtt.MQTTv311, transport="tcp")
client.on_connect = on_connect
#client.on_message = on_message
#client.on_subscribe = on_subscribe
#client.on_disconnect = on_disconnect
client.username_pw_set(username=UaID, password=None)
print (client.connect("api.yosmart.com", 8003, 30))

test1 = client.subscribe(topicResp)
#logging.debug(test1)
test2 = client.subscribe(topicReport)
#logging.debug(test2)
test3 = client.subscribe(topicReportAll)
#logging.debug(test3)
