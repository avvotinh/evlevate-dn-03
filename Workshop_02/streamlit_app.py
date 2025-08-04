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
        file_handler.upload_file_widget()
        file_handler.display_file_info()

        st.divider()
        st.header("⚙️ Điều khiển")
        chat_interface.clear_chat_history()

        st.divider()
        st.markdown("### ℹ️ Thông tin")
        st.markdown("""
        **Financial Analyzer Chatbot** được xây dựng với:
        - 🤖 Azure OpenAI
        - 📊 Streamlit
        - 📈 Pandas & Python

        *Phiên bản: 1.0.0*
        """)

    # Main area - Chat interface + câu hỏi gợi ý
    col1, col2 = st.columns([3, 1])

    with col1:
        # Hiển thị lịch sử chat
        chat_interface.display_chat_history()

        # Input chat
        chat_interface.chat_input_handler()

        # Hiển thị câu hỏi gợi ý dưới chat
        if st.session_state.get('file_processed', False):
            st.markdown("### 💡 Câu hỏi gợi ý:")
            for i, question in enumerate(chat_interface.get_sample_questions()):
                if st.button(question, key=f"sample_{i}", use_container_width=True):
                    chat_interface.process_user_message(question)
                    st.experimental_rerun()

    with col2:
        # Thêm không gian cho tương lai (metrics, biểu đồ...)
        st.markdown("## 📈 Thống kê nhanh")
        if st.session_state.get('file_processed', False):
            st.info(f"Đang phân tích: **{st.session_state.company_name}**")
        else:
            st.write("Chưa có dữ liệu để hiển thị.")


def add_custom_css():
    """Thêm CSS tùy chỉnh"""
    st.markdown("""
    <style>
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
    </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    add_custom_css()
    main()
