import asyncio
import nest_asyncio

from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient


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
    """Parallelize searching for multiple entities."""
    tasks = [search_entity_description(entity) for entity in entities]
    descriptions = await asyncio.gather(*tasks)
    return dict(zip(entities, descriptions))


def search_entities_sync(entities: list[str]):
    """Synchronous wrapper that Streamlit can call."""
    try:
        # Check if an event loop is already running (Streamlit context)
        nest_asyncio.apply()
    except ImportError:
        pass

    return asyncio.run(process_entities(entities))
