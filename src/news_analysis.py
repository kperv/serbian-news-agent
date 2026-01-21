import os

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.parse_news import prepare_article
from src.utils import load_from_cache, save_to_cache

load_dotenv()
VIJESTI_RSS = os.getenv("VIJESTI_RSS", "https://www.vijesti.me/rss")
CACHE_FILE = os.getenv("CACHE_FILE", "article_cache.json")


class ArticleInfo(BaseModel):
    summary: str = Field(description="Concise summary in Russian")
    entities: list[str] = Field(
        description="List of people, organizations, and locations from the article"
    )
    study_lemmas: list[str] = Field(description="Key vocabulary words for study")


def init_model():
    llm = ChatOpenAI(model="gpt-5-nano", temperature=0)
    system_instruction = """
        You are a language agent specializing in Serbian news. 
        Provide a concise Russian summary, extract key entities, 
        and identify useful Serbian study lemmas (nouns, verbs, adjectives).
        The summary should capture the main points and essence of the article while being brief and to the point. Avoid adding any personal opinions or extraneous information.
        These lemmas should include nouns, verbs and adjectives that are central to understanding the article. Exclude any entities already listed. Lemmas should be useful for language learning.
        """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_instruction),
            ("human", "Analyze the following article:\n\n{article_text}"),
        ]
    )
    structured_llm = llm.with_structured_output(ArticleInfo)
    return prompt | structured_llm


def analyze_article(chain, article_text: str) -> ArticleInfo:
    return chain.invoke({"article_text": article_text})
