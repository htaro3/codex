"""Utilities for Agent2Agent MCP communication."""
from typing import Dict, Any
import httpx


def format_mcp(role: str, content: str) -> Dict[str, Any]:
    """Return a minimal MCP message."""
    return {"role": role, "content": content}


async def send_mcp(url: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Send an MCP message to a remote agent."""
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=message, timeout=10)
        res.raise_for_status()
        return res.json()
