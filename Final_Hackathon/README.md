# 🤖 AI Agent EDINET - Final Hackathon Project

Một hệ thống AI Agent thông minh được thiết kế để xử lý và phân tích dữ liệu tài chính từ EDINET (Electronic Disclosure for Investors' NETwork), tích hợp các công nghệ AI tiên tiến để cung cấp insights tài chính toàn diện.

## 🎯 Tổng quan

AI Agent EDINET là một ứng dụng AI đa module được phát triển để:

- Tự động thu thập dữ liệu từ EDINET API
- Xử lý và phân tích báo cáo tài chính phức tạp
- Cung cấp phân tích thông minh thông qua LLM
- Tạo visualizations và báo cáo tương tác
- Quản lý bộ nhớ và trạng thái của AI agent

## ✨ Tính năng chính

### 🔄 Agent Orchestration

- **Multi-Agent Architecture**: Điều phối nhiều AI agents chuyên biệt
- **State Management**: Quản lý trạng thái phức tạp của hệ thống
- **Memory Management**: Lưu trữ và truy xuất ngữ cảnh hội thoại
- **Tool Management**: Tích hợp và quản lý các công cụ chuyên biệt

### 📊 Data Processing & Analysis

- **EDINET Integration**: Kết nối trực tiếp với EDINET API
- **Document Processing**: Xử lý đa dạng loại báo cáo tài chính:
  - Semi-Annual Reports (160)
  - Quarterly Reports (140)
  - Extraordinary Reports (180)
  - Large Holding Reports (350)
  - Securities Registration Statements (030)
  - Securities Reports (120)

### 🧠 AI & Machine Learning

- **LLM Integration**: Tích hợp Azure OpenAI cho phân tích thông minh
- **Embeddings Generation**: Tạo vector embeddings cho tìm kiếm ngữ nghĩa
- **Vector Database**: Lưu trữ và truy vấn dữ liệu bằng Pinecone
- **Guardrails**: Đảm bảo tính chính xác và an toàn của AI responses

### 🛠️ Advanced Tools

- **Financial Calculator**: Tính toán các chỉ số tài chính phức tạp
- **Data Visualization**: Tạo charts và graphs tương tác
- **Session Management**: Quản lý phiên làm việc người dùng

### 🖥️ User Interface

- **Streamlit App**: Giao diện web thân thiện và trực quan
- **Interactive Dashboard**: Dashboard theo dõi real-time
- **Multi-language Support**: Hỗ trợ tiếng Nhật và tiếng Anh

## 🏗️ Kiến trúc hệ thống

```
src/
├── agents/              # AI Agent Core
│   ├── orchestrator.py     # Agent điều phối chính
│   ├── state_machine.py    # Quản lý trạng thái
│   ├── memory_manager.py   # Quản lý bộ nhớ
│   └── tool_manager.py     # Quản lý tools
├── config/              # Configuration
│   └── config.py           # Cấu hình hệ thống
├── ingestion/           # Data Ingestion
│   ├── edinet_fetcher.py   # EDINET API client
│   └── document_processors.py # Xử lý documents
├── storage/             # Data Storage
│   └── vector_db.py        # Vector database interface
├── embeddings/          # AI Embeddings
│   └── embeddings_generator.py # Tạo embeddings
├── llm/                 # Language Models
│   └── llm_generator.py    # LLM interface
├── tools/               # Specialized Tools
│   ├── financial_calculator.py # Tính toán tài chính
│   └── visualization.py    # Data visualization
├── ui/                  # User Interface
│   ├── app.py             # Streamlit application
│   └── session_state.py   # Session management
├── utils/               # Utilities
│   ├── guardrails.py      # AI safety measures
│   ├── helpers.py         # Helper functions
│   └── logger.py          # Logging system
└── main.py              # Entry point
```

## 🚀 Cài đặt và Setup

### Prerequisites

- Python 3.8+
- Azure OpenAI API access
- Pinecone API key
- EDINET API credentials

### 1. Clone Repository

```bash
git clone <repository-url>
cd Final_Hackathon
```

### 2. Environment Setup

**Windows:**

```bash
# Chạy script setup tự động
scripts\setup.bat
```

**Linux/Mac:**

```bash
# Chạy script setup tự động
./scripts/setup.sh
```

**Manual Setup:**

```bash
# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Tạo file `.env` trong thư mục root:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=your_deployment_name

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_API_ENDPOINT=your_pinecone_endpoint

# EDINET API Configuration
EDINET_API_ENDPOINT=https://disclosure.edinet-fsa.go.jp/api/v1/
EDINET_API_KEY=your_edinet_api_key
```

## 🎮 Sử dụng

### Quick Start

**Windows:**

```bash
scripts\run.bat
```

**Linux/Mac:**

```bash
./scripts/run.sh
```

**Manual Start:**

```bash
# Activate environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run application
streamlit run src/main.py
```

### Sử dụng từng Module

#### 1. EDINET Data Fetcher

```python
from src.ingestion.edinet_fetcher import EDINETFetcher

fetcher = EDINETFetcher()
documents = fetcher.fetch_documents(doc_type="160", period="2024")
```

#### 2. Document Processing

```python
from src.ingestion.document_processors import process_documents

processed_data = process_documents(documents)
```

#### 3. Financial Analysis

```python
from src.tools.financial_calculator import FinancialCalculator

calculator = FinancialCalculator()
ratios = calculator.calculate_ratios(financial_data)
```

#### 4. AI Analysis

```python
from src.llm.llm_generator import LLMGenerator

llm = LLMGenerator()
analysis = llm.analyze_financial_data(processed_data)
```

## 📊 Tính năng nâng cao

### Multi-Agent Orchestration

Hệ thống sử dụng kiến trúc multi-agent với các agent chuyên biệt:

- **Data Agent**: Chuyên thu thập và xử lý dữ liệu
- **Analysis Agent**: Phân tích tài chính chuyên sâu
- **Visualization Agent**: Tạo charts và graphs
- **Communication Agent**: Tương tác với người dùng

### Memory Management

- **Short-term Memory**: Lưu trữ ngữ cảnh hội thoại hiện tại
- **Long-term Memory**: Lưu trữ knowledge base và insights
- **Episodic Memory**: Ghi nhớ các phiên làm việc trước đó

### Tool Integration

Hệ thống tích hợp đa dạng tools chuyên biệt:

- Financial ratio calculations
- Trend analysis
- Risk assessment
- Market comparison
- Regulatory compliance checking

## 🔍 Pinecone Vector Database Operations

### 🎯 **Mục đích**
Hệ thống Pinecone được thiết kế để:
- **Semantic Search**: Tìm kiếm sản phẩm bằng ngôn ngữ tự nhiên
- **Similarity Matching**: So sánh độ tương tự giữa các sản phẩm
- **Intelligent Recommendations**: Gợi ý sản phẩm dựa trên vector embeddings
- **Multilingual Support**: Hỗ trợ tìm kiếm tiếng Việt và tiếng Anh

### 🚀 **Core Files (3 files chính)**
```
db/
├── data_processor.py          # Xử lý seed data thành vector documents
├── processed_documents.json   # 150 documents đã xử lý (50 laptops + 50 phones + 50 reviews)
└── pinecone_methods.py        # Complete Pinecone operations toolkit
```

### 📊 **Pinecone Methods - Complete Toolkit**

#### **1. Seed Data (Khởi tạo dữ liệu)**
```bash
# Upload tất cả seed data lên Pinecone
python db/pinecone_methods.py seedData
```

#### **2. Query (Tìm kiếm)**
```bash
# Tìm kiếm sản phẩm bằng text
python db/pinecone_methods.py query "laptop gaming RTX 4070"
python db/pinecone_methods.py query "điện thoại camera đẹp" 5

# Kết quả trả về: tên sản phẩm, giá, category, similarity score
```

#### **3. Upsert (Thêm/Cập nhật)**
```bash
# Thêm sản phẩm mới
python db/pinecone_methods.py upsert "iPhone 16 Pro Max với camera 48MP" "phone_051" '{"type":"product","category":"smartphone","price":40000000}'
```

#### **4. Update (Sửa đổi)**
```bash
# Cập nhật metadata hoặc text
python db/pinecone_methods.py update "phone_001" "iPhone 15 Pro Max updated specs" '{"price":32000000}'
```

#### **5. Compare (So sánh)**
```bash
# So sánh độ tương tự giữa 2 text
python db/pinecone_methods.py compare "laptop gaming" "máy tính chơi game"
```

#### **6. List (Thống kê)**
```bash
# Xem thông tin index và sample data
python db/pinecone_methods.py list
```

### 🔍 **Query Examples (Ví dụ tìm kiếm)**
```bash
# Gaming laptops
python db/pinecone_methods.py query "laptop gaming mạnh mẽ RTX 4070"

# Budget smartphones
python db/pinecone_methods.py query "điện thoại giá rẻ pin trâu"

# Business laptops
python db/pinecone_methods.py query "laptop doanh nghiệp ThinkPad"

# Camera phones
python db/pinecone_methods.py query "smartphone chụp ảnh đẹp 200MP"

# Vietnamese natural language
python db/pinecone_methods.py query "tôi cần máy tính để lập trình Python"
```

### 🗂️ **Data Structure**
- **150 documents total**:
  - 50 Laptops (Dell, HP, Lenovo, ASUS, etc.)
  - 50 Smartphones (iPhone, Samsung, Xiaomi, etc.)
  - 50 Reviews (user feedback với pros/cons)
- **Vector dimension**: 1536
- **Similarity metric**: Cosine
- **Index name**: `edinet-index`

### 🌐 **View Data on Pinecone Console**
1. Visit: https://app.pinecone.io/
2. Login with your Pinecone account
3. Find index: `edinet-index`
4. Browse ~150 vectors with metadata
5. Use Query tab for similarity search

### 🎮 **Interactive Testing**
```bash
# For interactive testing, use:
python test_pinecone.py query
```

## �📄 License

Project này được phát triển cho mục đích học tập và nghiên cứu trong khuôn khổ Elevate AI Hackathon.

## 👥 Team & Contact

**Elevate AI - DN03 - Group 3**

Nếu có thắc mắc hoặc cần hỗ trợ:

1. Tạo issue trong repository
2. Kiểm tra documentation tại `/docs`
3. Xem logs trong `/logs` directory
4. Liên hệ team qua workshop channels

## 🔄 Version History

- **v1.0.0**: Initial release với core features
- **v1.1.0**: Thêm multi-agent architecture
- **v1.2.0**: Enhanced memory management
- **v1.3.0**: Advanced visualization tools
- **v2.0.0**: Full EDINET integration

---

**⚡ Powered by Azure OpenAI, LangChain, and Streamlit**

> Hệ thống này được thiết kế để democratize financial analysis through AI, making complex financial data accessible and actionable for all users.
