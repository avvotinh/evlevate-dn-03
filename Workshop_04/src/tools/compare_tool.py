"""
Compare Tool for E-commerce AI Product Advisor
Implements side-by-side product comparison functionality.
"""

import json
from typing import Dict, List, Optional, Any, Type, Union
from pydantic import BaseModel, Field, field_validator

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from src.services.pinecone_service import pinecone_service
from src.utils.logger import get_logger

logger = get_logger("compare_tool")


class CompareInput(BaseModel):
    """Input schema for CompareTool"""
    product_ids: Optional[Union[List[str], str]] = Field(
        default=[],
        description="List of product IDs to compare (2-3 products recommended). Can be a JSON string or list."
    )
    comparison_aspects: Optional[List[str]] = Field(
        default=None,
        description="Specific aspects to compare (e.g., ['performance', 'price', 'camera', 'battery'])"
    )
    include_reviews: Optional[bool] = Field(
        default=True,
        description="Whether to include review analysis in comparison"
    )
    
    @field_validator('product_ids')
    @classmethod
    def parse_product_ids(cls, v):
        """Parse product_ids from string or list"""
        if isinstance(v, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, str):
                    # Single product ID
                    return [parsed]
            except json.JSONDecodeError:
                # If not JSON, treat as comma-separated string
                if ',' in v:
                    return [item.strip() for item in v.split(',')]
                else:
                    return [v.strip()]
        elif isinstance(v, list):
            return v
        elif v is None:
            return []
        else:
            return [str(v)]


class CompareTool(BaseTool):
    """Tool for comparing multiple products side by side"""
    
    name: str = "compare_products"
    description: str = """So sánh chi tiết nhiều sản phẩm cạnh nhau.
    
    Sử dụng tool này khi:
    - Khách hàng muốn so sánh 2-3 sản phẩm cụ thể
    - Cần phân tích ưu nhược điểm từng sản phẩm
    - Muốn đưa ra kết luận về sản phẩm phù hợp nhất
    - So sánh theo khía cạnh cụ thể (giá, hiệu năng, camera, v.v.)
    
    INPUT FORMAT:
    {
        "product_ids": ["tên hoặc ID sản phẩm 1", "tên hoặc ID sản phẩm 2"],
        "comparison_aspects": ["khía cạnh 1", "khía cạnh 2"],
        "include_reviews": true/false
    }
    
    VÍ DỤ SỬ DỤNG:
    - {"product_ids": ["iPhone 15", "iPhone 15 Pro Max"], "comparison_aspects": ["giá", "camera", "hiệu năng"]}
    - {"product_ids": ["Dell XPS 15", "MacBook Air M2"], "comparison_aspects": ["hiệu năng", "giá", "pin"]}
    
    Tool sẽ tự động tìm sản phẩm theo tên và trả về bảng so sánh chi tiết."""
    
    args_schema: Type[BaseModel] = CompareInput
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
                    # Fall back to treating as product_ids
                    return self._run(product_ids=[tool_input], **kwargs)
            else:
                # Regular string input, treat as single product or comma-separated
                if ',' in tool_input:
                    product_ids = [p.strip() for p in tool_input.split(',')]
                else:
                    product_ids = [tool_input.strip()]
                return self._run(product_ids=product_ids, **kwargs)
        except Exception as e:
            logger.error(f"❌ Error in compare tool run: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi so sánh sản phẩm: {str(e)}",
                "comparison": {}
            }, ensure_ascii=False)
    
    def _get_product_by_id_or_name(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get product details by ID or name"""
        try:
            # First try to get by exact ID
            products = pinecone_service.search_products(
                query=identifier,
                filters={"id": identifier},
                top_k=1,
                include_reviews=True
            )
            if products:
                return products[0]
            
            # If not found by ID, try searching by name
            products = pinecone_service.search_products(
                query=identifier,
                top_k=5,  # Get multiple to find best match
                include_reviews=True
            )
            
            # Find the best match by name similarity
            for product in products:
                product_name = product.get('name', '').lower()
                identifier_lower = identifier.lower()
                
                # Check for exact name match or close match
                if identifier_lower in product_name or product_name in identifier_lower:
                    return product
                    
                # Check for partial matches with high similarity
                words_in_identifier = set(identifier_lower.split())
                words_in_name = set(product_name.split())
                
                # If at least 2 words match, consider it a good match
                common_words = words_in_identifier.intersection(words_in_name)
                if len(common_words) >= 2:
                    return product
            
            # If still no match, return first result if available
            return products[0] if products else None
            
        except Exception as e:
            logger.error(f"❌ Error getting product {identifier}: {e}")
            return None
    
    def _extract_key_specs(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key specs for comparison table"""
        specs = product.get("specs", {})
        key_specs = {}
        
        # Common specs for laptops
        if product.get("category") == "laptop":
            key_specs.update({
                "CPU": specs.get("processor", specs.get("cpu", "N/A")),
                "RAM": specs.get("ram", specs.get("memory", "N/A")),
                "Storage": specs.get("storage", specs.get("hard_drive", "N/A")),
                "Display": specs.get("display", specs.get("screen", "N/A")),
                "Graphics": specs.get("graphics", specs.get("gpu", "N/A")),
                "OS": specs.get("operating_system", specs.get("os", "N/A"))
            })
        
        # Common specs for smartphones
        elif product.get("category") == "smartphone":
            key_specs.update({
                "Display": specs.get("display", specs.get("screen", "N/A")),
                "Chipset": specs.get("chipset", specs.get("processor", "N/A")),
                "RAM": specs.get("ram", specs.get("memory", "N/A")),
                "Storage": specs.get("storage", specs.get("internal_storage", "N/A")),
                "Camera": specs.get("camera", specs.get("main_camera", "N/A")),
                "Battery": specs.get("battery", specs.get("battery_capacity", "N/A")),
                "OS": specs.get("operating_system", specs.get("os", "N/A"))
            })
        
        # Remove N/A values
        key_specs = {k: v for k, v in key_specs.items() if v != "N/A"}
        
        return key_specs
    
    def _run(
        self,
        product_ids: Optional[Union[List[str], str, Dict]] = None,
        comparison_aspects: Optional[List[str]] = None,
        include_reviews: Optional[bool] = True,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs  # Add this to catch extra parameters
    ) -> str:
        """Execute the compare tool"""
        try:
            # Debug: Log raw input
            logger.info(f"🔧 Raw input - product_ids type: {type(product_ids)}, value: {product_ids}")
            logger.info(f"🔧 Raw input - comparison_aspects: {comparison_aspects}")
            logger.info(f"🔧 Raw input - kwargs: {kwargs}")
            
            # Handle case where entire input is passed as first argument
            if isinstance(product_ids, dict):
                input_data = product_ids
                product_ids = input_data.get("product_ids") or input_data.get("product_names", [])
                comparison_aspects = input_data.get("comparison_aspects") or input_data.get("aspects", comparison_aspects)
                include_reviews = input_data.get("include_reviews", include_reviews)
            
            # Handle case where input is passed as kwargs
            if "product_names" in kwargs:
                product_ids = kwargs["product_names"]
            if "aspects" in kwargs:
                comparison_aspects = kwargs["aspects"]
            
            # Handle case where product_ids is a list containing a JSON string
            if isinstance(product_ids, list) and len(product_ids) == 1 and isinstance(product_ids[0], str):
                json_string = product_ids[0]
                logger.info(f"🔧 Trying to parse JSON string: {json_string}")
                try:
                    # Try to parse the single string as JSON
                    parsed_json = json.loads(json_string)
                    logger.info(f"🔧 Parsed JSON: {parsed_json}")
                    if isinstance(parsed_json, dict):
                        product_ids = parsed_json.get("product_ids", [])
                        comparison_aspects = parsed_json.get("comparison_aspects", comparison_aspects)
                        include_reviews = parsed_json.get("include_reviews", include_reviews)
                        logger.info(f"🔧 Extracted product_ids: {product_ids}")
                        logger.info(f"🔧 Extracted comparison_aspects: {comparison_aspects}")
                except json.JSONDecodeError as e:
                    logger.error(f"🔧 JSON decode error: {e}")
                    # If not JSON, treat as comma-separated product names
                    if ',' in json_string:
                        product_ids = [name.strip() for name in json_string.split(',')]
                    else:
                        product_ids = [json_string]
            
            # Handle case where product_ids is a string that might be JSON
            elif isinstance(product_ids, str):
                try:
                    parsed_json = json.loads(product_ids)
                    if isinstance(parsed_json, dict):
                        comparison_aspects = parsed_json.get("comparison_aspects", comparison_aspects)
                        include_reviews = parsed_json.get("include_reviews", include_reviews)
                        product_ids = parsed_json.get("product_ids", [])
                    elif isinstance(parsed_json, list):
                        product_ids = parsed_json
                    else:
                        product_ids = [product_ids]
                except json.JSONDecodeError:
                    # If not JSON, treat as single product or comma-separated
                    if ',' in product_ids:
                        product_ids = [name.strip() for name in product_ids.split(',')]
                    else:
                        product_ids = [product_ids]
            
            # Ensure product_ids is a list
            if not isinstance(product_ids, list):
                product_ids = []
                
            logger.info(f"🔍 Comparing products: {product_ids}")
            logger.info(f"🔍 Comparison aspects: {comparison_aspects}")
            logger.info(f"🔍 Product count: {len(product_ids) if product_ids else 0}")
            
            # Validate inputs
            if not product_ids or len(product_ids) < 2:
                return json.dumps({
                    "success": False,
                    "error": "Để so sánh sản phẩm, tôi cần ID hoặc tên của ít nhất 2 sản phẩm.\nBạn vui lòng tìm kiếm sản phẩm trước, sau đó tôi sẽ giúp bạn so sánh.",
                    "comparison": {},
                    "next_action": "Hãy tìm kiếm sản phẩm trước khi so sánh",
                    "debug_info": {
                        "received_product_ids": str(product_ids),
                        "product_count": len(product_ids) if product_ids else 0
                    }
                }, ensure_ascii=False)
            
            if len(product_ids) > 3:
                return json.dumps({
                    "success": False,
                    "error": f"Tôi chỉ có thể so sánh tối đa 3 sản phẩm cùng lúc. Bạn đã chọn {len(product_ids)} sản phẩm: {product_ids}. Vui lòng chọn lại.",
                    "comparison": {},
                    "debug_info": {
                        "received_product_ids": str(product_ids),
                        "product_count": len(product_ids)
                    }
                }, ensure_ascii=False)
            
            # Get product details
            products = []
            not_found = []
            
            for identifier in product_ids:
                product = self._get_product_by_id_or_name(identifier)
                if product:
                    products.append(product)
                    logger.info(f"✅ Found product: {product.get('name', identifier)}")
                else:
                    not_found.append(identifier)
                    logger.warning(f"❌ Product not found: {identifier}")
            
            if not products:
                return json.dumps({
                    "success": False,
                    "error": f"Không tìm thấy sản phẩm với tên/ID: {', '.join(product_ids)}.\nVui lòng kiểm tra lại tên sản phẩm hoặc tìm kiếm trước khi so sánh.",
                    "comparison": {},
                    "suggestions": [
                        "Sử dụng search_products để tìm sản phẩm trước",
                        "Kiểm tra lại tên sản phẩm",
                        "Sử dụng ID sản phẩm thay vì tên"
                    ]
                }, ensure_ascii=False)
            
            if not_found:
                logger.warning(f"Products not found: {not_found}")
                # Continue with found products but mention the missing ones
            
            # Check if products are from same category
            categories = set(product.get("category") for product in products)
            if len(categories) > 1:
                logger.warning(f"Comparing products from different categories: {categories}")
            
            # Set default comparison aspects based on category
            if not comparison_aspects:
                if "laptop" in categories:
                    comparison_aspects = ["performance", "price", "display", "portability", "battery"]
                elif "smartphone" in categories:
                    comparison_aspects = ["performance", "camera", "battery", "display", "price"]
                else:
                    comparison_aspects = ["price", "features", "rating", "brand"]
            
            # Build comparison table
            comparison_table = {
                "basic_info": {},
                "specs": {},
                "features": {},
                "reviews_summary": {} if include_reviews else None
            }
            
            for product in products:
                product_name = product.get("name", "Unknown")
                
                # Basic info
                comparison_table["basic_info"][product_name] = {
                    "brand": product.get("brand"),
                    "price": f"{product.get('price', 0):,.0f} {product.get('currency', 'VND')}",
                    "rating": f"{product.get('rating', 0)}/5",
                    "category": product.get("category")
                }
                
                # Key specs
                key_specs = self._extract_key_specs(product)
                comparison_table["specs"][product_name] = key_specs
                
                # Features
                features = product.get("features", [])
                comparison_table["features"][product_name] = features[:5]  # Top 5 features
                
                # Reviews summary
                if include_reviews and "reviews" in product:
                    reviews = product["reviews"]
                    avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0
                    comparison_table["reviews_summary"][product_name] = {
                        "total_reviews": len(reviews),
                        "avg_rating": round(avg_rating, 1),
                        "recent_feedback": reviews[0].get("content", "")[:100] + "..." if reviews else "Chưa có đánh giá"
                    }
            
            # Prepare result
            result = {
                "success": True,
                "message": f"So sánh {len(products)} sản phẩm thành công",
                "products_compared": [p.get("name") for p in products],
                "comparison_aspects": comparison_aspects,
                "comparison_table": comparison_table,
                "total_products": len(products),
                "raw_products_data": products
            }
            
            if not_found:
                result["warnings"] = [f"Không tìm thấy sản phẩm: {', '.join(not_found)}"]
            
            logger.info(f"✅ Comparison completed: {len(products)} products")
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Compare tool error: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi so sánh sản phẩm: {str(e)}",
                "comparison": {}
            })
    
    async def _arun(
        self,
        product_ids: Optional[Union[List[str], str, Dict]] = None,
        comparison_aspects: Optional[List[str]] = None,
        include_reviews: Optional[bool] = True,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """Async version of the tool"""
        return self._run(product_ids, comparison_aspects, include_reviews, run_manager, **kwargs)


# Create tool instance
compare_tool = CompareTool()
