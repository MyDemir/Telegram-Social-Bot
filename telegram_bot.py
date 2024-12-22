import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.error import BadRequest
from twitter import get_twitter_updates

def load_user_info():
    try:
        with open("user_info.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_info(user_info):
    with open("user_info.json", "w") as file:
        json.dump(user_info, file, indent=4)

user_info = load_user_info()

# Start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Merhaba! Bot, kaynak kanal ile hedef kanal arasında mesaj kopyalayacak.\n'
        'İlk olarak, iki kanal ID\'si veya kullanıcı adı girmeniz gerekecek.\n'
        'Örnek: /set_channels @kaynakkanal @hedefkanal'
    )

# Kanal seçimi için düğmeler
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Kaynak Kanal Seç", callback_data='set_source')],
        [InlineKeyboardButton("Hedef Kanal Seç", callback_data='set_target')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Lütfen bir işlem seçin:', reply_markup=reply_markup)

# Callback fonksiyonu (Düğmeye tıklanınca çalışır)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'set_source':
        context.user_data['step'] = 'source'
        await query.edit_message_text('Kaynak kanalı belirtin. Örnek: @kaynakkanal')
    
    elif query.data == 'set_target':
        context.user_data['step'] = 'target'
        await query.edit_message_text('Hedef kanalı belirtin. Örnek: @hedefkanal')

# Kaynak veya hedef kanalı kaydetme
async def handle_channel_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    step = context.user_data.get('step')

    if not step:
        await update.message.reply_text("Lütfen önce bir seçenek belirleyin.")
        return

    channel = update.message.text.strip()
    
    if step == 'source':
        user_info[user_id] = user_info.get(user_id, {})
        user_info[user_id]['source_channel'] = channel
        await update.message.reply_text(f"Kaynak kanal {channel} olarak ayarlandı.")
    
    elif step == 'target':
        user_info[user_id] = user_info.get(user_id, {})
        user_info[user_id]['target_channel'] = channel
        await update.message.reply_text(f"Hedef kanal {channel} olarak ayarlandı.")
    
    save_user_info(user_info)
    context.user_data['step'] = None

# Mesajları kopyalamak için handler
async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    source_channel = user_info[user_id]['source_channel']
    target_channel = user_info[user_id]['target_channel']
    
    try:
        if update.message.chat.username == source_channel:
            await context.bot.send_message(target_channel, update.message.text)
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")

# Twitter güncellemelerini gönderme fonksiyonu
async def forward_twitter_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    twitter_target = user_info[user_id].get('twitter_target')
    if not twitter_target:
        await update.message.reply_text('Twitter hedefi belirlenmedi.')
        return

    twitter_updates = get_twitter_updates(twitter_target)
    await update.message.reply_text(
        f"Twitter hedefinden alınan güncellemeler:\n{twitter_updates}"
        )
