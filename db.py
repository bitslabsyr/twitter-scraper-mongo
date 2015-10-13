from datetime import datetime
from sqlalchemy.sql import select
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, \
    ForeignKey, Boolean, DateTime

engine = create_engine('mysql://ccds:CcdsUser@128.230.247.136/twitter', echo=True)
metadata = MetaData()

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('id_str', String(255), nullable=False, unique=True),
    Column('name', String(255), nullable=False),
    Column('screen_name', String(255), nullable=False, unique=True),
    Column('location', String(255)),
    Column('favourites_count', Integer, nullable=False),
    Column('followers_count', Integer, nullable=False),
    Column('verified', Boolean, nullable=False),
    Column('url', String(255)),
    Column('description', String(255)),
    Column('statuses_count', Integer, nullable=False),
    Column('friends_count', Integer, nullable=False)
)

tweets = Table('tweets', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', None, ForeignKey('users.id')),
    Column('id_str', String(255), nullable=False, unique=True),
    Column('in_reply_to_user_id_str', String(255)),
    Column('in_reply_to_status_id', String(255)),
    Column('in_reply_to_screen_name', String(255)),
    Column('text', String(255), nullable=False),
    Column('retweet_count', Integer, nullable=False),
    Column('created_at', DateTime)
)

urls = Table('urls', metadata,
    Column('id', Integer, primary_key=True),
    Column('tweet_id', None, ForeignKey('tweets.id')),
    Column('url', String(255), nullable=False)
)

mentions = Table('mentions', metadata,
    Column('id', Integer, primary_key=True),
    Column('tweet_id', None, ForeignKey('tweets.id')),
    Column('user_mention_screen_name', String(255), nullable=False)
)

hashtags = Table('hashtags', metadata,
    Column('id', Integer, primary_key=True),
    Column('tweet_id', None, ForeignKey('tweets.id')),
    Column('hashtag_text', String(255), nullable=False)
)

media = Table('media', metadata,
    Column('id', Integer, primary_key=True),
    Column('tweet_id', None, ForeignKey('tweets.id')),
    Column('https_media_url', String(255), nullable=False)
)

def insert_user(user, conn):
    result = conn.execute(users.insert(), [user])
    return result.inserted_primary_key

def update_user(user, conn):
    update = users.update().where(users.c.screen_name == user['screen_name']).\
        values(
            name=user['name'],
            location=user['location'],
            favourites_count=user['favourites_count'],
            url=user['url'],
            followers_count=user['followers_count'],
            verified=user['verified'],
            description=user['description'],
            statuses_count=user['statuses_count'],
            friends_count=user['friends_count']
        )

    conn.execute(update)

def insert_or_update_user(user, conn):
    for key in user.keys():
        if len(key.split('_count')) > 1:
            user[key] = int(user[key])

    s = select([users.c.id, users.c.screen_name]).\
        where(users.c.screen_name == user['screen_name'])

    result = conn.execute(s)
    if result.rowcount:
        update_user(user, conn)
        user_id = result.first()[0]
    else:
        user_id = insert_user(user, conn)

    return user_id

def update_tweet_info(tweet, conn):
    update = tweets.update().where(tweets.c.id_str == tweet['id_str']).\
        values(
            retweet_count=tweet['retweet_count'],
            created_at=tweet['created_at']
        )

    conn.execute(update)

def insert_tweet_info(tweet, conn):
    result = conn.execute(tweets.insert(), [tweet])
    return result.inserted_primary_key

def insert_entities(entities, tweet_id, conn):
    if entities['urls']:
        for url in entities['urls']:
            ins = urls.insert().values(tweet_id=tweet_id, url=url)
            conn.execute(ins)

    if entities['user_mentions']:
        for mention in entities['user_mentions']:
            ins = mentions.insert().values(tweet_id=tweet_id, user_mention_screen_name=mention)
            conn.execute(ins)

    if entities['hashtags']:
        for hashtag in entities['hashtags']:
            ins = hashtags.insert().values(tweet_id=tweet_id, hashtag_text=hashtag)
            conn.execute(ins)

    if entities['media']:
        for media_item in entities['media']:
            ins = media.insert().values(tweet_id=tweet_id, https_media_url=media_item)
            conn.execute(ins)

def insert_or_update_tweet(tweet, user_id, conn):
    entities = tweet.pop('entities')
    tweet['retweet_count'] = int(tweet['retweet_count'])
    tweet['created_at'] = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +%f %Y')
    tweet['user_id'] = user_id

    s = select([tweets.c.id, tweets.c.id_str]).\
        where(tweets.c.id_str == tweet['id_str'])

    result = conn.execute(s)
    if result.rowcount:
        update_tweet_info(tweet, conn)
    else:
        tweet_id = insert_tweet_info(tweet, conn)
        insert_entities(entities, tweet_id, conn)

def insert_tweet_data(tweet):
    user_info = tweet['user']
    tweet_info = tweet['tweet']

    conn = connect()
    user_id = insert_or_update_user(user_info, conn)
    insert_or_update_tweet(tweet_info, user_id, conn)

def connect():
    return engine.connect()

def init():
    metadata.create_all(engine)
