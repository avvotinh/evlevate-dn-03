"""
Enhanced LangGraph Agent for E-commerce AI Product Advisor
Improved implementation with ReAct Agent compatibility and advanced features
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
import json
import re

from src.services.llm_service import llm_service
from src.tools.tool_manager import ToolManager
from src.utils.logger import get_logger

logger = get_logger("langgraph_agent")


class AgentState(TypedDict):
    """Enhanced state for LangGraph agent"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_input: str
    session_id: Optional[str]
    current_step: str
    intent: str
    tools_used: List[str]
    search_results: Optional[Dict[str, Any]]
    comparison_results: Optional[Dict[str, Any]]
    recommendation_results: Optional[Dict[str, Any]]
    context_data: Optional[str]
    final_response: Optional[str]
    iteration_count: int
    error_count: int
    reasoning_steps: List[Dict[str, Any]]


class ProductAdvisorLangGraphAgent:
    """Enhanced LangGraph-based Product Advisor Agent"""
    
    def __init__(self):
        """Initialize LangGraph agent with ReAct compatibility"""
        self.tool_manager = ToolManager()
        self.llm = llm_service.get_llm()
        
        # Memory management similar to ReAct agent
        self.memories: Dict[str, ConversationBufferWindowMemory] = {}
        
        self.graph = self._create_graph()
        logger.info("✅ Enhanced LangGraph Agent initialized")
    
    def _get_memory(self, session_id: str) -> ConversationBufferWindowMemory:
        """Get or create memory for session"""
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferWindowMemory(
                k=10, memory_key="chat_history", return_messages=True,
                output_key="output", input_key="input"
            )
        return self.memories[session_id]
    
    def _create_graph(self) -> StateGraph:
        """Create enhanced LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes with error handling
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("handle_greeting", self._handle_greeting)
        workflow.add_node("search_products", self._search_products)
        workflow.add_node("compare_products", self._compare_products)
        workflow.add_node("recommend_products", self._recommend_products)
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
                "direct": "generate_response",
                "error": "handle_error"
            }
        )
        
        # All nodes can lead to response generation or error handling
        workflow.add_edge("handle_greeting", "generate_response")
        workflow.add_edge("search_products", "generate_response")
        workflow.add_edge("compare_products", "generate_response")
        workflow.add_edge("recommend_products", "generate_response")
        workflow.add_edge("handle_error", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()

    def _classify_intent_with_llm(self, user_input: str) -> str:
        """Use LLM to classify user intent intelligently"""
        try:
            intent_prompt = f"""Phân tích ý định của người dùng và trả về CHÍNH XÁC một trong các intent sau:

INTENT OPTIONS:
- greeting: Chào hỏi, cảm ơn, hỏi về AI
- search: Tìm kiếm thông tin sản phẩm cụ thể, hỏi cấu hình, thông số, giá
- compare: So sánh 2+ sản phẩm
- recommend: Xin gợi ý, tư vấn sản phẩm phù hợp với nhu cầu
- direct: Câu hỏi đơn giản khác

USER INPUT: "{user_input}"

EXAMPLES:
- "Xin chào" → greeting
- "Dell Inspiron 14 5420 cấu hình như thế nào" → search
- "iPhone 15 vs Samsung S24" → compare
- "Gợi ý laptop cho sinh viên" → recommend
- "Cảm ơn bạn" → greeting

Chỉ trả về TÊN INTENT (greeting/search/compare/recommend/direct):"""

            response = self.llm.invoke([HumanMessage(content=intent_prompt)])
            intent = response.content.strip().lower()

            # Validate intent
            valid_intents = ["greeting", "search", "compare", "recommend", "direct"]
            if intent in valid_intents:
                logger.info(f"🤖 LLM classified intent: {intent}")
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
        """LLM-powered intent analysis for better accuracy"""
        user_input = state["user_input"]

        try:
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
    
    def _route_intent(self, state: AgentState) -> str:
        """Enhanced routing with error handling"""
        return state.get("current_step", "error")
    
    def _handle_greeting(self, state: AgentState) -> AgentState:
        """Handle greeting messages"""
        try:
            greeting_response = """Xin chào! 👋 Tôi là AI Product Advisor - trợ lý AI chuyên tư vấn sản phẩm điện tử.

Tôi có thể giúp bạn:
🔍 Tìm kiếm laptop và smartphone phù hợp
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
    
    def _search_products(self, state: AgentState) -> AgentState:
        """Enhanced product search with error handling"""
        try:
            search_tool = self.tool_manager.get_tool("search")
            if not search_tool:
                raise Exception("Search tool not available")

            # Use string input for compatibility with existing tools
            search_query = state["user_input"]

            result = search_tool.run(search_query)
            state["search_results"] = result
            state["tools_used"].append("search_products")
            
            # Add reasoning step
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "search_products",
                "thought": f"Tìm kiếm sản phẩm với query: {state['user_input'][:50]}...",
                "action_input": search_query,
                "observation": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            }
            state["reasoning_steps"].append(reasoning_step)
            
            logger.info("✅ Search completed")
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            state["search_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1
        
        return state

    def _compare_products(self, state: AgentState) -> AgentState:
        """Enhanced product comparison with error handling"""
        try:
            compare_tool = self.tool_manager.get_tool("compare")
            if not compare_tool:
                raise Exception("Compare tool not available")

            # Use string input for compatibility with existing tools
            compare_query = state["user_input"]

            result = compare_tool.run(compare_query)
            state["comparison_results"] = result
            state["tools_used"].append("compare_products")

            # Add reasoning step
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "compare_products",
                "thought": f"So sánh sản phẩm với query: {state['user_input'][:50]}...",
                "action_input": compare_query,
                "observation": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            }
            state["reasoning_steps"].append(reasoning_step)

            logger.info("✅ Comparison completed")

        except Exception as e:
            logger.error(f"❌ Comparison failed: {e}")
            state["comparison_results"] = {"error": str(e), "success": False}
            state["error_count"] = state.get("error_count", 0) + 1

        return state

    def _recommend_products(self, state: AgentState) -> AgentState:
        """Enhanced product recommendation with error handling"""
        try:
            recommend_tool = self.tool_manager.get_tool("recommend")
            if not recommend_tool:
                raise Exception("Recommend tool not available")

            # Use string input for compatibility with existing tools
            recommend_query = state["user_input"]

            result = recommend_tool.run(recommend_query)
            state["recommendation_results"] = result
            state["tools_used"].append("recommend_products")

            # Add reasoning step
            reasoning_step = {
                "step": len(state.get("reasoning_steps", [])) + 1,
                "action": "recommend_products",
                "thought": f"Gợi ý sản phẩm với nhu cầu: {state['user_input'][:50]}...",
                "action_input": recommend_query,
                "observation": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            }
            state["reasoning_steps"].append(reasoning_step)

            logger.info("✅ Recommendation completed")

        except Exception as e:
            logger.error(f"❌ Recommendation failed: {e}")
            state["recommendation_results"] = {"error": str(e), "success": False}
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

            # Use RAG generation tool if we have context
            if context_parts:
                context = "\n".join(context_parts)
                state["context_data"] = context

                rag_tool = self.tool_manager.get_tool("answer_with_context")
                if rag_tool:
                    rag_input = {
                        "user_query": state["user_input"],
                        "context": context,
                        "response_type": "general"
                    }

                    result = rag_tool.run(rag_input)

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
                        "thought": "Sử dụng RAG để tạo câu trả lời từ context đã thu thập",
                        "action_input": str(rag_input),
                        "observation": state["final_response"][:100] + "..." if len(state["final_response"]) > 100 else state["final_response"]
                    }
                    state["reasoning_steps"].append(reasoning_step)

                    state["tools_used"].append("answer_with_context")
                else:
                    raise Exception("RAG tool not available")
            else:
                # Direct LLM response for simple queries
                response = self.llm.invoke([HumanMessage(content=state["user_input"])])
                state["final_response"] = response.content

            logger.info("✅ Response generated")

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
        """Enhanced chat method with ReAct compatibility"""
        try:
            if not session_id:
                session_id = "default"

            logger.info(f"🗣️ Processing user input: {user_input[:100]}...")

            # Get memory for session
            memory = self._get_memory(session_id)

            # Initialize enhanced state
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
                "context_data": None,
                "final_response": None,
                "iteration_count": 0,
                "error_count": 0,
                "reasoning_steps": []
            }

            # Run the graph
            final_state = self.graph.invoke(initial_state)

            # Update memory
            memory.save_context(
                {"input": user_input},
                {"output": final_state.get("final_response", "")}
            )

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
                "intent": final_state.get("intent", "unknown")
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

    def clear_memory(self, session_id: str = "default") -> bool:
        """Clear conversation memory for session"""
        try:
            if session_id in self.memories:
                self.memories[session_id].clear()
                logger.info(f"✅ Memory cleared for session: {session_id}")
                return True
            return False
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
        """Clear all sessions"""
        try:
            self.agent.memories.clear()
            logger.info("✅ All sessions cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing all sessions: {e}")
            return False

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.agent.memories.keys())


# Global instances
langgraph_agent = ProductAdvisorLangGraphAgent()
langgraph_agent_manager = LangGraphAgentManager()


def get_langgraph_agent_manager() -> LangGraphAgentManager:
    """Get global LangGraph agent manager instance"""
    return langgraph_agent_manager
