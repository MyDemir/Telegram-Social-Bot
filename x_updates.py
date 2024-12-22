import requests
from bs4 import BeautifulSoup
import re

def get_twitter_updates(username: str):
    # Nitter sayfasına istek göndermek için URL'yi oluşturuyoruz
    nitter_url = f"https://nitter.poast.org/{username}"

    try:
        # Nitter sayfasına HTTP isteği gönderiyoruz
        response = requests.get(nitter_url)
        response.raise_for_status()  # Hata varsa fırlatılır
        
        # Sayfanın HTML içeriğini BeautifulSoup ile parse ediyoruz
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tweetlerin bulunduğu HTML etiketini arıyoruz
        tweets = soup.find_all('div', class_='timeline-tweet')
        
        if not tweets:
            return "Tweet bulunamadı veya kullanıcı adı yanlış."
        
        updates = []
        for tweet in tweets:
            tweet_text = tweet.find('div', class_='tweet-content')
            tweet_media = tweet.find('div', class_='media')
            
            if tweet_text:
                # Tweetin metnini çıkarıyoruz
                tweet_content = tweet_text.get_text(strip=True)
                
                # Medya varsa, medya bağlantılarını çıkartıyoruz
                media_content = None
                if tweet_media:
                    # Görsellerin (resimlerin) bağlantılarını çıkartıyoruz
                    images = tweet_media.find_all('img', src=True)
                    media_content = []
                    for img in images:
                        img_url = img['src']
                        # Resim URL'lerini listeye ekliyoruz
                        media_content.append(img_url)

                # Eğer medya varsa, tweet metni ile medya bağlantılarını birleştiriyoruz
                if media_content:
                    updates.append(f"{tweet_content}\nMedya: {', '.join(media_content)}")
                else:
                    updates.append(tweet_content)

        # Tweet içeriklerini döndürüyoruz
        return "\n\n".join(updates)

    except requests.exceptions.RequestException as e:
        return f"Hata: {e}"
