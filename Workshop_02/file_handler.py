import streamlit as st
import tempfile
import os
from typing import Optional
from app import FinancialAnalyzer


class FileHandler:
    """Xử lý upload và phân tích file CSV"""

    def __init__(self):
        self.analyzer = None

    def upload_file_widget(self) -> Optional[str]:
        """Widget upload file với validation"""
        uploaded_file = st.file_uploader(
            "📁 Chọn file CSV để phân tích",
            type=['csv'],
            help="Upload file CSV chứa dữ liệu tài chính EDINET",
            key="csv_uploader"
        )

        if uploaded_file is not None:
            return self._process_uploaded_file(uploaded_file)
        return None

    def _process_uploaded_file(self, uploaded_file) -> str:
        """Xử lý file được upload"""
        try:
            # Tạo file tạm thời
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name

            # Khởi tạo analyzer và extract data
            self.analyzer = FinancialAnalyzer()
            data = self.analyzer.extract_data_from_csv(temp_path)

            # Lưu analyzer vào session state
            st.session_state.analyzer = self.analyzer
            st.session_state.file_processed = True
            st.session_state.company_name = data.get('company_name_en', 'Unknown Company')

            # Xóa file tạm
            os.unlink(temp_path)

            st.success(f"✅ Đã xử lý thành công dữ liệu của {st.session_state.company_name}")
            return temp_path

        except Exception as e:
            st.error(f"❌ Lỗi xử lý file: {str(e)}")
            return None

    def display_file_info(self):
        """Hiển thị thông tin file đã xử lý"""
        if st.session_state.get('file_processed', False):
            company_name = st.session_state.get('company_name', 'Unknown')
            st.info(f"📊 Đang phân tích dữ liệu của: **{company_name}**")
        else:
            st.warning("⚠️ Vui lòng upload file CSV để bắt đầu phân tích")
