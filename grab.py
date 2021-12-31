import tweepy
from tweepy.models import Status
from tweepy.parsers import JSONParser
import os
import json
import re

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

ignores = ["cryptotrendin", "dexscreener"]
cash_tag_path = '/home/opc/twitterCashTagGrab/'
# cash_tag_path = 'C:\\twitterCashTagGrab\\'

call_amount = 10
mentions_file_name = 'mentions.json'
since_id_file_name = 'since_id.txt'
since_id_path = cash_tag_path + since_id_file_name
mentions_path = cash_tag_path + mentions_file_name

cash_tag_reg = r"\$[a-zA-Z]{3,5}"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# check if main dir exists, if not create
if not os.path.isdir(cash_tag_path):
    os.makedirs(cash_tag_path)

# Get the current since_id if exists from previous run
since_id = 1
if os.path.isfile(since_id_path):
    with open(since_id_path, 'r') as f:
        since_id = int(f.read())

# Get mentions if exist from previous run
mentions = {}
if os.path.isfile(mentions_path):
    with open(mentions_path, 'r') as f:
        mentions = json.loads(f.read())

latest_tweet_time = None
for page in tweepy.Cursor(api.home_timeline, count=200, tweet_mode="extended", since_id=since_id).pages(call_amount):
    for status in page:
        if status.user.screen_name in ignores:
            continue
        matched = []
        for match in re.finditer(cash_tag_reg, status.full_text, re.MULTILINE):
            cash_tag = match.group().lower()
            if cash_tag not in matched:
                matched.append(cash_tag)
                meta = {
                    'id' : status.id,
                    'favorite_amount' : status.favorite_count,
                    'retweet_amount' : status.retweet_count,
                    'screen_name' : status.user.screen_name,
                    'created_at' : status.created_at,
                }
                if cash_tag in mentions:
                    mentions[cash_tag].append(meta)
                else:
                    mentions[cash_tag] = [meta]
        # know when the latest tweet was posted so the tool only fetches tweets after that in the next run
        if latest_tweet_time == None or latest_tweet_time < status.created_at:
            latest_tweet_time = status.created_at
            since_id = status.id

#write mentions/ current since_id to file
with open(since_id_path, 'w') as f:
    f.write(str(since_id))
with open(mentions_path, 'w') as f:
    f.write(json.dumps(mentions, sort_keys=True, indent=4, default=str))