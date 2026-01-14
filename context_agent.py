import asyncio
import os

from pydantic import Field
from dotenv import load_dotenv
from tavily import TavilyClient
from langgraph.types import Command
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent, AgentState
from langchain_mcp_adapters.client import MultiServerMCPClient

from utils import load_from_cache

CACHE_FILE = os.getenv("CACHE_FILE", "article_cache.json")


class EntityContext(AgentState):
    entity: str
    description: str = Field(default="")


load_dotenv()
tavily_client = TavilyClient()
client = MultiServerMCPClient(
    {
        "wikipedia-mcp": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["wikipedia-mcp@latest"],
        }
    }
)


@tool
def web_search(query: str) -> str:
    """Search the web for entity descriptions when Wikipedia lacks info."""
    results = tavily_client.search(query=query, max_results=3)
    return "\n".join(r["content"][:200] for r in results["results"])


async def get_wiki_tools():
    """Load Wikipedia tools once."""
    return await client.get_tools()


async def search_entity_description(entity: str) -> str:
    """Search Wikipedia MCP first, then web for entity description."""

    system_prompt = """
You are an agent that finds concise one-sentence descriptions for given entities. The entity is extracted from serbian news articles. You can update the entity name only if it is ambiguous.
First, use the Wikipedia MCP tool to search for the entity.
If Wikipedia does not return a satisfactory description, use the web search tool.
Output ONLY the description without any additional text.
"""
    wiki_tools = await get_wiki_tools()

    agent = create_agent(
        model="gpt-5-nano", tools=[*wiki_tools, web_search], system_prompt=system_prompt
    )

    result = await agent.ainvoke({"messages": [HumanMessage(content=entity)]})

    return result["messages"][-1].content


async def process_entities(entities: list[str]):
    # TODO: parallelize with asyncio.gather
    results = {}
    for entity in entities:
        description = await search_entity_description(entity)
        results[entity] = description
    return results


def search_entities(entities: list[str]):
    """Synchronous wrapper for entity description search."""

    return asyncio.run(process_entities(entities))


if __name__ == "__main__":
    article_info = load_from_cache()
    if article_info and "entities" in article_info:
        entities = article_info["entities"]
        descriptions = search_entities(entities)
        for entity, desc in descriptions.items():
            print(f"{entity}: {desc}")

    # TODO: save descriptions back to cache or other storage json
