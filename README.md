# codex

This repository contains a collection of tools for agents.

## Host Agent

The `host_agent` package provides a class that connects to Vertex AI's Gemini model and communicates with remote agents using the MCP protocol.
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
