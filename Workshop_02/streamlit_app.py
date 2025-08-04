import streamlit as st
from config import Config
from chat_interface import ChatInterface
from file_handler import FileHandler


def main():
    """Hàm chính của Streamlit app"""

    # Cấu hình trang
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout=Config.LAYOUT,
        initial_sidebar_state="expanded"
    )

    # Kiểm tra cấu hình
    Config.validate_config()

    # Tiêu đề chính
    st.title(Config.PAGE_TITLE)
    st.markdown("*Phân tích dữ liệu tài chính EDINET với AI*")

    # Khởi tạo các components
    file_handler = FileHandler()
    chat_interface = ChatInterface()

    # Sidebar - File upload và controls
    with st.sidebar:
        st.header("📂 Quản lý File")

        # Upload file
        file_handler.upload_file_widget()

        # Hiển thị thông tin file
        file_handler.display_file_info()

        st.divider()

        # Controls
        st.header("⚙️ Điều khiển")
        chat_interface.clear_chat_history()

        # Thông tin ứng dụng
        st.divider()
        st.markdown("### ℹ️ Thông tin")
        st.markdown("""
        **Financial Analyzer Chatbot** được xây dựng với:
        - 🤖 Azure OpenAI
        - 📊 Streamlit
        - 📈 Pandas & Python

        *Phiên bản: 1.0.0*
        """)

    # Main area - Chat interface
    col1, col2 = st.columns([3, 1])

    with col1:
        # Chat history
        chat_interface.display_chat_history()

        # Chat input
        chat_interface.chat_input_handler()

    with col2:
        # Sample questions (chỉ hiển thị khi đã upload file)
        if st.session_state.get('file_processed', False):
            chat_interface.display_sample_questions()


def add_custom_css():
    """Thêm CSS tùy chỉnh"""
    st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        background-color: #f8f9fa;
        color: #333;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background-color: #e9ecef;
        border-color: #0066cc;
        color: #0066cc;
    }

    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }

    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }

    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    add_custom_css()
    main()
