from dotenv import load_dotenv
import os

load_dotenv()

print("=== KIỂM TRA CẤU HÌNH ===")
config_vars = [
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_API_BASE",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_DEPLOYMENT_NAME"
]

for var in config_vars:
    value = os.getenv(var)
    status = "✅" if value else "❌"
    display_value = value[:20] + "..." if value and len(value) > 20 else value
    print(f"{status} {var}: {display_value}")
