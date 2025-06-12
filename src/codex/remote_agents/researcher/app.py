from fastapi import FastAPI

from ...vertex import ask_gemini
from ...a2a_utils import format_mcp

app = FastAPI(title="Researcher Agent")


@app.post("/mcp")
async def mcp(message: dict):
    content = message.get("content", "")
    prompt = f"Research the following topic and provide key points:\n\n{content}"
    answer = ask_gemini(prompt)
    return format_mcp("researcher", answer)
