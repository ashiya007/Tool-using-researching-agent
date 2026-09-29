import os
import json
from dotenv import load_dotenv
from groq import Groq

from tools.search import search

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

question = input("Ask me something: ")

messages = [
    {
        "role": "system",
        "content": """
You are a research assistant.

You have access to a web search tool.
Use the tool when the user needs information
that may require web research.
"""
    },
    {
        "role": "user",
        "content": question
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the web for information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message
if message.tool_calls:
    tool_call = message.tool_calls[0]

    tool_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if tool_name == "search":
        results = search(arguments["query"])

        print("\nSearch results:")
        for result in results:
            print("\nTitle:", result["title"])
            print("URL:", result["url"])
            print("Content:", result["content"])
print("\nLLM response:")
print(message)