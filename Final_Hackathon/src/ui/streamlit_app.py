import streamlit as st
from llm.streaming_llm import stream_chat_completion

# Session state khởi tạo
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Hãy nhập câu hỏi về dữ liệu tài chính."}
    ]

st.set_page_config(page_title="AI EDINET Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 AI Agent EDINET")

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Nhập tin nhắn mới
if prompt := st.chat_input("Nhập câu hỏi..."):
    # Thêm tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        # Tạo prompt messages cho LLM
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        # Stream và hiển thị từng token
        partial = ""
        for token in stream_chat_completion(messages):
            partial += token
            st.write(token, end="", flush=True)
        # Lưu phản hồi hoàn chỉnh
        st.session_state.messages.append({"role": "assistant", "content": partial})
