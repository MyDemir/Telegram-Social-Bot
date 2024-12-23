import requests
from xml.etree import ElementTree

def get_twitter_updates(twitter_target: str) -> tuple:
    """X (Twitter) güncellemelerini Nitter üzerinden RSS ile alır."""
    url = f"https://nitter.poast.org/{twitter_target}/rss"  # Nitter RSS URL'si
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP hatalarını kontrol et

        # Yanıtı kontrol et
        print(f"URL: {url}")
        print(f"Response Status Code: {response.status_code}")
        
        # XML parse işlemi
        root = ElementTree.fromstring(response.content)
        latest_item = root.find(".//channel/item")  # Son güncellemeyi al

        if latest_item is not None:
            tweet_text = latest_item.find("title").text
            tweet_url = latest_item.find("link").text
            print(f"Tweet Text: {tweet_text}")
            print(f"Tweet URL: {tweet_url}")
            return tweet_text, tweet_url
        else:
            print("Son tweet bulunamadı.")
            return None, None

    except requests.RequestException as e:
        print(f"Twitter'dan veri çekme hatası: {e}")
        return f"Twitter'dan veri çekme hatası: {e}", None

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        return f"Bir hata oluştu: {e}", None
