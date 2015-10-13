import sys
import os
import time
import json
import tweepy

from tweepy.error import TweepError
from tweepy.parsers import JSONParser
from db import insert_tweet_data

def parse_tweet_entities(entities):
    entities_dict = {
        'urls'          : [url['expanded_url'] for url in entities['urls']],
        'user_mentions' : [mention['screen_name'] for mention in entities['user_mentions']],
        'hashtags'      : [ht['text'] for ht in entities['hashtags']],
        'media'         : []
    }

    if 'media' in entities.keys():
        entities_dict['media'] = [item['media_url_https'] for item in entities['media'] if 'media' in entities.keys()]

    return entities_dict

def parse_tweet(status):
    status = status._json

    parsed_status_dict = {
        'tweet': {
            'text': status['text'],
            'retweet_count': status['retweet_count'],
            'id_str': status['id_str'],
            'in_reply_to_user_id_str': status['in_reply_to_user_id_str'],
            'in_reply_to_screen_name': status['in_reply_to_screen_name'],
            'in_reply_to_status_id_str': status['in_reply_to_status_id_str'],
            'created_at': status['created_at'],
            'entities': parse_tweet_entities(status['entities'])
        },
        'user': {
            'name': status['user']['name'],
            'location': status['user']['location'],
            'favourites_count': status['user']['favourites_count'],
            'url': status['user']['url'],
            'id_str': status['user']['id_str'],
            'followers_count': status['user']['followers_count'],
            'verified': status['user']['verified'],
            'description': status['user']['description'],
            'statuses_count': status['user']['statuses_count'],
            'friends_count': status['user']['friends_count'],
            'screen_name': status['user']['screen_name']
        }
    }

    return parsed_status_dict

def run_insert(filename):
    with open(filename, 'r') as infile:
        lines = infile.readlines()
        for line in lines:
            try:
                insert_tweet_data(json.loads(line))
            except:
                pass

    os.remove(filename)

def timeline(auth, handle):
    api_auth = tweepy.OAuthHandler(auth['consumer_key'], auth['consumer_secret'])
    api_auth.set_access_token(auth['access_token'], auth['access_token_secret'])
    api = tweepy.API(api_auth)

    print 'COLLECTING FOR: {}'.format(handle)
    print

    if api.verify_credentials:
        print 'Successfully authenticated with Twitter.'
        print 'Collecting...'
    else:
        print 'Failed to authenticate with Twitter. Please try again.'
        sys.exit(1)

    filename = '{}-timeline.json'.format(handle)
    with open(filename, 'a') as outfile:
        timeline = tweepy.Cursor(api.user_timeline, screen_name=handle, count=200).items()
        collecting = True
        status_count = 1

        while collecting:
            try:
                status = next(timeline)
                parsed_status = parse_tweet(status)
                outfile.write(json.dumps(parsed_status).encode('utf-8'))
                outfile.write('\n')
                status_count += 1

            except TweepError as e:
                print 'Received timeout. Sleeping for 15 minutes.'
                time.sleep(15 * 60)

            except StopIteration as e:
                collecting = False

    print
    print 'TOTAL Tweets Collected: {}'.format(status_count)
    print
    print 'Now inserting...'

    run_insert(filename)

    print 'Insertion completed'
    print

def run_timeline(auth):
    CANDIDATES_LIST = [
        'JimWebbUSA',
        'HillaryClinton',
        'JoeBiden',
        'martinomalley',
        'BernieSanders',
        'lincolnchafee',
        'lessig',
        'marcorubio',
        'JebBush',
        'tedcruz',
        'ChrisChristie',
        'ScottWalker',
        'JohnKasich',
        'GovMikeHuckabee',
        'BobbyJindal',
        'GovernorPerry',
        'Randpaul',
        'RealBenCarson',
        'CarlyforAmerica',
        'GovernorPataki',
        'LindseyGrahamSC',
        'ricksantorum',
        'realdonaldtrump',
        'gov_gilmore',
        'markforamerica'
    ]

    while True:
        for handle in CANDIDATES_LIST:
            timeline(auth, handle)

        print 'All candidates collected for. Resuming in 20 minutes.'
        time.sleep(20 * 60)
