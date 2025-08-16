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
from src.services.llm_service import llm_service
from src.prompts.prompt_manager import PromptType
from src.utils.prompt_helper import prompt_helper
from src.utils.logger import get_logger

logger = get_logger("recommend_tool")


class RecommendInput(BaseModel):
    """Input schema for RecommendTool"""
    user_needs: Optional[str] = Field(
        default="",
        description="User needs and preferences in Vietnamese (e.g., 'sinh viên IT, cần laptop lập trình, ngân sách 20 triệu')"
    )
    category: Optional[str] = Field(
        default=None,
        description="Product category: 'laptop' or 'smartphone'"
    )
    budget_min: Optional[float] = Field(
        default=None,
        description="Minimum budget in VND"
    )
    budget_max: Optional[float] = Field(
        default=None,
        description="Maximum budget in VND"
    )
    priority_features: Optional[List[str]] = Field(
        default=None,
        description="Priority features (e.g., ['performance', 'battery_life', 'camera', 'portability'])"
    )
    usage_purpose: Optional[str] = Field(
        default=None,
        description="Primary usage purpose (e.g., 'gaming', 'work', 'study', 'photography')"
    )
    num_recommendations: Optional[int] = Field(
        default=3,
        description="Number of recommendations to return (1-5)"
    )


class RecommendTool(BaseTool):
    """Tool for generating personalized product recommendations"""
    
    name: str = "recommend_products"
    description: str = """Đưa ra gợi ý sản phẩm phù hợp dựa trên nhu cầu và sở thích của khách hàng.
    
    Sử dụng tool này khi:
    - Khách hàng mô tả nhu cầu sử dụng (vd: "cần laptop cho lập trình")
    - Có thông tin về ngân sách và mục đích sử dụng
    - Cần gợi ý sản phẩm phù hợp với profile cụ thể
    - Khách hàng không biết chọn sản phẩm nào
    
    Tool sẽ phân tích nhu cầu và đưa ra gợi ý sản phẩm phù hợp nhất với lý do chi tiết."""
    
    args_schema: Type[BaseModel] = RecommendInput
    return_direct: bool = False
    
    def _analyze_user_needs(self, user_needs: str) -> Dict[str, Any]:
        """Analyze user needs using LLM to extract key requirements"""
        try:
           
            # Use prompt helper for safe formatting
            prompt = prompt_helper.safe_format_prompt(
                PromptType.RECOMMEND_ANALYSIS,
                user_needs=user_needs
            )
            
            if not prompt:
                logger.error("❌ Could not format recommendation analysis prompt")
                return {}

            response = llm_service.generate_text(
                prompt=prompt,
                context="recommendation",
                temperature=0.1
            )
            
            # Try to parse JSON from response  
            # generate_text returns string directly
            response_text = response if isinstance(response, str) else str(response)
                
            try:
                # Extract JSON from response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    analysis = json.loads(json_str)
                    return analysis
            except json.JSONDecodeError:
                pass
            
            # Fallback analysis
            return {
                "category": None,
                "budget_range": "không xác định",
                "usage_purpose": "general",
                "priority_features": [],
                "user_profile": "khách hàng cần tư vấn",
                "key_requirements": []
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing user needs: {e}")
            return {
                "category": None,
                "budget_range": "không xác định",
                "usage_purpose": "general",
                "priority_features": [],
                "user_profile": "khách hàng cần tư vấn",
                "key_requirements": []
            }
    
    def _score_product_relevance(self, product: Dict[str, Any], user_analysis: Dict[str, Any], priority_features: List[str]) -> float:
        """Score how relevant a product is to user needs"""
        try:
            score = 0.0
            max_score = 100.0
            
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
            
            # Usage purpose alignment (20 points max)
            usage_purpose = user_analysis.get("usage_purpose", "").lower()
            purpose_keywords = {
                "gaming": ["gaming", "game", "rtx", "nvidia", "high performance"],
                "work": ["business", "professional", "productivity", "office"],
                "study": ["student", "education", "lightweight", "portable"],
                "photography": ["camera", "photo", "image", "video"],
                "programming": ["developer", "coding", "ram", "ssd", "performance"]
            }
            
            if usage_purpose in purpose_keywords:
                keywords = purpose_keywords[usage_purpose]
                purpose_score = 0
                for keyword in keywords:
                    if any(keyword in pf for pf in product_features):
                        purpose_score += 4
                    elif any(keyword in spec_key or keyword in spec_val 
                           for spec_key, spec_val in product_specs.items()):
                        purpose_score += 3
                    elif keyword in product.get("description", "").lower():
                        purpose_score += 2
                
                score += min(purpose_score, 20)
            else:
                score += 10  # Default score
            
            # Brand reputation (20 points max)
            premium_brands = ["apple", "samsung", "dell", "hp", "lenovo", "asus", "sony"]
            brand = product.get("brand", "").lower()
            if brand in premium_brands:
                score += 15
            else:
                score += 10
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error(f"❌ Error scoring product relevance: {e}")
            return 50.0  # Default score
    
    def _generate_recommendation_explanation(self, product: Dict[str, Any], user_analysis: Dict[str, Any], rank: int) -> str:
        """Generate explanation for why this product is recommended"""
        try:
            # Use prompt helper to format product summary
            product_summary = prompt_helper.format_product_summary(product)
            
            # Use prompt helper for safe formatting
            prompt = prompt_helper.safe_format_prompt(
                PromptType.RECOMMEND_EXPLANATION,
                product_summary=json.dumps(product_summary, ensure_ascii=False),
                user_analysis=user_analysis,
                rank=rank
            )
            
            if not prompt:
                logger.error("❌ Could not format recommendation explanation prompt")
                return f"Sản phẩm {product.get('name')} phù hợp với nhu cầu của bạn."
            
            response = llm_service.generate_text(
                prompt=prompt,
                context="recommendation",
                temperature=0.3
            )
            
            # generate_text returns string directly
            return response if response else f"Sản phẩm {product.get('name')} phù hợp với nhu cầu của bạn."
            
        except Exception as e:
            logger.error(f"❌ Error generating explanation: {e}")
            return f"Sản phẩm {product.get('name')} được gợi ý dựa trên tiêu chí của bạn."
    
    def _run(
        self,
        user_needs: Optional[str] = "",
        category: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        priority_features: Optional[List[str]] = None,
        usage_purpose: Optional[str] = None,
        num_recommendations: Optional[int] = 3,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the recommend tool"""
        try:
            logger.info(f"🎯 Generating recommendations for: '{user_needs}'")
            
            # Validate inputs - if no user needs provided, return helpful message
            if not user_needs or not user_needs.strip():
                return json.dumps({
                    "success": False,
                    "error": "Để tôi có thể gợi ý sản phẩm phù hợp, bạn vui lòng cho tôi biết:\n- Bạn cần loại sản phẩm gì? (laptop hay smartphone)\n- Ngân sách dự kiến?\n- Mục đích sử dụng chính?",
                    "recommendations": [],
                    "next_action": "Hãy hỏi khách hàng về nhu cầu cụ thể trước khi gợi ý sản phẩm"
                }, ensure_ascii=False)
            
            num_recommendations = min(num_recommendations or 3, 5)
            
            # Analyze user needs with LLM
            user_analysis = self._analyze_user_needs(user_needs)
            
            # Override with explicit parameters
            if category:
                user_analysis["category"] = category
            if usage_purpose:
                user_analysis["usage_purpose"] = usage_purpose
            if priority_features:
                user_analysis["priority_features"] = priority_features
            
            # Prepare search filters
            filters = {}
            if user_analysis.get("category"):
                filters["category"] = user_analysis["category"].lower()
            
            # Budget filtering
            if budget_min is not None or budget_max is not None:
                price_filter = {}
                if budget_min:
                    price_filter["$gte"] = budget_min
                if budget_max:
                    price_filter["$lte"] = budget_max
                filters["price"] = price_filter
            
            # Get candidate products
            search_query = f"{user_needs} {user_analysis.get('usage_purpose', '')} {' '.join(user_analysis.get('priority_features', []))}"
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
                    user_analysis.get("priority_features", [])
                )
                scored_products.append((product, score))
            
            # Sort by score (highest first)
            scored_products.sort(key=lambda x: x[1], reverse=True)
            
            # Generate recommendations
            recommendations = []
            for i, (product, score) in enumerate(scored_products[:num_recommendations]):
                explanation = self._generate_recommendation_explanation(
                    product, user_analysis, i + 1
                )
                
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
        user_needs: Optional[str] = "",
        category: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        priority_features: Optional[List[str]] = None,
        usage_purpose: Optional[str] = None,
        num_recommendations: Optional[int] = 3,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of the tool"""
        return self._run(user_needs, category, budget_min, budget_max, priority_features, usage_purpose, num_recommendations, run_manager)


# Create tool instance
recommend_tool = RecommendTool()
