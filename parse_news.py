import os

import feedparser
from newspaper import Article
from dotenv import load_dotenv

from utils import save_to_cache

VIJESTI_RSS = os.getenv("VIJESTI_RSS", "https://www.vijesti.me/rss")
CACHE_FILE = os.getenv("CACHE_FILE", "article_cache.json")

load_dotenv()


def get_latest_news_link(rss_url):
    """Parses the RSS feed and returns the URL of the most recent article."""
    print(f"Fetching feed from: {rss_url}")
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        return None

    # Get the first (latest) entry
    latest_item = feed.entries[0]
    return latest_item.link


def extract_article(url):
    """Downloads and parses the full text from a specific news URL."""
    print(f"Scraping article: {url}")

    article = Article(url, language="sr")
    article.download()
    article.parse()
    print(f"Scraping article finished")
    return {"title": article.title, "text": article.text, "url": url}


def prepare_article():
    article_data = None
    article_url = get_latest_news_link(VIJESTI_RSS)

    if article_url:
        article_data = extract_article(article_url)
    else:
        print("Failed to retrieve any news items.")
    return article_data


if __name__ == "__main__":
    article = prepare_article()
    if article:
        save_to_cache(article)
        print("Article Title:", article["title"])
        print("Article URL:", article["url"])
        print("Article Text:", article["text"][:500], "...")
