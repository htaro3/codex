"""Remote agents exposing MCP endpoints."""

from .researcher import run as run_researcher
from .summarizer import run as run_summarizer

__all__ = ["run_researcher", "run_summarizer"]
