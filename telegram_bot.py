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
    try:
        chat_member = await update.message.chat.get_member(user_id)
        if chat_member.status not in ["administrator", "creator"]:
            await update.message.reply_text('Bu kanalda admin değilsiniz. Admin olmalısınız.')
            return
    except BadRequest as e:
        await update.message.reply_text('Kanal üyeliğinizi kontrol edemedim.')
        return

    # Manuel girilen kanal ID'leri işleme
    if len(user_input) == 3 and user_input[0] == '/set_channels':
        source_channel = user_input[1]
        target_channel = user_input[2]

        user_info = load_user_info()  # JSON'dan kullanıcı bilgilerini al
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

# Buton tıklamalarını işleme
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Butona tıklanınca kanalları seçme
    if query.data == 'select_channel':
        chat_list = await context.bot.get_chat_administrators(query.message.chat_id)
        channels = [chat.user.username for chat in chat_list if chat.user.username]
        
        if channels:
            await query.edit_message_text(
                f"Bulunduğunuz kanallar: {', '.join(channels)}\n"
                "Lütfen aşağıdaki formatla yanıt verin:\n"
                "/set_channels @kaynakkanal @hedefkanal"
            )
        else:
            await query.edit_message_text("Hiç kanal bulunamadı.")

# Mesajları kopyalamak için handler
async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    user_info = load_user_info()  # Kullanıcı bilgilerini yükle
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    source_channel = user_info[user_id].get('source_channel')
    target_channel = user_info[user_id].get('target_channel')
    
    # Kaynak kanalından gelen mesajı hedef kanala ilet
    try:
        if update.message.chat.id == source_channel:
            await context.bot.send_message(target_channel, update.message.text)
            await update.message.reply_text(f"Mesaj başarıyla {target_channel} kanalına iletildi.")
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")

# X (Twitter) güncellemelerini gönderme fonksiyonu
async def forward_twitter_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_info = load_user_info()

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
