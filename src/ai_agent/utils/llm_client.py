import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, provider: Optional[str] = None):
        if not self._initialized:
            self.provider = provider or os.getenv("LLM_PROVIDER", "mock")
            self.openai_key = os.getenv("OPENAI_API_KEY")
            self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            self._openai_client = None
            self._anthropic_client = None
            self.__class__._initialized = True
    
    def generate_response(self, prompt: str) -> str:
        if self.provider == "openai" and self.openai_key:
            return self._openai_generate(prompt)
        elif self.provider == "anthropic" and self.anthropic_key:
            return self._anthropic_generate(prompt)
        else:
            return self._mock_generate(prompt)
    
    def _openai_generate(self, prompt: str) -> str:
        try:
            if self._openai_client is None:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.openai_key)
            
            response = self._openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._mock_generate(prompt)
    
    def _anthropic_generate(self, prompt: str) -> str:
        try:
            if self._anthropic_client is None:
                import anthropic
                self._anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            response = self._anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return self._mock_generate(prompt)
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _mock_generate(self, prompt: str) -> str:
        return """Dear John,

Thank you for reaching out regarding the system outage that occurred last Tuesday.
Best regards,
Technical Support Team"""