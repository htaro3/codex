# codex

This repository hosts example remote agents for communication via a simple
MCP (Message Communication Protocol) endpoint. Each agent runs an HTTP server
that accepts `POST /mcp` requests with JSON payloads.

## Remote Agents

### Researcher
Location: `src/remote_agents/researcher`

The Researcher agent answers factual questions and gathers information.
Start the server with:

```python
from remote_agents.researcher import run
run()
```

Example Gemini 1.5 Pro prompt:

```
You are the Researcher agent for an autonomous system. Answer each
question with concise, factual information and include sources when
possible.
```

### Summarizer
Location: `src/remote_agents/summarizer`

The Summarizer agent condenses text into short summaries.
Start the server with:

```python
from remote_agents.summarizer import run
run()
```

Example Gemini 1.5 Pro prompt:

```
You are the Summarizer agent. Summarize the provided text into clear,
concise bullet points suitable for an executive briefing.
```
