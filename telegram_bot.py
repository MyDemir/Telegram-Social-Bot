from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,  # filters artık küçük harfle import ediliyor
    ContextTypes,
)
from bot.twitter import get_twitter_updates
from bot.config import TELEGRAM_BOT_TOKEN

user_info = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Merhaba! Ben Telegram Social Bot V2.\n'
        'Mesaj aktarımı yapmak için kaynak ve hedef grup bilgilerini girebilirsiniz.'
    )

async def set_source_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    source_group_id = update.message.text
    user_info[user_id] = {'source_group': source_group_id}
    
    await update.message.reply_text(
        f"Kaynak grup {source_group_id} olarak ayarlandı.\nŞimdi hedef grup ID'sini girin."
    )

async def set_target_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kaynak grup ID\'sini girin.')
        return

    target_group_id = update.message.text
    user_info[user_id]['target_group'] = target_group_id

    await update.message.reply_text(
        f"Hedef grup {target_group_id} olarak ayarlandı.\n"
        "Şimdi Twitter kullanıcı adı veya hashtag girin (örneğin: @username veya #hashtag)."
    )

async def set_twitter_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        await update.message.reply_text(
            'Lütfen önce kaynak ve hedef grup ID\'lerini ayarlayın.'
        )
        return

    twitter_target = update.message.text
    user_info[user_id]['twitter_target'] = twitter_target

    await update.message.reply_text(
        f"Twitter hedefi {twitter_target} olarak ayarlandı."
    )

async def forward_twitter_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        await update.message.reply_text(
            'Lütfen önce kaynak, hedef grup ve Twitter hedefi bilgilerini ayarlayın.'
        )
        return

    twitter_target = user_info[user_id].get('twitter_target')
    if not twitter_target:
        await update.message.reply_text(
            'Twitter hedefi belirlenmedi. Lütfen hedefi girin.'
        )
        return

    twitter_updates = get_twitter_updates(twitter_target)
    await update.message.reply_text(
        f"Twitter hedefinden alınan güncellemeler:\n{twitter_updates}"
    )
