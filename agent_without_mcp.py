import os
import ssl
import json
import httpx
import truststore

from groq import Groq
from dotenv import load_dotenv
from banking_data import get_unsettled_trades, get_payment_status

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

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_unsettled_trades",
            "description": "Get all unsettled mock FX trades",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_payment_status",
            "description": "Get payment status by payment ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {"type": "string"}
                },
                "required": ["payment_id"]
            }
        }
    }
]

functions = {
    "get_unsettled_trades": get_unsettled_trades,
    "get_payment_status": get_payment_status
}

messages = [{
    "role": "system",
    "content": "You are an FX banking assistant. Use tools for banking data. Data is mock."
}]

print("FX Assistant without MCP. Type exit to quit.")

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    messages.append({"role": "user", "content": question})

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            print("\nAssistant:", message.content)
            break

        
        for call in message.tool_calls:
            name = call.function.name
            raw_args = call.function.arguments or "{}"

            args = json.loads(raw_args)

            if not isinstance(args, dict):
                args = {}

            if name == "get_unsettled_trades":
                result = functions[name]()
            else:
                result = functions[name](**args)

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)
            })
