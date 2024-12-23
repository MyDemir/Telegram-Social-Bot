import requests
from xml.etree import ElementTree

def get_twitter_updates(twitter_target: str) -> tuple:
    """X (Twitter) güncellemelerini Nitter üzerinden RSS ile alır."""
    url = f"https://nitter.poast.org/{twitter_target}/rss"  # Nitter RSS URL'si
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP hatalarını kontrol et

        # XML parse işlemi
        root = ElementTree.fromstring(response.content)
        latest_item = root.find(".//channel/item")  # Son güncellemeyi al

        tweet_text = latest_item.find("title").text if latest_item else None
        tweet_url = latest_item.find("link").text if latest_item else None

        return tweet_text, tweet_url

    except requests.RequestException as e:
        return f"Twitter'dan veri çekme hatası: {e}", None

    except Exception as e:
        return f"Bir hata oluştu: {e}", None
