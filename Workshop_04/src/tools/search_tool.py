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
    query: str = Field(
        description="Natural language search query in Vietnamese (e.g., 'laptop cho lập trình', 'điện thoại gaming')"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="""Search filters and criteria. Can include:
        - category: 'laptop' or 'smartphone'  
        - subcategory: 'gaming', 'business', 'ultrabook', 'budget', 'flagship', 'mid-range'
        - brand: 'apple', 'samsung', 'dell', 'hp', 'asus', 'lenovo', 'acer', 'msi', 'xiaomi', 'oppo', 'vivo'
        - price_min: minimum price in VND
        - price_max: maximum price in VND
        - max_results: number of results (1-10, default 3)
        - include_reviews: true/false (default false)
        - rating_min: minimum rating (1-5)
        - in_stock: true/false to filter available products
        - os: 'windows', 'macos', 'ubuntu', 'ios', 'android' for OS preference
        - features: list of required features from actual data
        - use_cases: filter by intended usage from actual data
        """
    )


class SearchTool(BaseTool):
    """Tool for searching products using natural language queries"""
    
    name: str = "search_products"
    description: str = """🔍 TÌM KIẾM sản phẩm theo tiêu chí cụ thể.
    
    MỤC ĐÍCH: Tìm sản phẩm dựa trên các bộ lọc và tiêu chí nhất định
    
    SỬ DỤNG KHI:
    - Khách hàng TÌM sản phẩm cụ thể: "tìm laptop Dell", "iPhone 15 Pro Max"
    - Lọc theo thương hiệu: "laptop HP", "smartphone Samsung"  
    - Lọc theo giá: "laptop dưới 25 triệu", "điện thoại từ 10-20 triệu"
    - Lọc theo tính năng: "laptop có SSD", "smartphone camera 48MP"
    - Tìm theo mục đích sử dụng: "laptop gaming", "smartphone chụp ảnh"
    
    KHÔNG dùng cho: Gợi ý hoặc tư vấn sản phẩm phù hợp
    
    OUTPUT: Danh sách sản phẩm khớp với filters, không có ranking"""
    
    args_schema: Type[BaseModel] = SearchInput
    return_direct: bool = False

    def run(self, tool_input: str, **kwargs) -> str:
        """Override run method to handle JSON string input properly"""
        try:
            # If input is a JSON string, parse it
            if isinstance(tool_input, str) and tool_input.strip().startswith('{'):
                try:
                    parsed_input = json.loads(tool_input)
                    logger.info(f"🔧 Parsed JSON tool input: {parsed_input}")
                    return self._run(**parsed_input, **kwargs)
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Failed to parse JSON input: {tool_input}")
                    # Fall back to treating as query
                    return self._run(query=tool_input, **kwargs)
            else:
                # Regular string input, treat as query
                return self._run(query=tool_input, **kwargs)
        except Exception as e:
            logger.error(f"❌ Error in search tool run: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi tìm kiếm: {str(e)}",
                "products": []
            }, ensure_ascii=False)
    
    args_schema: Type[BaseModel] = SearchInput
    return_direct: bool = False
    
    def _run(
        self,
        query: str,
        metadata: Optional[Dict[str, Any]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """Execute the search tool"""
        try:
            logger.info(f"🔍 Searching products with query: '{query}'")
            logger.info(f"🎯 Search metadata: {metadata}")
            
            # Validate inputs - if no query, provide helpful message
            if not query or not query.strip():
                return json.dumps({
                    "success": False,
                    "error": "Để tìm kiếm sản phẩm, bạn vui lòng cho tôi biết:\n- Bạn đang tìm loại sản phẩm gì?\n- Có yêu cầu gì đặc biệt không?",
                    "products": [],
                    "next_action": "Hãy hỏi khách hàng muốn tìm sản phẩm gì"
                }, ensure_ascii=False)
            
            # Extract metadata parameters
            if metadata is None:
                metadata = {}
            
            category = metadata.get("category")
            brand = metadata.get("brand")
            price_min = metadata.get("price_min")
            price_max = metadata.get("price_max")
            max_results = metadata.get("max_results", 3)
            include_reviews = metadata.get("include_reviews", False)
            rating_min = metadata.get("rating_min")
            features = metadata.get("features", [])
            
            # Limit max_results
            max_results = min(max_results or 3, 10)

            # Prepare filters
            filters = {}
            if category and category.lower() in ["laptop", "smartphone"]:
                filters["category"] = category.lower()
            
            if brand and brand.strip():
                filters["brand"] = brand.lower().strip()
            
            # Add price filters
            if price_min is not None or price_max is not None:
                price_filter = {}
                if price_min is not None:
                    price_filter["$gte"] = price_min
                if price_max is not None:
                    price_filter["$lte"] = price_max
                filters["price"] = price_filter
            
            # Add rating filter
            if rating_min is not None:
                filters["rating"] = {"$gte": rating_min}
            
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
                "brand": brand,
                "price_range": {
                    "min": price_min,
                    "max": price_max
                } if price_min is not None or price_max is not None else None,
                "products": processed_products,
                "total_found": len(processed_products),
                "filters_applied": filters
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
        query: str,
        metadata: Optional[Dict[str, Any]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of the tool"""
        return self._run(query, metadata, run_manager)


# Create tool instance
search_tool = SearchTool()
