import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Cấu hình ứng dụng Streamlit"""

    # Azure OpenAI settings
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    # Streamlit settings
    PAGE_TITLE = "🏢 Financial Analyzer Chatbot"
    PAGE_ICON = "💰"
    LAYOUT = "wide"

    # File upload settings
    MAX_FILE_SIZE = 200  # MB
    ALLOWED_FILE_TYPES = ["csv"]

    @classmethod
    def validate_config(cls):
        """Kiểm tra cấu hình có đầy đủ không"""
        required_vars = [
            cls.AZURE_OPENAI_API_VERSION,
            cls.AZURE_OPENAI_API_BASE,
            cls.AZURE_OPENAI_API_KEY,
            cls.AZURE_OPENAI_DEPLOYMENT_NAME
        ]

        missing_vars = [var for var in required_vars if not var]
        if missing_vars:
            st.error("❌ Thiếu cấu hình Azure OpenAI. Vui lòng kiểm tra file .env")
            st.stop()

        return True
