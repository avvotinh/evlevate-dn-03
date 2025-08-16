"""
Services module for E-commerce AI Product Advisor
Contains external service integrations (Pinecone, OpenAI, LLM services)
"""

from .pinecone_service import PineconeService, pinecone_service
from .llm_service import LLMService, llm_service

__all__ = [
    "PineconeService",
    "pinecone_service", 
    "LLMService",
    "llm_service",
]
