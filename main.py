"""import os
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_messages, forward_twitter_updates
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# .env dosyasını yükleme
load_dotenv()

# TELEGRAM_BOT_TOKEN çevresel değişkeninden bot tokenini al
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni .env dosyasından alınamadı. Lütfen TELEGRAM_BOT_TOKEN değeri ekleyin.")

def main() -> None:
    # Telegram botunun token'ını .env dosyasından alıyoruz
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handler'lar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    
    # Text mesajlarını alıyoruz, fakat komutları hariç tutuyoruz
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_messages))
    
    application.add_handler(CommandHandler("forward_twitter_updates", forward_twitter_updates))

    # Botu çalıştır
    application.run_polling()

if __name__ == "__main__":
    main()
    """
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import json

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

CHANNELS_FILE = 'user_info.json'

async def start(update, context):
    await update.message.reply_text('Merhaba! Kanal ID\'leri veya kullanıcı adlarını girin.')

async def set_channels(update, context):
    user_id = update.message.from_user.id
    if len(context.args) < 2:
        await update.message.reply_text('Lütfen iki kanal ID\'si veya kullanıcı adı girin.')
        return

    source_channel = context.args[0]
    target_channel = context.args[1]

    # Kanal bilgilerini kaydet
    user_data = {}
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r') as f:
            user_data = json.load(f)

    user_data[str(user_id)] = {'source_channel': source_channel, 'target_channel': target_channel}
    
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(user_data, f)

    await update.message.reply_text(f'Kanal bilgileri kaydedildi: {source_channel} -> {target_channel}')

async def forward_messages(update, context):
    user_id = update.message.from_user.id
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r') as f:
            user_data = json.load(f)

        if str(user_id) in user_data:
            source_channel = user_data[str(user_id)]['source_channel']
            target_channel = user_data[str(user_id)]['target_channel']
            
            if update.message.chat.id == int(source_channel) or update.message.chat.username == source_channel:
                await context.bot.send_message(chat_id=target_channel, text=update.message.text)

async def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')  # .env dosyasından bot token'ını alıyoruz
    application = Application.builder().token(token).build()

    # Komutlar için handler'lar
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('set_channels', set_channels, pass_args=True))

    # Mesajları ileri iletmek için handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_messages))

    await application.run_polling()  # Polling'i başlatıyoruz

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
