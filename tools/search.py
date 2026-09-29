import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def search(query):
    response = tavily.search(query=query)

    results = []

    for result in response["results"]:
        results.append({
            "title": result["title"],
            "url": result["url"],
            "content": result["content"]
        })

    return results