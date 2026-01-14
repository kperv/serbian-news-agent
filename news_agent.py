from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pydantic import BaseModel
from typing import Any
import os
import json

from parse_news import prepare_article

load_dotenv()
VIJESTI_RSS = os.getenv("VIJESTI_RSS", "https://www.vijesti.me/rss")
CACHE_FILE = os.getenv("CACHE_FILE", "article_cache.json")


class ArticleInfo(BaseModel):
    summary: str
    entities: list[str]
    study_lemmas: list[str]


def init_agent() -> Any:
    system_prompt = """
You are a language agent specializing in Serbian news articles and extracting information useful for further study. 

The first task is to read a given Serbian news article and produce a concise summary in Russian.
The summary should capture the main points and essence of the article while being brief and to the point. Avoid adding any personal opinions or extraneous information.

The second task is to extract and list the main entities mentioned in the article, such as people, organizations, locations, and significant terms. 
Keep the list focused on the most relevant entities that are central to the article's content.

Finally, identify key lemmas that would be useful for further study or analysis of the article's content. 
These lemmas should include nouns, verbs and adjectives that are central to understanding the article. Exclude any entities already listed. Lemmas should be useful for language learning.

Your output should be structured in the following JSON format:
{
  "summary": "<Concise summary of the article in Serbian>",
  "entities": ["<Entity1>", "<Entity2>", "..."],
  "study_lemmas": ["<Lemma1>", "<Lemma2>", "..."]
"""
    news_agent = create_agent(
        model="gpt-5-nano",
        system_prompt=system_prompt,
        response_format=ArticleInfo,
    )
    return news_agent


def analyze_article(news_agent: Any, article_text: str) -> ArticleInfo:
    print("Analyzing article with language agent...")
    question = HumanMessage(content=f"Analyze the following article:\n\n{article_text}")

    response = news_agent.invoke({"messages": [question]})
    print
    return response["structured_response"]


def load_from_cache():
    """Loads data from the local JSON file if it exists."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


if __name__ == "__main__":
    article_info = load_from_cache()
    if article_info:
        news_agent = init_agent()
        analysis = analyze_article(news_agent, article_info["text"])

        print("Article Title:", article_info["title"])
        print("Article URL:", article_info["url"])
        print("Summary:", analysis.summary)
        print("Entities:", analysis.entities)
        print("Study Lemmas:", analysis.study_lemmas)
