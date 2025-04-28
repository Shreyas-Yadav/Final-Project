import sys
from config import Config
from clients.mcp_client import DockerMCPClient
from services.llm_service import LLMService
from agents.react_agent import ReactAgentBuilder
from utils.error_handling import handle_keyboard_interrupt

@handle_keyboard_interrupt
def main():
    """Main function to run the application."""
    try:
        # Set up environment
        github_token, openrouter_api_key = Config.setup_environment()
        
        # Create MCP client
        client = DockerMCPClient(github_token)
        client.start_server()
        
        # Create LLM
        llm = LLMService.create_openrouter_llm(openrouter_api_key,model="openai/gpt-4o-mini")
        
        # Create ReAct agent
        agent = ReactAgentBuilder.create_agent(client, llm)
        
        if not agent:
            print("Failed to create agent.")
            client.stop_server()
            sys.exit(1)
        
        # Run interactive loop
        try:
            # Example query
            query = "tell me 'Wireframe-to-Code' repository exists in my GitHub ?"
            print(f"\nExecuting query: {query}")
            response = agent.query(query)
            print(f"\nAgent response: {response}")
            
            # Interactive loop
            print("\nAgent is ready for queries. Enter 'exit' to quit.")
            while True:
                user_query = input("\nEnter your query: ")
                if user_query.lower() == 'exit':
                    break
                    
                response = agent.query(user_query)
                print(f"\nAgent response: {response}")
                
        finally:
            # Clean up
            if hasattr(agent, '_mcp_client') and agent._mcp_client:
                agent._mcp_client.stop_server()
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()