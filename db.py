# -*- coding: UTF-8 -*-
import sys
import json
import sys
import pymongo
import csv
import logging
import hashlib
import config as cfg
from pytz import timezone
from email.utils import parsedate_tz
from datetime import datetime
from collections import Counter


mongoClient = pymongo.MongoClient(cfg.MONGO_ACCOUNT['address'])

if cfg.MONGO_ACCOUNT['auth']:
    mongoClient.admin.authenticate(cfg.MONGO_ACCOUNT['username'], cfg.MONGO_ACCOUNT['password'])

mongoDB = mongoClient[cfg.DB_NAME]

logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='./logs/twitter-scraper.log',
                    level=logging.DEBUG)

def to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt

def insert_tweet_data(tweet):
    try:
        utc = timezone('UTC')
        docId = tweet['id']
        
        #tweet['created_at'] = utc.localize(datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +%f %Y'))
        
        tweet['stack_vars'] = { 'text_hash': None,
                            'created_ts': None,
                            'updated_at': None,
                            'hashtags': [],
                            'mentions': [],
                            'codes': [],
                            'track_kw': {},
                            'entities_counts': {},
                            'user': {},    
                            'full_tweet': {}}
        
        t = to_datetime(tweet['created_at'])
        tweet['stack_vars']['created_ts'] = t.strftime('%Y-%m-%d %H:%M:%S')
        tweet['stack_vars']['updated_at'] = datetime.utcnow()
        
        tweet['stack_vars']['full_tweet'] = {'display_text_range': [],
                                            'entities': None,
                                            'full_text': None}
        
        tweet['stack_vars']['full_tweet']['display_text_range'] = tweet['display_text_range']
        tweet['stack_vars']['full_tweet']['entities'] = tweet['entities']
        tweet['stack_vars']['full_tweet']['full_text'] = tweet['full_text']
        
        t = to_datetime(tweet['user']['created_at']) 
        tweet['stack_vars']['user']['created_ts'] = t.strftime('%Y-%m-%d %H:%M:%S')
        
        if 'entities' in tweet:
            hashtag_num = 0
            tweet['stack_vars']['hashtags'] = []
            tweet['stack_vars']['mentions'] = []
            tweet['stack_vars']['codes'] = []
    
            if "hashtags" in tweet['entities']:
                hashtag_num = len(tweet['entities']['hashtags'])
                for index in range(len(tweet['entities']['hashtags'])):
                    tweet['stack_vars']['hashtags'].append(tweet['entities']['hashtags'][index]['text'].lower())
    
            urls_num = 0
            coded_url_num = 0
            urls = []
            
            if "urls" in tweet['entities']:
                urls_num = len(tweet['entities']['urls'])
    
            mentions_num = 0
            if "user_mentions" in tweet['entities']:
                mentions_num = len(tweet['entities']['user_mentions'])
                for index in range(len(tweet['entities']['user_mentions'])):
                    if "screen_name" in tweet['entities']['user_mentions'][index]:
                        tweet['stack_vars']['mentions'].append(tweet['entities']['user_mentions'][index]['screen_name'].lower())
    
            tweet['stack_vars']['entities_counts'] = {  'urls': urls_num,
                                                        'hashtags': hashtag_num,
                                                        'user_mentions': mentions_num,
                                                        'coded_urls': coded_url_num };
    
            tweet['stack_vars']['hashtags'].sort()
            tweet['stack_vars']['mentions'].sort()
    
            tweet['stack_vars']['text_hash'] = hashlib.md5(tweet['stack_vars']['full_tweet']['full_text'].encode("utf-8")).hexdigest()
        
        
        
        
        isExist = mongoDB.TW_cand.find_one({'id': docId})
        if isExist is None:
            mongoDB.TW_cand.insert(tweet)
        else:
            mongoDB.TW_cand.update( { 'id': docId },
                                   { '$set': {'stack_vars.updated_at': tweet['stack_vars']['updated_at'],
                                              'retweet_count': tweet['retweet_count'],
                                              'favorite_count': tweet['favorite_count'],
                                              'user.followers_count': tweet['user']['followers_count'],
                                              'user.listed_count': tweet['user']['listed_count'],
                                              'user.friends_count': tweet['user']['friends_count']}},
                                   upsert=True, multi=False) 
        
    except Exception as e:
        template = "In insert_tweet_data(). An exception of type {0} occurred."
        message = template.format(str(e))
        logging.debug(message)

def insert_reply_data(tweet):
    try:
        utc = timezone('UTC')
        docId = tweet['id']
        
        tweet['created_at'] = utc.localize(datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +%f %Y'))
        tweet['updated_at'] = datetime.utcnow()
        tweet['text'] = tweet['text']
        
        isExist = mongoDB.TW_reply.find_one({'id': docId})
        if isExist is None:
            mongoDB.TW_reply.insert(tweet)
        else:
            mongoDB.TW_reply.update( { 'id': docId },
                                   { '$set': {'updated_at': tweet['updated_at'],
                                              'retweet_count': tweet['retweet_count'],
                                              'favorite_count': tweet['favorite_count'],
                                              'user.followers_count': tweet['user']['followers_count'],
                                              'user.listed_count': tweet['user']['listed_count'],
                                              'user.friends_count': tweet['user']['friends_count']}},
                                   upsert=True, multi=False) 
        
    except Exception as e:
        template = "In insert_reply_data(). An exception of type {0} occurred."
        message = template.format(str(e))
        logging.debug(message)          

def insert_candidate_data(tweet):
    try:
        utc = timezone('UTC')
        
        candId = tweet['user']['id']
        
        cand = {}
        cand['id'] = candId
        cand['screen_name'] = tweet['user']['screen_name']
        cand['name'] = tweet['user']['name']
        cand['followers_count'] = tweet['user']['followers_count']
        cand['listed_count'] = tweet['user']['listed_count']
        cand['friends_count'] = tweet['user']['friends_count']
        cand['created_at'] = utc.localize(datetime.strptime(tweet['user']['created_at'], '%a %b %d %H:%M:%S +%f %Y'))
        
        cand['updated_at'] = datetime.utcnow()
        
        isExist = mongoDB.TW_cand_info.find_one({'id': candId})
        if isExist is None:
            mongoDB.TW_cand_info.insert(cand)
        else:
            mongoDB.TW_cand_info.update( { 'id': candId },
                                   { '$set': {'updated_at': cand['updated_at'],
                                              'followers_count': cand['followers_count'],
                                              'listed_count': cand['listed_count'],
                                              'friends_count': cand['friends_count']}},
                                   upsert=True, multi=False) 
        
    except Exception as e:
        template = "In insert_candidate_data(). An exception of type {0} occurred."
        message = template.format(str(e))
        logging.debug(message)
            
def insert_tweet_log(tweet):
    try:
        utc = timezone('UTC')
        docId = tweet['id']
        
        log_data = {}
        log_data['tweet_id'] = tweet['id']
        log_data['retweet_count'] = tweet['retweet_count']
        log_data['favorite_count'] = tweet['favorite_count']
        
        log_data['user'] = {}
        log_data['user']['followers_count'] = tweet['user']['followers_count']
        log_data['user']['friends_count'] = tweet['user']['friends_count']        
        log_data['user']['listed_count'] = tweet['user']['listed_count']
     
        log_data['log_created_at'] = datetime.utcnow()
        
        mongoDB.TW_cand_crawl_history.insert(log_data)
        
    except Exception as e:
        template = "In insert_tweet_log(). An exception of type {0} occurred."
        message = template.format(str(e))
        logging.debug(message)   
        
     



