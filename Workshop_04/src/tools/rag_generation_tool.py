"""
RAG Generation Tool for E-commerce AI Product Advisor
Generates natural language responses using retrieved context from vector search.
"""

import json
from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from src.services.llm_service import LLMService
from src.prompts.prompt_manager import prompt_manager, PromptType
from src.utils.logger import get_logger

logger = get_logger("rag_generation_tool")


class RAGGenerationInput(BaseModel):
    """Input schema for RAGGenerationTool"""
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
    response_type: Optional[str] = Field(
        default="general",
        description="Type of response: 'general', 'comparison', 'recommendation', 'explanation'"
    )


class RAGGenerationTool(BaseTool):
    """Tool for generating natural language responses using retrieved context"""
    
    name: str = "answer_with_context"
    description: str = """Tạo câu trả lời tự nhiên dựa trên thông tin sản phẩm đã tìm được.
    
    Sử dụng tool này khi:
    - Đã có thông tin sản phẩm từ search/filter tools
    - Cần tạo câu trả lời chi tiết và tự nhiên
    - Muốn giải thích hoặc tư vấn dựa trên context
    - Cần tổng hợp thông tin từ nhiều nguồn
    
    Tool sẽ tạo ra câu trả lời hoàn chỉnh, thân thiện và hữu ích."""
    
    args_schema: Type[BaseModel] = RAGGenerationInput
    return_direct: bool = False
    
    def _run(
        self,
        user_query: str,
        context: Optional[str] = "",
        conversation_history: Optional[str] = "",
        response_type: Optional[str] = "general",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the RAG generation tool"""
        try:
            logger.info(f"🤖 Generating response for query: '{user_query[:50]}...'")
            
            # Validate inputs
            if not user_query or not user_query.strip():
                return json.dumps({
                    "success": False,
                    "error": "User query không được để trống",
                    "response": ""
                })
            
            # Context is optional - if empty, treat as general knowledge query
            if not context:
                context = ""
            
            # Build prompt based on response type
            system_prompt = prompt_manager.build_rag_system_prompt(response_type)
            user_prompt = prompt_manager.build_rag_user_prompt(user_query, context, conversation_history)
            
            # Generate response using LLM
            llm_service = LLMService()
            llm = llm_service.get_llm()
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = llm.invoke(full_prompt)
            
            # Extract content if response is AIMessage
            if hasattr(response, 'content'):
                generated_response = response.content
            else:
                generated_response = str(response)
            
            result = {
                "success": True,
                "response": generated_response.strip(),
                "response_type": response_type,
                "context_used": len(context) > 0,
                "query": user_query
            }
            
            logger.info("✅ RAG response generated successfully")
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ RAG generation error: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi tạo câu trả lời: {str(e)}",
                "response": "Xin lỗi, tôi gặp vấn đề khi tạo câu trả lời. Vui lòng thử lại."
            })
    
    async def _arun(
        self,
        user_query: str,
        context: Optional[str] = "",
        conversation_history: Optional[str] = "",
        response_type: Optional[str] = "general",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of the tool"""
        return self._run(user_query, context, conversation_history, response_type, run_manager)


# Create tool instance
rag_generation_tool = RAGGenerationTool()
