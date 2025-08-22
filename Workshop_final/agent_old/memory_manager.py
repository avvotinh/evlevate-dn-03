"""
Memory management utilities for the LangGraph Agent
"""

import json
from typing import Dict, Any, List

from src.utils.logger import get_logger
from .constants import AgentConstants

logger = get_logger("memory_manager")


class MemoryManager:
    """Dedicated class for memory management operations"""
    
    @staticmethod
    def extract_product_names_from_results(state: Dict[str, Any]) -> List[str]:
        """Extract product names from various result types"""
        product_names = []
        
        try:
            # Extract from search results
            if search_results := state.get("search_results"):
                product_names.extend(MemoryManager._extract_from_search(search_results))
            
            # Extract from comparison results
            if comparison_results := state.get("comparison_results"):
                product_names.extend(MemoryManager._extract_from_comparison(comparison_results))
            
            # Extract from recommendation results
            if recommendation_results := state.get("recommendation_results"):
                product_names.extend(MemoryManager._extract_from_recommendation(recommendation_results))
            
            # Remove duplicates and limit
            unique_products = list(dict.fromkeys(product_names))  # Preserves order
            return unique_products[:AgentConstants.MAX_PRODUCTS_TO_EXTRACT]
            
        except Exception as e:
            logger.error(f"❌ Error extracting product names: {e}")
            return []
    
    @staticmethod
    def _extract_from_search(search_results: Any) -> List[str]:
        """Extract product names from search results"""
        try:
            if isinstance(search_results, str):
                data = json.loads(search_results)
            elif isinstance(search_results, dict):
                data = search_results
            else:
                return []
            
            if data.get("success") and "products" in data:
                return [product.get("name", "") for product in data["products"] if product.get("name")]
                
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        return []
    
    @staticmethod
    def _extract_from_comparison(comparison_results: Any) -> List[str]:
        """Extract product names from comparison results"""
        try:
            if isinstance(comparison_results, str):
                data = json.loads(comparison_results)
            elif isinstance(comparison_results, dict):
                data = comparison_results
            else:
                return []
            
            if "products" in data:
                return [product.get("name", "") for product in data["products"] if product.get("name")]
                
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        return []
    
    @staticmethod
    def _extract_from_recommendation(recommendation_results: Any) -> List[str]:
        """Extract product names from recommendation results"""
        try:
            if isinstance(recommendation_results, str):
                data = json.loads(recommendation_results)
            elif isinstance(recommendation_results, dict):
                data = recommendation_results
            else:
                return []
            
            # Check various possible keys
            for key in ["recommendations", "products", "suggested_products"]:
                if key in data and isinstance(data[key], list):
                    return [item.get("name", "") for item in data[key] if isinstance(item, dict) and item.get("name")]
                    
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        return []
