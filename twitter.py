import tweepy
import os
import time
import telebot
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

def create_api():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

def get_user_tweets(username, count=5):
    api = create_api()
    try:
        tweets = api.user_timeline(screen_name=username, count=count, tweet_mode='extended')
        tweet_data = []
        for tweet in tweets:
            tweet_info = {
                'text': tweet.full_text,
                'created_at': tweet.created_at,
                'id': tweet.id_str,
                'type': 'retweet' if hasattr(tweet, 'retweeted_status') else 'quote' if hasattr(tweet, 'quoted_status') else 'tweet'
            }
            tweet_data.append(tweet_info)
        return tweet_data
    except tweepy.RateLimitError:
        print("Rate limit reached, waiting for 15 minutes...")
        time.sleep(15 * 60)
        return get_user_tweets(username, count)
    except tweepy.TweepError as e:
        print(f"Error fetching tweets: {e}")
        return None

def get_new_tweets(username, last_checked_time):
    tweets = get_user_tweets(username)
    
    if not tweets:
        return None
    
    new_tweets = []
    for tweet in tweets:
        tweet_time = tweet['created_at']
        if tweet_time > last_checked_time:
            new_tweets.append(tweet)
    
    return new_tweets if new_tweets else None

def check_tweets_periodically(username, interval_minutes=30):
    from telegram_bot import load_users
    users = load_users()
    chat_id = users.get(username, {}).get('chat_id', None)
    
    last_checked_time = datetime.now() - timedelta(minutes=interval_minutes)
    
    while True:
        new_tweets = get_new_tweets(username, last_checked_time)
        if new_tweets and chat_id:
            for tweet in new_tweets:
                bot.send_message(chat_id, f"Yeni Tweet: {tweet['text']}")
        
        last_checked_time = datetime.now()
        time.sleep(interval_minutes * 60)
