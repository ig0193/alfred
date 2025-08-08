import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") 
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
    
    DEFAULT_TOOL = "gmail"
    
    
    CONTEXT_SIMILARITY_THRESHOLD = 0.3
    
    MAX_CONTEXT_ITEMS = 10
    
    DRAFT_MAX_LENGTH = 1000