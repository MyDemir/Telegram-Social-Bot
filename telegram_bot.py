from telegram import Update, Chat
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,  # filters artık küçük harfle import ediliyor
    ContextTypes,
)
from twitter import get_twitter_updates
from config import TELEGRAM_BOT_TOKEN

user_info = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Merhaba! Ben Telegram Social Bot V2.\n'
        'Mesaj aktarımı yapmak için kaynak ve hedef grup bilgilerini girebilirsiniz.'
    )

# Kaynak grup ayarlama fonksiyonu
async def set_source_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    source_group_id = update.message.text.strip()
    user_info[user_id] = {'source_group': source_group_id}
    
    await update.message.reply_text(
        f"Kaynak grup {source_group_id} olarak ayarlandı.\nŞimdi hedef grup ID'sini girin."
    )

# Hedef grup ayarlama fonksiyonu
async def set_target_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    # Kaynak grup ID'si daha önce girildiyse, devam et
    if user_id not in user_info or 'source_group' not in user_info[user_id]:
        await update.message.reply_text('Lütfen önce kaynak grup ID\'sini girin.')
        return

    # Hedef grup bilgilerini al
    target_group_id = update.message.text.strip()  # ID'yi temizle

    # ID doğrulama işlemi
    if not target_group_id.startswith("-100"):
        await update.message.reply_text("Geçerli bir grup veya kanal ID'si girin (örneğin: -1001234567890).")
        return
    
    user_info[user_id]['target_group'] = target_group_id

    await update.message.reply_text(
        f"Hedef grup {target_group_id} olarak ayarlandı.\n"
        "Şimdi Twitter kullanıcı adı veya hashtag girin (örneğin: @username veya #hashtag)."
    )

# Twitter hedefi ayarlama fonksiyonu
async def set_twitter_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        await update.message.reply_text(
            'Lütfen önce kaynak ve hedef grup ID\'lerini ayarlayın.'
        )
        return

    twitter_target = update.message.text.strip()
    user_info[user_id]['twitter_target'] = twitter_target

    await update.message.reply_text(
        f"Twitter hedefi {twitter_target} olarak ayarlandı."
    )

# Twitter güncellemelerini gönderme fonksiyonu
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

# Grup ID doğrulama fonksiyonu
async def validate_group(update, context, group_type):
    chat_id = update.message.text.strip()
    chat_info = None

    try:
        # Kanal veya grup bilgilerini çekmeye çalış
        chat_info = await context.bot.get_chat(chat_id)
    except Exception as e:
        await update.message.reply_text(f"{group_type.capitalize()} grup bulunamadı. Lütfen geçerli bir ID girin.")
        return

    # Eğer geçerliyse ayarla
    if chat_info:
        if group_type == 'source':
            context.user_data['source_group_id'] = chat_info.id  # Grup/Kanal ID'si
            context.user_data['source_group_username'] = chat_info.username  # Grup/Kanal kullanıcı adı
            await update.message.reply_text(f"Kaynak grup '{chat_info.username}' olarak ayarlandı.")
        elif group_type == 'target':
            target_groups = context.user_data.get('target_groups', [])
            target_groups.append(chat_info.id)  # Grup/Kanal ID'si
            context.user_data['target_groups'] = target_groups
            await update.message.reply_text(f"Hedef grup '{chat_info.username}' olarak eklendi.")
    else:
        await update.message.reply_text(f"{group_type.capitalize()} grup ayarlanamadı. Lütfen tekrar deneyin.")

# Grup ekleme komutu için handler
async def handle_group_addition(update, context, group_type):
    await validate_group(update, context, group_type)
