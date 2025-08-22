"""
Streamlit UI for E-commerce AI Product Advisor Chatbot with LangGraph Agent
"""

import re
import time
import uuid
import streamlit as st

from src.config.config import Config
from src.utils.logger import get_logger

# Initialize logger
logger = get_logger("ui")

MARKDOWN_INDICATORS = ["**", "###", "##", "####", "*", "_", "|", "```", "`", "-", "1.", "2.", "•"]

REACT_PREFIXES_TO_REMOVE = [
    "Final Answer:", "final answer:", "FINAL ANSWER:",
    "Action:", "action:", "ACTION:",
    "Thought:", "thought:", "THOUGHT:",
    "Observation:", "observation:", "OBSERVATION:",
    "Question:", "question:", "QUESTION:"
]

# Try to import LangGraph agent
try:
    from src.agents.langgraph_agent import get_agent_manager
    LANGGRAPH_AVAILABLE = True
    logger.info("✅ LangGraph agent available")
except ImportError as e:
    logger.error(f"❌ LangGraph agent not available: {e}")
    LANGGRAPH_AVAILABLE = False
    get_agent_manager = None


def create_welcome_message() -> dict:
    """Create welcome message object"""
    return {
        "role": "assistant",
        "content": '''Xin chào! 👋 

Tôi là **AI Product Advisor** - trợ lý AI chuyên tư vấn sản phẩm điện tử.

Tôi có thể giúp bạn:

- 🔍 **Tìm kiếm sản phẩm**: Tìm sản phẩm điện tử theo nhu cầu
- ⚖️ **So sánh sản phẩm**: Phân tích chi tiết sự khác biệt giữa các sản phẩm  
- 💡 **Đưa ra gợi ý**: Tư vấn sản phẩm phù hợp với ngân sách và mục đích sử dụng
- 📝 **Xem đánh giá**: Tổng hợp và phân tích đánh giá từ người dùng

---

**Bạn cần tư vấn gì hôm nay?** 🤔'''
    }


def update_performance_metrics(response_time: float, success: bool):
    """Update performance metrics for LangGraph agent"""
    metrics = st.session_state.performance_metrics
    
    # Update running averages
    total_queries = metrics["total_queries"]
    metrics["avg_time"] = (metrics["avg_time"] * total_queries + response_time) / (total_queries + 1)
    metrics["success_rate"] = (metrics["success_rate"] * total_queries + (1 if success else 0)) / (total_queries + 1)
    metrics["total_queries"] += 1


def initialize_session_state():
    """Initialize session state for LangGraph agent"""

    # Initialize session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info(f"New session created: {st.session_state.session_id}")

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append(create_welcome_message())

    # LangGraph agent manager
    if "langgraph_agent_manager" not in st.session_state:
        if not LANGGRAPH_AVAILABLE or not get_agent_manager:
            st.error("❌ LangGraph agent không khả dụng!")
            st.stop()
        
        st.session_state.langgraph_agent_manager = get_agent_manager()
        logger.info("✅ LangGraph agent manager initialized")

    # Performance metrics
    if "performance_metrics" not in st.session_state:
        st.session_state.performance_metrics = {
            "avg_time": 0, 
            "success_rate": 0, 
            "total_queries": 0
        }


def setup_page_config():
    """Configure Streamlit page"""
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout="centered"
    )
    
    # Add custom CSS for better markdown rendering and agent selection
    st.markdown("""
    <style>
    /* Improve heading spacing */
    .stMarkdown h3 {
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
    .stMarkdown h4 {
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        color: #ff7f0e;
    }

    /* Improve list styling */
    .stMarkdown ul {
        padding-left: 1.5rem;
    }
    .stMarkdown li {
        margin-bottom: 0.5rem;
    }

    /* Bold text styling */
    .stMarkdown strong {
        color: #1f77b4;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


def setup_sidebar():
    """Simplified sidebar for LangGraph agent"""
    st.sidebar.title("🤖 LangGraph Agent")

    # Agent information
    st.sidebar.info("""
    🚀 **LangGraph Agent**
    - Graph-based workflow
    - Enhanced error handling
    - Better debugging
    - Conditional branching
    """)

    # Session management
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗂️ Session")

    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        # Re-add welcome message
        st.session_state.messages.append(create_welcome_message())
        st.sidebar.success("✅ Chat history cleared!")
        st.rerun()


def get_current_agent():
    """Get current LangGraph agent"""
    return st.session_state.langgraph_agent_manager.get_agent(st.session_state.session_id)


def get_agent_response(prompt: str, session_id: str) -> dict:
    """
    Get response from LangGraph agent with performance tracking

    Args:
        prompt: User input
        session_id: Session identifier

    Returns:
        Dict containing response and metadata
    """
    try:
        start_time = time.time()

        # Get current agent
        agent = get_current_agent()

        # Get response from agent
        result = agent.chat(prompt, session_id)

        end_time = time.time()
        response_time = end_time - start_time

        # Update performance metrics
        success = result.get("success", True)
        update_performance_metrics(response_time, success)

        logger.info(f"LangGraph Agent response generated in {response_time:.2f}s for session {session_id}")
        return result

    except Exception as e:
        logger.error(f"Error getting agent response: {e}")
        return {
            "response": "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
            "success": False,
            "error": str(e),
            "agent_type": "langgraph"
        }


def display_message_content(content: str):
    """Display message content with proper Markdown formatting"""
    try:
        # Clean up ReAct artifacts first
        content = clean_react_output(content)
        
        # Check if content contains structured formatting indicators
        has_markdown = any(indicator in content for indicator in MARKDOWN_INDICATORS)
        
        if has_markdown:
            # This looks like formatted content, use markdown with better formatting
            st.markdown(content, unsafe_allow_html=False)
        else:
            # Regular text, use write for better handling
            st.write(content)
            
    except Exception as e:
        # Fallback to simple write if markdown fails
        logger.warning(f"Markdown rendering failed, using fallback: {e}")
        st.write(content)


def clean_react_output(content: str) -> str:
    """Clean ReAct agent output artifacts"""
    if not content:
        return content
    
    try:
        cleaned = content
        for prefix in REACT_PREFIXES_TO_REMOVE:
            if cleaned.strip().startswith(prefix):
                cleaned = cleaned.replace(prefix, "", 1).strip()
        
        # Remove multiple empty lines
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
        
    except Exception as e:
        logger.warning(f"Error cleaning ReAct output: {e}")
        return content


def response_generator(response_text: str):
    """Generate streaming response with markdown awareness"""
    # Clean the response first
    cleaned_text = clean_react_output(response_text)
    
    # For markdown content, don't stream word by word as it breaks formatting
    has_markdown = any(indicator in cleaned_text for indicator in MARKDOWN_INDICATORS)
    
    if has_markdown:
        # For markdown content, stream in chunks to preserve formatting
        lines = cleaned_text.split('\n')
        for line in lines:
            yield line + '\n'
            time.sleep(0.1)  # Slower for better readability
    else:
        # For plain text, stream word by word
        words = cleaned_text.split()
        for word in words:
            yield word + " "
            time.sleep(0.05)

def main():
    """Main application function"""
    
    # Setup
    setup_page_config()
    initialize_session_state()
    
    # Sidebar
    setup_sidebar()
    
    # Main content
    st.title("🛍️ AI Product Advisor")
    st.markdown("**Trợ lý AI tư vấn sản phẩm điện tử thông minh**")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            display_message_content(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
        logger.info(f"User input: {prompt}")
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            display_message_content(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            # Show thinking indicator
            with st.spinner("🤔 Đang suy nghĩ..."):
                # Get response from LangGraph agent
                result = get_agent_response(prompt, st.session_state.session_id)
            
            if result["success"]:
                response_text = result["response"]

                # Clean response first
                cleaned_response = clean_react_output(response_text)

                # Check if response contains markdown
                has_markdown = any(indicator in cleaned_response for indicator in MARKDOWN_INDICATORS)

                if has_markdown:
                    # For markdown content, display directly without streaming to preserve formatting
                    display_message_content(cleaned_response)
                    response = cleaned_response
                else:
                    # For plain text, use streaming
                    response = st.write_stream(response_generator(cleaned_response))

            else:
                response = clean_react_output(result["response"])
                display_message_content(response)
                st.error("❌ Error with **LangGraph Agent**")
                if result.get("error"):
                    st.error(f"Chi tiết lỗi: {result['error']}")
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        logger.info("Response generated")


if __name__ == "__main__":
    main()
