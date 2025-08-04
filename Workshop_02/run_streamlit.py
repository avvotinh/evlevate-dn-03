import subprocess
import sys
import os


def run_streamlit():
    """Chạy Streamlit app"""
    try:
        # Đảm bảo đang ở đúng thư mục
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Chạy streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("🛑 Đã dừng ứng dụng")
    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    run_streamlit()
