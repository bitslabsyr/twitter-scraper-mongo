# -*- coding: UTF-8 -*-
import sys
import json
import sys
import pymongo
import csv
import logging
import config as cfg
from pytz import timezone
from datetime import datetime
from collections import Counter

mongoClient = pymongo.MongoClient()
mongoClient.admin.authenticate(cfg.MONGO_ACCOUNT['username'], cfg.MONGO_ACCOUNT['password'])
mongoDB = mongoClient[cfg.DB_NAME]

logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='./logs/twitter-scraper.log',
                    level=logging.DEBUG)

def insert_tweet_data(tweet):
    try:
        utc = timezone('UTC')
        docId = tweet['id']
        
        tweet['created_at'] = utc.localize(datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +%f %Y'))
        tweet['updated_at'] = datetime.utcnow()
        tweet['text'] = tweet['full_text']
        
        isExist = mongoDB.TW_cand.find_one({'id': docId})
        if isExist is None:
            mongoDB.TW_cand.insert(tweet)
        else:
            mongoDB.TW_cand.update( { 'id': docId },
                                   { '$set': {'updated_at': tweet['updated_at'],
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
        
     



