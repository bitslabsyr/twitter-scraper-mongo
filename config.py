#!/usr/bin/env python
from datetime import  datetime

# address: server address e.g. localhost and bangkok.ischool.syr.edu
# auth: True if MongoDB authentication is enabled. If True, username and password must be given
MONGO_ACCOUNT = {'address': 'localhost',
                 'auth': True,
                 'username': 'USERNAME',
                 'password': 'PASSWORD'}


DB_NAME = 'TestimelineCollection'

AUTH = {
    'consumer_key': 'XXX',
    'consumer_secret': 'XXX',
    'access_token': 'XXX',
    'access_token_secret': 'XXX'
}

# Format: date(YYYY, M, D, Hour, Min). If no date restriction desired, replace with False
COLLECT_FROM = datetime(2016, 1, 1, 0, 0)

CANDIDATES_LIST = ['handle', 'handle', 'handle']
