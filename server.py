import sys
from fastmcp import FastMCP, Context

mcp = FastMCP(name="Document Assistant")


def log(msg: str) -> None:
    # stdio transport uses the server's stdout for the MCP protocol,
    # so trace output MUST go to stderr to avoid corrupting the stream.
    print(msg, file=sys.stderr, flush=True)


@mcp.tool()
async def summarize_document(document_text: str, ctx: Context) -> str:
    """Generate a summary of the given document text."""
    log("[2] SERVER: summarize_document tool invoked")
    log("[3] SERVER: calling ctx.sample(...) — asking the CLIENT to generate (no LLM here)")
    # Request the client's LLM to summarize the document
    response = await ctx.sample(
        messages=f"Summarize the following document:\n{document_text}",
        system_prompt="You are an expert summarizer. Extract the key ideas and summarize them.",
        temperature=0.7,
        max_tokens=300,
        model_preferences="gpt-4o"
    )
    # Extract the generated summary text from the response
    log("[7] SERVER: received sampled text back from client, formatting tool result")
    summary = response.text.strip()
    return f"Summary:\n{summary}."


if __name__ == "__main__":
    mcp.run()   # stdio
