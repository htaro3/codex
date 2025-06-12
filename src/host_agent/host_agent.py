import socket

import vertexai
from vertexai.preview.generative_models import GenerativeModel


class HostAgent:
    """Interact with Gemini via Vertex AI and remote agents via the MCP protocol."""

    def __init__(self, project: str, location: str, mcp_host: str, mcp_port: int) -> None:
        """Initialize the host agent.

        Parameters
        ----------
        project: str
            Google Cloud project ID used for Vertex AI.
        location: str
            Region of the Vertex AI instance.
        mcp_host: str
            Hostname of the remote agent MCP server.
        mcp_port: int
            Port of the remote agent MCP server.
        """
        vertexai.init(project=project, location=location)
        self.model = GenerativeModel("gemini-pro")
        self.mcp_host = mcp_host
        self.mcp_port = mcp_port

    def query_gemini(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the textual response."""
        response = self.model.generate_content(prompt)
        return response.text

    def send_to_remote_agent(self, message: str) -> str:
        """Send a message to a remote agent using the MCP protocol."""
        with socket.create_connection((self.mcp_host, self.mcp_port)) as sock:
            sock.sendall(message.encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)
            data = sock.recv(4096)
        return data.decode("utf-8")

    def handle_user_input(self, prompt: str) -> str:
        """Process user input by querying Gemini and forwarding the reply."""
        gemini_reply = self.query_gemini(prompt)
        remote_reply = self.send_to_remote_agent(gemini_reply)
        return remote_reply
