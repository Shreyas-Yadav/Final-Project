from typing import List, Dict, Callable
from llama_index.core.tools import FunctionTool
from llama_index.core.tools.types import ToolMetadata

from clients.mcp_client import DockerMCPClient

class ToolFactory:
    """Factory class for creating LlamaIndex tools from MCP tools."""
    
    @staticmethod
    def create_tool_function(client: DockerMCPClient, tool_id: str) -> Callable:
        """Create a function that executes a specific MCP tool.
        
        Args:
            client: MCP client instance
            tool_id: ID of the MCP tool
            
        Returns:
            Function that executes the MCP tool
        """
        def execute_tool(**kwargs):
            return client.execute_tool(tool_id, kwargs)
        return execute_tool
    
    @staticmethod
    def create_llama_tools(client: DockerMCPClient) -> List[FunctionTool]:
        """Create LlamaIndex FunctionTools from MCP tools.
        
        Args:
            client: MCP client instance
            
        Returns:
            List of LlamaIndex FunctionTools
        """
        mcp_tools = client.list_tools()
        llama_tools = []
        
        for tool in mcp_tools:
            # Get tool details
            tool_id = tool.get("id")
            tool_name = tool.get("name", f"tool_{tool_id}")
            tool_description = tool.get("description", "No description provided")
            
            # Create tool function
            function = ToolFactory.create_tool_function(client, tool_id)
            
            # Create metadata
            metadata = ToolMetadata(
                name=tool_name,
                description=tool_description
            )
            
            # Create function tool
            llama_tool = FunctionTool(
                metadata=metadata,
                fn=function
            )
            
            llama_tools.append(llama_tool)
            print(f"Created tool: {tool_name}")
        
        return llama_tools
    
    @staticmethod
    def print_tools(tools: List[FunctionTool]) -> None:
        """Print available tools.
        
        Args:
            tools: List of LlamaIndex FunctionTools
        """
        print("\nAvailable MCP tools:")
        for i, tool in enumerate(tools):
            print(f"{i+1}. {tool.metadata.name}: {tool.metadata.description}")