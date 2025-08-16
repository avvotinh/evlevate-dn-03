"""
Search Tool for E-commerce AI Product Advisor
Implements semantic product search using Pinecone vector database.
"""

import json
from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from src.services.pinecone_service import pinecone_service
from src.utils.logger import get_logger

logger = get_logger("search_tool")


class SearchInput(BaseModel):
    """Input schema for SearchTool"""
    query: Optional[str] = Field(
        default="",
        description="Natural language search query in Vietnamese (e.g., 'laptop cho lập trình', 'điện thoại gaming')"
    )
    category: Optional[str] = Field(
        default=None,
        description="Product category to search in: 'laptop' or 'smartphone'"
    )
    max_results: Optional[int] = Field(
        default=3,
        description="Maximum number of results to return (1-10)"
    )
    include_reviews: Optional[bool] = Field(
        default=False,
        description="Whether to include product reviews in results"
    )


class SearchTool(BaseTool):
    """Tool for searching products using natural language queries"""
    
    name: str = "search_products"
    description: str = """Tìm kiếm sản phẩm bằng ngôn ngữ tự nhiên.
    
    Sử dụng tool này khi:
    - Khách hàng hỏi về sản phẩm cụ thể (vd: "tìm laptop gaming")
    - Cần tìm sản phẩm theo mô tả (vd: "laptop cho lập trình")
    - Tìm sản phẩm theo tính năng (vd: "điện thoại camera tốt")
    
    Tool sẽ trả về danh sách sản phẩm phù hợp nhất với độ tương đồng cao."""
    
    args_schema: Type[BaseModel] = SearchInput
    return_direct: bool = False
    
    def _run(
        self,
        query: Optional[str] = "",
        category: Optional[str] = None,
        max_results: Optional[int] = 5,
        include_reviews: Optional[bool] = False,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the search tool"""
        try:
            logger.info(f"🔍 Searching products with query: '{query}'")
            
            # Validate inputs - if no query, provide helpful message
            if not query or not query.strip():
                return json.dumps({
                    "success": False,
                    "error": "Để tìm kiếm sản phẩm, bạn vui lòng cho tôi biết:\n- Bạn đang tìm loại sản phẩm gì?\n- Có yêu cầu gì đặc biệt không?",
                    "products": [],
                    "next_action": "Hãy hỏi khách hàng muốn tìm sản phẩm gì"
                }, ensure_ascii=False)
            
            # Limit max_results
            max_results = min(max_results or 3, 10)

            # Prepare filters
            filters = {}
            if category and category.lower() in ["laptop", "smartphone"]:
                filters["category"] = category.lower()
            
            # Search products
            try:
                products = pinecone_service.search_products(
                    query=query.strip(),
                    filters=filters,
                    top_k=max_results,
                    include_reviews=include_reviews
                )
            except Exception as e:
                # Handle Pinecone connection errors
                error_msg = str(e).lower()
                if "not found" in error_msg or "404" in error_msg:
                    return json.dumps({
                        "success": False,
                        "error": "Cơ sở dữ liệu sản phẩm chưa được thiết lập. Vui lòng liên hệ quản trị viên để khởi tạo dữ liệu.",
                        "products": [],
                        "setup_required": True
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Lỗi kết nối cơ sở dữ liệu: {str(e)}",
                        "products": []
                    })
            
            # Format results
            if not products:
                return json.dumps({
                    "success": True,
                    "message": "Không tìm thấy sản phẩm phù hợp",
                    "products": [],
                    "suggestions": [
                        "Thử tìm kiếm với từ khóa khác",
                        "Mở rộng phạm vi giá",
                        "Thử danh mục sản phẩm khác"
                    ]
                })
            
            # Process products for better display
            processed_products = []
            for product in products:
                processed_product = {
                    "id": product.get("id"),
                    "name": product.get("name"),
                    "brand": product.get("brand"),
                    "category": product.get("category"),
                    "price": product.get("price"),
                    "currency": product.get("currency", "VND"),
                    "rating": product.get("rating", 0),
                    "description": product.get("description", ""),
                    "features": product.get("features", []),
                    "specs": product.get("specs", {}),
                    "similarity_score": round(product.get("similarity_score", 0), 3)
                }
                
                # Add reviews if requested
                if include_reviews and "reviews" in product:
                    processed_product["reviews"] = product["reviews"][:3]  # Limit to 3 reviews
                
                processed_products.append(processed_product)
            
            result = {
                "success": True,
                "message": f"Tìm thấy {len(processed_products)} sản phẩm phù hợp",
                "query": query,
                "category": category,
                "products": processed_products,
                "total_found": len(processed_products)
            }
            
            logger.info(f"✅ Search completed: {len(processed_products)} products found")
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Search tool error: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi tìm kiếm: {str(e)}",
                "products": []
            })
    
    async def _arun(
        self,
        query: Optional[str] = "",
        category: Optional[str] = None,
        max_results: Optional[int] = 5,
        include_reviews: Optional[bool] = False,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of the tool"""
        return self._run(query, category, max_results, include_reviews, run_manager)


# Create tool instance
search_tool = SearchTool()
