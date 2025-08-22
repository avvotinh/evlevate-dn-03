"""
LLM Service for E-commerce AI Product Advisor
Handles all LLM operations including text generation, intent classification, and response formatting.
Uses LangChain prompt templates for better prompt management.
"""

from enum import Enum
from openai import AzureOpenAI
from src.config.config import Config
from src.utils.logger import get_logger

logger = get_logger("llm_service")

class ResponseFormat(Enum):
    """Response format types"""
    CONVERSATIONAL = "conversational"
    STRUCTURED = "structured"
    COMPARISON = "comparison"
    RECOMMENDATION = "recommendation"


class LLMService:
    """Service for LLM operations using Azure OpenAI"""
    
    def __init__(self):
        """Initialize LLM service"""
        self.client = None
        self.model = Config.AZURE_OPENAI_LLM_MODEL
        self.temperature = Config.TEMPERATURE
        self.max_tokens = Config.MAX_TOKENS
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client (works with both Azure and custom endpoints)"""
        try:
            llm_config = Config.get_openai_config()

            # Check if using custom endpoint (not Azure)
            if "aiportalapi" in Config.AZURE_OPENAI_API_ENDPOINT:
                # Use regular OpenAI client for custom endpoint
                from openai import OpenAI
                self.client = OpenAI(
                    base_url=Config.AZURE_OPENAI_API_ENDPOINT,
                    api_key=Config.AZURE_OPENAI_LLM_API_KEY
                )
                logger.info("✅ Custom OpenAI LLM client initialized")
            else:
                # Use Azure OpenAI client
                self.client = AzureOpenAI(
                    api_key=llm_config["api_key"],
                    api_version=llm_config["api_version"],
                    azure_endpoint=llm_config["api_base"]
                )
                logger.info("✅ Azure OpenAI LLM client initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client: {e}")
            raise
    
    def get_llm(self):
        """Get LLM instance for LangChain integration"""
        try:
            llm_config = Config.get_openai_config()

            # Check if using custom endpoint (not Azure)
            if "aiportalapi" in Config.AZURE_OPENAI_API_ENDPOINT:
                # Use regular ChatOpenAI for custom endpoint
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    base_url=Config.AZURE_OPENAI_API_ENDPOINT,
                    api_key=Config.AZURE_OPENAI_LLM_API_KEY,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                logger.info("✅ Custom LangChain LLM instance created")
            else:
                # Use Azure ChatOpenAI
                from langchain_openai import AzureChatOpenAI
                llm = AzureChatOpenAI(
                    api_key=llm_config["api_key"],
                    api_version=llm_config["api_version"],
                    azure_endpoint=llm_config["api_base"],
                    deployment_name=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                logger.info("✅ Azure LangChain LLM instance created")

            return llm

        except Exception as e:
            logger.error(f"❌ Failed to create LangChain LLM: {e}")
            raise
    

# Singleton instance
llm_service = LLMService()
