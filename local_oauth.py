#!/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
#creds
client_id = '<id>'
client_secret = '<secret>'
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

#fetch2
print (token)
