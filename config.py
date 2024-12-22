import os
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

# Bot token'ını ve diğer çevresel değişkenleri al
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
#X_API_KEY = os.getenv('X_API_KEY')
#DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
