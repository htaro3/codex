from fastapi import FastAPI, HTTPException
import os

from ..a2a_utils import format_mcp, send_mcp
from ..vertex import ask_gemini

RESEARCHER_URL = os.getenv("RESEARCHER_URL", "http://localhost:8001/mcp")
SUMMARIZER_URL = os.getenv("SUMMARIZER_URL", "http://localhost:8002/mcp")

app = FastAPI(title="Host Agent")


@app.post("/query")
async def query(data: dict):
    query_text = data.get("query")
    if not query_text:
        raise HTTPException(status_code=400, detail="Missing query")

    # Ask researcher agent
    research_req = format_mcp("host", query_text)
    research_res = await send_mcp(RESEARCHER_URL, research_req)
    research_answer = research_res.get("content", "")

    # Optionally ask Gemini directly
    gemini_answer = ask_gemini(query_text)

    # Summarize using summarizer agent
    summary_req = format_mcp("host", research_answer)
    summary_res = await send_mcp(SUMMARIZER_URL, summary_req)
    summary = summary_res.get("content", "")

    return {"responses": [research_answer, gemini_answer, summary]}
