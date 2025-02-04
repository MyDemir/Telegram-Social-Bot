import os
import tweepy
from dotenv import load_dotenv
import json
import asyncio
from telegram import Bot

# .env dosyasını yükleyin
load_dotenv()

# Twitter API Anahtarlarını alıyoruz
TWITTER_API_KEY = os.getenv('API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

# Telegram Bot Token'ı
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Twitter API ile bağlantı kuruyoruz
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Telegram Bot'unu başlatıyoruz
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Kullanıcı bilgilerini yükleme
def load_user_info():
    try:
        with open("user_info.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Twitter kullanıcısının son tweet'lerini kontrol etme
def check_twitter_user(twitter_username):
    try:
        # Kullanıcının tweet'lerini çekiyoruz
        tweets = api.user_timeline(screen_name=twitter_username, count=1, tweet_mode="extended")
        if tweets:
            return tweets[0]
        else:
            return None
    except tweepy.TweepError as e:
        print(f"Twitter hatası: {e}")
        return None

# Tweet bildirimini gönderme
async def send_tweet_notification(tweet, chat_id):
    tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
    text = f"Yeni tweet! 🐦\n\n{tweet.full_text}\n\n🔗 [Tweeti Görüntüle]({tweet_url})"
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", disable_web_page_preview=True)

# Kullanıcı bilgilerini güncelleme
def update_user_info(user_info):
    with open("user_info.json", "w") as file:
        json.dump(user_info, file, indent=4)

# Twitter'dan gelen tweet'leri kontrol etme ve hedef kanala gönderme
async def start_twitter_check():
    user_info = load_user_info()
    
    for twitter_username, data in user_info.items():
        # Son tweet'i kontrol ediyoruz
        tweet = check_twitter_user(twitter_username)
        
        if tweet:
            last_tweet_id = data.get("last_tweet_id")
            
            if last_tweet_id != tweet.id:
                # Eğer tweet yeni ise, bildirimi gönderiyoruz
                await send_tweet_notification(tweet, data["chat_id"])
                
                # Kullanıcı bilgilerini güncelliyoruz
                data["last_tweet_id"] = tweet.id
                update_user_info(user_info)

# Asenkron olarak Twitter kontrolü başlatma
async def start_twitter_check_periodically():
    while True:
        await start_twitter_check()  # Twitter kontrol fonksiyonunu çalıştır
