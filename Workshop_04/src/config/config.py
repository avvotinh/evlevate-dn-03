"""
Simple configuration for E-commerce AI Product Advisor Chatbot
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Simple configuration class"""
    
    # API Keys from .env file
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "ecommerce-products")
    
    # Azure OpenAI
    AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")
    AZURE_OPENAI_EMBEDDING_API_KEY = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY", "")
    AZURE_OPENAI_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    AZURE_OPENAI_LLM_API_KEY = os.getenv("AZURE_OPENAI_LLM_API_KEY", "")
    AZURE_OPENAI_LLM_MODEL = os.getenv("AZURE_OPENAI_LLM_MODEL", "GPT-4o-mini")
    
    # Search Settings
    DEFAULT_TOP_K = 3
    MAX_TOP_K = 20
    SIMILARITY_THRESHOLD = 0.3  # Lowered from 0.5 to allow more relevant results
    
    # LLM Settings
    TEMPERATURE = 0.7
    MAX_TOKENS = 5000  # Increased for longer Final Answer responses
    DEFAULT_LANGUAGE = "vi"  # Vietnamese
    
    # UI Settings
    PAGE_TITLE = "AI Product Advisor"
    PAGE_ICON = "🛍️"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_fields = [
            cls.AZURE_OPENAI_API_ENDPOINT,
            cls.AZURE_OPENAI_EMBEDDING_API_KEY,
            cls.AZURE_OPENAI_LLM_API_KEY
        ]
        
        missing = [field for field in required_fields if not field]
        if missing:
            raise ValueError(f"Missing required environment variables in .env file")
        
        return True
    
    @classmethod
    def get_openai_config(cls):
        """Get OpenAI configuration"""
        return {
            "api_type": "azure",
            "api_base": cls.AZURE_OPENAI_API_ENDPOINT,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "api_key": cls.AZURE_OPENAI_LLM_API_KEY,
            "engine": cls.AZURE_OPENAI_LLM_MODEL,
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS
        }
    
    @classmethod
    def get_embedding_config(cls):
        """Get embedding configuration"""
        return {
            "api_type": "azure",
            "api_base": cls.AZURE_OPENAI_API_ENDPOINT,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "api_key": cls.AZURE_OPENAI_EMBEDDING_API_KEY,
            "engine": cls.AZURE_OPENAI_EMBEDDING_MODEL
        }


# Helper functions
def get_category_specs(category: str) -> list:
    """Get specs for a category"""
    return Config.CATEGORIES.get(category, {}).get("specs", [])


def get_price_ranges(category: str) -> list:
    """Get price ranges for a category"""
    return Config.CATEGORIES.get(category, {}).get("price_ranges", [])


def is_valid_category(category: str) -> bool:
    """Check if category is valid"""
    return category in Config.CATEGORIES


# Validate config on import
try:
    Config.validate()
    print("✅ Configuration loaded successfully")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("Please check your .env file")
