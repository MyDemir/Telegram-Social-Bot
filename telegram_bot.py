import json
from telegram import Update
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

# Start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
async def forward_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    source_channel = user_info[user_id]['source_channel']
    target_channel = user_info[user_id]['target_channel']

    # Mesajın türünü kontrol et ve uygun fonksiyonu çağır
    if update.message.text:  # Eğer metin mesajı varsa
        await send_message_to_channel(context, target_channel, update.message.text)
    elif update.message.photo:  # Eğer fotoğraf varsa
        photo = update.message.photo[-1].file_id  # En yüksek çözünürlüklü fotoğrafı al
        await send_photo_to_channel(context, target_channel, photo)
    elif update.message.video:  # Eğer video varsa
        video = update.message.video.file_id
        await send_video_to_channel(context, target_channel, video)
    elif update.message.document:  # Eğer dosya varsa
        file = update.message.document.file_id
        await send_document_to_channel(context, target_channel, file)
    else:
        print("Unsupported message type.")

# Herhangi bir mesajı hedef kanala ilet
async def send_message_to_channel(context, target_channel, message):
    try:
        await context.bot.send_message(
            chat_id=target_channel,
            text=message
        )
        print("Message sent successfully")
    except BadRequest as e:
        print(f"Error sending message: {e}")

# Fotoğrafı hedef kanala ilet
async def send_photo_to_channel(context, target_channel, photo):
    try:
        await context.bot.send_photo(
            chat_id=target_channel,
            photo=photo
        )
        print("Photo sent successfully")
    except BadRequest as e:
        print(f"Error sending photo: {e}")

# Video'yu hedef kanala ilet
async def send_video_to_channel(context, target_channel, video):
    try:
        await context.bot.send_video(
            chat_id=target_channel,
            video=video
        )
        print("Video sent successfully")
    except BadRequest as e:
        print(f"Error sending video: {e}")

# Dosyayı hedef kanala ilet
async def send_document_to_channel(context, target_channel, file):
    try:
        await context.bot.send_document(
            chat_id=target_channel,
            document=file
        )
        print("Document sent successfully")
    except BadRequest as e:
        print(f"Error sending document: {e}")
