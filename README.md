This project demonstrates a simple multi‑agent architecture using FastAPI and a
Next.js frontend.  Agents communicate via the Agent2Agent (A2A) protocol and use
Gemini (via Vertex AI) through a small stub.

## Architecture

- **Host Agent** – receives user queries, delegates work to remote agents and
  combines their results.
- **Researcher Agent** – researches a topic and returns key points.
- **Summarizer Agent** – summarizes text into a short paragraph.
- **A2A Utilities** – helper functions for formatting and sending MCP messages.

Each agent exposes an HTTP endpoint and communicates using minimal MCP JSON
messages.

## Backend Setup

Requirements:

- Python 3.10+

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the remote agents in separate terminals:

```bash
uvicorn codex.remote_agents.researcher.app:app --port 8001
uvicorn codex.remote_agents.summarizer.app:app --port 8002
```

Start the host agent (used by the frontend):

```bash
uvicorn codex.host_agent.app:app --port 8000
```

## Frontend Setup

Requirements:

- Node.js 18+

Install and run:

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:3000` and will send requests to the
host agent at `http://localhost:8000/query`.

## Example Response Format

The host agent returns JSON like:

```json
{
  "responses": ["research result", "gemini result", "summary"]
}
```

`ask_gemini` currently returns a stubbed response. Replace the implementation in
`src/codex/vertex.py` with a real Vertex AI client to use Gemini 1.5 Pro.
