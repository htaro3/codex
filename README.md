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
=======
# Codex

This repository contains a minimal Next.js frontend for interacting with a multi-agent backend.

## Prerequisites

- Node.js 18+ with npm

## Running the Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`.

The frontend expects an agent backend URL specified via `NEXT_PUBLIC_BACKEND_URL`.
By default it uses `http://localhost:8000`. To change it:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000 npm run dev
```

The backend should expose a `POST /query` endpoint that returns JSON:

```json
{
  "responses": ["agent reply 1", "agent reply 2"]
}
```

The web page allows you to send queries and displays the responses.
