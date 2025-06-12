from fastapi import FastAPI

from ...vertex import ask_gemini
from ...a2a_utils import format_mcp

app = FastAPI(title="Summarizer Agent")


@app.post("/mcp")
async def mcp(message: dict):
    content = message.get("content", "")
    prompt = f"Summarize the following in a short paragraph:\n\n{content}"
    summary = ask_gemini(prompt)
    return format_mcp("summarizer", summary)
