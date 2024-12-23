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

# Admin cache (önbellek)
admin_cache = {}

# Kaynak kanalındaki adminleri almak için fonksiyon
async def get_channel_admins(context: ContextTypes.DEFAULT_TYPE, chat_id) -> list:
    if chat_id in admin_cache:
        return admin_cache[chat_id]  # Cache'den admin listesini döndür
    
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        admin_cache[chat_id] = admin_ids  # Admin listesini önbelleğe al
        return admin_ids
    except Exception as e:
        print(f"Admin listesi alınırken hata oluştu: {e}")
        return []

# Admin kontrolü ekleyen start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    
    # Admin kontrolü yapılıyor
    admin_ids = await get_channel_admins(context, chat_id)
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
    chat_id = update.message.chat.id

    # Admin kontrolü
    admin_ids = await get_channel_admins(context, chat_id)
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
    chat_id = update.message.chat.id
    
    # Kaynak kanalın adminlerini al
    admin_ids = await get_channel_admins(context, chat_id)
    
    # Eğer kullanıcı admin değilse, mesajı iletme
    if user_id not in admin_ids:
        return

    # Admin olduğunda mesajı hedef kanala ilet
    if user_id in user_info:
        source_channel = user_info[user_id]['source_channel']
        target_channel = user_info[user_id]['target_channel']
        
        # Kaynak kanal doğrulaması (ID'leri integer yaparak karşılaştır)
        if chat_id != int(source_channel):
            return  # Kaynak kanal dışından gelen mesajlar işlenmez

        try:
            # Mesajı hedef kanala gönder
            if update.message.text:
                await context.bot.send_message(target_channel, update.message.text)
            elif update.message.photo:
                await context.bot.send_photo(
                    chat_id=target_channel,
                    photo=update.message.photo[-1].file_id,
                    caption=update.message.caption if update.message.caption else ""
                )
        except BadRequest as e:
            await update.message.reply_text(f"Bir hata oluştu: {e}")
    else:
        await update.message.reply_text("Kanal ayarları yapılmamış. Lütfen /set_channels komutunu kullanın.")
