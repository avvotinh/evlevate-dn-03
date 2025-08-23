"""
Enhanced LangGraph Agent for E-commerce AI Product Advisor
Improved implementation with native LangGraph memory and state management
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage
import json
import re
import uuid

from src.services.llm_service import llm_service
from src.tools.tool_manager import ToolManager
from src.tools.generation_tool import generation_tool
from src.prompts.prompt_manager import prompt_manager, PromptType
from src.utils.logger import get_logger

logger = get_logger("langgraph_agent")


class AgentState(TypedDict):
    """Enhanced state for LangGraph agent with conversation history"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_input: str
    session_id: Optional[str]
    current_step: str
    intent: str
    tools_used: List[str]
    search_results: Optional[Dict[str, Any]]
    comparison_results: Optional[Dict[str, Any]]
    recommendation_results: Optional[Dict[str, Any]]
    review_results: Optional[Dict[str, Any]]
    context_data: Optional[str]
    final_response: Optional[str]
    iteration_count: int
    error_count: int
    reasoning_steps: List[Dict[str, Any]]
    # Memory-related fields for context continuity
    conversation_history: List[Dict[str, str]]  # Lưu trữ lịch sử hội thoại
    previous_search_results: Optional[List[Dict[str, Any]]]  # Kết quả tìm kiếm trước đó
    previous_products: Optional[List[str]]  # Danh sách sản phẩm từ lần chat trước
    context_references: Optional[Dict[str, Any]]  # Tham chiếu ngữ cảnh


class ProductAdvisorLangGraphAgent:
    """Enhanced LangGraph-based Product Advisor Agent with native memory management"""
    
    def __init__(self):
        """Initialize LangGraph agent with native memory saver"""
        self.tool_manager = ToolManager()
        self.llm = llm_service.get_llm()
        
        # Native LangGraph memory management
        self.memory_saver = MemorySaver()
        
        self.graph = self._create_graph()
        logger.info("✅ Enhanced LangGraph Agent initialized with native memory")
    
    def _create_graph(self) -> StateGraph:
        """Create enhanced LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes with error handling
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("handle_greeting", self._handle_greeting)
        workflow.add_node("search_products", self._search_products)
        workflow.add_node("compare_products", self._compare_products)
        workflow.add_node("recommend_products", self._recommend_products)
        workflow.add_node("get_reviews", self._get_reviews)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Define entry point
        workflow.set_entry_point("analyze_intent")
        
        # Enhanced conditional routing
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_intent,
            {
                "greeting": "handle_greeting",
                "search": "search_products",
                "compare": "compare_products", 
                "recommend": "recommend_products",
                "review": "get_reviews",
                "direct": "generate_response",
                "error": "handle_error"
            }
        )
        
        # All nodes can lead to response generation or error handling
        workflow.add_edge("handle_greeting", END)  # Greeting ends directly
        workflow.add_edge("search_products", "generate_response")
        workflow.add_edge("compare_products", "generate_response")
        workflow.add_edge("recommend_products", "generate_response")
        workflow.add_edge("get_reviews", "generate_response")
        workflow.add_edge("handle_error", END)
        workflow.add_edge("generate_response", END)
        
        # Compile with memory saver for persistent state management
        return workflow.compile(checkpointer=self.memory_saver)

    def _get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """Retrieve conversation history from memory for context continuity"""
        try:
            thread_config = {"configurable": {"thread_id": session_id}}
            logger.info(f"🔍 Retrieving conversation history for session: {session_id}")
            
            # Try to get the last state from memory
            try:
                # Get checkpoint history
                checkpoints = list(self.graph.get_state_history(config=thread_config))
                logger.info(f"🔍 Found {len(checkpoints)} checkpoints")
                
                if checkpoints:
                    # Get the most recent successful state
                    for i, checkpoint in enumerate(checkpoints):
                        logger.info(f"🔍 Checkpoint {i}: has values={bool(checkpoint.values)}, error_count={checkpoint.values.get('error_count', 0) if checkpoint.values else 'N/A'}")
                        
                        if checkpoint.values and not checkpoint.values.get("error_count", 0):
                            last_state = checkpoint.values
                            logger.info(f"🔍 Using checkpoint {i} with keys: {list(last_state.keys())}")
                            
                            # Extract products with detailed logging
                            extracted_products = self._extract_product_names_from_results(last_state)
                            
                            result = {
                                "conversation_history": last_state.get("conversation_history", []),
                                "previous_search_results": last_state.get("search_results"),
                                "previous_products": extracted_products,
                                "context_references": {
                                    "last_intent": last_state.get("intent"),
                                    "last_tools_used": last_state.get("tools_used", []),
                                    "last_response": last_state.get("final_response")
                                }
                            }
                            logger.info(f"🔍 Memory context result: previous_products={extracted_products}, last_intent={last_state.get('intent')}")
                            return result
                else:
                    logger.info("🔍 No checkpoints found")
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve checkpoint history: {e}")
            
            # If no history found, return empty
            logger.info("🔍 Returning empty memory context")
            return {
                "conversation_history": [],
                "previous_search_results": None,
                "previous_products": [],
                "context_references": {}
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error retrieving conversation history: {e}")
            return {
                "conversation_history": [],
                "previous_search_results": None,
                "previous_products": [],
                "context_references": {}
            }

    def _extract_product_names_from_results(self, state: Dict[str, Any]) -> List[str]:
        """Extract product names from previous results for context reference"""
        product_names = []
        try:
            logger.info(f"🔍 Extracting product names from state keys: {list(state.keys())}")
            
            # Extract from search results
            if state.get("search_results"):
                search_data = state["search_results"]
                logger.info(f"🔍 Search data type: {type(search_data)}")
                
                # Search tool always returns JSON string, so parse it
                if isinstance(search_data, str):
                    try:
                        parsed_data = json.loads(search_data)
                        logger.info(f"🔍 Parsed search data successfully")
                        
                        if parsed_data.get("success") and "products" in parsed_data:
                            products = parsed_data["products"]
                            logger.info(f"🔍 Found {len(products)} products in search results")
                            
                            for i, product in enumerate(products[:3]):  # Top 3 products
                                if isinstance(product, dict):
                                    # Lấy tên sản phẩm từ các key phổ biến
                                    name = product.get("name") or product.get("title") or product.get("product_name")
                                    if name:
                                        product_names.append(name)
                                        logger.info(f"🔍 Extracted product {i+1}: {name}")
                        else:
                            logger.warning(f"⚠️ Search not successful or no products: {parsed_data.get('success', False)}")
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Could not parse search results as JSON: {e}")
                        
                # Fallback: if search_data is already a dict (shouldn't happen but just in case)
                elif isinstance(search_data, dict):
                    if search_data.get("success") and "products" in search_data:
                        products = search_data["products"]
                        logger.info(f"🔍 Found {len(products)} products in dict format")
                        
                        for i, product in enumerate(products[:3]):
                            if isinstance(product, dict):
                                name = product.get("name")
                                if name:
                                    product_names.append(name)
                                    logger.info(f"🔍 Extracted product {i+1}: {name}")
            
            # Extract from comparison results (similar format)
            if state.get("comparison_results"):
                compare_data = state["comparison_results"]
                if isinstance(compare_data, str):
                    try:
                        parsed_data = json.loads(compare_data)
                        if "products" in parsed_data:
                            for product in parsed_data["products"]:
                                if isinstance(product, dict):
                                    name = product.get("name")
                                    if name and name not in product_names:
                                        product_names.append(name)
                    except json.JSONDecodeError:
                        logger.warning("⚠️ Could not parse comparison results")
                elif isinstance(compare_data, dict) and "products" in compare_data:
                    for product in compare_data["products"]:
                        if isinstance(product, dict):
                            name = product.get("name")
                            if name and name not in product_names:
                                product_names.append(name)
            
            # Extract from recommendation results
            if state.get("recommendation_results"):
                recommend_data = state["recommendation_results"]
                logger.info(f"🔍 Recommendation data type: {type(recommend_data)}")
                logger.info(f"🔍 Recommendation data preview: {str(recommend_data)[:200]}...")
                
                if isinstance(recommend_data, str):
                    try:
                        parsed_data = json.loads(recommend_data)
                        logger.info(f"🔍 Parsed recommendation data keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
                        
                        # Check for different possible keys
                        products_list = None
                        if "recommendations" in parsed_data:
                            products_list = parsed_data["recommendations"]
                            logger.info(f"🔍 Found 'recommendations' key with {len(products_list)} items")
                        elif "products" in parsed_data:
                            products_list = parsed_data["products"]
                            logger.info(f"🔍 Found 'products' key with {len(products_list)} items")
                        elif "suggested_products" in parsed_data:
                            products_list = parsed_data["suggested_products"]
                            logger.info(f"🔍 Found 'suggested_products' key with {len(products_list)} items")
                        
                        if products_list:
                            for i, product in enumerate(products_list[:3]):
                                if isinstance(product, dict):
                                    logger.info(f"🔍 Recommendation product {i+1} raw data: {product}")
                                    # Nếu có key 'product', lấy product['name']
                                    if "product" in product and isinstance(product["product"], dict):
                                        name = product["product"].get("name")
                                    else:
                                        name = product.get("name") or product.get("title") or product.get("product_name")
                                    if name and name not in product_names:
                                        product_names.append(name)
                                        logger.info(f"🔍 Extracted recommendation product {i+1}: {name}")
                        else:
                            logger.warning(f"⚠️ No products found in recommendation data. Available keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Could not parse recommendation results as JSON: {e}")
                        
                elif isinstance(recommend_data, dict):
                    logger.info(f"🔍 Recommendation data is dict with keys: {list(recommend_data.keys())}")
                    
                    # Check for different possible keys
                    products_list = None
                    if "recommendations" in recommend_data:
                        products_list = recommend_data["recommendations"]
                        logger.info(f"🔍 Found 'recommendations' key with {len(products_list)} items")
                    elif "products" in recommend_data:
                        products_list = recommend_data["products"]
                        logger.info(f"🔍 Found 'products' key with {len(products_list)} items")
                    elif "suggested_products" in recommend_data:
                        products_list = recommend_data["suggested_products"]
                        logger.info(f"🔍 Found 'suggested_products' key with {len(products_list)} items")
                    
                    if products_list:
                        for i, product in enumerate(products_list[:3]):
                            if isinstance(product, dict):
                                logger.info(f"🔍 Recommendation product {i+1} raw data: {product}")
                                if "product" in product and isinstance(product["product"], dict):
                                    name = product["product"].get("name")
                                else:
                                    name = product.get("name") or product.get("title") or product.get("product_name")
                                if name and name not in product_names:
                                    product_names.append(name)
                                    logger.info(f"🔍 Extracted recommendation product {i+1}: {name}")
                    else:
                        logger.warning(f"⚠️ No products found in recommendation dict. Available keys: {list(recommend_data.keys())}")
                                
            logger.info(f"🔍 Final extracted product names: {product_names}")
                            
        except Exception as e:
            logger.error(f"❌ Error extracting product names: {e}")
        
        return product_names  # No need to remove duplicates since we check above

    def _classify_intent_with_llm(self, user_input: str) -> str:
        """Use LLM to classify user intent intelligently"""
        try:
            # Get prompt template from prompt manager
            prompt_template = prompt_manager.get_prompt(PromptType.INTENT_CLASSIFICATION)
            if not prompt_template:
                logger.error("❌ Intent classification prompt not found")
                return None
            
            # Format prompt with user input
            intent_prompt = prompt_template.format(user_input=user_input)
            
            response = self.llm.invoke([HumanMessage(content=intent_prompt)])
            intent = response.content.strip().lower()

            # Validate intent
            valid_intents = ["greeting", "search", "compare", "recommend", "review", "direct"]
            if intent in valid_intents:
                logger.info(f"🎯 LLM classified intent: {intent}")
                return intent
            else:
                logger.warning(f"⚠️ LLM returned invalid intent: {intent}")
                return None

        except Exception as e:
            logger.error(f"❌ LLM intent classification failed: {e}")
            return None

    def _classify_intent_with_rules(self, user_input: str) -> str:
        """Fallback rule-based intent classification"""
        try:
            # Greeting detection
            if any(word in user_input for word in ["xin chào", "hello", "chào", "hi", "cảm ơn", "thank"]):
                return "greeting"
            # Comparison intent
            elif any(word in user_input for word in ["so sánh", "compare", "khác nhau", "vs", "versus"]):
                return "compare"
            # Recommendation intent
            elif any(word in user_input for word in ["gợi ý", "recommend", "nên mua", "phù hợp", "tư vấn"]):
                return "recommend"
            # Search intent - Enhanced to catch product-specific queries
            elif any(word in user_input for word in [
                "tìm", "search", "laptop", "smartphone", "điện thoại", "macbook", "dell", "hp", "asus",
                "iphone", "samsung", "xiaomi", "oppo", "vivo", "cấu hình", "thông số", "giá", "specs",
                "inspiron", "thinkpad", "pavilion", "vivobook", "galaxy", "redmi", "như thế nào", "ra sao"
            ]):
                return "search"
            # Direct response for simple queries
            else:
                return "direct"

        except Exception as e:
            logger.error(f"❌ Rule-based intent classification failed: {e}")
            return "direct"

    def _analyze_intent(self, state: AgentState) -> AgentState:
        """LLM-powered intent analysis with context awareness"""
        user_input = state["user_input"]

        try:
            # Check for context references first
            context_intent = self._detect_context_references(user_input, state)
            if context_intent:
                state["intent"] = context_intent["intent"]
                state["current_step"] = context_intent["intent"]
                
                # Store context products for use in tools
                if "products" in context_intent:
                    state["context_products"] = context_intent["products"]
                    logger.info(f"🔗 Storing context products for tools: {context_intent['products']}")
                
                # Add context-aware reasoning
                reasoning_step = {
                    "step": len(state.get("reasoning_steps", [])) + 1,
                    "action": "analyze_intent_with_context",
                    "thought": f"Phát hiện tham chiếu ngữ cảnh: '{user_input[:50]}...' -> {context_intent['intent']} (từ: {context_intent['reason']})",
                    "result": context_intent["intent"],
                    "context_reference": context_intent["reason"],
                    "context_products": context_intent.get("products", [])
                }
                if "reasoning_steps" not in state:
                    state["reasoning_steps"] = []
                state["reasoning_steps"].append(reasoning_step)
                
                logger.info(f"🎯 Context-aware intent: {context_intent['intent']} (reason: {context_intent['reason']})")
                return state

            # Use LLM for intelligent intent classification
            intent = self._classify_intent_with_llm(user_input)
            classification_method = "LLM"

            # Fallback to rule-based if LLM fails
            if not intent:
                intent = self._classify_intent_with_rules(user_input.lower())
                classification_method = "Rules"

            state["intent"] = intent
            state["current_step"] = intent

            # Add reasoning step with classification method info
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "analyze_intent",
                "thought": f"Phân tích ý định người dùng ({classification_method}): '{user_input[:50]}...' -> {intent}",
                "result": intent,
                "method": classification_method
            }
            if "reasoning_steps" not in state:
                state["reasoning_steps"] = []
            state["reasoning_steps"].append(reasoning_step)

            logger.info(f"🎯 Intent analyzed ({classification_method}): {intent}")

        except Exception as e:
            logger.error(f"❌ Intent analysis error: {e}")
            state["intent"] = "error"
            state["current_step"] = "error"
            state["error_count"] = state.get("error_count", 0) + 1

        return state

    def _detect_context_references(self, user_input: str, state: AgentState) -> Optional[Dict[str, str]]:
        """Detect if user input references previous conversation context"""
        try:
            user_lower = user_input.lower()
            
            # Enhanced context reference patterns
            context_reference_patterns = [
                "sản phẩm đó", "sản phẩm này", "của nó", "của chúng", "chúng",
                "những sản phẩm", "các sản phẩm", "vừa tìm", "trước đó", "đã tìm",
                "nó", "chúng nó", "cái đó", "cái này", "2 cái", "hai cái"
            ]
            
            # Check if user is referencing previous context
            has_context_reference = any(pattern in user_lower for pattern in context_reference_patterns)
            
            logger.info(f"🔍 Detecting context references in user input: '{user_lower}'")
            logger.info(f"🔍 Has context reference: {has_context_reference}")
            
            # Check for comparison references with previous products
            comparison_patterns = [
                "so sánh", "compare", "khác nhau", "vs", "versus", "khác gì",
                "2 sản phẩm", "hai sản phẩm", "cả hai", "2 cái", "hai cái", "2 laptop", "hai laptop",
                "chúng", "những sản phẩm", "các sản phẩm", "vừa tìm", "trước đó", "đã tìm"
            ]
            
            if any(pattern in user_lower for pattern in comparison_patterns):
                # Check if we have previous products to reference
                previous_products = state.get("previous_products", [])
                logger.info(f"🔍 Context check - previous_products: {previous_products}")
                
                if previous_products and len(previous_products) >= 2:
                    return {
                        "intent": "compare",
                        "reason": f"Tham chiếu so sánh từ sản phẩm trước: {', '.join(previous_products)}",
                        "products": previous_products  # Sử dụng tất cả sản phẩm có sẵn
                    }
                elif previous_products and len(previous_products) == 1:
                    # User wants to compare with the previous product
                    return {
                        "intent": "compare", 
                        "reason": f"So sánh với sản phẩm trước: {previous_products[0]}",
                        "products": [previous_products[0]]
                    }
            
            # Check for review references
            review_patterns = [
                "review", "đánh giá", "nhận xét", "ý kiến",
                "chúng có tốt không", "có đáng mua", "người dùng nói gì",
                "sản phẩm đó", "sản phẩm này", "của nó", "của chúng"
            ]
            
            if any(pattern in user_lower for pattern in review_patterns):
                previous_products = state.get("previous_products", [])
                if previous_products:
                    return {
                        "intent": "review",
                        "reason": f"Xem review cho sản phẩm: {', '.join(previous_products)}",
                        "products": previous_products  # Add products for context
                    }
            
            # Check for follow-up recommendations
            recommend_patterns = [
                "gợi ý thêm", "còn sản phẩm nào", "tương tự", "khác",
                "thay thế", "lựa chọn khác", "có gì tốt hơn"
            ]
            
            if any(pattern in user_lower for pattern in recommend_patterns):
                context_refs = state.get("context_references", {})
                if context_refs.get("last_intent") in ["search", "recommend"]:
                    return {
                        "intent": "recommend",
                        "reason": "Tìm gợi ý thêm dựa trên yêu cầu trước"
                    }
            
            # Enhanced: Check for generic context references without specific action
            if has_context_reference and not any([
                any(pattern in user_lower for pattern in comparison_patterns),
                any(pattern in user_lower for pattern in review_patterns),
                any(pattern in user_lower for pattern in recommend_patterns)
            ]):
                # This is a generic reference, need to determine intent from context
                previous_products = state.get("previous_products", [])
                if previous_products:
                    # Try to determine intent from the rest of the query
                    if any(word in user_lower for word in ["review", "đánh giá", "nhận xét", "ý kiến"]):
                        return {
                            "intent": "review",
                            "reason": f"Generic context reference + review intent: {', '.join(previous_products)}",
                            "products": previous_products
                        }
                    elif any(word in user_lower for word in ["so sánh", "compare", "khác"]):
                        return {
                            "intent": "compare",
                            "reason": f"Generic context reference + compare intent: {', '.join(previous_products)}",
                            "products": previous_products  # Sử dụng tất cả sản phẩm có sẵn
                        }
                    else:
                        # Default to search/info about the products
                        return {
                            "intent": "search",
                            "reason": f"Generic context reference: {', '.join(previous_products)}",
                            "products": previous_products
                        }
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error detecting context references: {e}")
            return None
    
    def _route_intent(self, state: AgentState) -> str:
        """Enhanced routing with error handling"""
        return state.get("current_step", "error")
    
    def _handle_greeting(self, state: AgentState) -> AgentState:
        """Handle greeting messages"""
        try:
            greeting_response = """Xin chào! 👋 Tôi là AI Product Advisor - trợ lý AI chuyên tư vấn sản phẩm điện tử.

Tôi có thể giúp bạn:
🔍 Tìm kiếm các sản phẩm điện tử thông minh
⚖️ So sánh sản phẩm chi tiết
💡 Đưa ra gợi ý dựa trên nhu cầu
💰 Tư vấn theo ngân sách

Bạn đang tìm sản phẩm gì hôm nay?"""
            
            state["final_response"] = greeting_response
            state["tools_used"].append("handle_greeting")
            
            # Add reasoning step
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "handle_greeting",
                "thought": "Người dùng chào hỏi, tôi sẽ trả lời thân thiện và giới thiệu dịch vụ",
                "result": "greeting_completed"
            }
            state["reasoning_steps"].append(reasoning_step)
            
            logger.info("✅ Greeting handled")
            
        except Exception as e:
            logger.error(f"❌ Greeting handling failed: {e}")
            state["final_response"] = "Xin chào! Tôi có thể giúp gì cho bạn?"
            state["error_count"] = state.get("error_count", 0) + 1
        
        return state
    
    def _extract_search_params(self, user_input: str) -> Dict[str, Any]:
        """Extract search parameters from user input using LLM"""
        try:
            # Get prompt template from prompt manager
            prompt_template = prompt_manager.get_prompt(PromptType.SEARCH_EXTRACTION)
            if not prompt_template:
                logger.error("❌ Search extraction prompt not found")
                return self._fallback_search_params(user_input)
            
            # Format prompt with user input
            extract_prompt = prompt_template.format(user_input=user_input)
            
            response = self.llm.invoke([HumanMessage(content=extract_prompt)])
            params = json.loads(response.content.strip())
            logger.info(f"🎯 Extracted search params: {params}")
            return params
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract search params: {e}")
            return self._fallback_search_params(user_input)
    
    def _fallback_search_params(self, user_input: str) -> Dict[str, Any]:
        """Fallback method to extract basic search parameters using regex"""
        try:
            # Fallback: try to extract basic info with regex
            fallback_metadata = {
                "category": None,
                "brand": None,
                "price_min": None,
                "price_max": None,
                "max_results": 3,
                "include_reviews": False
            }
            
            # Simple category detection
            if any(word in user_input.lower() for word in ["laptop", "macbook"]):
                fallback_metadata["category"] = "laptop"
            elif any(word in user_input.lower() for word in ["điện thoại", "smartphone", "iphone"]):
                fallback_metadata["category"] = "smartphone"
            
            # Simple brand detection
            brands = ["apple", "samsung", "dell", "hp", "asus", "xiaomi", "oppo", "vivo", "lenovo", "acer", "sony", "huawei"]
            for brand in brands:
                if brand in user_input.lower():
                    fallback_metadata["brand"] = brand
                    break
            
            # Extract max_results (số lượng sản phẩm)
            quantity_patterns = [
                r'tìm (\d+)',
                r'cho tôi (\d+)',
                r'(\d+) sản phẩm',
                r'(\d+) chiếc',
                r'(\d+) laptop',
                r'(\d+) điện thoại'
            ]
            for pattern in quantity_patterns:
                match = re.search(pattern, user_input.lower())
                if match:
                    quantity = int(match.group(1))
                    if 1 <= quantity <= 10:
                        fallback_metadata["max_results"] = quantity
                    break
            
            # Handle special cases for quantity
            if any(word in user_input.lower() for word in ["một vài", "mấy"]):
                fallback_metadata["max_results"] = 4
            elif any(word in user_input.lower() for word in ["nhiều", "tất cả"]):
                fallback_metadata["max_results"] = 10

            # Simple price detection (basic regex)
            price_patterns = [
                r'dưới (\d+) triệu',
                r'trên (\d+) triệu', 
                r'từ (\d+)-(\d+) triệu',
                r'khoảng (\d+)-(\d+) triệu',
                r'khoảng (\d+) triệu'
            ]
            for pattern in price_patterns:
                match = re.search(pattern, user_input.lower())
                if match:
                    if 'dưới' in pattern:
                        fallback_metadata["price_max"] = float(match.group(1)) * 1000000
                    elif 'trên' in pattern:
                        fallback_metadata["price_min"] = float(match.group(1)) * 1000000
                    elif 'từ' in pattern and len(match.groups()) == 2:
                        fallback_metadata["price_min"] = float(match.group(1)) * 1000000
                        fallback_metadata["price_max"] = float(match.group(2)) * 1000000
                    elif 'khoảng' in pattern and len(match.groups()) == 2:
                        fallback_metadata["price_min"] = float(match.group(1)) * 1000000
                        fallback_metadata["price_max"] = float(match.group(2)) * 1000000
                    elif 'khoảng' in pattern and len(match.groups()) == 1:
                        price = float(match.group(1)) * 1000000
                        fallback_metadata["price_min"] = price * 0.8
                        fallback_metadata["price_max"] = price * 1.2
                    break
                    
            return {
                "query": user_input,
                "metadata": fallback_metadata
            }
        except Exception as e:
            logger.error(f"❌ Fallback search params extraction failed: {e}")
            return {
                "query": user_input,
                "metadata": {
                    "category": None,
                    "brand": None,
                    "price_min": None,
                    "price_max": None,
                    "max_results": 3,
                    "include_reviews": False
                }
            }

    def _search_products(self, state: AgentState) -> AgentState:
        """Enhanced product search with intelligent parameter extraction"""
        try:
            search_tool = self.tool_manager.get_tool("search")
            if not search_tool:
                raise Exception("Search tool not available")

            # Extract structured parameters from user input
            search_params = self._extract_search_params(state["user_input"])
            
            # Create JSON input for the tool
            search_input = json.dumps(search_params, ensure_ascii=False)

            result = search_tool.run(search_input)
            state["search_results"] = result
            state["tools_used"].append("search_products")
            
            # Add reasoning step
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "search_products",
                "thought": f"Tìm kiếm sản phẩm với params: {search_params}",
                "action_input": search_input,
                "observation": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            }
            state["reasoning_steps"].append(reasoning_step)
            
            logger.info("✅ Search completed with structured input")
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            state["search_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1
        
        return state

    def _extract_compare_params(self, user_input: str) -> Dict[str, Any]:
        """Extract comparison parameters from user input using LLM"""
        try:
            # Get prompt template from prompt manager
            prompt_template = prompt_manager.get_prompt(PromptType.COMPARE_EXTRACTION)
            if not prompt_template:
                logger.error("❌ Compare extraction prompt not found")
                return self._fallback_compare_params(user_input)
            
            # Format prompt with user input
            extract_prompt = prompt_template.format(user_input=user_input)
            
            response = self.llm.invoke([HumanMessage(content=extract_prompt)])
            params = json.loads(response.content.strip())
            logger.info(f"🎯 Extracted compare params: {params}")
            return params
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract compare params: {e}")
            return self._fallback_compare_params(user_input)

    def _compare_products(self, state: AgentState) -> AgentState:
        """Enhanced product comparison with context awareness"""
        try:
            compare_tool = self.tool_manager.get_tool("compare")
            if not compare_tool:
                raise Exception("Compare tool not available")

            # Check for context products first
            compare_params = {}
            if state.get("context_products"):
                # Use context products directly
                context_products = state["context_products"]
                logger.info(f"🔗 Using context products for comparison: {context_products}")
                
                compare_params = {
                    "product_names": context_products,
                    "comparison_aspects": ["giá", "hiệu năng", "thiết kế", "camera"],
                    "include_reviews": True
                }
            else:
                # Extract structured parameters from user input
                compare_params = self._extract_compare_params(state["user_input"])
                
                # Enhance with context if needed
                if len(compare_params.get("product_names", [])) < 2:
                    # Try to use previous products from context
                    previous_products = state.get("previous_products", [])
                    if len(previous_products) >= 2:
                        compare_params["product_names"] = previous_products  # Sử dụng tất cả sản phẩm có sẵn
                        logger.info(f"🔗 Using previous products for comparison: {previous_products}")
                    elif len(previous_products) == 1:
                        # Try to extract one more product from current input
                        current_products = compare_params.get("product_names", [])
                        if current_products:
                            compare_params["product_names"] = [previous_products[0], current_products[0]]
                            logger.info(f"🔗 Comparing previous product {previous_products[0]} with {current_products[0]}")
            
            # Create JSON input for the tool
            compare_input = json.dumps({
                "product_ids": compare_params["product_names"],  # Tool will search by name
                "comparison_aspects": compare_params["comparison_aspects"],
                "include_reviews": compare_params["include_reviews"]
            }, ensure_ascii=False)

            result = compare_tool.run(compare_input)
            state["comparison_results"] = result
            state["tools_used"].append("compare_products")

            # Add reasoning step
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "compare_products",
                "thought": f"So sánh sản phẩm với params: {compare_params}",
                "action_input": compare_input,
                "observation": str(result)[:100] + "..." if len(str(result)) > 100 else str(result),
                "used_context_products": bool(state.get("context_products"))
            }
            state["reasoning_steps"].append(reasoning_step)

            logger.info("✅ Comparison completed with context awareness")

        except Exception as e:
            logger.error(f"❌ Comparison failed: {e}")
            state["comparison_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1

        return state

    def _extract_recommend_params(self, user_input: str) -> Dict[str, Any]:
        """Extract recommendation parameters from user input using LLM"""
        try:
            # Get prompt template from prompt manager
            prompt_template = prompt_manager.get_prompt(PromptType.RECOMMEND_EXTRACTION)
            if not prompt_template:
                logger.error("❌ Recommend extraction prompt not found")
                return self._fallback_recommend_params(user_input)
            
            # Format prompt with user input
            extract_prompt = prompt_template.format(user_input=user_input)
            
            response = self.llm.invoke([HumanMessage(content=extract_prompt)])
            params = json.loads(response.content.strip())
            logger.info(f"🎯 Extracted recommend params: {params}")
            return params
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract recommend params: {e}")
            return self._fallback_recommend_params(user_input)
            params = json.loads(response.content.strip())
            logger.info(f"🎯 Extracted recommend params: {params}")
            return params
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract recommend params: {e}")
            return {
                "user_needs": user_input,
                "metadata": {
                    "category": None,
                    "brand": None,
                    "budget_min": None,
                    "budget_max": None,
                    "priority_features": [],
                    "usage_purpose": None,
                    "num_recommendations": 3,
                    "rating_min": None,
                    "must_have_features": []
                }
            }

    def _extract_review_params(self, user_input: str) -> Dict[str, Any]:
        """Extract review parameters from user input"""
        try:
            # Simple extraction for review - just need product name
            import re
            
            # Initialize params
            params = {
                "product_name": "",
                "limit": 5,
                "sort_by": "newest"
            }
            
            # Extract product name from various patterns
            # Pattern 1: "review về [product]", "reviews [product]"
            patterns = [
                r"reviews?\s+(?:về\s+)?(.+?)(?:\s*$|\s+là|\s+như|\s+có)",
                r"đánh giá\s+(?:về\s+)?(.+?)(?:\s*$|\s+là|\s+như|\s+có)",
                r"nhận xét\s+(?:về\s+)?(.+?)(?:\s*$|\s+là|\s+như|\s+có)",
                r"ý kiến\s+(?:về\s+)?(.+?)(?:\s*$|\s+là|\s+như|\s+có)",
                r"(?:cho\s+tôi\s+)?xem\s+reviews?\s+(?:về\s+)?(.+?)(?:\s*$|\s+là|\s+như|\s+có)",
                r"(.+?)\s+(?:reviews?|đánh giá|nhận xét|ý kiến)",
                # Fallback: take everything after common phrases
                r"(?:reviews?\s+|đánh giá\s+|nhận xét\s+|ý kiến\s+|xem\s+)(.+)"
            ]
            
            product_name = ""
            for pattern in patterns:
                match = re.search(pattern, user_input.lower().strip())
                if match:
                    product_name = match.group(1).strip()
                    break
            
            # Clean product name
            if product_name:
                # Remove common words
                stop_words = ["về", "của", "cho", "là", "như", "có", "thế", "nào", "gì"]
                words = product_name.split()
                cleaned_words = [word for word in words if word not in stop_words]
                product_name = " ".join(cleaned_words)
                
                params["product_name"] = product_name
            else:
                # Fallback: use the whole input cleaned
                params["product_name"] = user_input.strip()
            
            logger.info(f"🎯 Extracted review params: {params}")
            return params
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract review params: {e}")
            return {
                "product_name": user_input.strip(),
                "limit": 5,
                "sort_by": "newest"
            }

    def _recommend_products(self, state: AgentState) -> AgentState:
        """Enhanced product recommendation with intelligent parameter extraction"""
        try:
            recommend_tool = self.tool_manager.get_tool("recommend")
            if not recommend_tool:
                raise Exception("Recommend tool not available")

            # Extract structured parameters from user input
            recommend_params = self._extract_recommend_params(state["user_input"])
            
            # Create JSON input for the tool
            recommend_input = json.dumps(recommend_params, ensure_ascii=False)

            result = recommend_tool.run(recommend_input)
            state["recommendation_results"] = result
            state["tools_used"].append("recommend_products")
            
            # Debug logging for recommendation results
            logger.info(f"🔍 Recommendation tool result type: {type(result)}")
            logger.info(f"🔍 Recommendation tool result preview: {str(result)[:200]}...")

            # Add reasoning step
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "recommend_products",
                "thought": f"Gợi ý sản phẩm với params: {recommend_params}",
                "action_input": recommend_input,
                "observation": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            }
            state["reasoning_steps"].append(reasoning_step)

            logger.info("✅ Recommendation completed with structured input")

        except Exception as e:
            logger.error(f"❌ Recommendation failed: {e}")
            state["recommendation_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1

        return state

    def _get_reviews(self, state: AgentState) -> AgentState:
        """Get product reviews with context awareness and intelligent parameter extraction"""
        try:
            review_tool = self.tool_manager.get_tool("review")
            if not review_tool:
                raise Exception("Review tool not available")

            # Check for context products first (from context detection)
            review_params = {}
            target_product = None
            
            if state.get("context_products"):
                # Use the first context product for reviews
                context_products = state["context_products"]
                target_product = context_products[0] if context_products else None
                logger.info(f"🔗 Using context product for reviews: {target_product}")
                
                review_params = {
                    "product_name": target_product,
                    "limit": 5,
                    "sort_by": "newest"
                }
            elif state.get("previous_products"):
                # Use the first previous product if no context products
                previous_products = state["previous_products"]
                target_product = previous_products[0] if previous_products else None
                logger.info(f"🔗 Using previous product for reviews: {target_product}")
                
                review_params = {
                    "product_name": target_product,
                    "limit": 5,
                    "sort_by": "newest"
                }
            else:
                # Extract product name from user input as fallback
                review_params = self._extract_review_params(state["user_input"])
                target_product = review_params.get("product_name", "unknown")
                logger.info(f"📝 Extracted product from user input: {target_product}")
            
            # Use the review tool directly
            result = review_tool._run(**review_params)
            state["review_results"] = result
            state["tools_used"].append("get_product_reviews")
            
            # Add reasoning step with context information
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "get_product_reviews",
                "thought": f"Lấy reviews cho sản phẩm: {target_product}",
                "action_input": str(review_params),
                "observation": str(result)[:100] + "..." if len(str(result)) > 100 else str(result),
                "context_source": "context_products" if state.get("context_products") else (
                    "previous_products" if state.get("previous_products") else "user_input"
                )
            }
            state["reasoning_steps"].append(reasoning_step)

            logger.info("✅ Reviews retrieved successfully")

        except Exception as e:
            logger.error(f"❌ Get reviews failed: {e}")
            state["review_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1

        return state

    def _generate_response(self, state: AgentState) -> AgentState:
        """Enhanced response generation with ReAct-style RAG"""
        try:
            # Skip if response already generated (e.g., greeting)
            if state.get("final_response"):
                return state

            # Collect context from all results
            context_parts = []

            # Check search results
            if state.get("search_results"):
                search_result = state["search_results"]
                if isinstance(search_result, dict) and not search_result.get("error"):
                    context_parts.append(f"Search results: {search_result}")
                elif isinstance(search_result, str):
                    context_parts.append(f"Search results: {search_result}")

            # Check comparison results
            if state.get("comparison_results"):
                compare_result = state["comparison_results"]
                if isinstance(compare_result, dict) and not compare_result.get("error"):
                    context_parts.append(f"Comparison: {compare_result}")
                elif isinstance(compare_result, str):
                    context_parts.append(f"Comparison: {compare_result}")

            # Check recommendation results
            if state.get("recommendation_results"):
                recommend_result = state["recommendation_results"]
                if isinstance(recommend_result, dict) and not recommend_result.get("error"):
                    context_parts.append(f"Recommendations: {recommend_result}")
                elif isinstance(recommend_result, str):
                    context_parts.append(f"Recommendations: {recommend_result}")

            # Check review results
            if state.get("review_results"):
                review_result = state["review_results"]
                if isinstance(review_result, dict) and not review_result.get("error"):
                    context_parts.append(f"Reviews: {review_result}")
                elif isinstance(review_result, str):
                    context_parts.append(f"Reviews: {review_result}")


            # Extract raw results safely
            search_data = ""
            compare_data = ""
            recommend_data = ""
            review_data = ""
            
            if state.get("search_results"):
                search_data = str(state["search_results"]) if state["search_results"] else ""
            if state.get("comparison_results"):
                compare_data = str(state["comparison_results"]) if state["comparison_results"] else ""
            if state.get("recommendation_results"):
                recommend_data = str(state["recommendation_results"]) if state["recommendation_results"] else ""
            if state.get("review_results"):
                review_data = str(state["review_results"]) if state["review_results"] else ""

            # Create conversation history for context
            conversation_history_text = ""
            conv_history = state.get("conversation_history", [])
            if conv_history:
                history_parts = []
                for i, conv in enumerate(conv_history[-3:], 1):  # Last 3 conversations
                    history_parts.append(f"Lần {i}: User: {conv.get('user', '')}\nAI: {conv.get('assistant', '')}")
                conversation_history_text = "\n\n".join(history_parts)

            # Create simplified input for RAG tool
            rag_input_data = {
                "user_query": state["user_input"],
                "intent": state.get("intent", "general"),
                "context": "\n".join(context_parts) if context_parts else "",
                "conversation_history": conversation_history_text,
                "tools_used": state.get("tools_used", []),
                "search_results": search_data,
                "comparison_results": compare_data,
                "recommendation_results": recommend_data,
                "review_results": review_data,
                # Add context references for better continuity
                "previous_products": state.get("previous_products", []),
                "context_references": state.get("context_references", {})
            }
            
            # Call generation tool with dictionary input (not JSON string)
            result = generation_tool.run(rag_input_data)

            # Parse RAG tool result safely
            if isinstance(result, dict):
                if result.get("success"):
                    state["final_response"] = result.get("response", "Không thể tạo phản hồi")
                else:
                    state["final_response"] = result.get("response", str(result))
            elif isinstance(result, str):
                # Try to parse JSON response
                try:
                    result_data = json.loads(result)
                    if isinstance(result_data, dict):
                        state["final_response"] = result_data.get("response", result)
                    else:
                        state["final_response"] = result
                except json.JSONDecodeError:
                    state["final_response"] = result
            else:
                state["final_response"] = str(result)

            # Add reasoning step
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "answer_with_context",
                "thought": f"Sử dụng Natural RAG với intent '{state.get('intent')}' từ {len(state.get('tools_used', []))} tools đã thực hiện",
                "action_input": json.dumps(rag_input_data, ensure_ascii=False),
                "observation": state["final_response"][:100] + "..." if len(state["final_response"]) > 100 else state["final_response"]
            }
            state["reasoning_steps"].append(reasoning_step)

            state["tools_used"].append("answer_with_context")
            state["context_data"] = "\n".join(context_parts) if context_parts else ""

            # Update conversation history
            current_conversation = {
                "user": state["user_input"],
                "assistant": state["final_response"],
                "timestamp": str(uuid.uuid4()),  # Simple timestamp substitute
                "intent": state.get("intent", "unknown"),
                "tools_used": state.get("tools_used", [])
            }
            
            if "conversation_history" not in state:
                state["conversation_history"] = []
            state["conversation_history"].append(current_conversation)
            
            # Keep only last 5 conversations to prevent memory bloat
            if len(state["conversation_history"]) > 5:
                state["conversation_history"] = state["conversation_history"][-5:]

            logger.info("✅ Response generated with conversation history updated")

        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            state["final_response"] = self._get_error_response(str(e))
            state["error_count"] = state.get("error_count", 0) + 1

        return state

    def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors gracefully"""
        error_msg = "Xin lỗi, tôi gặp khó khăn trong việc xử lý yêu cầu của bạn. Bạn có thể thử lại hoặc diễn đạt khác không?"
        state["final_response"] = error_msg
        logger.error(f"❌ Error handled for session: {state.get('session_id', 'unknown')}")
        return state

    def _get_error_response(self, error: str) -> str:
        """Get user-friendly error response"""
        if "setup_required" in error or "NOT_FOUND" in error:
            return "❌ **Cơ sở dữ liệu chưa được thiết lập**\n\n🔧 **Cách khắc phục:**\n1. Chạy lệnh: `python scripts/insert_sample_data.py`\n2. Đảm bảo Pinecone index 'ecommerce-products' đã được tạo\n\n💡 Sau khi thiết lập xong, hãy thử lại câu hỏi của bạn!"
        else:
            return f"Xin lỗi, có lỗi xảy ra: {error}. Bạn có thể thử lại không?"

    def chat(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced chat method with native LangGraph memory management and context continuity"""
        try:
            if not session_id:
                session_id = str(uuid.uuid4())

            logger.info(f"🗣️ Processing user input: {user_input[:100]}... (session: {session_id[:8]})")

            # Retrieve conversation history from memory
            memory_context = self._get_conversation_history(session_id)

            # Initialize enhanced state with memory context
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "user_input": user_input,
                "session_id": session_id,
                "current_step": "",
                "intent": "",
                "tools_used": [],
                "search_results": None,
                "comparison_results": None,
                "recommendation_results": None,
                "review_results": None,
                "context_data": None,
                "final_response": None,
                "iteration_count": 0,
                "error_count": 0,
                "reasoning_steps": [],
                # Memory context from previous conversations
                "conversation_history": memory_context.get("conversation_history", []),
                "previous_search_results": memory_context.get("previous_search_results"),
                "previous_products": memory_context.get("previous_products", []),
                "context_references": memory_context.get("context_references", {}),
                "context_products": []  # For storing products from context detection
            }

            # Create thread config for this session
            thread_config = {"configurable": {"thread_id": session_id}}

            # Run the graph with memory support
            final_state = self.graph.invoke(initial_state, config=thread_config)

            # Extract intermediate steps for compatibility
            intermediate_steps = []
            for step in final_state.get("reasoning_steps", []):
                if step.get("action") and step.get("observation"):
                    # Create ReAct-style intermediate step
                    action_obj = type('Action', (), {
                        'tool': step["action"],
                        'tool_input': step.get("action_input", "")
                    })()
                    intermediate_steps.append((action_obj, step["observation"]))

            return {
                "response": final_state.get("final_response", "Không thể tạo phản hồi"),
                "tools_used": final_state.get("tools_used", []),
                "reasoning_steps": final_state.get("reasoning_steps", []),
                "intermediate_steps": intermediate_steps,
                "session_id": session_id,
                "success": final_state.get("error_count", 0) == 0,
                "agent_type": "langgraph",
                "intent": final_state.get("intent", "unknown"),
                # Additional context info for debugging
                "context_info": {
                    "has_previous_context": len(memory_context.get("conversation_history", [])) > 0,
                    "previous_products": memory_context.get("previous_products", []),
                    "context_references_used": bool(memory_context.get("context_references"))
                }
            }

        except Exception as e:
            logger.error(f"❌ LangGraph chat error: {e}")
            return {
                "response": self._get_error_response(str(e)),
                "tools_used": [],
                "reasoning_steps": [],
                "intermediate_steps": [],
                "session_id": session_id,
                "success": False,
                "error": str(e),
                "agent_type": "langgraph"
            }

    def _fallback_compare_params(self, user_input: str) -> Dict[str, Any]:
        """Fallback method to extract basic comparison parameters using regex"""
        try:
            # Fallback: try to extract product names from user input
            # Look for vs, so sánh, khác patterns
            vs_patterns = [r'(.+?)\s+vs\s+(.+)', r'so sánh\s+(.+?)\s+và\s+(.+)', r'(.+?)\s+khác\s+gì\s+(.+)']
            product_names = []
            
            for pattern in vs_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    product_names = [match.group(1).strip(), match.group(2).strip()]
                    break
            
            # If no pattern found, try to extract from common product names
            if not product_names:
                # Extract known product patterns
                product_patterns = [
                    r'(iPhone \d+[^,\s]*)',
                    r'(Samsung[^,\s]+)',
                    r'(Dell[^,\s]+)', 
                    r'(HP[^,\s]+)',
                    r'(MacBook[^,\s]*)',
                    r'(Asus[^,\s]+)',
                    r'(Lenovo[^,\s]+)'
                ]
                
                for pattern in product_patterns:
                    matches = re.findall(pattern, user_input, re.IGNORECASE)
                    product_names.extend(matches)
                
                # Remove duplicates
                product_names = list(set(product_names))
            
            return {
                "product_names": product_names if len(product_names) >= 2 else [user_input],
                "comparison_aspects": ["giá", "hiệu năng", "thiết kế", "camera"],
                "include_reviews": True
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback compare params extraction failed: {e}")
            return {
                "product_names": [user_input],
                "comparison_aspects": ["giá", "hiệu năng", "thiết kế", "camera"],
                "include_reviews": True
            }

    def _fallback_recommend_params(self, user_input: str) -> Dict[str, Any]:
        """Fallback method to extract basic recommendation parameters using regex"""
        try:
            # Basic metadata extraction
            fallback_metadata = {
                "category": None,
                "brand": None,
                "budget_min": None,
                "budget_max": None,
                "priority_features": [],
                "usage_purpose": None,
                "num_recommendations": 3,
                "rating_min": None,
                "must_have_features": []
            }
            
            # Category detection
            if any(word in user_input.lower() for word in ["laptop", "macbook"]):
                fallback_metadata["category"] = "laptop"
            elif any(word in user_input.lower() for word in ["điện thoại", "smartphone", "iphone"]):
                fallback_metadata["category"] = "smartphone"
            
            # Brand detection
            brands = ["apple", "samsung", "dell", "hp", "asus", "xiaomi", "oppo", "vivo", "lenovo", "acer"]
            for brand in brands:
                if brand in user_input.lower():
                    fallback_metadata["brand"] = brand
                    break
            
            # Usage purpose detection
            if any(word in user_input.lower() for word in ["gaming", "game", "chơi game"]):
                fallback_metadata["usage_purpose"] = "gaming"
                fallback_metadata["priority_features"] = ["performance", "gaming"]
            elif any(word in user_input.lower() for word in ["sinh viên", "học tập", "học"]):
                fallback_metadata["usage_purpose"] = "study"
                fallback_metadata["priority_features"] = ["portability", "battery_life"]
            elif any(word in user_input.lower() for word in ["lập trình", "programming", "code", "dev"]):
                fallback_metadata["usage_purpose"] = "work"
                fallback_metadata["priority_features"] = ["performance", "display_quality"]
            elif any(word in user_input.lower() for word in ["chụp ảnh", "camera", "photography"]):
                fallback_metadata["usage_purpose"] = "photography"
                fallback_metadata["priority_features"] = ["camera"]
            
            # Budget detection
            price_patterns = [
                r'dưới (\d+) triệu',
                r'trên (\d+) triệu', 
                r'từ (\d+)-(\d+) triệu',
                r'khoảng (\d+) triệu'
            ]
            for pattern in price_patterns:
                match = re.search(pattern, user_input.lower())
                if match:
                    if 'dưới' in pattern:
                        fallback_metadata["budget_max"] = float(match.group(1)) * 1000000
                    elif 'trên' in pattern:
                        fallback_metadata["budget_min"] = float(match.group(1)) * 1000000
                    elif 'từ' in pattern:
                        fallback_metadata["budget_min"] = float(match.group(1)) * 1000000
                        fallback_metadata["budget_max"] = float(match.group(2)) * 1000000
                    elif 'khoảng' in pattern:
                        price = float(match.group(1)) * 1000000
                        fallback_metadata["budget_min"] = price * 0.8
                        fallback_metadata["budget_max"] = price * 1.2
                    break
            
            # Must have features detection
            if any(word in user_input.lower() for word in ["ssd", "ổ cứng ssd"]):
                fallback_metadata["must_have_features"].append("ssd")
            if any(word in user_input.lower() for word in ["touchscreen", "cảm ứng"]):
                fallback_metadata["must_have_features"].append("touchscreen")
            
            return {
                "user_needs": user_input,
                "metadata": fallback_metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback recommend params extraction failed: {e}")
            return {
                "user_needs": user_input,
                "metadata": {
                    "category": None,
                    "brand": None,
                    "budget_min": None,
                    "budget_max": None,
                    "priority_features": [],
                    "usage_purpose": None,
                    "num_recommendations": 3,
                    "rating_min": None,
                    "must_have_features": []
                }
            }

    def clear_memory(self, session_id: str = "default") -> bool:
        """Clear conversation memory for session using LangGraph native memory"""
        try:
            # In LangGraph with MemorySaver, we can't directly clear individual sessions
            # But we can create a new memory saver instance to effectively clear all sessions
            self.memory_saver = MemorySaver()
            self.graph = self._create_graph()  # Recreate graph with new memory
            logger.info(f"✅ Memory cleared (all sessions reset)")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing memory: {e}")
            return False


# Enhanced Agent Manager for LangGraph
class LangGraphAgentManager:
    """Manages LangGraph agent instances and sessions"""

    def __init__(self):
        self.agent = ProductAdvisorLangGraphAgent()
        logger.info("✅ LangGraphAgentManager initialized")

    def get_agent(self, session_id: str = "default") -> ProductAdvisorLangGraphAgent:
        """Get agent instance (single instance with session management)"""
        return self.agent

    def clear_session(self, session_id: str) -> bool:
        """Clear specific session"""
        return self.agent.clear_memory(session_id)

    def clear_all_sessions(self) -> bool:
        """Clear all sessions by recreating the agent"""
        try:
            # LangGraph MemorySaver doesn't have .memories attribute
            # We recreate the agent to clear all memory
            self.agent = ProductAdvisorLangGraphAgent()
            logger.info("✅ All sessions cleared by recreating agent")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing all sessions: {e}")
            return False

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs - Note: With MemorySaver, session tracking is handled internally"""
        # With native LangGraph memory, sessions are managed internally
        # We can't easily list active sessions, so return empty list
        logger.info("ℹ️ Session tracking handled by LangGraph MemorySaver")
        return []


# Global instances
langgraph_agent_manager = LangGraphAgentManager()

def get_agent_manager() -> LangGraphAgentManager:
    """Get global LangGraph agent manager instance"""
    return langgraph_agent_manager
