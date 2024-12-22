import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest
from twitter import get_twitter_updates  # Twitter güncellemelerini almak için

# Kullanıcı bilgilerini saklayacak JSON dosyasını açma
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
        'Merhaba! Bot, kaynak kanal ile hedef kanal arasında mesaj kopyalayacak.'
        ' İlk olarak, iki kanal ID\'si veya kullanıcı adı girmeniz gerekecek. '
        'Örnek: /set_channels @kaynakkanal @hedefkanal'
    )

# Botun üye olduğu kanalları al
async def get_bot_channels(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    # Botun katıldığı tüm kanalların bilgilerini manuel olarak saklayabilirsiniz
    bot_channels = [
        {'id': '@grafikmerdo', 'name': 'GrafikMerdo'},
        {'id': '@cryptomerdoo', 'name': 'Cryptomerdoo'}
    ]
    
    # Inline keyboard ile kanalları seçtirme
    keyboard = [
        [InlineKeyboardButton(channel['name'], callback_data=channel['id'])] for channel in bot_channels
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if step == 'source':
        await update.message.reply_text(
            "Kaynak kanalını seçin:",
            reply_markup=reply_markup
        )
    elif step == 'target':
        await update.message.reply_text(
            "Hedef kanalını seçin:",
            reply_markup=reply_markup
        )

# Kanal seçildiğinde yapılacak işlem
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    selected_channel = query.data  # Seçilen kanal ID'si
    user_id = update.callback_query.from_user.id
    
    await query.answer()  # Inline butonun durumunu güncelle
    
    # Eğer kullanıcı kaynak kanal seçtiyse, kaynak kanal kaydedilir
    if 'source_channel' not in user_info.get(user_id, {}):
        user_info[user_id] = {'source_channel': selected_channel}
        save_user_info(user_info)
        await query.edit_message_text(
            f"Kaynak kanal olarak {selected_channel} seçildi. Şimdi hedef kanalını seçin."
        )
        await get_bot_channels(update, context, step='target')
    # Eğer kullanıcı hedef kanal seçtiyse, hedef kanal kaydedilir
    elif 'target_channel' not in user_info.get(user_id, {}):
        user_info[user_id]['target_channel'] = selected_channel
        save_user_info(user_info)
        await query.edit_message_text(
            f"Hedef kanal olarak {selected_channel} seçildi."
        )
        await query.message.reply_text(
            f"Kaynak kanal: {user_info[user_id]['source_channel']}\n"
            f"Hedef kanal: {user_info[user_id]['target_channel']} olarak ayarlandı."
        )

# Kanal ID'si veya kullanıcı adı al
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    # Admin kontrolü
    if not update.message.chat.get_member(user_id).status in ["administrator", "creator"]:
        await update.message.reply_text('Bu kanalda admin değilsiniz. Admin olmalısınız.')
        return

    # Kanal bilgilerini almak için kaynak kanal seçme adımına geçilir
    await get_bot_channels(update, context, step='source')

# Mesajları kopyalamak için handler
async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    source_channel = user_info[user_id]['source_channel']
    target_channel = user_info[user_id]['target_channel']
    
    # Mesajları hedef kanala ilet
    try:
        if update.message.chat.id == source_channel:
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
