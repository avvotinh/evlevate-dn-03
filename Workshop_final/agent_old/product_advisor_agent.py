"""
Main ProductAdvisorAgent class for LangGraph Agent
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from functools import lru_cache

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from src.services.llm_service import llm_service
from src.tools.tool_manager import ToolManager
from src.tools.generation_tool import generation_tool
from src.prompts.prompt_manager import prompt_manager, PromptType
from src.utils.logger import get_logger

from .constants import AgentConstants
from .state import AgentState
from .parameter_extractor import ParameterExtractor
from .memory_manager import MemoryManager

logger = get_logger("product_advisor_agent")


class ProductAdvisorAgent:
    """LangGraph Agent with better architecture and error handling"""
    
    def __init__(self):
        """Initialize agent with improved architecture"""
        self.constants = AgentConstants()
        self.tool_manager = ToolManager()
        self.llm = llm_service.get_llm()
        self.memory_saver = MemorySaver()
        self.parameter_extractor = ParameterExtractor()
        self.memory_manager = MemoryManager()
        
        self.graph = self._create_graph()
        logger.info("✅ LangGraph Agent initialized")
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("handle_greeting", self._handle_greeting)
        workflow.add_node("search_products", self._search_products)
        workflow.add_node("compare_products", self._compare_products)
        workflow.add_node("recommend_products", self._recommend_products)
        workflow.add_node("get_reviews", self._get_reviews)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Define entry point and routing
        workflow.set_entry_point("analyze_intent")
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
        
        # Add edges to end
        workflow.add_edge("handle_greeting", END)
        workflow.add_edge("search_products", "generate_response")
        workflow.add_edge("compare_products", "generate_response")
        workflow.add_edge("recommend_products", "generate_response")
        workflow.add_edge("get_reviews", "generate_response")
        workflow.add_edge("handle_error", END)
        workflow.add_edge("generate_response", END)
        
        return workflow.compile(checkpointer=self.memory_saver)
    
    @lru_cache(maxsize=100)
    def _classify_intent_cached(self, user_input: str) -> str:
        """Cached intent classification for performance"""
        return self._classify_intent_with_llm(user_input)
    
    def _classify_intent_with_llm(self, user_input: str) -> Optional[str]:
        """Use LLM to classify user intent"""
        try:
            prompt_template = prompt_manager.get_prompt(PromptType.INTENT_CLASSIFICATION)
            if not prompt_template:
                return None
            
            intent_prompt = prompt_template.format(user_input=user_input)
            response = self.llm.invoke([HumanMessage(content=intent_prompt)])
            intent = response.content.strip().lower()
            
            if intent in self.constants.VALID_INTENTS:
                logger.info(f"🎯 LLM classified intent: {intent}")
                return intent
            else:
                logger.warning(f"⚠️ Invalid intent from LLM: {intent}")
                return None
                
        except Exception as e:
            logger.error(f"❌ LLM intent classification failed: {e}")
            return None
    
    def _analyze_intent(self, state: AgentState) -> AgentState:
        """Analyze user intent with context awareness"""
        user_input = state["user_input"]
        
        try:
            # Check for context references first
            if context_intent := self._detect_context_references(user_input, state):
                return self._apply_context_intent(state, context_intent, user_input)
            
            # Use cached LLM classification
            intent = self._classify_intent_cached(user_input)
            
            # Fallback to rules if needed
            if not intent:
                intent = self._classify_intent_with_rules(user_input.lower())
                classification_method = "Rules"
            else:
                classification_method = "LLM"
            
            return self._apply_intent(state, intent, user_input, classification_method)
            
        except Exception as e:
            logger.error(f"❌ Intent analysis error: {e}")
            state["intent"] = "error"
            state["current_step"] = "error" 
            state["error_count"] = state.get("error_count", 0) + 1
            return state
    
    def _apply_context_intent(self, state: AgentState, context_intent: Dict, user_input: str) -> AgentState:
        """Apply context-aware intent to state"""
        state["intent"] = context_intent["intent"]
        state["current_step"] = context_intent["intent"]
        
        if "products" in context_intent:
            state["context_products"] = context_intent["products"]
        
        reasoning_step = {
            "step": len(state.get("reasoning_steps", [])) + 1,
            "action": "analyze_intent_with_context",
            "thought": f"Context reference detected: '{user_input[:50]}...' -> {context_intent['intent']}",
            "result": context_intent["intent"],
            "context_reference": context_intent["reason"]
        }
        
        if "reasoning_steps" not in state:
            state["reasoning_steps"] = []
        state["reasoning_steps"].append(reasoning_step)
        
        return state
    
    def _apply_intent(self, state: AgentState, intent: str, user_input: str, method: str) -> AgentState:
        """Apply classified intent to state"""
        state["intent"] = intent
        state["current_step"] = intent
        
        reasoning_step = {
            "step": len(state.get("reasoning_steps", [])) + 1,
            "action": "analyze_intent",
            "thought": f"Intent classification ({method}): '{user_input[:50]}...' -> {intent}",
            "result": intent,
            "method": method
        }
        
        if "reasoning_steps" not in state:
            state["reasoning_steps"] = []
        state["reasoning_steps"].append(reasoning_step)
        
        return state
    
    def _detect_context_references(self, user_input: str, state: AgentState) -> Optional[Dict[str, Any]]:
        """Detect context references in user input"""
        user_lower = user_input.lower()
        
        # Comparison patterns
        comparison_patterns = [
            "so sánh", "compare", "khác nhau", "vs", "versus", "khác gì",
            "2 sản phẩm", "hai sản phẩm", "cả hai", "chúng"
        ]
        
        if any(pattern in user_lower for pattern in comparison_patterns):
            previous_products = state.get("previous_products", [])
            if len(previous_products) >= 2:
                return {
                    "intent": "compare",
                    "reason": f"Reference to previous products: {', '.join(previous_products[:2])}",
                    "products": previous_products[:2]
                }
        
        # Review patterns
        review_patterns = ["review", "đánh giá", "nhận xét", "có tốt không"]
        if any(pattern in user_lower for pattern in review_patterns):
            previous_products = state.get("previous_products", [])
            if previous_products:
                return {
                    "intent": "review", 
                    "reason": f"Review request for: {', '.join(previous_products)}"
                }
        
        return None
    
    def _classify_intent_with_rules(self, user_input: str) -> str:
        """Rule-based intent classification as fallback"""
        if any(word in user_input for word in ["xin chào", "hello", "hi"]):
            return "greeting"
        elif any(word in user_input for word in ["so sánh", "compare", "vs"]):
            return "compare"
        elif any(word in user_input for word in ["gợi ý", "recommend", "tư vấn"]):
            return "recommend"
        elif any(word in user_input for word in ["tìm", "search", "laptop", "smartphone"]):
            return "search"
        elif any(word in user_input for word in ["review", "đánh giá"]):
            return "review"
        else:
            return "direct"
    
    def _route_intent(self, state: AgentState) -> str:
        """Route based on current step"""
        return state.get("current_step", "error")
    
    def _handle_greeting(self, state: AgentState) -> AgentState:
        """Handle greeting with natural conversational response"""
        greeting_response = '''Chào bạn! 👋 Rất vui được gặp bạn hôm nay!

Mình là AI Product Advisor, một trợ lý thông minh chuyên giúp bạn tìm hiểu và lựa chọn các sản phẩm điện tử phù hợp nhất.

Mình có thể hỗ trợ bạn:
- Tìm kiếm sản phẩm theo nhu cầu và ngân sách 🔍
- So sánh chi tiết giữa các sản phẩm để bạn đưa ra quyết định tốt nhất ⚖️
- Đưa ra những gợi ý thông minh dựa trên mục đích sử dụng của bạn 💡
- Tổng hợp đánh giá từ người dùng thực tế 📝

Bạn đang quan tâm đến sản phẩm nào, hoặc có câu hỏi gì mình có thể giúp được không? Cứ thoải mái chia sẻ nhé! 😊'''
        
        state["final_response"] = greeting_response
        state["tools_used"] = state.get("tools_used", []) + ["handle_greeting"]
        
        return state
    
    def _search_products(self, state: AgentState) -> AgentState:
        """Search products with improved parameter extraction"""
        try:
            search_tool = self.tool_manager.get_tool("search")
            if not search_tool:
                raise Exception("Search tool not available")
            
            # Extract parameters using dedicated extractor
            search_params = self.parameter_extractor.extract_search_params(state["user_input"], self.llm)
            search_input = json.dumps(search_params, ensure_ascii=False)
            
            result = search_tool.run(search_input)
            state["search_results"] = result
            state["tools_used"] = state.get("tools_used", []) + ["search_products"]
            
            self._add_reasoning_step(state, "search_products", f"Search with params: {search_params}", result)
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            state["search_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1
        
        return state
    
    def _compare_products(self, state: AgentState) -> AgentState:
        """Compare products with context awareness"""
        try:
            compare_tool = self.tool_manager.get_tool("compare")
            if not compare_tool:
                raise Exception("Compare tool not available")
            
            # Use context products if available
            if context_products := state.get("context_products"):
                compare_params = {
                    "product_names": context_products,
                    "comparison_aspects": ["giá", "hiệu năng", "thiết kế", "camera"],
                    "include_reviews": True
                }
            else:
                compare_params = self.parameter_extractor.extract_compare_params(state["user_input"], self.llm)
            
            compare_input = json.dumps(compare_params, ensure_ascii=False)
            result = compare_tool.run(compare_input)
            
            state["comparison_results"] = result
            state["tools_used"] = state.get("tools_used", []) + ["compare_products"]
            
            self._add_reasoning_step(state, "compare_products", f"Compare with params: {compare_params}", result)
            
        except Exception as e:
            logger.error(f"❌ Comparison failed: {e}")
            state["comparison_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1
        
        return state
    
    def _recommend_products(self, state: AgentState) -> AgentState:
        """Recommend products with intelligent extraction"""
        try:
            recommend_tool = self.tool_manager.get_tool("recommend")
            if not recommend_tool:
                raise Exception("Recommend tool not available")
            
            recommend_params = self.parameter_extractor.extract_recommend_params(state["user_input"], self.llm)
            recommend_input = json.dumps(recommend_params, ensure_ascii=False)
            
            result = recommend_tool.run(recommend_input)
            state["recommendation_results"] = result
            state["tools_used"] = state.get("tools_used", []) + ["recommend_products"]
            
            self._add_reasoning_step(state, "recommend_products", f"Recommend with params: {recommend_params}", result)
            
        except Exception as e:
            logger.error(f"❌ Recommendation failed: {e}")
            state["recommendation_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1
        
        return state
    
    def _get_reviews(self, state: AgentState) -> AgentState:
        """Get product reviews"""
        try:
            review_tool = self.tool_manager.get_tool("review")
            if not review_tool:
                raise Exception("Review tool not available")
            
            # Simple product name extraction for reviews
            product_name = state["user_input"].replace("review", "").replace("đánh giá", "").strip()
            
            result = review_tool._run(product_name=product_name, limit=5, sort_by="newest")
            state["review_results"] = result
            state["tools_used"] = state.get("tools_used", []) + ["get_reviews"]
            
            self._add_reasoning_step(state, "get_reviews", f"Get reviews for: {product_name}", result)
            
        except Exception as e:
            logger.error(f"❌ Get reviews failed: {e}")
            state["review_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate response using collected context"""
        if state.get("final_response"):
            return state
        
        try:
            # Collect context and generate response
            context_data = self._collect_tool_contexts(state)
            rag_input = self._prepare_rag_input(state, context_data)
            response = self._call_generation_tool(rag_input)
            
            state = self._update_state_with_response(state, response, context_data)
            
        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            state["final_response"] = self._get_error_response(str(e))
            state["error_count"] = state.get("error_count", 0) + 1
        
        return state
    
    def _collect_tool_contexts(self, state: AgentState) -> Dict[str, str]:
        """Collect context from all executed tools"""
        context_parts = []
        
        for result_key in ["search_results", "comparison_results", "recommendation_results", "review_results"]:
            if result := state.get(result_key):
                if isinstance(result, dict) and not result.get("error"):
                    context_parts.append(f"{result_key}: {result}")
                elif isinstance(result, str):
                    context_parts.append(f"{result_key}: {result}")
        
        return {
            "context": "\\n".join(context_parts),
            "tools_used": state.get("tools_used", [])
        }
    
    def _prepare_rag_input(self, state: AgentState, context_data: Dict) -> Dict[str, Any]:
        """Prepare input for RAG generation"""
        return {
            "user_query": state["user_input"],
            "intent": state.get("intent", "general"),
            "context": context_data["context"],
            "tools_used": context_data["tools_used"],
            "search_results": str(state.get("search_results", "")),
            "comparison_results": str(state.get("comparison_results", "")),
            "recommendation_results": str(state.get("recommendation_results", "")),
            "review_results": str(state.get("review_results", "")),
            "previous_products": state.get("previous_products", [])
        }
    
    def _call_generation_tool(self, rag_input: Dict[str, Any]) -> Any:
        """Call the generation tool with error handling"""
        try:
            result = generation_tool.run(rag_input)
            return result
        except Exception as e:
            logger.error(f"❌ Generation tool failed: {e}")
            return {"success": False, "response": "Không thể tạo phản hồi"}
    
    def _update_state_with_response(self, state: AgentState, response: Any, context_data: Dict) -> AgentState:
        """Update state with generated response"""
        # Parse response
        if isinstance(response, dict):
            if response.get("success"):
                state["final_response"] = response.get("response", "Không thể tạo phản hồi")
            else:
                state["final_response"] = response.get("response", str(response))
        elif isinstance(response, str):
            try:
                result_data = json.loads(response)
                state["final_response"] = result_data.get("response", response)
            except json.JSONDecodeError:
                state["final_response"] = response
        else:
            state["final_response"] = str(response)
        
        # Update conversation history
        self._update_conversation_history(state)
        
        # Add tools used
        state["tools_used"] = state.get("tools_used", []) + ["answer_with_context"]
        state["context_data"] = context_data["context"]
        
        return state
    
    def _update_conversation_history(self, state: AgentState) -> None:
        """Update conversation history with current exchange"""
        current_conversation = {
            "user": state["user_input"],
            "assistant": state["final_response"],
            "timestamp": str(uuid.uuid4()),
            "intent": state.get("intent", "unknown"),
            "tools_used": state.get("tools_used", [])
        }
        
        if "conversation_history" not in state:
            state["conversation_history"] = []
        
        state["conversation_history"].append(current_conversation)
        
        # Keep only recent conversations
        if len(state["conversation_history"]) > self.constants.MAX_CONVERSATION_HISTORY:
            state["conversation_history"] = state["conversation_history"][-self.constants.MAX_CONVERSATION_HISTORY:]
    
    def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors gracefully"""
        state["final_response"] = "Xin lỗi, tôi gặp khó khăn xử lý yêu cầu. Bạn có thể thử lại không?"
        return state
    
    def _add_reasoning_step(self, state: AgentState, action: str, thought: str, observation: Any) -> None:
        """Add reasoning step to state"""
        reasoning_step = {
            "step": len(state.get("reasoning_steps", [])) + 1,
            "action": action,
            "thought": thought,
            "observation": str(observation)[:100] + "..." if len(str(observation)) > 100 else str(observation)
        }
        
        if "reasoning_steps" not in state:
            state["reasoning_steps"] = []
        state["reasoning_steps"].append(reasoning_step)
    
    def _get_error_response(self, error: str) -> str:
        """Get user-friendly error response"""
        if "setup_required" in error or "NOT_FOUND" in error:
            return "❌ **Database chưa được thiết lập**\\n\\n🔧 Chạy: `python scripts/insert_sample_data.py`"
        else:
            return f"Xin lỗi, có lỗi: {error}. Bạn thử lại được không?"
    
    def chat(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Main chat method with improved error handling"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            logger.info(f"🗣️ Processing: {user_input[:50]}... (session: {session_id[:8]})")
            
            # Get memory context
            memory_context = self._get_conversation_history(session_id)
            
            # Initialize state
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
                # Memory context
                "conversation_history": memory_context.get("conversation_history", []),
                "previous_products": memory_context.get("previous_products", []),
                "context_references": memory_context.get("context_references", {})
            }
            
            # Run graph
            thread_config = {"configurable": {"thread_id": session_id}}
            final_state = self.graph.invoke(initial_state, config=thread_config)
            
            # Extract intermediate steps
            intermediate_steps = []
            for step in final_state.get("reasoning_steps", []):
                if step.get("action") and step.get("observation"):
                    intermediate_steps.append((step["action"], step["observation"]))
            
            return {
                "response": final_state.get("final_response", "Không thể tạo phản hồi"),
                "tools_used": final_state.get("tools_used", []),
                "reasoning_steps": final_state.get("reasoning_steps", []),
                "intermediate_steps": intermediate_steps,
                "session_id": session_id,
                "success": final_state.get("error_count", 0) == 0,
                "intent": final_state.get("intent", "unknown")
            }
            
        except Exception as e:
            logger.error(f"❌ Chat error: {e}")
            return self._create_error_response(str(e), session_id)
    
    def _create_error_response(self, error: str, session_id: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "response": self._get_error_response(error),
            "tools_used": [],
            "reasoning_steps": [],
            "intermediate_steps": [],
            "session_id": session_id,
            "success": False,
            "error": error,
        }
    
    def _get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """Get conversation history from memory"""
        try:
            thread_config = {"configurable": {"thread_id": session_id}}
            checkpoints = list(self.graph.get_state_history(config=thread_config))
            
            if checkpoints:
                for checkpoint in checkpoints:
                    if checkpoint.values and not checkpoint.values.get("error_count", 0):
                        last_state = checkpoint.values
                        extracted_products = self.memory_manager.extract_product_names_from_results(last_state)
                        
                        return {
                            "conversation_history": last_state.get("conversation_history", []),
                            "previous_products": extracted_products,
                            "context_references": {
                                "last_intent": last_state.get("intent"),
                                "last_tools_used": last_state.get("tools_used", [])
                            }
                        }
            
            return {
                "conversation_history": [],
                "previous_products": [],
                "context_references": {}
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error retrieving conversation history: {e}")
            return {"conversation_history": [], "previous_products": [], "context_references": {}}
    
    def clear_memory(self, session_id: str = "default") -> bool:
        """Clear memory by recreating graph"""
        try:
            self.memory_saver = MemorySaver()
            self.graph = self._create_graph()
            logger.info("✅ Memory cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing memory: {e}")
            return False
