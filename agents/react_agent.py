from typing import List, Optional
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openrouter import OpenRouter
from llama_index.core.tools import ToolOutput 

from clients.mcp_client import DockerMCPClient
from services.llm_service import LLMService
from tools.tool_factory import ToolFactory

class ReactAgentBuilder:
    """Builder class for creating ReAct agents."""


    @staticmethod
    def _default_failure_handler(callback_manager, exc) -> ToolOutput:
        """
        Called when the agent hits the max-iteration limit or otherwise
        can’t follow the ReAct format.  Return either:
          • ToolOutput           → becomes the agent’s final answer
          • str                  → used as the Answer: text
          • raise exc            → re-throw to caller
        """
        print("Agent failed to reason correctly. Returning default failure message.")
        # return ToolOutput(content="I couldn’t solve this with the tools I have.")


    
    @staticmethod
    def create_agent(
        client: DockerMCPClient,
        llm: OpenRouter,
        verbose: bool = True
    ) -> Optional[ReActAgent]:
        """Create a ReAct agent with MCP tools.
        
        Args:
            client: MCP client instance
            llm: LLM instance
            verbose: Whether to enable verbose mode
            
        Returns:
            ReAct agent instance or None if creation fails
        """
        try:
            # Get tools from MCP client
            tools = ToolFactory.create_llama_tools(client)
            
            if not tools:
                print("No tools were found. Cannot create ReAct agent.")
                return None
            
            # Print available tools
            ToolFactory.print_tools(tools)
            
            # Create ReAct agent
            react_agent = ReActAgent.from_tools(
                tools=tools,
                llm=llm,
                verbose=verbose,
                max_iterations=5,
                handle_reasoning_failure_fn=ReactAgentBuilder._default_failure_handler,
                handle_tool_failure_fn=ReactAgentBuilder._default_failure_handler,
            )
            
            print("\nReAct agent created successfully with MCP tools")
            # Attach client to agent for cleanup later
            react_agent._mcp_client = client
            return react_agent
            
        except Exception as e:
            print(f"Error creating ReAct agent: {e}")
            client.stop_server()
            return None