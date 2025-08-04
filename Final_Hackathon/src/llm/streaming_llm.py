import os
from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

def stream_chat_completion(messages):
    """
    Gọi Azure OpenAI với stream=True, trả về generator các token.
    """
    response = openai.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=messages,
        temperature=0.1,
        stream=True
    )
    for chunk in response:
        # Lấy nội dung token mới nhất, nếu không có trả về ""
        delta = getattr(chunk.choices[0].delta, "content", "")
        yield delta or ""
