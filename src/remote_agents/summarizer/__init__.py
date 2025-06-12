import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class MCPHandler(BaseHTTPRequestHandler):
    """Simple MCP endpoint for the Summarizer agent."""

    def do_POST(self):
        if self.path != "/mcp":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            message = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error": "invalid json"}')
            return
        response = {"role": "summarizer", "received": message}
        data = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run(host: str = "0.0.0.0", port: int = 8002) -> None:
    """Run the MCP server for the Summarizer agent."""
    server = HTTPServer((host, port), MCPHandler)
    print(f"Summarizer MCP server running on {host}:{port}")
    server.serve_forever()
