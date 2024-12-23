import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest

# Logger ayarları
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

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
        logging.info(f"Mesaj kaynaktan gelmedi. Kaynak Kanal: {source_channel}, Gelen Kanal: {update.message.chat.id}")
        return  # Eğer kaynaktan gelmiyorsa, işlem yapılmaz

    # Mesaj tipi kontrolü
    if update.message.text:
        # Metin mesajı gönder
        try:
            await context.bot.send_message(target_channel, update.message.text)
            logging.info(f"Metin mesajı gönderildi. Hedef Kanal: {target_channel}")
        except BadRequest as e:
            logging.error(f"Metin mesajı gönderilirken hata oluştu: {e}")

    # Fotoğraf kontrolü
    elif update.message.photo:
        # Fotoğraf gönder
        try:
            photo = update.message.photo[-1]  # Fotoğrafın en yüksek çözünürlüğünü alıyoruz
            await context.bot.send_photo(target_channel, photo.file_id)
            logging.info(f"Fotoğraf gönderildi. Hedef Kanal: {target_channel}")
        except BadRequest as e:
            logging.error(f"Fotoğraf gönderilirken hata oluştu: {e}")

    # Video kontrolü
    elif update.message.video:
        # Video gönder
        try:
            await context.bot.send_video(target_channel, update.message.video.file_id)
            logging.info(f"Video gönderildi. Hedef Kanal: {target_channel}")
        except BadRequest as e:
            logging.error(f"Video gönderilirken hata oluştu: {e}")

    # Belge kontrolü
    elif update.message.document:
        # Belge gönder
        try:
            await context.bot.send_document(target_channel, update.message.document.file_id)
            logging.info(f"Belge gönderildi. Hedef Kanal: {target_channel}")
        except BadRequest as e:
            logging.error(f"Belge gönderilirken hata oluştu: {e}")

    # Diğer medya türleri (ses, sticker, vs.) eklemek için benzer kontroller yapılabilir.
    else:
        logging.info("Desteklenmeyen medya türü alındı.")
