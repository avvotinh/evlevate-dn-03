"""
Review Tool for E-commerce AI Product Advisor
Retrieves and analyzes product reviews from the vector database.
"""

import json
from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from src.services.pinecone_service import pinecone_service
from src.utils.logger import get_logger

logger = get_logger("review_tool")


class ReviewInput(BaseModel):
    """Input schema for ReviewTool"""
    product_name: str = Field(
        description="Tên sản phẩm cần xem reviews (e.g., 'iPhone 15 Pro Max', 'Dell XPS 15')"
    )
    product_id: Optional[str] = Field(
        default="",
        description="ID sản phẩm nếu biết chính xác"
    )
    limit: Optional[int] = Field(
        default=5,
        description="Số lượng reviews tối đa (1-10, default 5)"
    )
    rating_filter: Optional[int] = Field(
        default=None,
        description="Lọc theo rating cụ thể (1-5 sao)"
    )
    sort_by: Optional[str] = Field(
        default="newest",
        description="Sắp xếp theo: 'newest', 'oldest', 'rating_high', 'rating_low', 'helpful'"
    )


class ReviewTool(BaseTool):
    """Tool for retrieving and analyzing product reviews"""
    
    name: str = "get_product_reviews"
    description: str = """📝 XEM REVIEWS của sản phẩm cụ thể.
    
    🎯 **MỤC ĐÍCH**: Lấy và hiển thị đánh giá từ người dùng thực tế
    
    📋 **SỬ DỤNG KHI**:
    - "Tôi muốn xem reviews của [sản phẩm]"
    - "Đánh giá về [sản phẩm] như thế nào?"
    - "Reviews người dùng về [sản phẩm]"
    - "Ý kiến khách hàng về [sản phẩm]"
    - "Nhận xét về [sản phẩm]"
    
    🔍 **FEATURES**:
    - Tìm sản phẩm theo tên
    - Lấy reviews chi tiết với rating, ưu nhược điểm
    - Sắp xếp theo tiêu chí khác nhau
    - Tóm tắt xu hướng đánh giá
    - Highlight điểm mạnh/yếu chính
    
    📊 **OUTPUT**: Danh sách reviews với summary và insights"""
    
    args_schema: Type[BaseModel] = ReviewInput
    return_direct: bool = False

    def _run(
        self,
        product_name: str,
        product_id: Optional[str] = "",
        limit: Optional[int] = 5,
        rating_filter: Optional[int] = None,
        sort_by: Optional[str] = "newest",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the review tool"""
        try:
            logger.info(f"📝 Getting reviews for product: '{product_name}'")
            
            # Validate inputs
            if not product_name or not product_name.strip():
                return json.dumps({
                    "success": False,
                    "error": "Tên sản phẩm không được để trống",
                    "reviews": []
                }, ensure_ascii=False)
            
            limit = max(1, min(limit or 5, 10))  # Ensure limit is between 1-10
            
            # Step 1: Find the product if no product_id provided
            if not product_id:
                product_id = self._find_product_id(product_name)
                if not product_id:
                    return json.dumps({
                        "success": False,
                        "error": f"Không tìm thấy sản phẩm '{product_name}'",
                        "reviews": [],
                        "suggestion": "Thử tìm kiếm với từ khóa khác hoặc kiểm tra chính tả"
                    }, ensure_ascii=False)
            
            # Step 2: Get reviews for the product
            reviews = self._get_reviews_for_product(product_id, limit, rating_filter)
            
            if not reviews:
                return json.dumps({
                    "success": False,
                    "error": f"Không tìm thấy reviews cho sản phẩm này",
                    "reviews": [],
                    "product_name": product_name,
                    "product_id": product_id
                }, ensure_ascii=False)
            
            # Step 3: Sort reviews
            sorted_reviews = self._sort_reviews(reviews, sort_by)
            
            # Step 4: Generate review summary and insights
            summary = self._generate_review_summary(sorted_reviews)
            
            result = {
                "success": True,
                "product_name": product_name,
                "product_id": product_id,
                "total_reviews": len(sorted_reviews),
                "reviews": sorted_reviews,
                "summary": summary,
                "sort_by": sort_by,
                "rating_filter": rating_filter
            }
            
            logger.info(f"✅ Retrieved {len(sorted_reviews)} reviews for '{product_name}'")
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Review tool error: {e}")
            return json.dumps({
                "success": False,
                "error": f"Lỗi khi lấy reviews: {str(e)}",
                "reviews": []
            }, ensure_ascii=False)
    
    def _find_product_id(self, product_name: str) -> Optional[str]:
        """Find product ID by searching for product name"""
        try:
            # Search for the product using existing search functionality
            products = pinecone_service.search_products(
                query=product_name,
                filters=None,
                top_k=1,
                include_reviews=False
            )
            
            if products and len(products) > 0:
                product_id = products[0].get('id')
                logger.info(f"🔍 Found product ID: {product_id} for '{product_name}'")
                return product_id
            
            logger.warning(f"⚠️ No product found for: '{product_name}'")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding product: {e}")
            return None
    
    def _get_reviews_for_product(
        self, 
        product_id: str, 
        limit: int, 
        rating_filter: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get reviews for a specific product with optional rating filter"""
        try:
            # Use pinecone service to get reviews
            all_reviews = pinecone_service.get_product_reviews(product_id, limit=50)  # Get more for filtering
            
            # Apply rating filter if specified
            if rating_filter is not None:
                filtered_reviews = [r for r in all_reviews if r.get('rating') == rating_filter]
                logger.info(f"🔍 Filtered {len(all_reviews)} reviews to {len(filtered_reviews)} with rating {rating_filter}")
                return filtered_reviews[:limit]
            
            return all_reviews[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting reviews: {e}")
            return []
    
    def _sort_reviews(self, reviews: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """Sort reviews by specified criteria"""
        try:
            if sort_by == "newest":
                return sorted(reviews, key=lambda x: x.get('date', ''), reverse=True)
            elif sort_by == "oldest":
                return sorted(reviews, key=lambda x: x.get('date', ''))
            elif sort_by == "rating_high":
                return sorted(reviews, key=lambda x: x.get('rating', 0), reverse=True)
            elif sort_by == "rating_low":
                return sorted(reviews, key=lambda x: x.get('rating', 0))
            elif sort_by == "helpful":
                return sorted(reviews, key=lambda x: x.get('helpful_count', 0), reverse=True)
            else:
                # Default to newest
                return sorted(reviews, key=lambda x: x.get('date', ''), reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Error sorting reviews: {e}")
            return reviews
    
    def _generate_review_summary(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary and insights from reviews"""
        try:
            if not reviews:
                return {}
            
            # Calculate rating distribution
            ratings = [r.get('rating', 0) for r in reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[f"{i}_star"] = ratings.count(i)
            
            # Extract common pros and cons
            all_pros = []
            all_cons = []
            
            for review in reviews:
                if review.get('pros'):
                    all_pros.extend(review['pros'])
                if review.get('cons'):
                    all_cons.extend(review['cons'])
            
            # Count frequency of pros and cons
            from collections import Counter
            top_pros = Counter(all_pros).most_common(5)
            top_cons = Counter(all_cons).most_common(5)
            
            # Recent vs older reviews trend
            recent_ratings = []
            older_ratings = []
            
            for review in reviews:
                date_str = review.get('date', '')
                if date_str:
                    if '2025' in date_str:
                        recent_ratings.append(review.get('rating', 0))
                    else:
                        older_ratings.append(review.get('rating', 0))
            
            summary = {
                "average_rating": round(avg_rating, 1),
                "total_reviews": len(reviews),
                "rating_distribution": rating_distribution,
                "top_pros": [{"feature": pro[0], "mentions": pro[1]} for pro in top_pros],
                "top_cons": [{"feature": con[0], "mentions": con[1]} for con in top_cons],
                "recent_trend": {
                    "recent_avg": round(sum(recent_ratings) / len(recent_ratings), 1) if recent_ratings else 0,
                    "older_avg": round(sum(older_ratings) / len(older_ratings), 1) if older_ratings else 0,
                    "recent_count": len(recent_ratings),
                    "older_count": len(older_ratings)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating summary: {e}")
            return {}

    async def _arun(
        self,
        product_name: str,
        product_id: Optional[str] = "",
        limit: Optional[int] = 5,
        rating_filter: Optional[int] = None,
        sort_by: Optional[str] = "newest",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of the review tool"""
        return self._run(
            product_name, product_id, limit, rating_filter, sort_by, run_manager
        )


# Create tool instance
review_tool = ReviewTool()
