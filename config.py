#!/usr/bin/env python
from datetime import  datetime

MONGO_ACCOUNT = {'username': 'xxx',
                 'password': 'xxx'}

DB_NAME = 'TestimelineCollection'

AUTH = {
    'consumer_key': 'xxx',
    'consumer_secret': 'xxx',
    'access_token': 'xxx',
    'access_token_secret': 'xxx'
}

# Format: date(YYYY, M, D, Hour, Min)
COLLECT_FROM = datetime(2016, 1, 1, 0, 0)

CANDIDATES_LIST = ['muooomoo', 'JeffHemsley', 'profjsg']