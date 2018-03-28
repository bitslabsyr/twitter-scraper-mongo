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
from db_dev import insert_tweet_data
from db_dev import insert_candidate_data
from db_dev import insert_tweet_log
from db_dev import insert_reply_data


def run_insert(filename, type):
    with open(filename, 'r') as infile:
        lines = infile.readlines()
        for line in lines:
            try:
                if(type == 'tweet'):
                    insert_tweet_data(json.loads(line))
                    insert_candidate_data(json.loads(line))
                    insert_tweet_log(json.loads(line))
                elif(type == 'reply'):
                    insert_reply_data(json.loads(line))
            except Exception as e:
                template = "In insert(). An exception of type {0} occurred."
                message = template.format(str(e))
                logging.debug(message)
                
def timeline(filename, handle, replies, api):
    status_count = 0
    
    with open(filename, 'a') as outfile:
        timeline = tweepy.Cursor(api.user_timeline, 
                                 screen_name=handle, 
                                 count=200).items()
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
                if e.reason == 'Twitter error response: status code = 404':
                    print('Error: Username %s not found' % (handle))
                    logging.debug('Error: Username %s not found' % (handle))
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

def collect(auth, handle):
    
    api_auth = tweepy.OAuthHandler(auth['consumer_key'], auth['consumer_secret'])
    api_auth.set_access_token(auth['access_token'], auth['access_token_secret'])
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
    
    filename = './rawdata/reply/reply-{}-{}.json'.format(handle, datetime.utcnow().strftime("%Y%m%d%H"))

    #print('Collecting replies...')
    #reply_count, reply_counts_dict = replies(filename, handle, api)
    #print('TOTAL Replies Collected: {}'.format(reply_count))
    #print('')

    #print('Now inserting replies...')
    #run_insert(filename, 'reply')
    #print('Insertion completed')
    #print('')
        
    filename = './rawdata/original/original-{}-{}.json'.format(handle, datetime.utcnow().strftime("%Y%m%d%H"))

    print('Collecting {}\'s timeline'.format(handle))
    status_count = timeline(filename, handle, reply_counts_dict, api)
    print('')
    print('TOTAL Tweets Collected: {}'.format(status_count))
    print('')

    print('Now inserting...')
    run_insert(filename, 'tweet')
    print('Insertion completed')
    print('')


def run_timeline(auth):
        
    CANDIDATES_LIST = cfg.CANDIDATES_LIST
    
    while True:
        for handle in CANDIDATES_LIST:
            collect(auth, handle)

        print('All candidates were collected. Resuming in an hour.')
        time.sleep(60 * 60)

