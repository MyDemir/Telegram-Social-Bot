import tweepy
import time
from telegram.ext import ContextTypes
from telegram import Update

# Twitter API bağlantısını kurma
def create_twitter_api():
    auth = tweepy.OAuthHandler('API_KEY', 'API_SECRET_KEY')
    auth.set_access_token('ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET')
    return tweepy.API(auth)

# Yeni tweet olup olmadığını kontrol etme
async def check_twitter_for_new_tweets(context: ContextTypes.DEFAULT_TYPE) -> None:
    api = create_twitter_api()
    user_data = load_user_info()  # Kullanıcı verilerini yükle

    for username, info in user_data.items():
        # Twitter'dan son tweeti al
        tweets = api.user_timeline(screen_name=username, count=1, tweet_mode='extended')
        
        if tweets:
            latest_tweet = tweets[0]
            last_tweet_id = info.get("last_tweet_id")

            if latest_tweet.id_str != last_tweet_id:
                # Yeni tweet var, Telegram'a bildir
                user_data[username]["last_tweet_id"] = latest_tweet.id_str
                save_user_info(user_data)  # Yeni tweet ID'sini kaydediyoruz

                # Telegram'a bildirim gönder
                await send_telegram_notification(context, info['chat_id'], username, latest_tweet)
            else:
                pass

# Periyodik kontrol için kullanılan fonksiyon
async def start_twitter_check(context: ContextTypes.DEFAULT_TYPE) -> None:
    await check_twitter_for_new_tweets(context)  # Tweet kontrolünü başlat
