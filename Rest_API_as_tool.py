"""
Multi-Agent MCP Tools System
───────────────────────────
A multi-agent system for interacting with GitHub repositories using specialized agents:
1. Repository Agent: Handles repository operations
2. Issue Agent: Handles issue operations
3. User Agent: Handles user operations
4. Master Agent: Orchestrates the specialized agents

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
import json
from typing import List, Optional, Dict, Any, Tuple
from dotenv import load_dotenv

from llama_index.core.tools import FunctionTool, ToolMetadata
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

# Define agent types
class AgentType:
    REPO = "repository"
    ISSUE = "issue"
    USER = "user"
    MASTER = "master"

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

def create_llm(openrouter_key: str) -> OpenRouter:
    """Create an OpenRouter LLM instance."""
    return OpenRouter(
        model="openai/gpt-4o-mini",  # You can change this to any model OpenRouter supports
        api_key=openrouter_key,
    )

def build_repo_agent(llm: OpenRouter) -> Optional[ReActAgent]:
    """Build a specialized agent for repository operations."""
    try:
        # Collect repository tools
        repo_tools = [
            create_repository_tool,
            create_or_update_file_tool,
            create_branch_tool,
            fork_repository_tool,
            get_file_contents_tool,
            list_branches_tool,
            search_repositories_tool,
        ]
        
        # Create ReAct agent
        agent = ReActAgent.from_tools(
            tools=repo_tools,
            llm=llm,
            verbose=True,
            max_iterations=5,
            system_prompt=(
                "You are a specialized GitHub Repository Agent. "
                "You handle repository-related operations like creating repositories, "
                "managing files, creating branches, and forking repositories. "
                "Focus only on repository operations and provide detailed responses."
            )
        )
        
        return agent
    
    except Exception as e:
        print(f"Error building repository agent: {e}")
        return None

def build_issue_agent(llm: OpenRouter) -> Optional[ReActAgent]:
    """Build a specialized agent for issue operations."""
    try:
        # Collect issue tools
        issue_tools = [
            close_issue.close_issue_tool,
            comment_issue.comment_issue_tool,
            create_issue.create_issue_tool,
            get_issue.get_issue_tool,
            list_issues.list_issues_tool,
            search_issues.search_issues_tool,
        ]
        
        # Create ReAct agent
        agent = ReActAgent.from_tools(
            tools=issue_tools,
            llm=llm,
            verbose=True,
            max_iterations=5,
            system_prompt=(
                "You are a specialized GitHub Issue Agent. "
                "You handle issue-related operations like creating issues, "
                "commenting on issues, closing issues, and searching for issues. "
                "Focus only on issue operations and provide detailed responses."
            )
        )
        
        return agent
    
    except Exception as e:
        print(f"Error building issue agent: {e}")
        return None

def build_user_agent(llm: OpenRouter) -> Optional[ReActAgent]:
    """Build a specialized agent for user operations."""
    try:
        # Collect user tools
        user_tools = [
            get_authenticated_user.get_authenticated_user_tool,
            get_user.get_user_tool,
            list_followers.list_followers_tool,
            list_following.list_following_tool,
            list_user_repos.list_user_repos_tool,
        ]
        
        # Create ReAct agent
        agent = ReActAgent.from_tools(
            tools=user_tools,
            llm=llm,
            verbose=True,
            max_iterations=5,
            system_prompt=(
                "You are a specialized GitHub User Agent. "
                "You handle user-related operations like getting user information, "
                "listing followers, listing following, and listing user repositories. "
                "Focus only on user operations and provide detailed responses."
            )
        )
        
        return agent
    
    except Exception as e:
        print(f"Error building user agent: {e}")
        return None

def create_agent_tool(agent: ReActAgent, agent_type: str) -> FunctionTool:
    """Create a tool that represents a specialized agent."""
    
    # Use a lambda function to directly handle the input parameter
    return FunctionTool(
        fn=lambda **kwargs: str(agent.chat(kwargs.get('input', ''))),
        metadata=ToolMetadata(
            name=f"{agent_type}_agent",
            description=f"Use the {agent_type} agent to handle {agent_type}-related operations."
        )
    )

def build_master_agent(
    repo_agent: ReActAgent,
    issue_agent: ReActAgent,
    user_agent: ReActAgent,
    llm: OpenRouter,
    github_username: str
) -> Optional[ReActAgent]:
    """Build a master agent that orchestrates the specialized agents."""
    try:
        # Create tools for each specialized agent
        repo_agent_tool = create_agent_tool(repo_agent, AgentType.REPO)
        issue_agent_tool = create_agent_tool(issue_agent, AgentType.ISSUE)
        user_agent_tool = create_agent_tool(user_agent, AgentType.USER)
        
        # Collect all agent tools
        agent_tools = [
            repo_agent_tool,
            issue_agent_tool,
            user_agent_tool,
        ]
        
        # Create ReAct agent
        agent = ReActAgent.from_tools(
            tools=agent_tools,
            llm=llm,
            verbose=True,
            max_iterations=10,
            system_prompt=(
                f"You are a Master GitHub Agent that orchestrates specialized agents. "
                f"You have access to the following specialized agents:\n"
                f"1. Repository Agent: Handles repository operations\n"
                f"2. Issue Agent: Handles issue operations\n"
                f"3. User Agent: Handles user operations\n\n"
                f"All operations will only access repositories owned by: {github_username}\n\n"
                f"When given a task, analyze it and delegate to the appropriate specialized agent. "
                f"For complex tasks that require multiple agents, break down the task and delegate each part. "
                f"Ensure that you handle dependencies between tasks correctly."
            )
        )
        
        return agent
    
    except Exception as e:
        print(f"Error building master agent: {e}")
        return None

def build_multi_agent_system() -> Optional[Tuple[ReActAgent, Dict[str, ReActAgent]]]:
    """Build a multi-agent system with specialized agents and a master agent."""
    try:
        # Load environment variables
        github_token, github_username, openrouter_key = load_environment_variables()
        
        print(f"\nUsing GitHub account: {github_username}")
        
        # Create LLM
        llm = create_llm(openrouter_key)
        
        # Build specialized agents
        print("\nBuilding specialized agents...")
        repo_agent = build_repo_agent(llm)
        issue_agent = build_issue_agent(llm)
        user_agent = build_user_agent(llm)
        
        if not repo_agent or not issue_agent or not user_agent:
            print("Failed to build one or more specialized agents.")
            return None
        
        # Build master agent
        print("\nBuilding master agent...")
        master_agent = build_master_agent(repo_agent, issue_agent, user_agent, llm, github_username)
        
        if not master_agent:
            print("Failed to build master agent.")
            return None
        
        # Create a dictionary of all agents
        agents = {
            AgentType.REPO: repo_agent,
            AgentType.ISSUE: issue_agent,
            AgentType.USER: user_agent,
            AgentType.MASTER: master_agent
        }
        
        # Print available agents
        print("\nAvailable specialized agents:")
        print(f"All agents will only access repositories owned by: {github_username}")
        
        for agent_type in agents:
            if agent_type != AgentType.MASTER:
                print(f"- {agent_type.capitalize()} Agent")
        
        return master_agent, agents
    
    except Exception as e:
        print(f"Error building multi-agent system: {e}")
        return None

def run_interactive_loop(master_agent: ReActAgent, agents: Dict[str, ReActAgent]) -> None:
    """Run an interactive loop for communicating with the multi-agent system."""
    print("\n=== Multi-Agent MCP Tools System ===")
    print("Type 'exit' to quit the program.")
    print("Type 'help' to see available commands.")
    print("Type 'agents' to see available agents.")
    
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
                print("  agents - Show available agents")
                print("  Any other input will be sent to the master agent")
                continue
            
            # Check for agents command
            if user_input.lower() == "agents":
                print("\nAvailable agents:")
                print("  1. Master Agent - Orchestrates the specialized agents")
                print("  2. Repository Agent - Handles repository operations")
                print("  3. Issue Agent - Handles issue operations")
                print("  4. User Agent - Handles user operations")
                continue
            
            # Check for clear command
            if user_input.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Check if user wants to use a specific agent
            if user_input.lower().startswith("use "):
                parts = user_input.split(" ", 2)
                if len(parts) < 3:
                    print("Invalid command. Format: use <agent_type> <query>")
                    continue
                
                agent_type = parts[1].lower()
                query = parts[2]
                
                if agent_type == "repo" or agent_type == "repository":
                    agent = agents[AgentType.REPO]
                elif agent_type == "issue":
                    agent = agents[AgentType.ISSUE]
                elif agent_type == "user":
                    agent = agents[AgentType.USER]
                elif agent_type == "master":
                    agent = agents[AgentType.MASTER]
                else:
                    print(f"Unknown agent type: {agent_type}")
                    continue
                
                print(f"\n{agent_type.capitalize()} Agent is thinking...")
                response = agent.chat(query)
                print(f"\n{agent_type.capitalize()} Agent: {response}")
            else:
                # Send input to master agent
                print("\nMaster Agent is thinking...")
                response = master_agent.chat(user_input)
                
                # Display agent response
                print(f"\nMaster Agent: {response}")
            
        except KeyboardInterrupt:
            print("\nOperation interrupted by user. Type 'exit' to quit.")
        except Exception as e:
            print(f"\nError: {e}")

def main():
    """Main function."""
    try:
        # Build multi-agent system
        result = build_multi_agent_system()
        
        if not result:
            print("Failed to build multi-agent system. Exiting...")
            sys.exit(1)
        
        master_agent, agents = result
        
        # Run interactive loop
        run_interactive_loop(master_agent, agents)
        
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Goodbye!")

if __name__ == "__main__":
    main()
