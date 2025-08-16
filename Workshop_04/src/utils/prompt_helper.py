"""
Prompt Helper Utilities for E-commerce AI Product Advisor
Provides utility functions for formatting prompts, data, and responses
"""

import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

from src.prompts.prompt_manager import PromptType
from src.utils.logger import get_logger

logger = get_logger("prompt_helper")


class DataFormatter:
    """Utility class for formatting data for prompts"""
    
    @staticmethod
    def format_product_basic_info(product: Dict[str, Any]) -> str:
        """Format product basic information for display"""
        try:
            name = product.get('name', 'Unknown Product')
            brand = product.get('brand', 'Unknown Brand')
            price = product.get('price', 0)
            currency = product.get('currency', 'VND')
            rating = product.get('rating', 0)
            category = product.get('category', 'Unknown')
            
            return f"""🏷️ **{name}**
- Thương hiệu: {brand}
- Giá: {price:,.0f} {currency}
- Đánh giá: {rating}/5 ⭐
- Loại: {category}"""
        except Exception as e:
            logger.error(f"Error formatting product basic info: {e}")
            return "Không thể hiển thị thông tin sản phẩm"
    
    @staticmethod
    def format_product_specs(product: Dict[str, Any]) -> str:
        """Format product specifications for display"""
        try:
            specs = product.get('specs', {})
            if not specs:
                return "Không có thông số kỹ thuật"
            
            formatted_specs = []
            for key, value in specs.items():
                # Convert key to readable format
                readable_key = key.replace('_', ' ').title()
                formatted_specs.append(f"- {readable_key}: {value}")
            
            return "📋 **Thông số kỹ thuật:**\n" + "\n".join(formatted_specs)
        except Exception as e:
            logger.error(f"Error formatting product specs: {e}")
            return "Không thể hiển thị thông số kỹ thuật"
    
    @staticmethod
    def format_product_features(product: Dict[str, Any]) -> str:
        """Format product features for display"""
        try:
            features = product.get('features', [])
            if not features:
                return "Không có tính năng đặc biệt"
            
            formatted_features = [f"✨ {feature}" for feature in features[:10]]  # Limit to 10 features
            return "🎯 **Tính năng nổi bật:**\n" + "\n".join(formatted_features)
        except Exception as e:
            logger.error(f"Error formatting product features: {e}")
            return "Không thể hiển thị tính năng"
    
    @staticmethod
    def format_product_reviews(product: Dict[str, Any], max_reviews: int = 3) -> str:
        """Format product reviews for display"""
        try:
            reviews = product.get('reviews', [])
            if not reviews:
                return "Chưa có đánh giá từ người dùng"
            
            formatted_reviews = []
            for i, review in enumerate(reviews[:max_reviews]):
                rating = review.get('rating', 0)
                content = review.get('content', 'Không có nội dung')
                # Truncate long reviews
                if len(content) > 200:
                    content = content[:200] + "..."
                
                formatted_reviews.append(f"⭐ {rating}/5: {content}")
            
            total_reviews = len(reviews)
            avg_rating = sum(r.get('rating', 0) for r in reviews) / len(reviews)
            
            header = f"💬 **Đánh giá ({total_reviews} đánh giá, trung bình {avg_rating:.1f}/5):**"
            return header + "\n" + "\n".join(formatted_reviews)
        except Exception as e:
            logger.error(f"Error formatting product reviews: {e}")
            return "Không thể hiển thị đánh giá"


class ComparisonFormatter:
    """Utility class for formatting comparison data"""
    
    @staticmethod
    def format_comparison_data(products: List[Dict[str, Any]]) -> str:
        """Format product data for comparison analysis"""
        try:
            if not products:
                return "Không có sản phẩm để so sánh"
            
            formatted_data = []
            
            for i, product in enumerate(products, 1):
                product_info = f"""
**SẢN PHẨM {i}: {product.get('name', 'Unknown')}**
{DataFormatter.format_product_basic_info(product)}

{DataFormatter.format_product_specs(product)}

{DataFormatter.format_product_features(product)}

{DataFormatter.format_product_reviews(product, max_reviews=2)}
---
"""
                formatted_data.append(product_info)
            
            return "\n".join(formatted_data)
        except Exception as e:
            logger.error(f"Error formatting comparison data: {e}")
            return "Không thể định dạng dữ liệu so sánh"
    
    @staticmethod
    def format_comparison_table(products: List[Dict[str, Any]], aspects: List[str] = None) -> str:
        """Format comparison table for products"""
        try:
            if not products:
                return "Không có sản phẩm để tạo bảng so sánh"
            
            # Default aspects if not provided
            if not aspects:
                category = products[0].get('category', 'unknown')
                if category == 'laptop':
                    aspects = ['CPU', 'RAM', 'Storage', 'Display', 'Graphics', 'Price']
                elif category == 'smartphone':
                    aspects = ['Display', 'Chipset', 'RAM', 'Storage', 'Camera', 'Battery', 'Price']
                else:
                    aspects = ['Brand', 'Price', 'Rating', 'Features']
            
            # Create table header
            product_names = [p.get('name', 'Unknown')[:20] for p in products]  # Truncate long names
            header = f"| **Tiêu chí** | {' | '.join(product_names)} |"
            separator = "|" + "|".join([" --- " for _ in range(len(products) + 1)]) + "|"
            
            # Create table rows
            rows = [header, separator]
            
            for aspect in aspects:
                row_data = [f"**{aspect}**"]
                
                for product in products:
                    value = ComparisonFormatter._get_product_value_for_aspect(product, aspect)
                    row_data.append(value)
                
                rows.append("| " + " | ".join(row_data) + " |")
            
            return "\n".join(rows)
        except Exception as e:
            logger.error(f"Error formatting comparison table: {e}")
            return "Không thể tạo bảng so sánh"
    
    @staticmethod
    def _get_product_value_for_aspect(product: Dict[str, Any], aspect: str) -> str:
        """Get product value for a specific comparison aspect"""
        try:
            aspect_lower = aspect.lower()
            specs = product.get('specs', {})
            
            # Price handling
            if aspect_lower == 'price' or aspect_lower == 'giá':
                price = product.get('price', 0)
                currency = product.get('currency', 'VND')
                return f"{price:,.0f} {currency}"
            
            # Brand handling
            elif aspect_lower == 'brand' or aspect_lower == 'thương hiệu':
                return product.get('brand', 'N/A')
            
            # Rating handling
            elif aspect_lower == 'rating' or aspect_lower == 'đánh giá':
                rating = product.get('rating', 0)
                return f"{rating}/5 ⭐"
            
            # Features handling
            elif aspect_lower == 'features' or aspect_lower == 'tính năng':
                features = product.get('features', [])
                return f"{len(features)} tính năng"
            
            # Technical specs handling
            else:
                # Try to find in specs with various key formats
                possible_keys = [
                    aspect_lower,
                    aspect_lower.replace(' ', '_'),
                    aspect_lower.replace(' ', ''),
                    aspect.lower(),
                    aspect.upper(),
                    aspect
                ]
                
                for key in possible_keys:
                    if key in specs:
                        return str(specs[key])
                
                # Special mappings for common specs
                spec_mappings = {
                    'cpu': ['processor', 'chipset', 'cpu'],
                    'ram': ['memory', 'ram'],
                    'storage': ['storage', 'hard_drive', 'internal_storage'],
                    'display': ['screen', 'display'],
                    'graphics': ['gpu', 'graphics'],
                    'camera': ['main_camera', 'camera'],
                    'battery': ['battery_capacity', 'battery'],
                    'os': ['operating_system', 'os']
                }
                
                for mapped_keys in spec_mappings.values():
                    if aspect_lower in mapped_keys:
                        for key in mapped_keys:
                            if key in specs:
                                return str(specs[key])
                
                return "N/A"
        except Exception as e:
            logger.error(f"Error getting product value for aspect {aspect}: {e}")
            return "Error"


class PromptHelper:
    """Main prompt helper class with formatting utilities"""
    
    def __init__(self):
        """Initialize prompt helper"""
        self.data_formatter = DataFormatter()
        self.comparison_formatter = ComparisonFormatter()
        logger.info("✅ Prompt helper initialized")
    
    def format_product_for_prompt(self, product: Dict[str, Any], include_reviews: bool = True) -> str:
        """Format product data for use in prompts"""
        try:
            sections = [
                self.data_formatter.format_product_basic_info(product),
                self.data_formatter.format_product_specs(product),
                self.data_formatter.format_product_features(product)
            ]
            
            if include_reviews:
                sections.append(self.data_formatter.format_product_reviews(product))
            
            return "\n\n".join(sections)
        except Exception as e:
            logger.error(f"Error formatting product for prompt: {e}")
            return "Không thể định dạng thông tin sản phẩm"
    
    def format_products_list(self, products: List[Dict[str, Any]], max_products: int = 10) -> str:
        """Format list of products for prompts"""
        try:
            if not products:
                return "Không có sản phẩm nào được tìm thấy"
            
            formatted_products = []
            for i, product in enumerate(products[:max_products], 1):
                product_summary = f"""
{i}. {self.data_formatter.format_product_basic_info(product)}
"""
                formatted_products.append(product_summary)
            
            total_count = len(products)
            if total_count > max_products:
                formatted_products.append(f"\n... và {total_count - max_products} sản phẩm khác")
            
            return "\n".join(formatted_products)
        except Exception as e:
            logger.error(f"Error formatting products list: {e}")
            return "Không thể định dạng danh sách sản phẩm"
    
    def format_comparison_data(self, products: List[Dict[str, Any]]) -> str:
        """Format comparison data (wrapper for ComparisonFormatter)"""
        return self.comparison_formatter.format_comparison_data(products)
    
    def format_comparison_table(self, products: List[Dict[str, Any]], aspects: List[str] = None) -> str:
        """Format comparison table (wrapper for ComparisonFormatter)"""
        return self.comparison_formatter.format_comparison_table(products, aspects)
    
    def safe_format_prompt(
        self, 
        prompt_type: PromptType, 
        **kwargs
    ) -> Optional[str]:
        """Safely format prompt with error handling"""
        try:
            # Import here to avoid circular imports
            from src.prompts.prompt_manager import prompt_manager
            
            # Get the prompt template
            prompt_template = prompt_manager.get_prompt(prompt_type)
            
            if not prompt_template:
                logger.error(f"Prompt template not found for type: {prompt_type}")
                return None
            
            # Format the prompt with provided kwargs
            formatted_prompt = prompt_template.format(**kwargs)
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"Error formatting prompt {prompt_type}: {e}")
            return None
    
    def extract_search_parameters(self, user_query: str) -> Dict[str, Any]:
        """Extract search parameters from user query"""
        try:
            query_lower = user_query.lower()
            params = {
                "category": None,
                "price_range": None,
                "brand": None,
                "features": []
            }
            
            # Category detection
            if any(word in query_lower for word in ['laptop', 'máy tính', 'computer']):
                params["category"] = "laptop"
            elif any(word in query_lower for word in ['điện thoại', 'smartphone', 'phone', 'mobile']):
                params["category"] = "smartphone"
            
            # Price detection
            price_keywords = ['dưới', 'under', 'below', 'tối đa', 'max', 'không quá']
            for keyword in price_keywords:
                if keyword in query_lower:
                    # Try to extract price number
                    words = query_lower.split()
                    for i, word in enumerate(words):
                        if keyword in word and i + 1 < len(words):
                            try:
                                price_text = words[i + 1]
                                # Handle Vietnamese number format
                                if 'triệu' in price_text or 'tr' in price_text:
                                    price_num = float(price_text.replace('triệu', '').replace('tr', '').strip())
                                    params["price_range"] = {"max": price_num * 1000000}
                                elif 'nghìn' in price_text or 'k' in price_text:
                                    price_num = float(price_text.replace('nghìn', '').replace('k', '').strip())
                                    params["price_range"] = {"max": price_num * 1000}
                            except (ValueError, IndexError):
                                continue
            
            # Brand detection
            brands = ['apple', 'samsung', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 
                     'xiaomi', 'oppo', 'vivo', 'huawei', 'sony', 'lg']
            for brand in brands:
                if brand in query_lower:
                    params["brand"] = brand.title()
                    break
            
            # Feature detection
            features = ['gaming', 'game', 'chơi game', 'văn phòng', 'office', 'thiết kế', 'design',
                       'đồ họa', 'graphics', 'lập trình', 'programming', 'học tập', 'study']
            for feature in features:
                if feature in query_lower:
                    params["features"].append(feature)
            
            return params
        except Exception as e:
            logger.error(f"Error extracting search parameters: {e}")
            return {}
    
    def format_error_message(self, error: str, context: str = "") -> str:
        """Format error message for user display"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            error_msg = f"⚠️ **Đã xảy ra lỗi** ({timestamp})\n\n"
            error_msg += f"**Chi tiết:** {error}\n"
            
            if context:
                error_msg += f"**Ngữ cảnh:** {context}\n"
            
            error_msg += "\n💡 **Gợi ý:**\n"
            error_msg += "- Vui lòng thử lại câu hỏi với cách diễn đạt khác\n"
            error_msg += "- Kiểm tra lại tên sản phẩm hoặc thông tin tìm kiếm\n"
            error_msg += "- Liên hệ hỗ trợ nếu lỗi tiếp tục xảy ra"
            
            return error_msg
        except Exception:
            return "⚠️ Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau."
    
    def format_success_message(self, message: str, data: Any = None) -> str:
        """Format success message for user display"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            success_msg = f"✅ **Thành công** ({timestamp})\n\n"
            success_msg += f"{message}\n"
            
            if data:
                if isinstance(data, dict) and 'count' in data:
                    success_msg += f"\n📊 **Kết quả:** {data['count']} items"
                elif isinstance(data, list):
                    success_msg += f"\n📊 **Kết quả:** {len(data)} items"
            
            return success_msg
        except Exception:
            return f"✅ {message}"


# Create global instance
prompt_helper = PromptHelper()
