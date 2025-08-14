# chatbot_interface.py - Entertainment Chatbot với Streamlit Chat Interface

import streamlit as st
import os
from datetime import datetime
from chatbot import EntertainmentBot

# ==============================================
# 1. Streamlit Configuration
# ==============================================
st.set_page_config(
    page_title="🎬 Entertainment Chat Bot",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS cho chat interface
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .chat-container {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #dcf8c6;
        text-align: right;
    }
    .bot-message {
        background-color: #f1f1f1;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================
# 2. Initialize Entertainment Bot
# ==============================================
@st.cache_resource
def initialize_bot():
    """Initialize the EntertainmentBot instance."""
    try:
        with st.spinner("🚀 Initializing Entertainment Bot..."):
            bot = EntertainmentBot()
            bot.load_sample_data()
            # Không khởi tạo TTS để tránh lỗi trong web interface
            return bot
    except Exception as e:
        st.error(f"Failed to initialize bot: {str(e)}")
        return None

# ==============================================
# 3. Session State Management
# ==============================================
def initialize_session_state():
    """Initialize all session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "bot" not in st.session_state:
        st.session_state.bot = initialize_bot()
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# ==============================================
# 4. Helper Functions
# ==============================================
def add_message_to_history(role, content):
    """Add a message to chat history."""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M")
    }
    st.session_state.messages.append(message)
    return message

def clear_chat_history():
    """Clear all chat messages."""
    st.session_state.messages = []
    st.session_state.chat_history = []

def get_bot_response(user_input):
    """Get response from EntertainmentBot."""
    if st.session_state.bot is None:
        return "❌ Bot chưa được khởi tạo thành công. Vui lòng kiểm tra cấu hình API."
    
    try:
        response = st.session_state.bot.generate_recommendation(user_input)
        return response
    except Exception as e:
        return f"❌ Lỗi khi tạo gợi ý: {str(e)}"

# ==============================================
# 5. Main Chat Interface
# ==============================================
def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🎬 Entertainment Chat Bot")
    st.markdown("---")
    st.markdown("**Hỏi tôi về phim, chương trình TV mà bạn muốn xem!**")
    
    # Sidebar với thông tin và controls
    with st.sidebar:
        st.header("🎯 Hướng dẫn sử dụng")
        st.markdown("""
        **Ví dụ câu hỏi:**
        - "Tôi muốn xem phim khoa học viễn tưởng như Inception"
        - "Gợi ý cho tôi phim hài"
        - "Chương trình TV kinh dị hay"
        - "Phim hành động có rating cao"
        - "Phim tâm lý đen tối"
        """)
        
        # Clear chat button
        if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
            clear_chat_history()
            st.rerun()
        
        # Bot status
        bot_status = "🟢 Hoạt động" if st.session_state.bot else "🔴 Lỗi"
        st.markdown(f"**Trạng thái Bot:** {bot_status}")
        
        # Statistics
        total_messages = len(st.session_state.messages)
        st.markdown(f"**Tổng tin nhắn:** {total_messages}")
    
    # ==============================================
    # 6. Display Chat History
    # ==============================================
    
    # Container for chat messages
    chat_container = st.container()
    
    with chat_container:
        # Display welcome message if no chat history
        if not st.session_state.messages:
            with st.chat_message("assistant"):
                st.markdown("""
                👋 **Chào mừng đến với Entertainment Bot!**
                
                Tôi có thể gợi ý phim và chương trình TV dựa trên sở thích của bạn.
                Hãy cho tôi biết bạn muốn xem gì?
                
                💡 *Ví dụ: "Tôi muốn xem phim sci-fi như Inception"*
                """)
        
        # Display all messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(f"{message['content']}")
                # Show timestamp in small text
                st.caption(f"🕒 {message['timestamp']}")
    
    # ==============================================
    # 7. Chat Input and Response Generation
    # ==============================================
    
    # Chat input
    if prompt := st.chat_input("Hỏi tôi về phim hoặc chương trình TV..."):
        # Add user message to chat history
        add_message_to_history("user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕒 {datetime.now().strftime('%H:%M')}")
        
        # Generate and display bot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Đang tìm kiếm gợi ý..."):
                response = get_bot_response(prompt)
            
            # Stream the response (simulate typing effect)
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate streaming by displaying response word by word
            import time
            words = response.split()
            for word in words:
                full_response += word + " "
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.05)  # Adjust speed here
            
            message_placeholder.markdown(full_response)
            st.caption(f"🕒 {datetime.now().strftime('%H:%M')}")
        
        # Add bot response to chat history
        add_message_to_history("assistant", response)

    # ==============================================
    # 8. Footer Information
    # ==============================================
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
        🎬 Entertainment Bot | Powered by Azure OpenAI & ChromaDB<br>
        💡 Tip: Hãy mô tả chi tiết sở thích của bạn để nhận được gợi ý tốt nhất!
    </div>
    """, unsafe_allow_html=True)

# ==============================================
# 9. Example Queries Section (Expandable)
# ==============================================
    with st.expander("📝 Xem thêm ví dụ câu hỏi"):
        st.markdown("""
        **🎭 Thể loại:**
        - "Phim hài hay nhất"
        - "Chương trình TV kinh dị"
        - "Phim hành động với rating cao"
        
        **🎯 So sánh:**
        - "Phim giống như The Matrix"
        - "Chương trình TV như Friends"
        - "Phim tâm lý như Fight Club"
        
        **⭐ Theo rating:**
        - "Phim có rating trên 9.0"
        - "Chương trình TV được đánh giá cao"
        - "Phim kinh điển hay nhất"
        
        **📅 Theo thời gian:**
        - "Phim ra mắt trong thập niên 90"
        - "Chương trình TV mới nhất"
        - "Phim cũ nhưng vẫn hay"
        """)

if __name__ == "__main__":
    main()