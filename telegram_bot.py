import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo, InputMediaAnimation, InputMediaDocument
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
async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    source_channel = user_info[user_id]['source_channel']
    target_channel = user_info[user_id]['target_channel']
    
    # Mesajın kaynak kanalından gelip gelmediğini kontrol et
    if update.message.chat.id != int(source_channel):  # source_channel ID'si doğrulanır
        return  # Eğer kaynaktan gelmiyorsa, işlem yapılmaz

    media_group = []
    if update.message.text:
        media_group.append(update.message.text)

    # Fotoğraf gönderme
    if update.message.photo:
        for photo in update.message.photo:
            media_group.append(InputMediaPhoto(photo.file_id))
    
    # Video gönderme
    if update.message.video:
        media_group.append(InputMediaVideo(update.message.video.file_id))

    # GIF gönderme
    if update.message.animation:
        media_group.append(InputMediaAnimation(update.message.animation.file_id))

    # Dosya gönderme
    if update.message.document:
        media_group.append(InputMediaDocument(update.message.document.file_id))

    if media_group:
        try:
            if len(media_group) == 1:
                # Sadece metin veya tek medya öğesi varsa
                await context.bot.send_message(target_channel, media_group[0])
            else:
                # Birden fazla medya öğesi varsa, media_group kullanarak gönder
                await context.bot.send_media_group(target_channel, media_group)
        except BadRequest as e:
            await update.message.reply_text(f"Bir hata oluştu: {e}")

# X (Twitter) güncellemelerini gönderme fonksiyonu
async def forward_twitter_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    twitter_target = user_info[user_id].get('twitter_target')
    if not twitter_target:
        await update.message.reply_text('Twitter hedefi belirlenmedi.')
        return

    # X (Twitter) güncellemelerini al
    twitter_updates = get_twitter_updates(twitter_target)
    await update.message.reply_text(
        f"Twitter hedefinden alınan güncellemeler:\n{twitter_updates}"
    )

# Twitter güncellemelerini almak için placeholder fonksiyonu
def get_twitter_updates(target):
    # Gerçek X (Twitter) güncellemeleri almak için burada API kullanabilirsiniz.
    # Şu an için örnek bir mesaj döndürüyor.
    return f"Burada {target} için güncellemeler olacak."
