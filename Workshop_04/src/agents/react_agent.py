"""
ReAct Agent for E-commerce AI Product Advisor
Implements LangChain ReAct pattern for reasoning and acting with tools
"""

from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory

from src.services.llm_service import llm_service
from src.tools.tool_manager import ToolManager
from src.prompts.prompt_manager import prompt_manager, PromptType
from src.utils.logger import get_logger

logger = get_logger("react_agent")


class ProductAdvisorReActAgent:
    """ReAct Agent for product advisory conversations"""
    
    def __init__(self):
        """
        Initialize ReAct Agent
        """
        self.tool_manager = ToolManager()
        
        # Initialize memory for conversation context
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            memory_key="chat_history",
            return_messages=True,
            output_key="output",  # Specify which output key to use
            input_key="input"     # Specify which input key to use
        )
        
        # Initialize the agent
        self.agent_executor = self._create_agent()
        
        logger.info("✅ ProductAdvisorReActAgent initialized successfully")
    
    def _create_agent(self) -> AgentExecutor:
        """Create the ReAct agent with tools and prompt"""
        try:
            # Get tools and LLM
            tools = self.tool_manager.get_all_tools()
            llm = llm_service.get_llm()
            
            # Get ReAct prompt template
            prompt_template = prompt_manager.get_prompt(PromptType.REACT_AGENT)
            
            # Create ReAct agent
            agent = create_react_agent(
                llm=llm,
                tools=tools,
                prompt=prompt_template
            )
            
            # Create custom parsing error handler
            def handle_parsing_error(error) -> str:
                logger.warning(f"⚠️ ReAct parsing error: {error}")
                
                # Safely convert error to string
                try:
                    error_str = str(error) if error else ""
                    error_lower = error_str.lower()
                except Exception:
                    error_str = ""
                    error_lower = ""
                
                # Check if error contains valid Vietnamese response patterns
                vietnamese_patterns = [
                    "tôi đã tìm thấy", "dưới đây là", "sản phẩm phù hợp", 
                    "gợi ý", "khuyến nghị", "so sánh", "thông tin", "đặc điểm",
                    "dell", "hp", "lenovo", "macbook", "iphone", "samsung", "asus"
                ]
                
                # Extract content from parsing error message  
                if "could not parse llm output:" in error_lower:
                    try:
                        # Find the actual response content
                        if "`" in error_str:
                            # Content is wrapped in backticks
                            start_idx = error_str.find("`") + 1
                            end_idx = error_str.rfind("`")
                            if start_idx > 0 and end_idx > start_idx:
                                actual_content = error_str[start_idx:end_idx].strip()
                                # Check if this contains Vietnamese response content
                                if any(word in actual_content.lower() for word in vietnamese_patterns):
                                    return f"Final Answer: {actual_content}"
                        
                        # Try to extract any Vietnamese content from the error
                        for pattern in vietnamese_patterns:
                            if pattern in error_lower:
                                # Extract content around the pattern
                                pattern_idx = error_lower.find(pattern)
                                if pattern_idx >= 0:
                                    # Extract a reasonable chunk around the pattern
                                    start = max(0, pattern_idx - 50)
                                    end = min(len(error_str), pattern_idx + 500)
                                    content_chunk = error_str[start:end].strip()
                                    
                                    # Clean up the content
                                    content_chunk = content_chunk.replace("Could not parse LLM output:", "")
                                    content_chunk = content_chunk.replace("Invalid Format:", "")
                                    content_chunk = content_chunk.replace("Missing 'Action:'", "")
                                    
                                    if len(content_chunk) > 20:
                                        return f"Final Answer: {content_chunk}"
                                
                    except Exception as e:
                        logger.error(f"Error extracting content from parsing error: {e}")
                
                # Default fallback - guide agent to use proper format
                return """Thought: Tôi cần tìm kiếm thông tin sản phẩm để trả lời khách hàng, sau đó sử dụng answer_with_context để tạo câu trả lời hoàn chỉnh.
Action: search_products
Action Input: {"query": "sản phẩm phù hợp", "max_results": 5}"""
            
            # Create agent executor with better error handling
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=handle_parsing_error,  # Use custom handler
                return_intermediate_steps=True,
                max_iterations=5,  # Allow more iterations
            )
            
            logger.info(f"✅ ReAct agent created with {len(tools)} tools")
            return agent_executor
            
        except Exception as e:
            logger.error(f"❌ Failed to create ReAct agent: {e}")
            raise
    
    def chat(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user input and return agent response
        
        Args:
            user_input: User's message
            session_id: Optional session identifier
            
        Returns:
            Dict containing response and metadata
        """
        try:
            logger.info(f"🗣️  Processing user input: {user_input[:100]}...")
            
             
            # Invoke the agent (memory is handled automatically by AgentExecutor)
            result = self.agent_executor.invoke({
                "input": user_input
            })
            
            # Process and enhance the response
            raw_output = result.get("output", "")
            processed_response = self._process_agent_output(raw_output, result)
            
            # Extract response components
            response = {
                "response": processed_response,
                "intermediate_steps": result.get("intermediate_steps", []),
                "session_id": session_id,
                "tools_used": self._extract_tools_used(result.get("intermediate_steps", [])),
                "reasoning_steps": self._extract_reasoning_steps(result.get("intermediate_steps", [])),
                "success": True,
                "agent_type": "react"
            }
            
            logger.info("✅ Agent response generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in agent chat: {e}")
            # Safely convert exception to string
            error_str = str(e) if e else "Unknown error"
            return {
                "response": self._get_error_response(error_str),
                "intermediate_steps": [],
                "session_id": session_id,
                "tools_used": [],
                "reasoning_steps": [],
                "success": False,
                "error": error_str,
                "agent_type": "react"
            }
    
    def _extract_tools_used(self, intermediate_steps: List) -> List[str]:
        """Extract list of tools used during reasoning"""
        tools_used = []
        try:
            for step in intermediate_steps:
                if len(step) >= 2 and hasattr(step[0], 'tool'):
                    tool_name = step[0].tool
                    if tool_name not in tools_used:
                        tools_used.append(tool_name)
        except Exception as e:
            logger.error(f"❌ Error extracting tools used: {e}")
        
        return tools_used
    
    def _process_agent_output(self, raw_output: str, result: Dict[str, Any]) -> str:
        """Process and enhance agent output for more natural responses"""
        try:
            if not raw_output or raw_output.strip() == "":
                return self._get_default_response(result)
            
                # Check if this is a parsing error with useful content
                if "Invalid Format" in raw_output or "Missing 'Action:'" in raw_output:
                    # Try to extract useful information from the error
                    lines = raw_output.split('\n')
                    useful_content = []
                    for line in lines:
                        if not line.startswith("Invalid Format") and not line.startswith("Missing") and line.strip():
                            if "tôi đã tìm thấy" in line.lower() or "dưới đây là" in line.lower():
                                useful_content.append(line.strip())
                    
                    if useful_content:
                        return ' '.join(useful_content)
                    else:
                        # Fallback to a helpful message
                        return "Tôi hiểu yêu cầu của bạn về sản phẩm. Hãy để tôi tìm kiếm thông tin chi tiết..."
                
                # Check if output contains answer_with_context result
                if "answer_with_context" in str(intermediate_steps):
                    # Extract the actual response from answer_with_context tool
                    for step in intermediate_steps:
                        if len(step) >= 2 and hasattr(step[0], 'tool') and step[0].tool == "answer_with_context":
                            observation = str(step[1])
                            try:
                                # Parse JSON response from answer_with_context
                                import json
                                result_data = json.loads(observation)
                                if result_data.get("success") and result_data.get("response"):
                                    return result_data["response"]
                            except (json.JSONDecodeError, KeyError):
                                # If JSON parsing fails, try to extract content directly
                                if '"response":' in observation:
                                    start_idx = observation.find('"response":') + 11
                                    # Find the end of the response value
                                    response_part = observation[start_idx:]
                                    if response_part.startswith('"'):
                                        end_idx = response_part.find('"', 1)
                                        if end_idx > 0:
                                            return response_part[1:end_idx]            # Check for database setup errors in intermediate steps
            intermediate_steps = result.get("intermediate_steps", [])
            for step in intermediate_steps:
                if len(step) >= 2:
                    observation = str(step[1])
                    if "setup_required" in observation or "NOT_FOUND" in observation or "chưa được thiết lập" in observation:
                        return "❌ **Cơ sở dữ liệu chưa được thiết lập**\n\n🔧 **Cách khắc phục:**\n1. Chạy lệnh: `python scripts/insert_sample_data.py`\n2. Hoặc: `scripts\\insert_data.bat` (Windows)\n3. Đảm bảo Pinecone index 'ecommerce-products' đã được tạo\n\n💡 Sau khi thiết lập xong, hãy thử lại câu hỏi của bạn!"
            
            # Check for database setup errors in the output
            if "setup_required" in raw_output or "chưa được thiết lập" in raw_output:
                return "❌ **Cơ sở dữ liệu chưa được thiết lập**\n\n🔧 **Cách khắc phục:**\n1. Chạy lệnh: `python scripts/insert_sample_data.py`\n2. Hoặc: `scripts\\insert_data.bat` (Windows)\n3. Đảm bảo Pinecone index 'ecommerce-products' đã được tạo\n\n💡 Sau khi thiết lập xong, hãy thử lại câu hỏi của bạn!"
            
            # Clean up the output
            processed_output = self._clean_agent_output(raw_output)
            
            # Add context-aware enhancements
            enhanced_output = self._enhance_response_context(processed_output, result)
            
            return enhanced_output
            
        except Exception as e:
            logger.error(f"❌ Error processing agent output: {e}")
            return raw_output or "Tôi xin lỗi, có vấn đề trong quá trình xử lý. Bạn có thể thử lại câu hỏi không?"
    
    def _clean_agent_output(self, output: str) -> str:
        """Clean up agent output to remove artifacts"""
        try:
            # Remove common ReAct artifacts
            output = output.replace("Final Answer:", "").strip()
            output = output.replace("Action:", "").strip()
            output = output.replace("Observation:", "").strip()
            
            # Remove multiple newlines
            import re
            output = re.sub(r'\n\s*\n', '\n\n', output)
            
            # Ensure proper Vietnamese formatting
            if not output.endswith(('.', '!', '?', ':', '😊', '👍', '✅')):
                output += "."
            
            return output.strip()
            
        except Exception as e:
            logger.error(f"❌ Error cleaning agent output: {e}")
            return output
    
    def _enhance_response_context(self, output: str, result: Dict[str, Any]) -> str:
        """Add contextual enhancements to the response"""
        try:
            tools_used = self._extract_tools_used(result.get("intermediate_steps", []))
            
            # Add helpful context based on tools used
            if "search_products" in tools_used:
                if "không tìm thấy" in output.lower() or "không có sản phẩm" in output.lower():
                    output += "\n\n💡 *Gợi ý: Bạn có thể thử tìm kiếm với từ khóa khác hoặc mở rộng tiêu chí tìm kiếm.*"
                else:
                    output += "\n\n❓ *Bạn có muốn tôi so sánh các sản phẩm này hoặc tìm thêm thông tin chi tiết không?*"
            
            if "compare_products" in tools_used:
                output += "\n\n🎯 *Nếu bạn cần thêm thông tin về sản phẩm nào đó, hãy cho tôi biết nhé!*"
            
            if "recommend_products" in tools_used:
                output += "\n\n💭 *Bạn có muốn tôi giải thích thêm về lý do khuyến nghị hoặc tìm các lựa chọn khác không?*"
            
            return output
            
        except Exception as e:
            logger.error(f"❌ Error enhancing response context: {e}")
            return output
    
    def _get_default_response(self, result: Dict[str, Any]) -> str:
        """Get default response when agent output is empty"""
        tools_used = self._extract_tools_used(result.get("intermediate_steps", []))
        
        if tools_used:
            return f"Tôi đã sử dụng các công cụ {', '.join(tools_used)} để tìm thông tin, nhưng gặp khó khăn trong việc tạo câu trả lời. Bạn có thể nói rõ hơn về nhu cầu của mình không?"
        else:
            return "Tôi hiểu bạn đang tìm kiếm thông tin về sản phẩm. Bạn có thể cho tôi biết cụ thể bạn quan tâm đến loại sản phẩm nào không? Ví dụ: laptop, smartphone, hoặc có ngân sách và nhu cầu sử dụng như thế nào?"
    
    def _get_error_response(self, error_msg: str) -> str:
        """Get user-friendly error response"""
        friendly_errors = {
            "timeout": "Xin lỗi, có vấn đề kết nối. Bạn có thể thử lại không?",
            "parse": "Tôi gặp khó khăn trong việc hiểu yêu cầu của bạn. Bạn có thể diễn đạt lại một cách khác không?",
            "tool": "Có vấn đề với việc tìm kiếm thông tin sản phẩm. Bạn hãy thử lại sau một chút nhé.",
            "llm": "Hệ thống AI tạm thời gặp sự cố. Vui lòng thử lại sau ít phút.",
            "not found": "Cơ sở dữ liệu sản phẩm chưa được thiết lập. Vui lòng chạy script khởi tạo dữ liệu hoặc liên hệ quản trị viên.",
            "setup_required": "Hệ thống cần được thiết lập trước. Vui lòng chạy: python scripts/insert_sample_data.py"
        }
        
        # Safely convert error_msg to string and lowercase
        try:
            error_str = str(error_msg) if error_msg else ""
            error_lower = error_str.lower()
        except Exception:
            error_lower = ""
        
        # Check for specific error types
        for error_type, friendly_msg in friendly_errors.items():
            if error_type in error_lower:
                return friendly_msg
        
        # Default friendly error
        return "Xin lỗi, tôi gặp một chút vấn đề kỹ thuật. Bạn có thể thử lại câu hỏi không? 😊"
    
    def _extract_reasoning_steps(self, intermediate_steps: List) -> List[Dict[str, str]]:
        """Extract reasoning steps for debugging/transparency"""
        reasoning_steps = []
        try:
            for i, step in enumerate(intermediate_steps):
                if len(step) >= 2:
                    action = step[0]
                    observation = step[1]
                    
                    reasoning_steps.append({
                        "step": i + 1,
                        "thought": getattr(action, 'log', ''),
                        "action": getattr(action, 'tool', ''),
                        "action_input": str(getattr(action, 'tool_input', '')),
                        "observation": str(observation)[:200] + "..." if len(str(observation)) > 200 else str(observation)
                    })
        except Exception as e:
            logger.error(f"❌ Error extracting reasoning steps: {e}")
        
        return reasoning_steps
    
    def clear_memory(self) -> bool:
        """Clear conversation memory"""
        try:
            self.memory.clear()
            logger.info("✅ Conversation memory cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing memory: {e}")
            return False


class AgentManager:
    """Manages agent instances and sessions"""
    
    def __init__(self):
        """Initialize agent manager"""
        self.agents: Dict[str, ProductAdvisorReActAgent] = {}
        logger.info("✅ AgentManager initialized")
    
    def get_agent(self, session_id: str = "default") -> ProductAdvisorReActAgent:
        """Get or create agent for session"""
        if session_id not in self.agents:
            # Create agent without limits for better performance
            self.agents[session_id] = ProductAdvisorReActAgent()
            logger.info(f"✅ Created new agent for session: {session_id}")
        
        return self.agents[session_id]
    
    def clear_session(self, session_id: str) -> bool:
        """Clear specific session"""
        try:
            if session_id in self.agents:
                self.agents[session_id].clear_memory()
                del self.agents[session_id]
                logger.info(f"✅ Session {session_id} cleared")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error clearing session {session_id}: {e}")
            return False
    
    def clear_all_sessions(self) -> bool:
        """Clear all sessions"""
        try:
            self.agents.clear()
            logger.info("✅ All sessions cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing all sessions: {e}")
            return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.agents.keys())


# Global agent manager instance
agent_manager = AgentManager()


def get_agent_manager() -> AgentManager:
    """Get global agent manager instance"""
    return agent_manager
