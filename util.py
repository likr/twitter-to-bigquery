import os
from datetime import datetime
import tweepy

attrs = [
    'user.screen_name',
    'user.name',
    'user.lang',
    'user.id',
    'user.url',
    'user.description',
    'user.location',
    'contributors',
    'in_reply_to_status_id',
    'in_reply_to_user_id',
    'text',
    'source',
    'id',
    'retweeted_status.id',
    'retweeted_status.user.id',
    'coordinates.type',
    'retweet_count',
]
timestamp_attrs = [
    'created_at',
    'user.created_at',
]
entity_attrs = [
    'entities.hashtags',
    'entities.user_mentions',
    'entities.urls',
]
entity_item_attrs = [
    'text',
    'screen_name',
    'url',
]
coordinates_attrs = [
    'coordinates',
]


def get(obj, keystr):
    for key in keystr.split('.'):
        if key not in obj or obj[key] is None:
            return None
        obj = obj[key]
    return obj


def set(obj, keystr, value):
    keys = keystr.split('.')
    for key in keys[:-1]:
        if key not in obj:
            obj[key] = {}
        obj = obj[key]
    obj[keys[-1]] = value


def convert_date_format(s):
    d = datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')
    return d.strftime('%Y-%m-%d %H:%M:%S')


def convert_indices(item):
    [start, stop] = item['indices']
    obj = {
        'start': start,
        'stop': stop,
    }
    for key in entity_item_attrs:
        d = get(item, key)
        if d is not None:
            set(obj, key, d)
    return obj


def convert_coordinates(item):
    assert item['type'] == 'Point'
    [long, lat] = item['coordinates']
    return {
        'type': item['type'],
        'coordinates': [
            {
                'lat': lat,
                'long': long,
            }
        ]
    }


def convert(status):
    obj = {}
    for key in attrs:
        d = get(status, key)
        if d is not None:
            set(obj, key, d)
    for key in timestamp_attrs:
        v = get(status, key)
        if v is not None:
            set(obj, key, convert_date_format(v))
    for key in entity_attrs:
        set(obj, key, [convert_indices(item) for item in get(status, key)])
    for key in coordinates_attrs:
        d = get(status, key)
        if d:
            set(obj, key, convert_coordinates(d))
    return obj


def get_api():
    auth = tweepy.OAuthHandler(
        os.environ['TWITTER_CONSUMER_KEY'],
        os.environ['TWITTER_CONSUMER_SECRET'])
    auth.set_access_token(
        os.environ['TWITTER_ACCESS_TOKEN_KEY'],
        os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    return tweepy.API(auth)
