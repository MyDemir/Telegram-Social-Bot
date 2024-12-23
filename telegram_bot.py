import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest

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

# Kaynak kanalındaki adminleri almak için fonksiyon
async def get_channel_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> list:
    chat_id = update.message.chat.id
    admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admins]
    return admin_ids

# Admin kontrolü ekleyen start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Admin kontrolü yapılıyor
    admin_ids = await get_channel_admins(update, context)
    if user_id not in admin_ids:
        await update.message.reply_text("Bu komutu kullanmaya yetkiniz yok.")
        return

    keyboard = [
        [InlineKeyboardButton("Kanal Seç", callback_data='select_channel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        'Merhaba! Kanal ayarlamak için butona tıklayın veya @kanalismi olarak manuel giriş yapın.',
        reply_markup=reply_markup
    )

# Kanal ID'si veya kullanıcı adı al
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()

    # Admin kontrolü
    admin_ids = await get_channel_admins(update, context)
    if user_id not in admin_ids:
        await update.message.reply_text("Bu komutu kullanmaya yetkiniz yok.")
        return

    # Kanal bilgisi ayarlama
    if len(user_input) == 3 and user_input[0] == '/set_channels':
        source_channel = user_input[1]
        target_channel = user_input[2]

        user_info[user_id] = {
            "source_channel": source_channel,
            "target_channel": target_channel
        }
        save_user_info(user_info)

        await update.message.reply_text(
            f"Kaynak kanal: {source_channel}\nHedef kanal: {target_channel} olarak ayarlandı."
        )
    else:
        await update.message.reply_text('Lütfen iki kanal ID\'si girin. Örnek: /set_channels @kanal1 @kanal2')

# Mesajları kopyalamak için handler
async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Kaynak kanalın adminlerini al
    admin_ids = await get_channel_admins(update, context)
    
    # Eğer kullanıcı admin değilse, mesajı iletme
    if user_id not in admin_ids:
        return

    # Admin olduğunda mesajı hedef kanala ilet
    source_channel = user_info[user_id]['source_channel']
    target_channel = user_info[user_id]['target_channel']
    
    # Kaynak kanal bilgileri
    if update.message.chat.id != int(source_channel):  # Kaynak kanal doğrulaması
        return  # Eğer kaynaktan gelmiyorsa, işlem yapılmaz

    try:
        # Mesajı hedef kanala gönder
        await context.bot.send_message(target_channel, update.message.text)
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")
