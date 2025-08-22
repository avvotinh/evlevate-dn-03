"""
Prompt Templates for E-commerce AI Product Advisor
Manages all prompts using LangChain PromptTemplate and ChatPromptTemplate
"""

from typing import Dict, List, Any, Optional
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger("prompts")


class PromptType(Enum):
    """Types of prompts available"""
    SYSTEM_BASE = "system_base"
    
    # Tool-specific prompts
    RECOMMEND_EXPLANATION = "recommend_explanation"
    COMPARE_ANALYSIS = "compare_analysis"
    
    # Service prompts
    FALLBACK_SYSTEM = "fallback_system"
    
    # LangGraph agent prompts
    INTENT_CLASSIFICATION = "intent_classification"
    SEARCH_EXTRACTION = "search_extraction"
    COMPARE_EXTRACTION = "compare_extraction"
    RECOMMEND_EXTRACTION = "recommend_extraction"
    
    # Generation tool prompts
    GENERATION_BASE_SYSTEM = "generation_base_system"
    GENERATION_COMPARE_INTENT = "generation_compare_intent"
    GENERATION_RECOMMEND_INTENT = "generation_recommend_intent"
    GENERATION_SEARCH_INTENT = "generation_search_intent"
    GENERATION_REVIEW_INTENT = "generation_review_intent"
    GENERATION_DIRECT_INTENT = "generation_direct_intent"
    GENERATION_CONSOLIDATED = "generation_consolidated"


class PromptManager:
    """Manages all prompt templates for the application"""
    
    def __init__(self):
        """Initialize prompt manager with all templates"""
        self.templates = {}
        self._initialize_templates()
        logger.info("✅ Prompt templates initialized")
    
    def _initialize_templates(self):
        """Initialize all prompt templates"""
        # Base system prompt
        self.templates[PromptType.SYSTEM_BASE] = self._create_system_base_prompt()

        # LangGraph agent prompts
        self.templates[PromptType.INTENT_CLASSIFICATION] = self._create_intent_classification_prompt()
        self.templates[PromptType.SEARCH_EXTRACTION] = self._create_search_extraction_prompt()
        self.templates[PromptType.COMPARE_EXTRACTION] = self._create_compare_extraction_prompt()
        self.templates[PromptType.RECOMMEND_EXTRACTION] = self._create_recommend_extraction_prompt()
        
        # Generation tool prompts
        self.templates[PromptType.GENERATION_BASE_SYSTEM] = self._create_generation_base_system_prompt()
        self.templates[PromptType.GENERATION_COMPARE_INTENT] = self._create_generation_compare_intent_prompt()
        self.templates[PromptType.GENERATION_RECOMMEND_INTENT] = self._create_generation_recommend_intent_prompt()
        self.templates[PromptType.GENERATION_SEARCH_INTENT] = self._create_generation_search_intent_prompt()
        self.templates[PromptType.GENERATION_REVIEW_INTENT] = self._create_generation_review_intent_prompt()
        self.templates[PromptType.GENERATION_DIRECT_INTENT] = self._create_generation_direct_intent_prompt()
        self.templates[PromptType.GENERATION_CONSOLIDATED] = self._create_generation_consolidated_prompt()
        
        # Service prompts
        self.templates[PromptType.FALLBACK_SYSTEM] = self._create_fallback_system_prompt()
        
    
    def _create_system_base_prompt(self) -> ChatPromptTemplate:
        """Create base system prompt template"""
        
        system_template = """Bạn là AI Product Advisor - trợ lý AI chuyên tư vấn sản phẩm điện tử thông minh và thân thiện.

🎯 VAI TRÒ:
- Tư vấn viên sản phẩm điện tử chuyên nghiệp  
- Hiểu biết sâu về laptop và smartphone
- Giao tiếp bằng tiếng Việt tự nhiên và thân thiện
- Luôn đặt lợi ích khách hàng lên hàng đầu

📋 NHIỆM VỤ CHÍNH:
- Giúp khách hàng tìm sản phẩm phù hợp với nhu cầu và ngân sách
- So sánh và đánh giá sản phẩm một cách khách quan
- Đưa ra gợi ý dựa trên phân tích kỹ thuật và kinh nghiệm
- Giải thích thông số kỹ thuật bằng ngôn ngữ dễ hiểu
- Hỗ trợ quyết định mua hàng thông minh

⚡ QUY TẮC GIAO TIẾP:
1. Luôn trả lời bằng tiếng Việt
2. Giữ tone thân thiện, chuyên nghiệp nhưng không gò bó
3. Đưa ra thông tin chính xác, không bịa đặt
4. Hỏi thêm chi tiết khi cần làm rõ nhu cầu
5. Tập trung vào giá trị và lợi ích thực tế
6. Thừa nhận khi không biết và đề xuất tìm hiểu thêm

🛍️ SẢN PHẨM CHUYÊN MÔN:
- 💻 Laptop: gaming, lập trình, văn phòng, design, học tập
- 📱 Smartphone: camera, gaming, pin, công việc, giải trí

💡 PHONG CÁCH TƯ VẤN:
- Phân tích nhu cầu trước khi gợi ý sản phẩm
- So sánh ưu/nhược điểm một cách cân bằng  
- Đưa ra nhiều lựa chọn với các mức giá khác nhau
- Giải thích lý do tại sao sản phẩm phù hợp
- Đề cập đến điểm cần lưu ý (nếu có)

🎨 NGỮ CẢNH: {context}

📝 HƯỚNG DẪN ĐẶC BIỆT: {special_instructions}"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template)
        ])
    
    def get_prompt(self, prompt_type: PromptType, **kwargs) -> Any:
        """Get a specific prompt template"""
        try:
            if prompt_type not in self.templates:
                logger.error(f"❌ Prompt type not found: {prompt_type}")
                return None
            
            template = self.templates[prompt_type]
            return template
            
        except Exception as e:
            logger.error(f"❌ Error getting prompt: {e}")
            return None
    
    def format_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """Format a prompt with given variables"""
        try:
            template = self.get_prompt(prompt_type, **kwargs)
            if not template:
                return ""
            
            if isinstance(template, ChatPromptTemplate):
                messages = template.format_messages(**kwargs)
                return messages[0].content if messages else ""
            elif isinstance(template, PromptTemplate):
                return template.format(**kwargs)
            else:
                logger.error(f"❌ Unknown template type: {type(template)}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error formatting prompt: {e}")
            return ""
    
    def get_chat_messages(self, prompt_type: PromptType, **kwargs) -> List[Dict[str, str]]:
        """Get formatted chat messages for ChatPromptTemplate"""
        try:
            template = self.get_prompt(prompt_type, **kwargs)
            if not template or not isinstance(template, ChatPromptTemplate):
                return []
            
            messages = template.format_messages(**kwargs)
            return [{"role": msg.type, "content": msg.content} for msg in messages]
            
        except Exception as e:
            logger.error(f"❌ Error getting chat messages: {e}")
            return []
    
    def get_intent_specific_instructions(self, intent: str, tools_used: List[str] = None) -> str:
        """Get intent-specific instructions for generation tool"""
        try:
            if tools_used is None:
                tools_used = []
            
            if intent == "compare" or "compare_products" in tools_used:
                template = self.get_prompt(PromptType.GENERATION_COMPARE_INTENT)
                return template.format() if template else ""
            
            elif intent == "recommend" or "recommend_products" in tools_used:
                template = self.get_prompt(PromptType.GENERATION_RECOMMEND_INTENT)
                return template.format() if template else ""
            
            elif intent == "search" or "search_products" in tools_used:
                template = self.get_prompt(PromptType.GENERATION_SEARCH_INTENT)
                return template.format() if template else ""
            
            else:  # direct or general
                template = self.get_prompt(PromptType.GENERATION_DIRECT_INTENT)
                return template.format() if template else ""
            
        except Exception as e:
            logger.error(f"❌ Error getting intent instructions: {e}")
            return ""
    
    def build_generation_prompt(
        self,
        user_query: str,
        intent: str,
        context: str = "",
        conversation_history: str = "",
        tools_used: List[str] = None
    ) -> str:
        """Build consolidated generation prompt using templates"""
        try:
            # Get base system prompt
            base_template = self.get_prompt(PromptType.GENERATION_BASE_SYSTEM)
            base_system = base_template.format() if base_template else ""
            
            # Get intent-specific instructions
            intent_instructions = self.get_intent_specific_instructions(intent, tools_used)
            
            # Build context section
            context_section = ""
            if context and context.strip():
                context_section = f"\n=== THÔNG TIN SẢN PHẨM ===\n{context}"
            
            # Build conversation section
            conversation_section = ""
            if conversation_history and conversation_history.strip():
                conversation_section = f"\n=== LỊCH SỬ ===\n{conversation_history}"
            
            # Get consolidated template
            consolidated_template = self.get_prompt(PromptType.GENERATION_CONSOLIDATED)
            if consolidated_template:
                return consolidated_template.format(
                    base_system=base_system,
                    intent_instructions=intent_instructions,
                    user_query=user_query,
                    context_section=context_section,
                    conversation_section=conversation_section
                )
            else:
                # Fallback to manual building
                prompt_parts = [
                    base_system,
                    intent_instructions,
                    f"\n=== CÂU HỎI ===\n{user_query}",
                ]
                
                if context_section:
                    prompt_parts.append(context_section)
                
                if conversation_section:
                    prompt_parts.append(conversation_section)
                
                prompt_parts.append("\n=== HƯỚNG DẪN ===\nTạo câu trả lời hoàn chỉnh, tự nhiên và hữu ích cho người dùng.")
                
                return "\n".join(prompt_parts)
            
        except Exception as e:
            logger.error(f"❌ Error building generation prompt: {e}")
            return f"Hệ thống gặp lỗi khi xây dựng prompt: {str(e)}"

    
    def _create_fallback_system_prompt(self) -> PromptTemplate:
        """Create fallback system prompt for LLM service"""
        template = """Bạn là AI Product Advisor - trợ lý AI chuyên tư vấn sản phẩm điện tử.
        
Nhiệm vụ: Tư vấn laptop và smartphone bằng tiếng Việt thân thiện và chuyên nghiệp.
Ngữ cảnh: {context}

Quy tắc:
- Luôn trả lời bằng tiếng Việt
- Đưa ra thông tin chính xác và hữu ích  
- Hỏi thêm khi cần làm rõ nhu cầu
- Tập trung vào lợi ích khách hàng"""

        return PromptTemplate(
            template=template,
            input_variables=["context"]
        )

    def _create_intent_classification_prompt(self) -> PromptTemplate:
        """Create intent classification prompt for LangGraph agent"""
        template = """Phân tích ý định của người dùng và trả về CHÍNH XÁC một trong các intent sau:

INTENT OPTIONS:
- greeting: Chào hỏi, cảm ơn, hỏi về AI
- search: Tìm kiếm thông tin sản phẩm cụ thể, hỏi cấu hình, thông số, giá
- compare: So sánh 2+ sản phẩm
- recommend: Xin gợi ý, tư vấn sản phẩm phù hợp với nhu cầu
- review: Xem đánh giá, nhận xét, reviews của sản phẩm
- direct: Câu hỏi tổng quát về công nghệ, thuật ngữ, khái niệm

USER INPUT: "{user_input}"

EXAMPLES:
- "Xin chào" → greeting
- "Dell Inspiron 14 5420 cấu hình như thế nào" → search
- "iPhone 15 vs Samsung S24" → compare
- "Gợi ý laptop cho sinh viên" → recommend
- "Tôi muốn xem reviews iPhone 15" → review
- "Đánh giá về Dell XPS 15" → review
- "Người dùng nói gì về Samsung S24?" → review
- "Reviews laptop gaming ASUS ROG" → review
- "Cảm ơn bạn" → greeting
- "RAM là gì?" → direct
- "Sự khác biệt giữa SSD và HDD" → direct
- "CPU Intel Core i7 nghĩa là gì?" → direct
- "Làm thế nào để chọn laptop phù hợp?" → direct
- "Màn hình OLED có ưu điểm gì?" → direct
- "Xu hướng smartphone 2024" → direct

Chỉ trả về TÊN INTENT (greeting/search/compare/recommend/review/direct):"""

        return PromptTemplate(
            template=template,
            input_variables=["user_input"]
        )

    def _create_search_extraction_prompt(self) -> PromptTemplate:
        """Create search parameter extraction prompt for LangGraph agent"""
        template = """Phân tích câu hỏi sau và trích xuất thông tin tìm kiếm sản phẩm:

USER INPUT: "{user_input}"

Trả về JSON với format:
{{
    "query": "từ khóa tìm kiếm chính (loại bỏ thương hiệu và giá)",
    "metadata": {{
        "category": "laptop" hoặc "smartphone" hoặc null,
        "brand": "tên thương hiệu (apple, samsung, dell, hp, asus, xiaomi, oppo, vivo, lenovo, acer, sony, huawei, v.v.) hoặc null",
        "price_min": số tiền tối thiểu (VND) hoặc null,
        "price_max": số tiền tối đa (VND) hoặc null,
        "max_results": số lượng sản phẩm cần tìm (1-10, mặc định 3),
        "include_reviews": true/false
    }}
}}

VÍ DỤ:
- "tìm laptop gaming" → {{"query": "laptop gaming", "metadata": {{"category": "laptop", "brand": null, "price_min": null, "price_max": null, "max_results": 3, "include_reviews": false}}}}
- "Dell Inspiron 14 5420 cấu hình như thế nào" → {{"query": "Inspiron 14 5420 cấu hình", "metadata": {{"category": "laptop", "brand": "dell", "price_min": null, "price_max": null, "max_results": 3, "include_reviews": true}}}}
- "điện thoại Samsung dưới 15 triệu" → {{"query": "điện thoại", "metadata": {{"category": "smartphone", "brand": "samsung", "price_min": null, "price_max": 15000000, "max_results": 3, "include_reviews": false}}}}
- "laptop HP từ 20-30 triệu cho lập trình" → {{"query": "laptop lập trình", "metadata": {{"category": "laptop", "brand": "hp", "price_min": 20000000, "price_max": 30000000, "max_results": 3, "include_reviews": false}}}}
- "tìm 2 laptop lập trình khoảng giá 20-25 triệu" → {{"query": "laptop lập trình", "metadata": {{"category": "laptop", "brand": null, "price_min": 20000000, "price_max": 25000000, "max_results": 2, "include_reviews": false}}}}
- "cho tôi 5 điện thoại tốt nhất" → {{"query": "điện thoại tốt nhất", "metadata": {{"category": "smartphone", "brand": null, "price_min": null, "price_max": null, "max_results": 5, "include_reviews": false}}}}

QUAN TRỌNG:
- Trích xuất chính xác tên thương hiệu (apple, samsung, dell, hp, asus, xiaomi, oppo, vivo, lenovo, acer, sony, huawei)
- Nhận dạng giá từ các cụm từ: "dưới X triệu", "trên X triệu", "từ X-Y triệu", "khoảng X triệu"
- Nhận dạng số lượng từ các cụm từ: "tìm 2", "cho tôi 5", "3 sản phẩm", "một vài", "mấy chiếc"
- Loại bỏ thương hiệu và giá khỏi query chính
- 1 triệu = 1,000,000 VND
- max_results: nếu có số cụ thể thì dùng số đó, nếu "một vài/mấy" thì dùng 3-4, mặc định là 3

CHỈ TRẢ VỀ JSON:"""

        return PromptTemplate(
            template=template,
            input_variables=["user_input"]
        )

    def _create_compare_extraction_prompt(self) -> PromptTemplate:
        """Create comparison parameter extraction prompt for LangGraph agent"""
        template = """Phân tích câu hỏi so sánh sản phẩm sau và trích xuất thông tin:

USER INPUT: "{user_input}"

Trả về JSON với format:
{{
    "product_names": ["tên sản phẩm 1", "tên sản phẩm 2", ...],
    "comparison_aspects": ["khía cạnh 1", "khía cạnh 2", ...],
    "include_reviews": true/false
}}

VÍ DỤ:
- "so sánh iPhone 15 vs Samsung S24" → {{"product_names": ["iPhone 15", "Samsung Galaxy S24"], "comparison_aspects": ["giá", "camera", "hiệu năng"], "include_reviews": true}}
- "Dell XPS 15 khác gì MacBook Air M2" → {{"product_names": ["Dell XPS 15", "MacBook Air M2"], "comparison_aspects": ["hiệu năng", "giá", "thiết kế"], "include_reviews": true}}
- "iPhone 15 Pro Max vs iPhone 15 Pro về camera" → {{"product_names": ["iPhone 15 Pro Max", "iPhone 15 Pro"], "comparison_aspects": ["camera"], "include_reviews": false}}

QUAN TRỌNG:
- Trích xuất chính xác tên sản phẩm từ câu hỏi
- Nếu không có khía cạnh cụ thể, dùng: ["giá", "hiệu năng", "thiết kế", "camera"]
- include_reviews = true nếu câu hỏi cần đánh giá chi tiết

CHỈ TRẢ VỀ JSON:"""

        return PromptTemplate(
            template=template,
            input_variables=["user_input"]
        )

    def _create_recommend_extraction_prompt(self) -> PromptTemplate:
        """Create recommendation parameter extraction prompt for LangGraph agent"""
        template = """Phân tích câu hỏi xin gợi ý sản phẩm sau và trích xuất thông tin:

USER INPUT: "{user_input}"

Trả về JSON với format:
{{
    "user_needs": "mô tả chi tiết nhu cầu người dùng",
    "metadata": {{
        "category": "laptop" hoặc "smartphone" hoặc null,
        "brand": "thương hiệu ưa thích (apple, samsung, dell, hp, asus, v.v.) hoặc null",
        "budget_min": số tiền tối thiểu (VND) hoặc null,
        "budget_max": số tiền tối đa (VND) hoặc null,
        "priority_features": ["tính năng ưu tiên 1", "tính năng 2", ...],
        "usage_purpose": "gaming" hoặc "work" hoặc "study" hoặc "photography" hoặc null,
        "num_recommendations": 3-5,
        "rating_min": rating tối thiểu (1-5) hoặc null,
        "must_have_features": ["tính năng bắt buộc"] hoặc []
    }}
}}

VÍ DỤ:
- "gợi ý laptop cho sinh viên" → {{"user_needs": "laptop phù hợp sinh viên học tập", "metadata": {{"category": "laptop", "brand": null, "budget_min": null, "budget_max": null, "priority_features": ["portability", "battery_life"], "usage_purpose": "study", "num_recommendations": 3, "rating_min": null, "must_have_features": []}}}}
- "tư vấn điện thoại Samsung gaming dưới 15 triệu" → {{"user_needs": "smartphone Samsung gaming hiệu năng cao trong ngân sách 15 triệu", "metadata": {{"category": "smartphone", "brand": "samsung", "budget_min": null, "budget_max": 15000000, "priority_features": ["performance", "gaming"], "usage_purpose": "gaming", "num_recommendations": 3, "rating_min": null, "must_have_features": []}}}}
- "laptop Dell cho lập trình viên 20-30 triệu, cần SSD" → {{"user_needs": "laptop Dell mạnh mẽ cho lập trình viên với ngân sách 20-30 triệu", "metadata": {{"category": "laptop", "brand": "dell", "budget_min": 20000000, "budget_max": 30000000, "priority_features": ["performance", "display_quality"], "usage_purpose": "work", "num_recommendations": 4, "rating_min": null, "must_have_features": ["ssd"]}}}}

PRIORITY FEATURES có thể là: performance, battery_life, camera, portability, display_quality, gaming, storage
USAGE PURPOSE có thể là: gaming, work, study, photography, programming
MUST_HAVE_FEATURES có thể là: ssd, touchscreen, 4k, waterproof, dual_sim, fast_charging

CHỈ TRẢ VỀ JSON:"""

        return PromptTemplate(
            template=template,
            input_variables=["user_input"]
        )

    def _create_generation_base_system_prompt(self) -> PromptTemplate:
        """Create base system prompt for generation tool"""
        template = """Bạn là AI Product Advisor - trợ lý tư vấn sản phẩm điện tử chuyên nghiệp.

🎯 NHIỆM VỤ: Tạo câu trả lời tự nhiên, hữu ích dựa trên thông tin sản phẩm được cung cấp.

⚡ NGUYÊN TẮC:
- Luôn dựa trên thông tin chính xác từ context
- Ngôn ngữ tự nhiên, thân thiện như bạn bè am hiểu công nghệ
- Giải thích thuật ngữ kỹ thuật bằng cách dễ hiểu
- Đưa ra lời khuyên thiết thực và có căn cứ"""

        return PromptTemplate(
            template=template,
            input_variables=[]
        )

    def _create_generation_compare_intent_prompt(self) -> PromptTemplate:
        """Create compare intent instructions for generation tool"""
        template = """
🔍 NHIỆM VỤ SO SÁNH:
- Tạo bảng so sánh chi tiết các thông số kỹ thuật chính
- Phân tích ưu/nhược điểm từng sản phẩm một cách khách quan
- Đưa ra kết luận về sản phẩm phù hợp cho từng nhu cầu
- Gợi ý lựa chọn dựa trên ngân sách và mục đích sử dụng
- Format: Sử dụng bảng, bullet points và đánh giá tổng quan"""

        return PromptTemplate(
            template=template,
            input_variables=[]
        )

    def _create_generation_recommend_intent_prompt(self) -> PromptTemplate:
        """Create recommendation intent instructions for generation tool"""
        template = """
💡 NHIỆM VỤ GỢI Ý:
- Giải thích lý do gợi ý từng sản phẩm dựa trên nhu cầu người dùng
- Phân tích độ phù hợp của từng sản phẩm với yêu cầu cụ thể
- So sánh điểm mạnh/yếu của các sản phẩm được gợi ý
- Đưa ra khuyến nghị ưu tiên theo thứ tự hợp lý
- Format: Liệt kê theo thứ tự ưu tiên với giải thích chi tiết"""

        return PromptTemplate(
            template=template,
            input_variables=[]
        )

    def _create_generation_search_intent_prompt(self) -> PromptTemplate:
        """Create search intent instructions for generation tool"""
        template = """
🔍 NHIỆM VỤ GIẢI THÍCH:
- Phân tích chi tiết thông tin sản phẩm và thông số kỹ thuật
- Giải thích ý nghĩa của các specs bằng ngôn ngữ dễ hiểu
- Đánh giá sản phẩm dựa trên tính năng và hiệu suất
- Cung cấp insights về giá trị và use cases thực tế
- Format: Structured với headings, specs table, và practical insights"""

        return PromptTemplate(
            template=template,
            input_variables=[]
        )

    def _create_generation_review_intent_prompt(self) -> PromptTemplate:
        """Create review intent instructions for generation tool"""
        template = """
📝 NHIỆM VỤ CHO INTENT 'REVIEW':
Trình bày reviews/đánh giá sản phẩm một cách rõ ràng, hữu ích và dễ hiểu.

🎯 **Cách trình bày reviews:**
- Tóm tắt tổng quan về sản phẩm và đánh giá
- Hiển thị rating trung bình và phân bố đánh giá
- Highlight những ưu điểm được nhắc đến nhiều nhất
- Highlight những nhược điểm thường gặp
- Trích dẫn các review tiêu biểu (cả tích cực và tiêu cực)

📊 **Cấu trúc trình bày:**
1. **Tổng quan:** Điểm đánh giá trung bình và số lượng reviews
2. **Điểm mạnh phổ biến:** Top 3-5 ưu điểm được đề cập nhiều
3. **Điểm yếu thường gặp:** Top 3-5 nhược điểm được đề cập
4. **Reviews nổi bật:** 2-3 đánh giá chi tiết từ người dùng
5. **Xu hướng đánh giá:** So sánh reviews gần đây vs cũ (nếu có)

✨ **Gợi ý thêm:**
- Đề xuất xem thêm reviews theo rating cụ thể
- Gợi ý so sánh với sản phẩm tương tự
- Đề xuất tìm hiểu thêm về sản phẩm nếu quan tâm
"""

        return PromptTemplate(
            template=template,
            input_variables=[]
        )

    def _create_generation_direct_intent_prompt(self) -> PromptTemplate:
        """Create direct intent instructions for generation tool"""
        template = """
💬 NHIỆM VỤ CHO INTENT 'DIRECT':
Bạn là trợ lý AI thông minh, trả lời trực tiếp các câu hỏi tổng quát không liên quan đến sản phẩm cụ thể.

🎯 **Xử lý các loại câu hỏi:**
- Câu hỏi về công nghệ chung (không cần tìm sản phẩm cụ thể)
- Hỏi về thuật ngữ, khái niệm
- Yêu cầu giải thích hoặc hướng dẫn chung
- Câu hỏi "làm thế nào", "là gì", "tại sao"
- Hỏi về xu hướng, so sánh khái niệm

📋 **Cách trả lời:**
- Trả lời trực tiếp và chính xác
- Cung cấp thông tin hữu ích, cụ thể
- Giải thích đơn giản, dễ hiểu
- Đưa ra ví dụ thực tế nếu cần
- Gợi ý câu hỏi tiếp theo có liên quan

✨ **Gợi ý thông minh:**
- Nếu câu hỏi có thể dẫn đến tìm kiếm sản phẩm, gợi ý người dùng hỏi cụ thể hơn
- Đề xuất các chủ đề liên quan mà người dùng có thể quan tâm
- Kết nối với dịch vụ tư vấn sản phẩm nếu phù hợp

🗣️ **Tone:** Thân thiện, chuyên nghiệp, hữu ích như một chuyên gia tư vấn công nghệ"""

        return PromptTemplate(
            template=template,
            input_variables=[]
        )

    def _create_generation_consolidated_prompt(self) -> PromptTemplate:
        """Create consolidated prompt template for generation tool"""
        template = """{base_system}

{intent_instructions}

=== CÂU HỎI ===
{user_query}

{context_section}

{conversation_section}

=== HƯỚNG DẪN ===
Tạo câu trả lời hoàn chỉnh, tự nhiên và hữu ích cho người dùng."""

        return PromptTemplate(
            template=template,
            input_variables=[
                "base_system", 
                "intent_instructions", 
                "user_query", 
                "context_section", 
                "conversation_section"
            ]
        )


# Singleton instance
prompt_manager = PromptManager()
