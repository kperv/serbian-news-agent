import os

import feedparser
from dotenv import load_dotenv
from newspaper import Article, Config

VIJESTI_RSS = os.getenv("VIJESTI_RSS", "https://www.vijesti.me/rss")

load_dotenv()


def get_latest_news_link(rss_url):
    """Parses the RSS feed and returns the URL of the most recent article."""
    print(f"Fetching feed from: {rss_url}")
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        return None

    # Get the first (latest) entry
    # TODO: Consider holding a list of recent articles to avoid repeats
    latest_item = feed.entries[0]
    return latest_item.link


def extract_article(url):
    """Downloads and parses the full text from a specific news URL."""

    print(f"Scraping article: {url}")

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    config = Config()
    config.browser_user_agent = user_agent
    config.request_timeout = 10

    # 2. Pass the config to the Article
    article = Article(url, language="sr", config=config)

    try:
        article.download()
        article.parse()

        if not article.text.strip():
            print(
                "Warning: Extraction finished but text is empty. The site might be blocking."
            )

        print(f"Scraping article finished")
        return {"title": article.title, "text": article.text, "url": url}
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None


def prepare_article():
    article_data = None
    article_url = get_latest_news_link(VIJESTI_RSS)

    if article_url:
        article_data = extract_article(article_url)
    else:
        print("Failed to retrieve any news items.")
    return article_data
