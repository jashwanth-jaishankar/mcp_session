import asyncio
import json
import os
import sys
import ssl
import httpx
import truststore

from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

model = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

ssl_context = truststore.SSLContext(
    ssl.PROTOCOL_TLS_CLIENT
)

http_client = httpx.Client(
    verify=ssl_context
)

client = Groq(
    api_key=os.environ["GROQ_API_KEY"],
    http_client=http_client
)


async def main():
    async with streamable_http_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read, write, _):

        async with ClientSession(read, write) as session:
            await session.initialize()

            
            discovered = await session.list_tools()

            print("\nDiscovered MCP tools:")
            for tool in discovered.tools:
                print(f"- {tool.name}: {tool.description}")
                print(f"  Input schema: {json.dumps(tool.inputSchema, indent=2)}")

            tools = [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                }
            } for tool in discovered.tools]

            print(f"\nTotal tools discovered: {len(tools)}")


            messages = [{
                "role": "system",
                "content": "You are an FX banking assistant. Use tools for banking data. Data is mock."
            }]

            print("FX Assistant with MCP. Type exit to quit.")

            while True:
                question = input("\nYou: ")

                if question.lower() == "exit":
                    break

                messages.append({
                    "role": "user",
                    "content": question
                })

                while True:
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto"
                    )

                    message = response.choices[0].message
                    messages.append(
                        message.model_dump(exclude_none=True)
                    )

                    if not message.tool_calls:
                        print("\nAssistant:", message.content)
                        break

                    for call in message.tool_calls:
                        result = await session.call_tool(
                            call.function.name,
                            arguments=json.loads(
                                call.function.arguments or "{}"
                            )
                        )

                        content = [
                            item.text
                            for item in result.content
                            if getattr(item, "text", None)
                        ]

                        messages.append({
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": "\n".join(content)
                        })


if __name__ == "__main__":
    asyncio.run(main())