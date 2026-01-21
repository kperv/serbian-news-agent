import os
import json

from dotenv import load_dotenv


load_dotenv()
VIJESTI_RSS = os.getenv("VIJESTI_RSS", "https://www.vijesti.me/rss")
CACHE_FILE = os.getenv("CACHE_FILE", "article_cache.json")


def save_to_cache(data):
    """Saves the article dictionary to a local JSON file."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        # indent=4 makes it readable; ensure_ascii=False keeps Serbian characters (č, ć, etc.)
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_from_cache():
    """Loads data from the local JSON file if it exists."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
