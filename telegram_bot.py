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
async def get_channel_admins(chat_id, context: ContextTypes.DEFAULT_TYPE) -> list:
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        return [admin.user.id for admin in admins]
    except BadRequest as e:
        print(f"Admin listesi alınırken hata oluştu: {e}")
        return []

# Admin kontrolü ekleyen start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    admin_ids = await get_channel_admins(chat_id, context)
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

# /set_channels komutu
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()

    if len(user_input) == 3 and user_input[0] == '/set_channels':
        source_channel = user_input[1]
        target_channel = user_input[2]

        admin_ids = await get_channel_admins(source_channel, context)
        if user_id not in admin_ids:
            await update.message.reply_text("Bu komutu kullanmaya yetkiniz yok.")
            return

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

# /connect komutu (özel mesajdan kanal bağlama)
async def connect_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    args = context.args

    if len(args) != 2:
        await update.message.reply_text("Yanlış format! Örnek: /connect @kanal1 @kanal2")
        return

    source_channel = args[0]
    target_channel = args[1]

    try:
        source_admins = await get_channel_admins(source_channel, context)
        target_admins = await get_channel_admins(target_channel, context)

        admin_ids = source_admins + target_admins

        if user_id not in admin_ids:
            await update.message.reply_text("Bu kanalları ayarlamak için yetkiniz yok.")
            return

        user_info[user_id] = {
            "source_channel": source_channel,
            "target_channel": target_channel
        }
        save_user_info(user_info)

        await update.message.reply_text(
            f"Bağlantı kuruldu:\nKaynak: {source_channel}\nHedef: {target_channel}"
        )
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")

# Mesajları ileten handler
async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    admin_ids = await get_channel_admins(chat_id, context)
    if user_id not in admin_ids:
        return

    # Mesajı hedef kanala yönlendir
    if user_id in user_info:
        source_channel = user_info[user_id]['source_channel']
        target_channel = user_info[user_id]['target_channel']

        if chat_id == int(source_channel):
            try:
                await context.bot.forward_message(
                    chat_id=target_channel,
                    from_chat_id=chat_id,
                    message_id=update.message.message_id
                )
            except BadRequest as e:
                print(f"Mesaj iletilirken hata: {e}")
