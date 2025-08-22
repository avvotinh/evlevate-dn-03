"""
Generation Tool for E-commerce AI Product Advisor
Generates natural language responses using retrieved context from vector search.
"""

import json
from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from src.services.llm_service import llm_service
from src.prompts.prompt_manager import prompt_manager
from src.utils.logger import get_logger

logger = get_logger("generation_tool")


class GenerationInput(BaseModel):
    """Simplified input schema for GenerationTool"""
    user_query: str = Field(
        description="Original user query in Vietnamese"
    )
    context: Optional[str] = Field(
        default="",
        description="Retrieved context from search results (products, reviews, etc.)"
    )
    conversation_history: Optional[str] = Field(
        default="",
        description="Previous conversation context"
    )
    intent: str = Field(
        description="User intent: 'search', 'compare', 'recommend', 'greeting', 'direct'"
    )
    tools_used: Optional[List[str]] = Field(
        default_factory=list,
        description="List of tools used before RAG generation"
    )
    search_results: Optional[str] = Field(
        default="",
        description="Raw search results from search tool"
    )
    comparison_results: Optional[str] = Field(
        default="",
        description="Raw comparison results from compare tool"
    )
    recommendation_results: Optional[str] = Field(
        default="",
        description="Raw recommendation results from recommend tool"
    )
    review_results: Optional[str] = Field(
        default="",
        description="Raw review results from review tool"
    )


class GenerationTool(BaseTool):
    """Simplified tool for generating natural language responses using retrieved context"""
    
    name: str = "answer_with_context"
    description: str = """Tạo câu trả lời tự nhiên dựa trên user intent và context đã thu thập.

    🎯 **Thiết kế đơn giản và hiệu quả:**
    - Intent-driven: Sử dụng intent làm driver chính
    - Natural response: Tự động điều chỉnh tone phù hợp với context
    - Multi-source context: Xử lý context từ nhiều tools
    - Smart suggestions: Gợi ý next steps hữu ích
    
    📝 **Required parameters:**
    - user_query: Câu hỏi của người dùng
    - intent: Ý định chính ('search', 'compare', 'recommend', 'greeting', 'direct')
    
    📊 **Context sources:**
    - search_results: Raw output từ search tool
    - comparison_results: Raw output từ compare tool  
    - recommendation_results: Raw output từ recommend tool
    - review_results: Raw output từ review tool
    - tools_used: Danh sách tools đã execute
    
    ✨ **Smart features:**
    - Auto response type mapping từ intent
    - Context-aware natural language generation
    - Workflow summary cho multi-tool queries
    - Next-step suggestions
    - Direct intent: Trả lời câu hỏi tổng quát về công nghệ, thuật ngữ, khái niệm"""
    
    args_schema: Type[BaseModel] = GenerationInput
    return_direct: bool = False
    
    def _run(
        self,
        user_query: str,
        intent: str,
        context: Optional[str] = "",
        conversation_history: Optional[str] = "",
        tools_used: Optional[List[str]] = None,
        search_results: Optional[str] = "",
        comparison_results: Optional[str] = "",
        recommendation_results: Optional[str] = "",
        review_results: Optional[str] = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the simplified RAG generation tool"""
        try:
            logger.info(f"🤖 Generating response for query: '{user_query[:50]}...'")
            logger.info(f"🎯 Intent: {intent}")
            logger.info(f"🔧 Tools used: {tools_used or []}")
            
            # Validate inputs
            if not user_query or not user_query.strip():
                logger.warning("Empty user query provided")
                return json.dumps({
                    "success": False,
                    "error": "User query không được để trống",
                    "response": ""
                })
            
            if not intent:
                return json.dumps({
                    "success": False,
                    "error": "Intent is required",
                    "response": ""
                })
            
            # Initialize tools_used if None
            if tools_used is None:
                tools_used = []
            
            # Special handling for direct intent without tools
            if intent == "direct" and not tools_used and not context:
                logger.info("🎯 Processing direct intent without context - general knowledge mode")
            
            # Enhanced context processing based on tools used and intent
            context = self._build_context(
                context, search_results, comparison_results, 
                recommendation_results, review_results, tools_used, intent
            )
            
            # Build consolidated prompt using prompt manager
            final_prompt = prompt_manager.build_generation_prompt(
                user_query=user_query,
                intent=intent,
                context=context,
                conversation_history=conversation_history,
                tools_used=tools_used
            )
            
            # Generate response using LLM
            llm = llm_service.get_llm()
            response = llm.invoke(final_prompt)
            
            # Extract content if response is AIMessage
            if hasattr(response, 'content'):
                generated_response = response.content
            else:
                generated_response = str(response)
            
            result = {
                "success": True,
                "response": generated_response.strip(),
                "intent": intent,
                "context_used": len(context) > 0,
                "tools_used": tools_used,
                "query": user_query
            }
            
            logger.info("✅ Natural RAG response generated successfully")
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ RAG generation error: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi tạo câu trả lời: {str(e)}",
                "response": "Xin lỗi, tôi gặp vấn đề khi tạo câu trả lời. Vui lòng thử lại."
            })
    
    
    def _build_context(
        self, 
        context: str,
        search_results: str,
        comparison_results: str,
        recommendation_results: str,
        review_results: str,
        tools_used: List[str],
        intent: str
    ) -> str:
        """Build enhanced context from multiple sources - DATA ONLY, no instructions"""
        try:
            context_parts = []
            
            # Add original context if provided
            if context and context.strip():
                context_parts.append(f"=== CONTEXT ===\n{context}")
            
            # Process search results
            if search_results and "search_products" in tools_used:
                parsed_search = self._parse_tool_result(search_results)
                if parsed_search:
                    context_parts.append(f"=== SEARCH RESULTS ===\n{parsed_search}")
            
            # Process comparison results - RAW DATA ONLY
            if comparison_results and "compare_products" in tools_used:
                parsed_compare = self._parse_tool_result(comparison_results)
                if parsed_compare:
                    context_parts.append(f"=== COMPARISON RESULTS ===\n{parsed_compare}")
            
            # Process recommendation results - RAW DATA ONLY
            if recommendation_results and "recommend_products" in tools_used:
                parsed_recommend = self._parse_tool_result(recommendation_results)
                if parsed_recommend:
                    context_parts.append(f"=== RECOMMENDATION RESULTS ===\n{parsed_recommend}")
            
            # Process review results - RAW DATA ONLY
            if review_results and "get_product_reviews" in tools_used:
                parsed_reviews = self._parse_tool_result(review_results)
                if parsed_reviews:
                    context_parts.append(f"=== PRODUCT REVIEWS ===\n{parsed_reviews}")
            
            # For direct intent, add general knowledge context if no specific product data
            if intent == "direct" and not context_parts and not tools_used:
                context_parts.append("=== GENERAL ASSISTANT MODE ===\nTrả lời câu hỏi tổng quát, cung cấp thông tin hữu ích và đề xuất các câu hỏi tiếp theo phù hợp.")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"⚠️ Error building enhanced context: {e}")
            return context or ""
    
    def _parse_tool_result(self, tool_result: str) -> str:
        """Parse and clean tool result for better context"""
        try:
            # Validate input
            if not tool_result or not isinstance(tool_result, str):
                return ""
            
            tool_result = tool_result.strip()
            if not tool_result:
                return ""
            
            # Try to parse as JSON first - more robust check
            if tool_result.startswith(('{', '[')):
                try:
                    result_data = json.loads(tool_result)
                except json.JSONDecodeError:
                    # If JSON parsing fails, return cleaned string
                    return tool_result[:2000]  # Limit length to prevent token overflow
                
                # Extract meaningful data based on structure
                if isinstance(result_data, dict):
                    # Priority order for data extraction
                    for key in ["data", "products", "comparison", "recommendations", "results"]:
                        if result_data.get("success") and result_data.get(key):
                            return json.dumps(result_data[key], ensure_ascii=False, indent=2)
                        elif result_data.get(key):
                            return json.dumps(result_data[key], ensure_ascii=False, indent=2)
                    
                    # If no specific key found, return the whole dict
                    return json.dumps(result_data, ensure_ascii=False, indent=2)
                
                elif isinstance(result_data, list):
                    return json.dumps(result_data, ensure_ascii=False, indent=2)
            
            # Return truncated string if not JSON or parsing fails
            return tool_result[:2000]  # Prevent token overflow
            
        except Exception as e:
            logger.warning(f"Error parsing tool result: {e}")
            return tool_result[:1000] if isinstance(tool_result, str) else ""

    async def _arun(
        self,
        user_query: str,
        intent: str,
        context: Optional[str] = "",
        conversation_history: Optional[str] = "",
        tools_used: Optional[List[str]] = None,
        search_results: Optional[str] = "",
        comparison_results: Optional[str] = "",
        recommendation_results: Optional[str] = "",
        review_results: Optional[str] = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of the simplified tool"""
        return self._run(
            user_query, intent, context, conversation_history, tools_used,
            search_results, comparison_results, recommendation_results,
            review_results, run_manager
        )


# Create tool instance
generation_tool = GenerationTool()
