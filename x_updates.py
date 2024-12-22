import requests
from config import X_API_KEY

def send_updates(update, context):
    username = context.args[0]  # Kullanıcı adı al
    updates = get_x_updates(username)
    context.bot.send_message(chat_id=update.effective_chat.id, text=updates)

def get_x_updates(username):
    # Burada X platformuna API isteği yapılabilir. Bu örnekte basit bir mesaj döneceğiz.
    return f"{username}'ın son güncellemeleri: [Güncelleme içerik buraya gelir]."
