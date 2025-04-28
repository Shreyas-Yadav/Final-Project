from llama_index.llms.openrouter import OpenRouter

class LLMService:
    """Service for creating and managing LLM instances."""
    
    @staticmethod
    def create_openrouter_llm(api_key: str, model: str = "mistralai/mistral-7b-instruct") -> OpenRouter:
        """Create an OpenRouter LLM instance.
        
        Args:
            api_key: OpenRouter API key
            model: Model name to use
            
        Returns:
            OpenRouter LLM instance
        """
        if not api_key:
            raise ValueError("OpenRouter API key is required")
        
        return OpenRouter(
            api_key=api_key,
            model=model
        )