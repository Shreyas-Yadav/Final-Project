import json
import subprocess
from typing import List, Dict, Any, Optional

class DockerMCPClient:
    """Client for interacting with the GitHub MCP server running in a Docker container."""
    
    def __init__(self, github_token: str):
        """Initialize the MCP client with a GitHub token.
        
        Args:
            github_token: GitHub personal access token
        """
        self.github_token = github_token
        if not self.github_token:
            raise ValueError("GitHub personal access token is required")
        
        self.process = None
        self.tools_cache = None
    
    def start_server(self) -> None:
        """Start the Docker container for the MCP server."""
        if self.process:
            print("Server is already running")
            return
        
        print("Starting GitHub MCP server Docker container...")
        cmd = [
            "docker", "run", "-i", "--rm", "-p", "3000:3000",
            "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={self.github_token}",
            "ghcr.io/github/github-mcp-server"
        ]
        
        # Start the container with pipes for stdin/stdout
        self.process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )
        
        # Initialize the server
        self.rpc("initialize", {"clientInfo": {"name": "mcp-react-agent", "version": "0.1"}}, id_=0)
        print("MCP server initialized successfully")
    
    def stop_server(self) -> None:
        """Stop the Docker container."""
        if self.process:
            print("Stopping MCP server...")
            self.process.terminate()
            self.process = None
    
    def rpc(self, method: str, params: Dict = None, id_: int = 1) -> Dict:
        """Send a JSON-RPC message to the server and get the response."""
        if not self.process:
            self.start_server()
            
        msg = {"jsonrpc": "2.0", "id": id_, "method": method, "params": params or {}}
        try:
            self.process.stdin.write(json.dumps(msg) + "\n")
            self.process.stdin.flush()
            response = json.loads(self.process.stdout.readline())
            return response
        except Exception as e:
            print(f"RPC error: {e}")
            return {"error": str(e)}
    
    def list_tools(self) -> List[Dict]:
        """List all available tools from the MCP server."""
        if self.tools_cache:
            return self.tools_cache
            
        response = self.rpc("tools/list")
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"Found {len(tools)} tools")
            self.tools_cache = tools
            return tools
        else:
            print(f"Error getting tools: {response.get('error', 'Unknown error')}")
            return []
    
    def execute_tool(self, tool_id: str, params: Dict = None) -> Dict:
        """Execute a specific tool."""
        response = self.rpc("tools/invoke", {"toolId": tool_id, "params": params or {}})
        return response.get("result", {"error": response.get("error", "Unknown error")})