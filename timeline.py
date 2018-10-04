# -*- coding: UTF-8 -*-
import sys
import os
import inspect
import time
import json
import tweepy
import csv
import logging

import config as cfg
from datetime import datetime, timedelta
from pytz import timezone
from tweepy.error import TweepError
from tweepy.parsers import JSONParser
from db import insert_tweet_data
from db import insert_candidate_data
from db import insert_tweet_log
from db import insert_reply_data

def run_insert(filename, db_name, type='tweet'):
    with open(filename, 'r') as infile:
        lines = infile.readlines()
        for line in lines:
            try:
                if(type == 'tweet'):
                    insert_tweet_data(json.loads(line), db_name)
                    insert_candidate_data(json.loads(line), db_name)
                    insert_tweet_log(json.loads(line), db_name)
                elif(type == 'reply'):
                    insert_reply_data(json.loads(line), db_name)
            except Exception as e:
                template = "In insert(). An exception of type {0} occurred."
                message = template.format(str(e))
                logging.debug(message)
                
def timeline(filename, handle, replies, api):
    status_count = 0
    
    with open(filename, 'a') as outfile:
        timeline = tweepy.Cursor(api.user_timeline, 
                                 screen_name=handle, 
                                 count=200,tweet_mode='extended').items()
        collecting = True

        while collecting:
            try:
                status = next(timeline)
                status = status._json
                status['reply_count'] = None
                outfile.write(json.dumps(status).encode('utf-8').decode('utf-8'))
                outfile.write('\n')
                status_count += 1
                
                created_at = datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +%f %Y')
                if created_at < cfg.COLLECT_FROM:
                    collecting = False
                    break
                

            except TweepError as e:
                print(e.reason)
                if e.reason == 'Twitter error response: status code = 404':
                    print('Error: Username %s not found' % (handle))
                    logging.debug('Error: Username %s not found' % (handle))
                    collecting = False
                elif e.reason == '{"errors":[{"code":89,"message":"Invalid or expired token."}]}':
                    print('Error: Invalid or expired token.')
                    collecting = False
                    sys.exit(0)
                elif e.reason == 'Twitter error response: status code = 401':
                    print('Error: Username %s is private or suspended' % (handle))
                    logging.debug('Error: Username %s is private or suspended' % (handle))
                    collecting = False
                else:
                    print('Received timeout. Sleeping for 15 minutes.')
                    time.sleep(15 * 60)

            except StopIteration as e:
                collecting = False
                template = "In timeline(). An exception of type {0} occurred."
                message = template.format(str(e))
                logging.debug(message)

    return status_count

def replies(filename, handle, api):
    reply_count = 0
    reply_counts_dict = {}
    utc = timezone('UTC')
    with open(filename, 'a') as outfile:
        search_results = tweepy.Cursor(
            api.search,
            q='to:{}'.format(handle),
            result_type='recent',
            count=100
        ).items()

        collecting = True
        while collecting:
            try:
                status = next(search_results)
                parsed_status = status._json
                reply_id = parsed_status['in_reply_to_status_id_str']
                
                if reply_id is not None:
                    if reply_id in reply_counts_dict:
                        reply_counts_dict[reply_id] += 1
                    else:
                        reply_counts_dict[reply_id] = 1
                    
                    reply_count += 1

                    outfile.write(json.dumps(parsed_status).encode('utf-8'))
                    outfile.write('\n')
                    

            except TweepError as e:
                print('Received timeout. Sleeping for 15 minutes.',e)
                time.sleep(15 * 60)

            except StopIteration as e:
                collecting = False
                template = "In replies(). An exception of type {0} occurred."
                message = template.format(str(e))
                logging.debug(message)

    return reply_count, reply_counts_dict

def collect(params, handle, db_name):
    
    api_auth = tweepy.OAuthHandler(params['CONSUMER_KEY'], params['CONSUMER_SECRET'])
    api_auth.set_access_token(params['ACCESS_TOKEN'], params['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(api_auth)
    
    print('COLLECTING FOR: {}'.format(handle))
    print()

    if api.verify_credentials:
        print('Successfully authenticated with Twitter.')
    else:
        print('Failed to authenticate with Twitter. Please try again.')
        sys.exit(1)

    reply_counts_dict = []
    reply_count = None
    
    #filename = './rawdata/reply/reply-{}-{}.json'.format(handle, datetime.utcnow().strftime("%Y%m%d%H"))

    #print('Collecting replies...')
    #reply_count, reply_counts_dict = replies(filename, handle, api)
    #print('TOTAL Replies Collected: {}'.format(reply_count))
    #print('')

    #print('Now inserting replies...')
    #run_insert(filename, 'reply')
    #print('Insertion completed')
    #print('')
        
    filename = './rawdata/{}/original-{}-{}.json'.format(db_name, handle, datetime.utcnow().strftime("%Y%m%d%H"))

    print('Collecting {}\'s timeline'.format(handle))
    status_count = timeline(filename, handle, reply_counts_dict, api)
    print('')
    print('TOTAL Tweets Collected: {}'.format(status_count))
    print('')

    print('Now inserting...')
    run_insert(filename, db_name)
    print('Insertion completed')
    print('')


def run_timeline(input_filename):
    d = {}
    try:
        with open(input_filename) as f:
            for line in f:
                try:
                    (key, val) = line.split('=')
                    d[key] = val.strip()
                except:
                    pass
    except:
        print('Error: \"%s\" cannot be opened' % (input_filename))
        sys.exit(1)
    
    if 'DB_NAME' not in d.keys() or 'CONSUMER_KEY' not in d.keys() or 'CONSUMER_SECRET' not in d.keys() or 'ACCESS_TOKEN' not in d.keys() or 'ACCESS_TOKEN_SECRET' not in d.keys() or 'TERMS_LIST' not in d.keys():
        print('Error: Missing information in \"%s\":\n - DB_NAME\n - CONSUMER_SECRET\n - ACCESS_TOKEN\n - ACCESS_TOKEN_SECRET\n - TERMS_LIST' % (input_filename))
        sys.exit(1)
    
    db_name = ''.join(e for e in d['DB_NAME'] if e.isalnum())
    twitter_keys = {'CONSUMER_KEY': ''.join(e for e in d['CONSUMER_KEY'] if e.isalnum()),
                    'CONSUMER_SECRET': ''.join(e for e in d['CONSUMER_SECRET'] if e.isalnum()),
                    'ACCESS_TOKEN': ''.join(e for e in d['ACCESS_TOKEN'] if e.isalnum() or e == '-'),
                    'ACCESS_TOKEN_SECRET': ''.join(e for e in d['ACCESS_TOKEN_SECRET'] if e.isalnum())
                    }
    # Output Folders Handling #
    if not os.path.exists('./rawdata/' + db_name):
        os.makedirs('./rawdata/' + db_name)
    
    TERMS_LIST = d['TERMS_LIST']
    TERMS_LIST = TERMS_LIST.split(',')
    while True:
        for handle in TERMS_LIST:
            collect(twitter_keys, handle.strip(' /'), db_name)

        print('All candidates were collected. Resuming in an hour.')
        time.sleep(60 * 60)


