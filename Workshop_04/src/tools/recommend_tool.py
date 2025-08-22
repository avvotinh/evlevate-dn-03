"""
Recommend Tool for E-commerce AI Product Advisor
Implements intelligent product recommendation based on user needs and preferences.
"""

import json
from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from src.services.pinecone_service import pinecone_service
from src.utils.logger import get_logger

logger = get_logger("recommend_tool")


class RecommendInput(BaseModel):
    """Input schema for RecommendTool"""
    user_needs: str = Field(
        description="User needs and preferences in Vietnamese (e.g., 'sinh viên IT, cần laptop lập trình, ngân sách 20 triệu')"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="""User preferences and constraints for personalized recommendations. Can include:
        - category: 'laptop' or 'smartphone'
        - subcategory_preference: 'gaming', 'business', 'ultrabook', 'budget', 'flagship', 'mid-range'
        - brand_preference: preferred brand or list ['apple', 'samsung', 'dell', 'hp', 'asus', 'lenovo']
        - budget_min: minimum budget in VND
        - budget_max: maximum budget in VND
        - priority_features: most important features ['performance', 'battery_life', 'camera_quality', 'portability', 'display_quality', 'build_quality', 'storage', 'connectivity']
        - usage_scenarios: primary use cases ['gaming', 'work', 'study', 'content_creation', 'photography', 'programming', 'design', 'entertainment']
        - user_profile: user type ['student', 'professional', 'gamer', 'creator', 'business_user', 'casual_user']
        - num_recommendations: number of recommendations (1-5, default 3)
        - rating_threshold: minimum acceptable rating (1-5, default 3.5)
        - must_have_features: absolutely required features ['ssd', 'touchscreen', '4k_display', 'fast_charging', 'wireless_charging', 'fingerprint', 'face_unlock']
        - deal_breakers: features to avoid ['heavy_weight', 'poor_battery', 'low_storage', 'no_warranty']
        """
    )


class RecommendTool(BaseTool):
    """Tool for generating personalized product recommendations"""
    
    name: str = "recommend_products"
    name: str = "recommend_products"
    description: str = """💡 TƯ VẤN và GỢI Ý sản phẩm phù hợp với nhu cầu cá nhân.
    
    MỤC ĐÍCH: Đưa ra gợi ý sản phẩm tối ưu dựa trên phân tích nhu cầu người dùng
    
    SỬ DỤNG KHI:
    - Khách hàng CẦN TƯ VẤN: "gợi ý laptop cho sinh viên", "nên mua smartphone nào"
    - Mô tả nhu cầu sử dụng: "cần laptop lập trình", "smartphone chụp ảnh đẹp"
    - Có ngân sách và yêu cầu: "laptop gaming dưới 30 triệu", "iPhone hay Samsung tốt hơn"
    - Không biết chọn gì: "tư vấn laptop phù hợp", "điện thoại nào đáng mua"
    - So sánh lựa chọn: "Dell hay HP tốt hơn cho văn phòng"
    
    KHÔNG dùng cho: Tìm kiếm sản phẩm cụ thể đã biết tên
    
    OUTPUT: Top gợi ý có ranking + lý do chi tiết tại sao phù hợp"""
    
    args_schema: Type[BaseModel] = RecommendInput
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
                    # Fall back to treating as user_needs
                    return self._run(user_needs=tool_input, **kwargs)
            else:
                # Regular string input, treat as user_needs
                return self._run(user_needs=tool_input, **kwargs)
        except Exception as e:
            logger.error(f"❌ Error in recommend tool run: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi xử lý input: {str(e)}",
                "recommendations": []
            }, ensure_ascii=False)
    
    def _score_product_relevance(self, product: Dict[str, Any], user_analysis: Dict[str, Any], priority_features: List[str], must_have_features: List[str] = None) -> float:
        """Score how relevant a product is to user needs"""
        try:
            score = 0.0
            max_score = 100.0
            
            # Check must-have features first (disqualify if missing)
            if must_have_features:
                product_features = [f.lower() for f in product.get("features", [])]
                product_specs = {k.lower(): str(v).lower() for k, v in product.get("specs", {}).items()}
                product_description = product.get("description", "").lower()
                
                for must_feature in must_have_features:
                    feature_lower = must_feature.lower()
                    has_feature = (
                        any(feature_lower in pf for pf in product_features) or
                        any(feature_lower in spec_key or feature_lower in spec_val 
                           for spec_key, spec_val in product_specs.items()) or
                        feature_lower in product_description
                    )
                    if not has_feature:
                        logger.info(f"🚫 Product {product.get('name')} missing must-have feature: {must_feature}")
                        return 0.0  # Disqualify product
            
            # Base score from rating (20 points max)
            rating = product.get("rating", 0)
            score += (rating / 5.0) * 20
            
            # Feature matching (40 points max)
            product_features = [f.lower() for f in product.get("features", [])]
            product_specs = {k.lower(): str(v).lower() for k, v in product.get("specs", {}).items()}
            
            if priority_features:
                feature_score = 0
                for feature in priority_features:
                    feature_lower = feature.lower()
                    # Check in features
                    if any(feature_lower in pf for pf in product_features):
                        feature_score += 10
                    # Check in specs
                    elif any(feature_lower in spec_key or feature_lower in spec_val 
                           for spec_key, spec_val in product_specs.items()):
                        feature_score += 8
                
                score += min(feature_score, 40)
            else:
                score += 20  # Default score if no priority features
            
            # Usage scenarios alignment (20 points max)
            usage_scenarios = user_analysis.get("usage_scenarios", [])
            if usage_scenarios and usage_scenarios != ["general"]:
                scenario_keywords = {
                    "gaming": ["gaming", "game", "rtx", "nvidia", "high performance", "fps"],
                    "work": ["business", "professional", "productivity", "office", "enterprise"],
                    "study": ["student", "education", "lightweight", "portable", "battery"],
                    "photography": ["camera", "photo", "image", "megapixel", "lens"],
                    "programming": ["developer", "coding", "ram", "ssd", "performance", "compiler"],
                    "design": ["graphics", "gpu", "adobe", "creative", "design", "display"],
                    "content_creation": ["video", "editing", "rendering", "creator", "4k"],
                    "entertainment": ["media", "streaming", "display", "speakers", "entertainment"]
                }
                
                scenario_score = 0
                for scenario in usage_scenarios:
                    keywords = scenario_keywords.get(scenario.lower(), [])
                    for keyword in keywords:
                        if any(keyword in pf for pf in product_features):
                            scenario_score += 4
                        elif any(keyword in spec_key or keyword in spec_val 
                               for spec_key, spec_val in product_specs.items()):
                            scenario_score += 3
                        elif keyword in product.get("description", "").lower():
                            scenario_score += 2
                
                score += min(scenario_score, 20)
            else:
                score += 10  # Default score
            
            # Brand preference bonus (20 points max)
            brand_preference = user_analysis.get("brand_preference")
            product_brand = product.get("brand", "").lower()
            
            if brand_preference:
                if isinstance(brand_preference, list):
                    if any(brand.lower() in product_brand for brand in brand_preference):
                        score += 20  # Perfect match
                    else:
                        score += 5   # No match penalty
                elif isinstance(brand_preference, str):
                    if brand_preference.lower() in product_brand:
                        score += 20  # Perfect match
                    else:
                        score += 5   # No match penalty
                else:
                    score += 10  # No preference
            else:
                # No brand preference - judge by brand reputation
                premium_brands = ["apple", "samsung", "dell", "hp", "lenovo", "asus", "sony", "msi"]
                if product_brand in premium_brands:
                    score += 15
                else:
                    score += 10
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error(f"❌ Error scoring product relevance: {e}")
            return 50.0  # Default score
    
    def _run(
        self,
        user_needs: str,
        metadata: Optional[Dict[str, Any]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> str:
        """Execute the recommend tool"""
        try:
            logger.info(f"🎯 Generating recommendations for: '{user_needs}'")
            logger.info(f"📊 Recommendation metadata: {metadata}")
            
            # Validate inputs - if no user needs provided, return helpful message
            if not user_needs or not user_needs.strip():
                return json.dumps({
                    "success": False,
                    "error": "Để tôi có thể gợi ý sản phẩm phù hợp, bạn vui lòng cho tôi biết:\n- Bạn cần loại sản phẩm gì? (laptop hay smartphone)\n- Ngân sách dự kiến?\n- Mục đích sử dụng chính?",
                    "recommendations": [],
                    "next_action": "Hãy hỏi khách hàng về nhu cầu cụ thể trước khi gợi ý sản phẩm"
                }, ensure_ascii=False)
            
            # Extract metadata parameters with new naming
            if metadata is None:
                metadata = {}
            
            category = metadata.get("category")
            subcategory_preference = metadata.get("subcategory_preference")
            brand_preference = metadata.get("brand_preference")
            budget_min = metadata.get("budget_min")
            budget_max = metadata.get("budget_max")
            priority_features = metadata.get("priority_features", [])
            usage_scenarios = metadata.get("usage_scenarios", [])
            user_profile = metadata.get("user_profile")
            num_recommendations = metadata.get("num_recommendations", 3)
            rating_threshold = metadata.get("rating_threshold", 3.5)
            must_have_features = metadata.get("must_have_features", [])
            deal_breakers = metadata.get("deal_breakers", [])
            
            # Validate and limit num_recommendations
            num_recommendations = min(num_recommendations or 3, 5)
            
            # Use direct parameters for analysis
            user_analysis = {
                "category": category,
                "brand_preference": brand_preference,
                "subcategory_preference": subcategory_preference,
                "usage_scenarios": usage_scenarios or ["general"],
                "user_profile": user_profile or "general_user",
                "priority_features": priority_features or [],
                "key_requirements": [user_needs] if user_needs else []
            }
            
            # Prepare search filters
            filters = {}
            if category:
                filters["category"] = category.lower()
            
            # Handle brand preference (can be string or list)
            if brand_preference:
                if isinstance(brand_preference, list):
                    filters["brand"] = {"$in": [b.lower().strip() for b in brand_preference]}
                elif isinstance(brand_preference, str) and brand_preference.strip():
                    filters["brand"] = brand_preference.lower().strip()
            
            # Add subcategory preference
            if subcategory_preference:
                filters["subcategory"] = subcategory_preference.lower()
            
            # Budget filtering
            if budget_min is not None or budget_max is not None:
                price_filter = {}
                if budget_min:
                    price_filter["$gte"] = budget_min
                if budget_max:
                    price_filter["$lte"] = budget_max
                filters["price"] = price_filter
            
            # Rating filtering
            if rating_threshold is not None:
                filters["rating"] = {"$gte": rating_threshold}
            
            logger.info(f"🔍 Search filters applied: {filters}")

            # Build search query from available information
            search_parts = []
            if user_needs:
                search_parts.append(user_needs)
            if usage_scenarios and usage_scenarios != ["general"]:
                search_parts.extend(usage_scenarios)
            if priority_features:
                search_parts.extend(priority_features)
            
            search_query = " ".join(search_parts) if search_parts else "laptop smartphone"
            
            # Get candidate products
            candidates = pinecone_service.search_products(
                query=search_query,
                filters=filters,
                top_k=20,  # Get more candidates for better selection
                include_reviews=True
            )
            
            if not candidates:
                # Try broader search without filters
                candidates = pinecone_service.search_products(
                    query=user_needs,
                    top_k=20
                )
            
            if not candidates:
                return json.dumps({
                    "success": True,
                    "message": "Không tìm thấy sản phẩm phù hợp với yêu cầu",
                    "user_analysis": user_analysis,
                    "recommendations": [],
                    "suggestions": [
                        "Thử mở rộng ngân sách",
                        "Xem xét danh mục sản phẩm khác",
                        "Điều chỉnh yêu cầu tính năng"
                    ]
                })
            
            # Score and rank products
            scored_products = []
            for product in candidates:
                score = self._score_product_relevance(
                    product, 
                    user_analysis, 
                    user_analysis.get("priority_features", []),
                    must_have_features
                )
                # Only include products with score > 0 (passed must-have features check)
                if score > 0:
                    scored_products.append((product, score))
            
            # Sort by score (highest first)
            scored_products.sort(key=lambda x: x[1], reverse=True)
            
            # Generate recommendations
            recommendations = []
            for i, (product, score) in enumerate(scored_products[:num_recommendations]):
                explanation = f"Sản phẩm #{i + 1}: {product.get('name')} - Raw data for RAG processing"
                
                recommendation = {
                    "rank": i + 1,
                    "product": {
                        "id": product.get("id"),
                        "name": product.get("name"),
                        "brand": product.get("brand"),
                        "category": product.get("category"),
                        "price": product.get("price"),
                        "currency": product.get("currency", "VND"),
                        "rating": product.get("rating", 0),
                        "description": product.get("description", ""),
                        "features": product.get("features", []),
                        "specs": product.get("specs", {})
                    },
                    "relevance_score": round(score, 1),
                    "explanation": explanation,
                    "why_recommended": {
                        "matches_needs": True,
                        "price_appropriate": self._check_price_appropriate(product, budget_min, budget_max),
                        "feature_alignment": len([f for f in user_analysis.get("priority_features", []) 
                                                if any(f.lower() in pf.lower() for pf in product.get("features", []))]),
                        "rating": product.get("rating", 0)
                    }
                }
                recommendations.append(recommendation)
            
            result = {
                "success": True,
                "message": f"Đã tìm thấy {len(recommendations)} gợi ý phù hợp",
                "user_needs": user_needs,
                "user_analysis": user_analysis,
                "recommendations": recommendations,
                "total_candidates": len(candidates),
                "search_filters": filters
            }
            
            logger.info(f"✅ Generated {len(recommendations)} recommendations")
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Recommend tool error: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi tạo gợi ý: {str(e)}",
                "recommendations": []
            })
    
    def _check_price_appropriate(self, product: Dict[str, Any], budget_min: Optional[float], budget_max: Optional[float]) -> bool:
        """Check if product price is within budget"""
        price = product.get("price", 0)
        if budget_min and price < budget_min:
            return False
        if budget_max and price > budget_max:
            return False
        return True
    
    async def _arun(
        self,
        user_needs: str,
        metadata: Optional[Dict[str, Any]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of the tool"""
        return self._run(user_needs, metadata, run_manager)


# Create tool instance
recommend_tool = RecommendTool()
