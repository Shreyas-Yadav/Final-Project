import os
import sys
from dotenv import load_dotenv


class Config:
    """Handles configuration management for the application."""
    
    @staticmethod
    def get_github_token() -> str:
        """Get GitHub personal access token from environment variables."""
        github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        if not github_token:
            raise ValueError("GitHub personal access token not found in environment variables.")
        return github_token
    
    @staticmethod
    def get_openrouter_api_key() -> str:
        """Get OpenRouter API key from environment variables."""
        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise ValueError("OpenRouter API key not found in environment variables.")
        return openrouter_api_key
    
    @staticmethod
    def setup_environment() -> tuple:
        """Set up the environment and return required credentials."""
        try:
            load_dotenv()
            # Get GitHub token
            github_token = Config.get_github_token()
            
            # Get OpenRouter API key
            try:
                openrouter_api_key = Config.get_openrouter_api_key()
            except ValueError:
                print("Warning: OpenRouter API key not found in environment variables")
                print("Please set it with: export OPENROUTER_API_KEY=your_api_key")
                openrouter_api_key = input("Enter your OpenRouter API key: ")
                os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
            
            return github_token, openrouter_api_key
            
        except ValueError as e:
            print(f"Error: {e}")
            print("Please set GitHub token with: export GITHUB_PERSONAL_ACCESS_TOKEN=your_token")
            sys.exit(1)