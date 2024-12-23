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
    
    # Kaynak kanalında iletilen mesajları hedef kanala ilet
    if update.message.chat.id != int(source_channel):  # source_channel ID'si doğrulanır
        return  # Eğer kaynaktan gelmiyorsa, işlem yapılmaz

    # Bilgilendirme mesajı (daha kısa ve buton eklenmiş)
    informative_message = (
        f"🔔 *{source_channel} kanalında yeni içerik var!* 🔔\n\n"
        f"👉 *Göz atmak için aşağıdaki butona tıklayın!* 👈"
    )

    # MarkdownV2 karakterlerini kaçırma
    def escape_markdown(text):
        escape_chars = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", ".", "!", "|"]
        for char in escape_chars:
            text = text.replace(char, f"\\{char}")
        return text

    informative_message_escaped = escape_markdown(informative_message)

    # Bilgilendirme mesajını hedef kanala gönder
    try:
        # Bilgilendirme mesajını göndermek ve buton eklemek
        keyboard = [
            [InlineKeyboardButton("Kanalı Görüntüle", url=f"https://t.me/{source_channel}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(target_channel, informative_message_escaped, parse_mode="MarkdownV2", reply_markup=reply_markup)
        print(f"[Bilgi] Bilgilendirme mesajı {target_channel} kanalına başarıyla gönderildi.")
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")
        print(f"[Hata] Bilgilendirme mesajı gönderilemedi: {e}")

    # Metin mesajını hedef kanala ilet
    if update.message.text:
        try:
            await context.bot.send_message(target_channel, update.message.text)
        except BadRequest as e:
            await update.message.reply_text(f"Bir hata oluştu: {e}")
    
    # Fotoğraf, video, dosya gibi medya mesajlarını ilet
    if update.message.photo:
        try:
            await context.bot.send_photo(target_channel, update.message.photo[-1].file_id, caption=update.message.caption)
        except BadRequest as e:
            await update.message.reply_text(f"Bir hata oluştu: {e}")
    
    if update.message.video:
        try:
            await context.bot.send_video(target_channel, update.message.video.file_id, caption=update.message.caption)
        except BadRequest as e:
            await update.message.reply_text(f"Bir hata oluştu: {e}")
    
    if update.message.document:
        try:
            await context.bot.send_document(target_channel, update.message.document.file_id)
        except BadRequest as e:
            await update.message.reply_text(f"Bir hata oluştu: {e}")
