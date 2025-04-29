"""
MCP Tools Agent
───────────────────────────
Interact with GitHub repositories using LlamaIndex ReAct agent with MCP tools.
──────────────────────────────────────────────────────────────────
Prereqs
-------
pip install llama-index-core llama-index-llms-openrouter requests pydantic
Environment variables
---------------------
GITHUB_PERSONAL_ACCESS_TOKEN  # your fine-grained or classic PAT
GITHUB_USERNAME              # your GitHub username
OPENROUTER_API_KEY           # for LLM access
"""
from __future__ import annotations

import os
import sys
from typing import List, Optional
from dotenv import load_dotenv

from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.openrouter import OpenRouter

# Import Repo tools
from mcp_tools.repos import (
    create_repository_tool,
    create_or_update_file_tool,
    create_branch_tool,
    fork_repository_tool,
    get_file_contents_tool,
    list_branches_tool,
    search_repositories_tool
)

from mcp_tools.issues import (
    close_issue,
    comment_issue,
    create_issue,
    get_issue,
    list_issues,
    search_issues
)

from mcp_tools.users import (
    get_authenticated_user,
    get_user,
    list_followers,
    list_following,
    list_user_repos
)

def load_environment_variables() -> tuple:
    """Load environment variables and prompt for missing ones."""
    load_dotenv()
    
    # Get GitHub token
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("GitHub token not found in environment variables.")
        github_token = input("Enter your GitHub Personal Access Token: ")
        os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"] = github_token
    
    # Get GitHub username
    github_username = os.getenv("GITHUB_USERNAME")
    if not github_username:
        print("GitHub username not found in environment variables.")
        github_username = input("Enter your GitHub username: ")
        os.environ["GITHUB_USERNAME"] = github_username
    
    # Get OpenRouter API key
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        print("OpenRouter API key not found in environment variables.")
        openrouter_key = input("Enter your OpenRouter API key: ")
        os.environ["OPENROUTER_API_KEY"] = openrouter_key
    
    return github_token, github_username, openrouter_key

def build_agent() -> Optional[ReActAgent]:
    """Build a ReAct agent with MCP tools."""
    try:
        # Load environment variables
        github_token, github_username, openrouter_key = load_environment_variables()
        
        print(f"\nUsing GitHub account: {github_username}")
        
        # Create LLM
        llm = OpenRouter(
            model="openai/gpt-4o-mini",  # You can change this to any model OpenRouter supports
            api_key=openrouter_key,
        )
        
        # Collect all MCP tools
        repo_tools = [
            create_repository_tool,
            create_or_update_file_tool,
            create_branch_tool,
            fork_repository_tool,
            get_file_contents_tool,
            list_branches_tool,
            search_repositories_tool,
        ]

        issue_tools = [
            close_issue.close_issue_tool,
            comment_issue.comment_issue_tool,
            create_issue.create_issue_tool, 
            get_issue.get_issue_tool,
            list_issues.list_issues_tool,
            search_issues.search_issues_tool,
        ]  # Add issue-related tools here if needed

        user_tools = [
            get_authenticated_user.get_authenticated_user_tool,
            get_user.get_user_tool,
            list_followers.list_followers_tool,
            list_following.list_following_tool,
            list_user_repos.list_user_repos_tool,
        ]
        

        tools = repo_tools + issue_tools + user_tools  # Combine all tools
        # Print available tools
        print("\nAvailable MCP tools:")
        print(f"All tools will only access repositories owned by: {github_username}")
        for i, tool in enumerate(tools):
            print(f"{i+1}. {tool.metadata.name}: {tool.metadata.description}")
        
        # Create ReAct agent
        agent = ReActAgent.from_tools(
            tools=tools,  # Combine repo and issue tools
            llm=llm,
            verbose=True,  # Show tool calls in the console
            max_iterations=10,
        )
        
        return agent
    
    except Exception as e:
        print(f"Error building agent: {e}")
        return None

def run_interactive_loop(agent: ReActAgent) -> None:
    """Run an interactive loop for communicating with the agent."""
    print("\n=== MCP Tools Agent ===")
    print("Type 'exit' to quit the program.")
    print("Type 'help' to see available commands.")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting program...")
                break
            
            # Check for help command
            if user_input.lower() == "help":
                print("\nAvailable commands:")
                print("  help - Show this help message")
                print("  exit/quit - Exit the program")
                print("  clear - Clear the screen")
                print("  Any other input will be sent to the agent")
                continue
            
            # Check for clear command
            if user_input.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Send input to agent
            print("\nAgent is thinking...")
            response = agent.chat(user_input)
            
            # Display agent response
            print(f"\nAgent: {response}")
            
        except KeyboardInterrupt:
            print("\nOperation interrupted by user. Type 'exit' to quit.")
        except Exception as e:
            print(f"\nError: {e}")

def main():
    """Main function."""
    try:
        # Build agent
        agent = build_agent()
        
        if not agent:
            print("Failed to build agent. Exiting...")
            sys.exit(1)
        
        # Run interactive loop
        run_interactive_loop(agent)
        
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Goodbye!")

if __name__ == "__main__":
    main()
