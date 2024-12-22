import os
from dotenv import load_dotenv

def load_env():
    """.env dosyasındaki bilgileri yükler"""
    load_dotenv()

# Telegram Bot Token'ı
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
