"""
LLM Service for E-commerce AI Product Advisor
Handles all LLM operations including text generation, intent classification, and response formatting.
Uses LangChain prompt templates for better prompt management.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from enum import Enum

from openai import AzureOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.config.config import Config
from src.prompts.prompt_manager import prompt_manager, PromptType
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
        """Initialize Azure OpenAI client"""
        try:
            llm_config = Config.get_openai_config()
            self.client = AzureOpenAI(
                api_key=llm_config["api_key"],
                api_version=llm_config["api_version"],
                azure_endpoint=llm_config["api_base"]
            )
            logger.info("✅ Azure OpenAI LLM client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client: {e}")
            raise
    
    def _create_system_prompt(self, context: str = "general") -> str:
        """Create system prompt using prompt templates"""
        try:
            # Map context to special instructions
            special_instructions_map = {
                "search": "Tập trung vào việc giới thiệu kết quả tìm kiếm và hướng dẫn thu hẹp lựa chọn.",
                "comparison": "Tập trung vào việc so sánh chi tiết và đưa ra kết luận rõ ràng.",
                "recommendation": "Tập trung vào việc phân tích nhu cầu và đưa ra gợi ý phù hợp.",
                "filter": "Tập trung vào việc giải thích kết quả lọc và đề xuất tiêu chí bổ sung.",
                "general": "Hỗ trợ khách hàng một cách toàn diện về sản phẩm điện tử."
            }
            
            special_instructions = special_instructions_map.get(context, special_instructions_map["general"])
            
            # Get system prompt from prompt manager
            messages = prompt_manager.get_chat_messages(
                PromptType.SYSTEM_BASE,
                context=context,
                special_instructions=special_instructions
            )
            
            if messages:
                return messages[0]["content"]
            else:
                # Fallback to original system prompt
                return self._get_fallback_system_prompt(context)
                
        except Exception as e:
            logger.error(f"❌ Error creating system prompt: {e}")
            return self._get_fallback_system_prompt(context)
    
    def _get_fallback_system_prompt(self, context: str) -> str:
        """Fallback system prompt if template fails"""
        try:
            template = prompt_manager.get_prompt(PromptType.FALLBACK_SYSTEM)
            if template:
                return template.format(context=context)
        except Exception as e:
            logger.error(f"❌ Error getting fallback prompt: {e}")
        
        # Ultimate fallback
        return f"""Bạn là AI Product Advisor - trợ lý AI chuyên tư vấn sản phẩm điện tử.
        
Nhiệm vụ: Tư vấn laptop và smartphone bằng tiếng Việt thân thiện và chuyên nghiệp.
Ngữ cảnh: {context}

Quy tắc:
- Luôn trả lời bằng tiếng Việt
- Đưa ra thông tin chính xác và hữu ích  
- Hỏi thêm khi cần làm rõ nhu cầu
- Tập trung vào lợi ích khách hàng"""
    
    def get_llm(self):
        """Get LLM instance for LangChain integration"""
        try:
            from langchain_openai import AzureChatOpenAI
            
            llm_config = Config.get_openai_config()
            
            llm = AzureChatOpenAI(
                api_key=llm_config["api_key"],
                api_version=llm_config["api_version"],
                azure_endpoint=llm_config["api_base"],
                deployment_name=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            logger.info("✅ LangChain LLM instance created")
            return llm
            
        except Exception as e:
            logger.error(f"❌ Failed to create LangChain LLM: {e}")
            raise
    
    def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """General text generation method for tools"""
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({"role": "system", "content": self._create_system_prompt()})
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            
            generated_text = response.choices[0].message.content.strip()
            logger.info(f"✅ Generated text response (length: {len(generated_text)})")
            return generated_text
            
        except Exception as e:
            logger.error(f"❌ Text generation failed: {e}")
            return "Xin lỗi, có lỗi xảy ra khi tạo phản hồi. Vui lòng thử lại."


# Singleton instance
llm_service = LLMService()
