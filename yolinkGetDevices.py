#!/usr/bin/env python3

import hashlib
import time
import json
import requests
from cryptography.fernet import Fernet
from requests_oauthlib import OAuth2Session
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)


headers = {}
data = {}
authURL = 'https://api.yosmart.com/oauth/v2/authorization.htm'
tokenURL = 'https://api.yosmart.com/oauth/v2/getAccessToken.api'
client_id='60dd7fa7960d177187c82039'
client_secret='3f68536b695a435d8a1a376fc8254e70'
redirect_uri = 'https://127.0.0.1/blablabla'
csid = client_id
csseckey = client_secret

yolinkURL =  'https://api.yosmart.com/openApi' 

logging.basicConfig(level=logging.DEBUG)
#creds
client_id = '60dd7fa7960d177187c82039'
client_secret = '3f68536b695a435d8a1a376fc8254e70'
redirect_uri="https://127.0.0.1/yolink"

#oauth endpoints
authorization_base_url = "https://api.yosmart.com/oauth/v2/authorization.htm"
token_url = "https://api.yosmart.com/oauth/v2/getAccessToken.api"

yolinkOauth = OAuth2Session(client_id,redirect_uri=redirect_uri,scope=["create"])

#redirect
authorization_url, state = yolinkOauth.authorization_url(authorization_base_url)
print ("Go to the following link and log in:", authorization_url)
print ('After log in websire will redirect to blank page - copy address in address bar')
redirect_response = input('Paste the full redirect URL here:')
#fetch
token = yolinkOauth.fetch_token(token_url, client_secret=client_secret, authorization_response=redirect_response)

#fetch2
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


infoList = str(info).encode('utf-8')
jsonStr  = json.dumps(info, sort_keys=True, indent=4, separators=(',', ': '))

print(jsonStr+'\n')




'''
f = open('devicesV2.json', 'w')
json.dump(info, f)
f.close()
'''

# generate encryption key
key = Fernet.generate_key()
# write the key in a file of .key extension
with open('file_key.key', 'wb') as filekey:
    filekey.write(key)
# crate instance of Fernet
# and load generated key
fernet = Fernet(key)
'''
# read the file to encrypt
with open('test.txt', 'rb') as f:
    file = f.read()
'''    
# encrypt the file
encrypt_file = fernet.encrypt(infoList)
# open the file and wite the encryption data
with open('yolinkDeviceList.txt', 'wb') as encrypted_file:
    encrypted_file.write(encrypt_file)
print('File is encrypted')
#resp = session.get(authURL, headers=headers)

