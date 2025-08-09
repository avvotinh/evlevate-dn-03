# streamlit_app.py

import os
import json
import streamlit as st
from dotenv import load_dotenv
from chromadb import Client
from chromadb.config import Settings
from azure.core.credentials import AzureKeyCredential
from azure.ai.openai import OpenAIClient
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech
import soundfile as sf
import tempfile

# -----------------------------------------
# 1. Thiết lập môi trường và kết nối dịch vụ
# -----------------------------------------
load_dotenv()

# Azure OpenAI
AZURE_BASE = os.getenv("AZURE_OPENAI_API_BASE")
AZURE_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_KEY_EMBED = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY")
AZURE_KEY_LLM   = os.getenv("AZURE_OPENAI_LLM_API_KEY")
EMBED_MODEL     = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL       = os.getenv("AZURE_OPENAI_LLM_MODEL", "gpt-4o-mini")

client_llm = OpenAIClient(
    endpoint=AZURE_BASE,
    credential=AzureKeyCredential(AZURE_KEY_LLM),
    api_version=AZURE_VERSION,
)

# ChromaDB
chroma_client = Client(Settings(
    persist_directory="./chroma_db",
    anonymized_telemetry=False,
))
collection = chroma_client.get_or_create_collection(name="entertainment")

# SpeechT5
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
tts_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")

# Load sample data nếu database rỗng
@st.cache_resource
def init_data():
    if collection.count() == 0:
        with open("sample.json", "r", encoding="utf-8") as f:
            records = json.load(f)
        texts = [r["description"] for r in records]
        meta  = [{"title": r["title"], "type": r["type"], "year": r["year"]} for r in records]
        embeddings = client_llm.get_embeddings(
            model=EMBED_MODEL, input=texts
        ).data
        emb_list = [d.embedding for d in embeddings]
        collection.add(documents=texts, metadatas=meta, embeddings=emb_list)
    return collection

init_data()

# -----------------------------------------
# 2. Giao diện Streamlit
# -----------------------------------------
st.set_page_config(page_title="🎬 Entertainment Bot", layout="wide")
st.title("🎬 Entertainment Recommendation Bot")

# Chat history lưu tạm
if "history" not in st.session_state:
    st.session_state.history = []

def semantic_search(query, k=3):
    q_emb = client_llm.get_embeddings(model=EMBED_MODEL, input=[query]).data[0].embedding
    results = collection.query(query_embeddings=[q_emb], n_results=k)
    docs = results["documents"]
    metas = results["metadatas"]
    return docs, metas

def generate_response(query):
    docs, metas = semantic_search(query)
    # Chuẩn bị prompt
    context = "\n".join([f"- {m['title']} ({m['year']}): {doc}" for m, doc in zip(metas, docs)])
    prompt = (f"Bạn là một bot gợi ý giải trí. Dưới đây là các nội dung liên quan:\n"
              f"{context}\n\n"
              f"Người dùng nói: \"{query}\"\n"
              f"Hãy đưa ra 3 đề xuất phù hợp nhất với giải thích ngắn gọn.")
    chat_resp = client_llm.get_completions(
        model=LLM_MODEL,
        messages=[{"role":"system","content":prompt}]
    ).choices[0].message.content
    return chat_resp

def text_to_speech(text):
    inputs = processor(text=text, return_tensors="pt")
    speech = tts_model.generate_speech(
        inputs["input_ids"], speaker="alloy", sample_rate=16000
    )
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(tmp.name, speech.numpy(), 16000)
    return tmp.name

# Form nhập truy vấn
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Bạn muốn xem gì hôm nay?", "")
    submit = st.form_submit_button("Gửi")

if submit and user_input:
    st.session_state.history.append({"role": "user", "text": user_input})
    with st.spinner("Đang xử lý…"):
        bot_text = generate_response(user_input)
        st.session_state.history.append({"role": "bot", "text": bot_text})
        # TTS
        wav_path = text_to_speech(bot_text)
    # Hiển thị
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"**Bạn:** {msg['text']}")
        else:
            st.markdown(f"**Bot:** {msg['text']}")
    st.audio(wav_path, format="audio/wav")

# Footer hướng dẫn
st.write("---")
st.write("Gõ `exit` hoặc `quit` để kết thúc.")  
