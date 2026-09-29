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

# First LLM call
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message

# Check if the LLM wants to use a tool
if message.tool_calls:

    tool_call = message.tool_calls[0]

    tool_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if tool_name == "search":

        # Execute our Python search function
        results = search(arguments["query"])

        # Add the LLM's tool request to the conversation
        messages.append(message)

        # Add the tool results
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(results)
        })

        # Send everything back to the LLM
        final_response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages
        )

        print("\nFinal answer:")
        print(final_response.choices[0].message.content)

else:
    # If no search was needed
    print("\nAnswer:")
    print(message.content)