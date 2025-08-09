# streamlit_app.py

import os
import streamlit as st
from datetime import datetime
from chatbot import EntertainmentBot

# -----------------------------------------
# 1. Streamlit Configuration
# -----------------------------------------
st.set_page_config(
    page_title="🎬 Entertainment Bot",
    page_icon="🎬",
    layout="centered"
)

# Simple CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .result-box {
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# 2. Initialize Entertainment Bot
# -----------------------------------------
@st.cache_resource
def initialize_bot():
    """Initialize the EntertainmentBot instance."""
    with st.spinner("🚀 Initializing Bot..."):
        bot = EntertainmentBot()
        bot.load_sample_data()
        bot.initialize_tts()
        return bot

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_audio' not in st.session_state:
    st.session_state.current_audio = None
if 'current_response' not in st.session_state:
    st.session_state.current_response = None
if 'clear_input' not in st.session_state:
    st.session_state.clear_input = False

# Initialize bot
if 'bot' not in st.session_state:
    st.session_state.bot = initialize_bot()

# -----------------------------------------
# 3. Main Interface
# -----------------------------------------

# Header
st.markdown('<h1 class="main-header">🎬 Entertainment Bot</h1>', unsafe_allow_html=True)

# Input
user_input = st.text_input(
    "What are you looking for?",
    placeholder="e.g. Sci-fi movies like Inception",
    key="user_input",
    value="" if st.session_state.clear_input else st.session_state.get("user_input", "")
)

# Reset clear flag after clearing
if st.session_state.clear_input:
    st.session_state.clear_input = False

# Submit button
if st.button("🔍 Search", type="primary"):
    if user_input:
        with st.spinner("Searching..."):
            try:
                # Generate recommendation
                bot_response = st.session_state.bot.generate_recommendation(user_input)
                st.session_state.current_response = bot_response
                
                # Clear previous audio
                st.session_state.current_audio = None
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Display results
if st.session_state.current_response:
    st.markdown("### 📋 Results")
    
    # Display the response in a container with styling
    with st.container():
        st.info(st.session_state.current_response)
    
    # Auto-generate audio if TTS is available and no audio generated yet
    if st.session_state.bot.tts_model and not st.session_state.current_audio:
        with st.spinner("Generating audio..."):
            try:
                audio_file = st.session_state.bot.text_to_speech(st.session_state.current_response)
                st.session_state.current_audio = audio_file
                st.rerun()
            except Exception as e:
                st.error(f"Audio generation failed: {str(e)}")
    
    # Audio player - only show if audio exists
    if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
        st.markdown("### 🎤 Listen to Results")
        with open(st.session_state.current_audio, 'rb') as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format='audio/wav')
    
    # Clear button
    if st.button("🗑️ Clear Results"):
        st.session_state.current_response = None
        st.session_state.current_audio = None
        st.session_state.clear_input = True  # Set flag to clear input
        st.rerun()  
