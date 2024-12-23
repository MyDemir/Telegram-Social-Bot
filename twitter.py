import feedparser
import logging

# Logger kurulumu
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # DEBUG seviyesinde log tutacağız
)
logger = logging.getLogger(__name__)

def get_twitter_updates(username):
    try:
        # RSS feed URL'si oluşturma
        rss_url = f"https://nitter.poast.org/{username}/rss"
        logger.debug(f"RSS URL: {rss_url}")

        feed = feedparser.parse(rss_url)

        if len(feed.entries) == 0:
            logger.warning(f"@{username} için yeni tweet bulunamadı.")
            return None, None

        latest_entry = feed.entries[0]
        tweet_text = latest_entry.title
        tweet_url = latest_entry.link

        logger.info(f"Yeni tweet alındı: {tweet_text}")
        return tweet_text, tweet_url

    except Exception as e:
        logger.error(f"Bir hata oluştu: {e}", exc_info=True)  # Hata detayları ile loglama
        return None, None
