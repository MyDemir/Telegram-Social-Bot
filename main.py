from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram_bot import (
    start,
    set_source_group,
    set_target_group,
    set_twitter_target,
    forward_twitter_updates,
    handle_group_addition,
)
from config import TELEGRAM_BOT_TOKEN

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_source_group))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_target_group))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_twitter_target))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_twitter_updates))
    # Kaynak grup ekleme
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                          lambda update, context: handle_group_addition(update, context, 'source')))
    # Hedef grup ekleme
    application.add_handler
