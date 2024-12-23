import requests
from bs4 import BeautifulSoup

def get_twitter_updates(twitter_target: str) -> str:
    """X (Twitter) güncellemelerini Nitter üzerinden HTML parsing ile alır."""
    url = f"https://nitter.net/{twitter_target}"  # Nitter URL'si
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP hatalarını kontrol et

        # HTML içeriğini BeautifulSoup ile parse ediyoruz
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tweet'leri bulma (Nitter sayfasındaki tweet'ler <article> etiketlerinde yer alıyor)
        tweets = soup.find_all('article')

        if not tweets:
            return "Güncellemeler bulunamadı."

        # İlk birkaç tweet'in metinlerini alıyoruz
        tweet_texts = []
        for tweet in tweets[:5]:  # İlk 5 tweet'i alıyoruz
            tweet_content = tweet.find('div', {'class': 'tweet-text'})
            if tweet_content:
                tweet_texts.append(tweet_content.get_text())

        # Tweet'leri birleştirerek döndürüyoruz
        return "\n\n".join(tweet_texts)

    except requests.RequestException as e:
        return f"Twitter'dan veri çekme hatası: {e}"

    except Exception as e:
        return f"Bir hata oluştu: {e}"
