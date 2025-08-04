import os
import sys
import streamlit as st

# Thêm thư mục src vào sys.path để import llm
MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if MODULE_PATH not in sys.path:
    sys.path.append(MODULE_PATH)

from llm.streaming_llm import stream_chat_completion

# Khởi tạo session state cho chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Hãy nhập câu hỏi về dữ liệu tài chính."}
    ]

st.set_page_config(page_title="🤖 AI EDINET Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 AI Agent EDINET")
st.markdown("Phân tích dữ liệu tài chính EDINET theo thời gian thực qua streaming response.")

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Nhận input mới
if prompt := st.chat_input("Nhập câu hỏi..."):
    # 1. Hiển thị ngay tin nhắn của người dùng
    with st.chat_message("user"):
        st.markdown(prompt)
    # 2. Lưu vào lịch sử
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Khung assistant để stream response
    with st.chat_message("assistant"):
        # Chuẩn bị payload cho LLM
        payload = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        answer = ""
        placeholder = st.empty()
        # Stream tokens và cập nhật dần
        for token in stream_chat_completion(payload):
            if token:
                answer += token
                placeholder.markdown(answer)
        # Lưu phản hồi đầy đủ
        st.session_state.messages.append({"role": "assistant", "content": answer})
