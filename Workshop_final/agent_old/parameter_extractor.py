"""
Parameter extraction utilities for the LangGraph Agent
"""

import json
import re
from typing import Dict, Any

from langchain_core.messages import HumanMessage

from src.prompts.prompt_manager import prompt_manager, PromptType
from src.utils.logger import get_logger
from .constants import AgentConstants

logger = get_logger("parameter_extractor")


class ParameterExtractor:
    """Dedicated class for parameter extraction with fallback mechanisms"""
    
    @staticmethod
    def extract_search_params(user_input: str, llm) -> Dict[str, Any]:
        """Extract search parameters with LLM and fallback"""
        try:
            return ParameterExtractor._extract_with_llm(user_input, llm, PromptType.SEARCH_EXTRACTION)
        except Exception as e:
            logger.warning(f"⚠️ LLM extraction failed: {e}")
            return ParameterExtractor._fallback_search_params(user_input)
    
    @staticmethod
    def extract_compare_params(user_input: str, llm) -> Dict[str, Any]:
        """Extract comparison parameters with LLM and fallback"""
        try:
            return ParameterExtractor._extract_with_llm(user_input, llm, PromptType.COMPARE_EXTRACTION)
        except Exception as e:
            logger.warning(f"⚠️ LLM extraction failed: {e}")
            return ParameterExtractor._fallback_compare_params(user_input)
    
    @staticmethod
    def extract_recommend_params(user_input: str, llm) -> Dict[str, Any]:
        """Extract recommendation parameters with LLM and fallback"""
        try:
            return ParameterExtractor._extract_with_llm(user_input, llm, PromptType.RECOMMEND_EXTRACTION)
        except Exception as e:
            logger.warning(f"⚠️ LLM extraction failed: {e}")
            return ParameterExtractor._fallback_recommend_params(user_input)
    
    @staticmethod
    def _extract_with_llm(user_input: str, llm, prompt_type: PromptType) -> Dict[str, Any]:
        """Generic LLM-based parameter extraction"""
        prompt_template = prompt_manager.get_prompt(prompt_type)
        if not prompt_template:
            raise ValueError(f"Prompt template for {prompt_type} not found")
        
        extract_prompt = prompt_template.format(user_input=user_input)
        response = llm.invoke([HumanMessage(content=extract_prompt)])
        
        try:
            params = json.loads(response.content.strip())
            logger.info(f"🎯 LLM extracted params for {prompt_type}: {params}")
            return params
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from LLM: {e}")
    
    @staticmethod
    def _fallback_search_params(user_input: str) -> Dict[str, Any]:
        """Fallback search parameter extraction using regex"""
        fallback_metadata = {
            "category": None,
            "brand": None,
            "price_min": None,
            "price_max": None,
            "max_results": AgentConstants.DEFAULT_MAX_RESULTS,
            "include_reviews": False
        }
        
        # Category detection
        if any(word in user_input.lower() for word in ["laptop", "macbook"]):
            fallback_metadata["category"] = "laptop"
        elif any(word in user_input.lower() for word in ["điện thoại", "smartphone", "iphone"]):
            fallback_metadata["category"] = "smartphone"
        
        # Brand detection
        brands = ["apple", "samsung", "dell", "hp", "asus", "xiaomi", "oppo", "vivo", "lenovo", "acer"]
        for brand in brands:
            if brand in user_input.lower():
                fallback_metadata["brand"] = brand
                break
        
        return {
            "query": user_input,
            "metadata": fallback_metadata
        }
    
    @staticmethod
    def _fallback_compare_params(user_input: str) -> Dict[str, Any]:
        """Fallback comparison parameter extraction"""
        vs_patterns = [r'(.+?)\s+vs\s+(.+)', r'so sánh\s+(.+?)\s+và\s+(.+)', r'(.+?)\s+khác\s+gì\s+(.+)']
        product_names = []
        
        for pattern in vs_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                product_names = [match.group(1).strip(), match.group(2).strip()]
                break
        
        return {
            "product_names": product_names if len(product_names) >= 2 else [user_input],
            "comparison_aspects": ["giá", "hiệu năng", "thiết kế", "camera"],
            "include_reviews": True
        }
    
    @staticmethod
    def _fallback_recommend_params(user_input: str) -> Dict[str, Any]:
        """Fallback recommendation parameter extraction"""
        return {
            "user_needs": user_input,
            "metadata": {
                "category": None,
                "brand": None,
                "budget_min": None,
                "budget_max": None,
                "priority_features": [],
                "usage_purpose": None,
                "num_recommendations": AgentConstants.DEFAULT_MAX_RESULTS,
                "rating_min": None,
                "must_have_features": []
            }
        }
