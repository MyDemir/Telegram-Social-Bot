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
    # Kullanıcıya bilgilendirme mesajı gönder
    await update.message.reply_text(
        "Merhaba! Ben size kanal içeriğini bir kanaldan diğerine iletmek için yardımcı olacağım.\n\n"
        "Lütfen aşağıdaki adımları takip edin:\n"
        "1. Kaynak kanal ve hedef kanal bilgilerini yazın.\n"
        "2. Kanal bilgilerini doğru şekilde girdiğinizde işlemi gerçekleştireceğim.\n\n"
        "Örnek: /set_channels @kaynakkanal @hedefkanal"
    )

# Kanal ID'si veya kullanıcı adı al
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()

    if len(user_input) == 3 and user_input[0] == '/set_channels':
        source_channel_input = user_input[1]
        target_channel_input = user_input[2]

        # Kanal kullanıcı adı yerine ID kullanılıyorsa, doğrudan ID'yi kabul edelim
        if source_channel_input.startswith('@'):
            source_channel_id = await get_channel_id(context, source_channel_input)
            if source_channel_id is None:
                await update.message.reply_text("Kaynak kanal kullanıcı adı geçersiz veya bulunamadı.")
                return
        else:
            source_channel_id = int(source_channel_input)

        if target_channel_input.startswith('@'):
            target_channel_id = await get_channel_id(context, target_channel_input)
            if target_channel_id is None:
                await update.message.reply_text("Hedef kanal kullanıcı adı geçersiz veya bulunamadı.")
                return
        else:
            target_channel_id = int(target_channel_input)

        # Kullanıcı bilgilerini kaydedelim
        user_info[user_id] = {
            "source_channel": source_channel_id,
            "target_channel": target_channel_id
        }
        save_user_info(user_info)

        await update.message.reply_text(
            f"Başarıyla kanal bilgileri alındı!\n"
            f"Kaynak kanal: {source_channel_input} ({source_channel_id})\n"
            f"Hedef kanal: {target_channel_input} ({target_channel_id})"
        )
    else:
        await update.message.reply_text(
            "Lütfen iki kanal kullanıcı adı ya da ID'si girin. Örnek: /set_channels @kaynakkanal @hedefkanal"
        )

# Kanal kullanıcı adı ile ID almak
async def get_channel_id(context, username):
    try:
        channel = await context.bot.get_chat(username)
        return channel.id
    except Exception as e:
        return None

# Mesajları kopyalamak için handler
async def forward_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    source_channel = user_info[user_id]['source_channel']
    target_channel = user_info[user_id]['target_channel']
    
    # Mesajın kaynak kanalından gelip gelmediğini kontrol et
    if update.message.chat.id != int(source_channel):  # source_channel ID'si doğrulanır
        return  # Eğer kaynaktan gelmiyorsa, işlem yapılmaz

    # Kaynak kanalın linkini al
    source_channel_link = f"t.me/{update.message.chat.username}" if update.message.chat.username else f"Kanala Erişim Yok"

    # Kaynak kanal için bilgilendirme mesajı ve buton gönder
    try:
        # Buton oluşturuluyor
        keyboard = [
            [InlineKeyboardButton("Yeni İçerike Bak", url=source_channel_link)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            target_channel,
            "🔔 Analiz Kanalimizda Yeni içerik var! Kanala göz atmak için butona tıklayın. 🔔",
            reply_markup=reply_markup
        )
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")
