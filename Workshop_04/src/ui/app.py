"""
Streamlit UI for E-commerce AI Product Advisor Chatbot with ReAct Agent
"""

import streamlit as st
import time
import uuid
from datetime import datetime

from src.config.config import Config
from src.agents.react_agent import get_agent_manager
from src.utils.logger import get_logger

# Initialize logger
logger = get_logger("ui")

def initialize_session_state():
    """Initialize Streamlit session state"""
    
    # Initialize session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info(f"New session created: {st.session_state.session_id}")
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_message = {
            "role": "assistant",
            "content": "Xin chào! 👋 Tôi là AI Product Advisor - trợ lý AI chuyên tư vấn sản phẩm điện tử.\n\n"
                      "Tôi có thể giúp bạn:\n"
                      "🔍 Tìm kiếm laptop và smartphone phù hợp\n"
                      "⚖️ So sánh sản phẩm chi tiết\n"
                      "💡 Đưa ra gợi ý dựa trên nhu cầu\n"
                      "💰 Tư vấn theo ngân sách\n\n"
                      "Bạn đang tìm sản phẩm gì hôm nay?"
        }
        st.session_state.messages.append(welcome_message)
    
    # Agent manager
    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = get_agent_manager()
        logger.info("Agent manager initialized")


def setup_page_config():
    """Configure Streamlit page"""
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout="centered"
    )
    
    # Add custom CSS for better markdown rendering
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


def get_agent_response(prompt: str, session_id: str) -> dict:
    """
    Get response from ReAct agent
    
    Args:
        prompt: User input
        session_id: Session identifier
        
    Returns:
        Dict containing response and metadata
    """
    try:
        # Get agent for this session
        agent_manager = st.session_state.agent_manager
        agent = agent_manager.get_agent(session_id)
        
        # Get response from agent
        result = agent.chat(prompt, session_id)
        
        logger.info(f"Agent response generated for session {session_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting agent response: {e}")
        return {
            "response": "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
            "success": False,
            "error": str(e)
        }


def display_message_content(content: str):
    """Display message content with proper Markdown formatting"""
    try:
        # Clean up ReAct artifacts first
        content = clean_react_output(content)
        
        # Check if content contains structured formatting indicators
        markdown_indicators = ["**", "###", "##", "####", "*", "_", "|", "```", "`", "-", "1.", "2.", "•"]
        has_markdown = any(indicator in content for indicator in markdown_indicators)
        
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
        # Remove ReAct prefixes
        prefixes_to_remove = [
            "Final Answer:", "final answer:", "FINAL ANSWER:",
            "Action:", "action:", "ACTION:",
            "Thought:", "thought:", "THOUGHT:",
            "Observation:", "observation:", "OBSERVATION:",
            "Question:", "question:", "QUESTION:"
        ]
        
        cleaned = content
        for prefix in prefixes_to_remove:
            if cleaned.strip().startswith(prefix):
                cleaned = cleaned.replace(prefix, "", 1).strip()
        
        # Remove multiple empty lines
        import re
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
    markdown_indicators = ["**", "###", "##", "####", "*", "_", "|", "```", "`", "-", "1.", "2.", "•"]
    has_markdown = any(indicator in cleaned_text for indicator in markdown_indicators)
    
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


def setup_sidebar():
    """Setup sidebar with session management and options"""
    
    with st.sidebar:
        st.header("⚙️ Cài đặt")
        
        # Session info
        st.subheader("📝 Phiên hiện tại")
        st.caption(f"ID: {st.session_state.session_id[:8]}...")
        st.caption(f"Tin nhắn: {len(st.session_state.messages)}")
        
        # Display conversation summary
        try:
            agent_manager = st.session_state.agent_manager
            if st.session_state.session_id in agent_manager.get_active_sessions():
                summary = agent_manager.get_session_summary(st.session_state.session_id)
                st.caption(f"Tương tác: {summary.get('human_messages', 0)} câu hỏi")
                st.caption(f"Memory: {summary.get('total_messages', 0)}/{summary.get('memory_window', 10)} tin nhắn")
        except Exception:
            pass
        
        # Clear conversation
        if st.button("🗑️ Xóa cuộc trò chuyện", help="Xóa toàn bộ lịch sử chat"):
            agent_manager = st.session_state.agent_manager
            agent_manager.clear_session(st.session_state.session_id)
            st.session_state.messages = []
            # Re-add welcome message
            welcome_message = {
                "role": "assistant", 
                "content": "Cuộc trò chuyện đã được làm mới! Tôi có thể giúp gì cho bạn?"
            }
            st.session_state.messages.append(welcome_message)
            st.rerun()
        
        # Info section
        st.subheader("ℹ️ Thông tin")
        st.markdown("""
        **Công cụ có sẵn:**
        - 🔍 Tìm kiếm sản phẩm
        - 🔧 Lọc theo tiêu chí  
        - ⚖️ So sánh sản phẩm
        - 💡 Gợi ý sản phẩm
        
        **Sản phẩm hỗ trợ:**
        - 💻 Laptop (gaming, văn phòng, design)
        - 📱 Smartphone (camera, gaming, pin)
        """)


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
                # Get response from ReAct agent
                result = get_agent_response(prompt, st.session_state.session_id)
            
            if result["success"]:
                response_text = result["response"]
                
                # Clean response first
                cleaned_response = clean_react_output(response_text)
                
                # Check if response contains markdown
                markdown_indicators = ["**", "###", "##", "####", "*", "_", "|", "```", "`", "-", "1.", "2.", "•"]
                has_markdown = any(indicator in cleaned_response for indicator in markdown_indicators)
                
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
                if result.get("error"):
                    st.error(f"Chi tiết lỗi: {result['error']}")
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        logger.info("Response generated")


if __name__ == "__main__":
    main()
