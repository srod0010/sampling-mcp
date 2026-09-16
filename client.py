from fastmcp import Client
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext
from litellm import acompletion
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

# A minimal client-side implementation (not the complete logic): to particularly demonstrate the sampling handler.


async def sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    ctx: RequestContext
) -> str:
    """Handle sampling requests using LiteLLM and OpenAI GPT-4o."""
    print("[4] CLIENT: sampling_handler invoked — the server's ctx.sample landed here", flush=True)
    chat_messages = []
    if params.systemPrompt:
        chat_messages.append(
            {"role": "system", "content": params.systemPrompt})
    for m in messages:
        if m.content.type == "text":
            chat_messages.append({"role": m.role, "content": m.content.text})
    if params.modelPreferences:
        # if it's a list, take first supported; if string, use directly.
        # This is demonstrational, however, in reality a more robust handling logic and fallback is needed.
        preferred_model = params.modelPreferences.hints[0].name
    print(f"    ↳ params from server: model={preferred_model} "
          f"temperature={params.temperature} max_tokens={params.maxTokens}", flush=True)
    try:
        print(f"[5] CLIENT: calling the real LLM ({preferred_model}) via LiteLLM…", flush=True)
        response = await acompletion(
            model=preferred_model,
            messages=chat_messages,
            temperature=params.temperature,
            max_tokens=params.maxTokens,
            api_key=os.getenv("OPENAI_API_KEY"),  # .env file approach can also be used
        )
        generated_text = response["choices"][0]["message"]["content"]
        print("[6] CLIENT: LLM returned text — returning it to the server as the sampling result", flush=True)
    except Exception as e:
        generated_text = f"[Error: LLM failed: {e}]"

    return generated_text

client = Client("server.py", sampling_handler=sampling_handler)  # stdio


async def main():

    print(client.transport)
    async with client:
        f = open("sample.txt", "r")
        print("[1] CLIENT: calling tool 'summarize_document' on the server", flush=True)
        result = await client.call_tool("summarize_document", {"document_text": f.read()})
        print("[8] CLIENT: tool result received:\n", flush=True)
        print(result)

    # Connection is closed automatically here
    print(f"Connected?: {client.is_connected()}")   # False: since connection gets closed gracefully.
    # The client operates asynchronously within the async with block.
    # This context manager automatically handles the connection, initializations, and clean up upon exit.

if __name__ == "__main__":
    # cd /Users/saviorodrigues/Developer/sampling-mcp-code
    # uv run client.py
    asyncio.run(main())
