import requests
from bs4 import BeautifulSoup

# Asenkron hale getirdik
async def get_x_updates(username):
    x_url = f"https://nitter.poast.org/{username}"
    response = requests.get(x_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.find_all('div', class_='tweet-content')
        updates = [post.get_text() for post in posts]
        if updates:
            return "\n\n".join(updates)
        else:
            return "Henüz bir güncelleme yok."
    else:
        return "X'ten veri alınamadı!"
