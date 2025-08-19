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

# Try to import LangGraph agent
try:
    from src.agents.langgraph_agent import get_langgraph_agent_manager
    LANGGRAPH_AVAILABLE = True
    logger.info("✅ LangGraph agent available")
except ImportError as e:
    logger.warning(f"⚠️ LangGraph agent not available: {e}")
    LANGGRAPH_AVAILABLE = False
    get_langgraph_agent_manager = None

def initialize_session_state():
    """Enhanced session state with agent selection support"""

    # Initialize session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info(f"New session created: {st.session_state.session_id}")

    # Agent selection
    if "agent_type" not in st.session_state:
        st.session_state.agent_type = "ReAct Agent"  # Default

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

    # Agent managers
    if "react_agent_manager" not in st.session_state:
        st.session_state.react_agent_manager = get_agent_manager()
        logger.info("ReAct agent manager initialized")

    if "langgraph_agent_manager" not in st.session_state:
        if LANGGRAPH_AVAILABLE and get_langgraph_agent_manager:
            st.session_state.langgraph_agent_manager = get_langgraph_agent_manager()
            logger.info("✅ LangGraph agent manager initialized")
        else:
            st.session_state.langgraph_agent_manager = None
            logger.warning("⚠️ LangGraph agent manager not available")

    # Performance metrics
    if "performance_metrics" not in st.session_state:
        st.session_state.performance_metrics = {
            "react": {"avg_time": 0, "success_rate": 0, "total_queries": 0},
            "langgraph": {"avg_time": 0, "success_rate": 0, "total_queries": 0}
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
    """Enhanced sidebar with agent comparison and settings"""
    st.sidebar.title("🤖 Agent Settings")

    # Agent selection
    agent_options = ["ReAct Agent"]
    if LANGGRAPH_AVAILABLE and st.session_state.langgraph_agent_manager is not None:
        agent_options.append("LangGraph Agent")

    agent_type = st.sidebar.selectbox(
        "Choose Agent Type",
        agent_options,
        index=agent_options.index(st.session_state.agent_type) if st.session_state.agent_type in agent_options else 0,
        help="ReAct: Traditional reasoning loop, LangGraph: Enhanced graph-based workflow"
    )

    # Handle agent type change
    if agent_type != st.session_state.agent_type:
        st.session_state.agent_type = agent_type
        st.sidebar.success(f"✅ Switched to {agent_type}")
        logger.info(f"Agent switched to: {agent_type}")
        st.rerun()

    # Agent information
    st.sidebar.markdown("---")
    if agent_type == "ReAct Agent":
        st.sidebar.info("""
        🔄 **ReAct Agent**
        - Traditional reasoning loop
        - Proven stability
        - LangChain standard
        - Thought → Action → Observation
        """)
    else:
        st.sidebar.info("""
        🚀 **LangGraph Agent**
        - Graph-based workflow
        - Enhanced error handling
        - Better debugging
        - Conditional branching
        """)

    # Performance metrics
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Performance")

    metrics = st.session_state.performance_metrics
    current_agent = "react" if agent_type == "ReAct Agent" else "langgraph"

    if metrics[current_agent]["total_queries"] > 0:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Avg Time", f"{metrics[current_agent]['avg_time']:.2f}s")
        with col2:
            st.metric("Success Rate", f"{metrics[current_agent]['success_rate']:.1%}")

        st.sidebar.metric("Total Queries", metrics[current_agent]["total_queries"])
    else:
        st.sidebar.info("No performance data yet")

    # Session management
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗂️ Session")

    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        # Re-add welcome message
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
        st.sidebar.success("✅ Chat history cleared!")
        st.rerun()


def get_current_agent():
    """Get current agent based on selection"""
    if st.session_state.agent_type == "ReAct Agent":
        return st.session_state.react_agent_manager.get_agent(st.session_state.session_id)
    else:
        if st.session_state.langgraph_agent_manager is not None:
            return st.session_state.langgraph_agent_manager.get_agent(st.session_state.session_id)
        else:
            # Fallback to ReAct if LangGraph not available
            return st.session_state.react_agent_manager.get_agent(st.session_state.session_id)


def get_agent_response(prompt: str, session_id: str) -> dict:
    """
    Enhanced agent response with performance tracking

    Args:
        prompt: User input
        session_id: Session identifier

    Returns:
        Dict containing response and metadata
    """
    import time

    try:
        start_time = time.time()

        # Get current agent
        agent = get_current_agent()

        # Get response from agent
        result = agent.chat(prompt, session_id)

        end_time = time.time()
        response_time = end_time - start_time

        # Update performance metrics
        agent_key = "react" if st.session_state.agent_type == "ReAct Agent" else "langgraph"
        metrics = st.session_state.performance_metrics[agent_key]

        # Update running averages
        total_queries = metrics["total_queries"]
        metrics["avg_time"] = (metrics["avg_time"] * total_queries + response_time) / (total_queries + 1)
        metrics["success_rate"] = (metrics["success_rate"] * total_queries + (1 if result.get("success", True) else 0)) / (total_queries + 1)
        metrics["total_queries"] += 1

        logger.info(f"{st.session_state.agent_type} response generated in {response_time:.2f}s for session {session_id}")
        return result

    except Exception as e:
        logger.error(f"Error getting agent response: {e}")
        return {
            "response": "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
            "success": False,
            "error": str(e),
            "agent_type": st.session_state.agent_type.lower().replace(" ", "_")
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

                # Show agent info and tools used
                tools_used = result.get("tools_used", [])

                if tools_used:
                    st.success(f"✅ Response generated using **{st.session_state.agent_type}**")
                    st.info(f"🔧 Tools used: {', '.join(tools_used)}")
                else:
                    st.success(f"✅ Response generated using **{st.session_state.agent_type}**")

            else:
                response = clean_react_output(result["response"])
                display_message_content(response)
                st.error(f"❌ Error with **{st.session_state.agent_type}**")
                if result.get("error"):
                    st.error(f"Chi tiết lỗi: {result['error']}")
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        logger.info("Response generated")


if __name__ == "__main__":
    main()
