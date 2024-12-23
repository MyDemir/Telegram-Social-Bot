import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram_bot import start, set_channels, set_twitter, send_channel_update_notification
from twitter import get_twitter_updates  # twitter.py dosyasını ekleyelim

def main():
    load_dotenv()

    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Bot tokeni bulunamadı. .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("set_twitter", set_twitter))

    # Test komutu
    application.add_handler(CommandHandler("test_twitter", test_twitter))

    # Kanal mesaj bildirimleri
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, send_channel_update_notification))

    application.run_polling()

async def test_twitter(update, context):
    user_input = update.message.text.strip().split()
    
    if len(user_input) == 2:
        twitter_username = user_input[1].lstrip('@')  # Kullanıcı adını alıyoruz
        tweet_text, tweet_url = get_twitter_updates(twitter_username)  # Twitter güncellemelerini alıyoruz
        
        if tweet_text and tweet_url:
            await update.message.reply_text(
                f"Son tweet:\n{tweet_text}\n{tweet_url}"
            )
        else:
            await update.message.reply_text(f"Tweet alınamadı.")
    else:
        await update.message.reply_text("Kullanım: /test_twitter @kullaniciadi")

if __name__ == "__main__":
    main()
