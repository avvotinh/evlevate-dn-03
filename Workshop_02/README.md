# 🏢 Simple Financial Analyzer

A comprehensive financial analysis tool that processes Japanese financial data from EDINET (Electronic Disclosure for Investors' NETwork) CSV files and provides AI-powered analysis using Azure OpenAI.

## 📋 Features

- **CSV Data Processing**: Extracts and processes financial data from EDINET CSV files
- **AI-Powered Analysis**: Uses Azure OpenAI for intelligent financial analysis
- **Financial Calculations**: Automated calculation of key financial ratios and growth rates
- **Investment Analysis**: Generates comprehensive investment summaries with recommendations
- **Conversation Interface**: Interactive chat-based analysis interface

## 🔧 Technical Stack

- **Python 3.8+**: Core programming language
- **Azure OpenAI**: AI-powered analysis and chat interface
- **Pandas**: Data processing and manipulation
- **Tenacity**: Retry mechanism for API calls
- **dotenv**: Environment variable management

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Azure OpenAI account and API credentials
- Access to EDINET financial data CSV files

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Workshop_02
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**

   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env with your Azure OpenAI credentials
   nano .env
   ```

4. **Configure Environment Variables**

   Edit the `.env` file with your Azure OpenAI credentials:

   ```bash
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_API_BASE=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT_NAME=GPT-4o-mini
   ```

## 🚀 Usage

### Basic Usage

Run the financial analyzer with a CSV file:

```bash
python app.py --file samples/sample01.csv
```

### Command Line Options

| Option   | Description                     | Required |
| -------- | ------------------------------- | -------- |
| `--file` | Path to the CSV file to analyze | Yes      |

### Example Output

```
🏢 Simple Financial Analyzer
==================================================

📊 Extracting data from: samples/sample01.csv
✅ Read 1460 records
✅ Processed data for: Toyota Motor Corporation

🤖 Running 5 Sample Analyses:
==================================================

🔍 Sample 1: What is the company's basic information...
----------------------------------------
Based on the financial data, here is Toyota Motor Corporation's basic information:

**Company Information:**
- Japanese Name: トヨタ自動車株式会社
- English Name: Toyota Motor Corporation
- EDINET Code: E02144

...
```

## 📊 Analysis Capabilities

### 1. Company Overview

- Company names (Japanese & English)
- EDINET code
- Document information

### 2. Financial Growth Analysis

- Net Income growth rate
- EPS (Earnings Per Share) growth
- Asset growth analysis
- Revenue trend analysis

### 3. Financial Ratios

- **ROE (Return on Equity)**: Measures profitability relative to shareholders' equity
- **ROA (Return on Assets)**: Measures how efficiently assets generate profit
- **Equity Ratio**: Measures financial stability and leverage

### 4. EPS Performance Analysis

- Current vs. prior period EPS comparison
- Growth rate calculation
- Performance rating (Excellent/Good/Positive/Declining)

### 5. Investment Summary

- Comprehensive investment analysis
- Strength identification
- Overall recommendation (Buy/Hold/Sell)

## 🗂️ Project Structure

```
Workshop_02/
├── app.py                      # Main application file
├── document_processors.py      # CSV processing and data extraction
├── utils.py                   # Utility functions for file handling
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── samples/                 # Sample CSV files
│   └── sample01.csv
├── outputs/                 # Analysis output files
└── __pycache__/            # Python cache files
```

## 🔍 Key Components

### FinancialAnalyzer Class

The main class that handles financial data processing and AI analysis:

- `extract_data_from_csv()`: Processes EDINET CSV files
- `calculate_growth_rate()`: Calculates growth rates for financial metrics
- `calculate_financial_ratios()`: Computes ROE, ROA, and equity ratios
- `analyze_eps_performance()`: Analyzes EPS performance and trends
- `generate_investment_summary()`: Creates comprehensive investment analysis
- `chat()`: Provides interactive AI-powered financial analysis

## 🛠️ API Integration

### Azure OpenAI Integration

The tool uses Azure OpenAI's function calling feature to:

1. **Structured Analysis**: Uses predefined functions for consistent financial calculations
2. **Intelligent Responses**: Leverages GPT models for natural language analysis
3. **Error Handling**: Implements retry mechanisms for API reliability
4. **Cost Optimization**: Uses appropriate model parameters and token limits

### Function Calling Tools

| Function                      | Purpose                       | Parameters              |
| ----------------------------- | ----------------------------- | ----------------------- |
| `calculate_growth_rate`       | Calculate metric growth rates | `metric` (string)       |
| `calculate_financial_ratios`  | Compute financial ratios      | None                    |
| `get_company_overview`        | Retrieve company information  | None                    |
| `analyze_eps_performance`     | Analyze EPS trends            | None                    |
| `generate_investment_summary` | Create investment analysis    | `focus_area` (optional) |

## 📋 Requirements

### Python Dependencies

```
pandas>=1.5.0
openai>=1.0.0
chardet>=5.0.0
python-dotenv>=1.0.0
tenacity>=8.0.0
```

### System Requirements

- Python 3.8+
- 4GB+ RAM (for processing large CSV files)
- Internet connection (for Azure OpenAI API calls)

## 📄 License

This project is part of the Elevate AI workshop series. Please refer to your workshop materials for licensing information.

## 🤝 Support

For support and questions:

1. Check the troubleshooting section above
2. Review the `chatbot.log` file for detailed error information
3. Ensure all environment variables are correctly configured
4. Verify your Azure OpenAI service is active and accessible

## 🔄 Version History

- **v1.0.0**: Initial release with basic financial analysis capabilities
- Enhanced error handling and validation
- Comprehensive logging system
- Interactive chat interface

---

**Note**: This tool is designed for educational and research purposes as part of the Elevate AI workshop series. Ensure compliance with your organization's data handling and AI usage policies.
