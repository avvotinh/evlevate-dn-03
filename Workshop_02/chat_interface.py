import streamlit as st
from typing import List, Dict
import time


class ChatInterface:
    """Giao diện chat cho Financial Analyzer"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Khởi tạo session state cho chat"""
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Xin chào! Tôi là trợ lý phân tích tài chính. Hãy upload file CSV để bắt đầu phân tích. 📊"
                }
            ]

        if "analyzer" not in st.session_state:
            st.session_state.analyzer = None

        if "file_processed" not in st.session_state:
            st.session_state.file_processed = False

    def display_chat_history(self):
        """Hiển thị lịch sử chat"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def get_sample_questions(self) -> List[str]:
        """Trả về danh sách câu hỏi mẫu"""
        return [
            "Thông tin cơ bản của công ty là gì?",
            "Tính tỷ lệ tăng trưởng lợi nhuận ròng",
            "Phân tích các chỉ số ROE, ROA và tỷ lệ vốn chủ sở hữu",
            "Đánh giá hiệu suất EPS (Earnings Per Share)",
            "Tạo báo cáo tổng hợp đầu tư với khuyến nghị"
        ]

    def display_sample_questions(self):
        """Hiển thị câu hỏi mẫu dưới dạng buttons"""
        if st.session_state.get('file_processed', False):
            st.markdown("### 💡 Câu hỏi gợi ý:")

            cols = st.columns(2)
            sample_questions = self.get_sample_questions()

            for i, question in enumerate(sample_questions):
                col = cols[i % 2]
                with col:
                    if st.button(question, key=f"sample_{i}", use_container_width=True):
                        self.process_user_message(question)

    def process_user_message(self, user_input: str):
        """Xử lý tin nhắn từ người dùng"""
        if not st.session_state.get('file_processed', False):
            st.error("⚠️ Vui lòng upload file CSV trước khi đặt câu hỏi!")
            return

        # Thêm tin nhắn người dùng vào lịch sử
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Hiển thị tin nhắn người dùng
        with st.chat_message("user"):
            st.markdown(user_input)

        # Xử lý và hiển thị phản hồi
        with st.chat_message("assistant"):
            with st.spinner("🤔 Đang phân tích..."):
                try:
                    response = st.session_state.analyzer.chat(user_input)
                    st.markdown(response)

                    # Thêm phản hồi vào lịch sử
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    error_msg = f"❌ Có lỗi xảy ra: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

    def chat_input_handler(self):
        """Xử lý input từ chat"""
        user_input = st.chat_input(
            placeholder="Nhập câu hỏi về phân tích tài chính...",
            disabled=not st.session_state.get('file_processed', False)
        )

        if user_input:
            self.process_user_message(user_input)

    def clear_chat_history(self):
        """Xóa lịch sử chat"""
        if st.button("🗑️ Xóa lịch sử chat", type="secondary"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Lịch sử chat đã được xóa. Hãy tiếp tục đặt câu hỏi! 😊"
                }
            ]
            st.rerun()
