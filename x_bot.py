import requests
from bs4 import BeautifulSoup

def get_x_updates(username):
    x_url = f"https://nitter.poast.org/{username}"  # X (Twitter) kullanıcı ismi
    response = requests.get(x_url)

    if response.status_code == 200:
        # Sayfa içeriğini BeautifulSoup ile parse et
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tweet içeriklerini çekmek
        posts = soup.find_all('div', class_='tweet-content')

        updates = []
        for post in posts:
            post_text = post.get_text()
            updates.append(post_text)

        if updates:
            return "\n\n".join(updates)  # X (Twitter) güncellemelerini birleştirip geri döndürüyoruz
        else:
            return "Henüz bir güncelleme yok."
    else:
        return "X'ten veri alınamadı!"
