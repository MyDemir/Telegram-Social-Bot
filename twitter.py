import requests
from xml.etree import ElementTree

def get_twitter_updates(twitter_target: str) -> tuple:
    """X (Twitter) güncellemelerini Nitter üzerinden RSS ile alır."""
    url = f"https://nitter.poast.org/{twitter_target}/rss"  # Nitter RSS URL'si
    try:
        # Nitter RSS feed'ini al
        response = requests.get(url)
        response.raise_for_status()  # HTTP hatalarını kontrol et
        
        # XML verisini parse et
        root = ElementTree.fromstring(response.content)
        latest_item = root.find(".//channel/item")  # Son güncellemeyi al

        # Tweet metni ve URL'sini al
        tweet_text = latest_item.find("title").text if latest_item else None
        tweet_url = latest_item.find("link").text if latest_item else None

        if tweet_text and tweet_url:
            return tweet_text, tweet_url  # Eğer veri bulunursa döndürüyoruz
        else:
            return "Son tweet bulunamadı.", None  # Eğer tweet yoksa hata mesajı döndür

    except requests.RequestException as e:
        return f"Twitter'dan veri çekme hatası: {e}", None  # Bağlantı veya HTTP hatası

    except Exception as e:
        return f"Bir hata oluştu: {e}", None  # Diğer hatalar
