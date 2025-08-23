# 🧪 E-commerce AI Product Advisor Chatbot - Test Suite

## 📋 Overview

This directory contains comprehensive unit tests and integration tests for the **E-commerce AI Product Advisor Chatbot** with LangGraph Agent architecture. The test suite covers all system components, technologies, and functionalities.

## 🎯 Test Coverage

### **Components Tested:**
- ✅ **Configuration Management** (`test_config.py`)
- ✅ **LLM Service** (`test_llm_service.py`) - Azure OpenAI integration
- ✅ **Pinecone Service** (`test_pinecone_service.py`) - Vector database operations
- ✅ **Tools** (`test_tools.py`) - Search, Compare, Recommend, Review, Generation
- ✅ **Agents** (`test_agents.py`) - LangGraph agent workflows
- ✅ **Utilities** (`test_utils.py`) - Logger, prompt helper
- ✅ **Prompts** (`test_prompts.py`) - Prompt management and templates
- ✅ **End-to-End Integration** (`test_end_to_end.py`) - Complete workflows

### **Technologies Tested:**
- 🤖 **LangGraph** - Agent state management and workflows
- 🧠 **LangChain** - LLM integration and tools
- 🔍 **Pinecone** - Vector database operations
- ☁️ **Azure OpenAI** - LLM and embedding services
- 🖥️ **Streamlit** - UI components (integration tests)
- 🇻🇳 **Vietnamese Language** - Text processing and responses

## 🚀 Quick Start

### **Option 1: Run All Tests (Batch File)**
```bash
# Windows
run_all_tests.bat

# This will run all test categories and generate reports
```

### **Option 2: Run All Tests (Python Script)**
```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --types unit integration

# Quick validation (unit + smoke tests only)
python run_tests.py --quick
```

### **Option 3: Manual pytest Commands**
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html -v

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
pytest tests/ -m "smoke" -v              # Smoke tests only
pytest tests/ -m "vietnamese" -v         # Vietnamese language tests
```

## 📁 Directory Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── pytest.ini                 # Pytest settings
├── requirements-test.txt       # Testing dependencies
├── README.md                   # This file
│
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_config.py          # Configuration tests
│   ├── test_llm_service.py     # LLM service tests
│   ├── test_pinecone_service.py # Pinecone service tests
│   ├── test_tools.py           # Tools tests
│   ├── test_agents.py          # Agent tests
│   ├── test_utils.py           # Utilities tests
│   └── test_prompts.py         # Prompt tests
│
├── integration/                # Integration tests
│   ├── __init__.py
│   └── test_end_to_end.py      # End-to-end workflow tests
│
├── fixtures/                   # Test data and fixtures
│   └── test_data.json          # Sample products, reviews, conversations
│
├── mocks/                      # Mock objects and responses
│
└── reports/                    # Generated test reports
    ├── coverage_html/          # HTML coverage report
    ├── coverage.xml            # XML coverage report
    ├── junit.xml               # JUnit test results
    └── test_summary.json       # Comprehensive test summary
```

## 🧪 Test Categories

### **1. Unit Tests** (`tests/unit/`)
Tests individual components in isolation with mocked dependencies.

**Coverage:**
- Configuration loading and validation
- Service initialization and methods
- Tool functionality and error handling
- Agent state management
- Utility functions
- Prompt templates and formatting

**Example:**
```bash
pytest tests/unit/test_tools.py::TestSearchTool::test_search_tool_success -v
```

### **2. Integration Tests** (`tests/integration/`)
Tests component interactions and end-to-end workflows.

**Coverage:**
- Complete conversation flows
- Service integration
- Multi-turn conversations
- Error recovery workflows
- Memory persistence

**Example:**
```bash
pytest tests/integration/test_end_to_end.py::TestEndToEndWorkflows::test_complete_search_workflow -v
```

### **3. Smoke Tests** (Marker: `@pytest.mark.smoke`)
Critical functionality tests for basic system validation.

**Example:**
```bash
pytest tests/ -m "smoke" -v
```

### **4. Vietnamese Language Tests** (Marker: `@pytest.mark.vietnamese`)
Tests specifically for Vietnamese language support.

**Example:**
```bash
pytest tests/ -m "vietnamese" -v
```

## 🔧 Test Configuration

### **Environment Variables**
```bash
TEST_MODE=true                    # Enable test mode
AZURE_OPENAI_API_KEY=test_key    # Mock API key for testing
PINECONE_API_KEY=test_key        # Mock Pinecone key for testing
```

### **Pytest Markers**
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.smoke` - Smoke tests
- `@pytest.mark.vietnamese` - Vietnamese language tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.external` - Tests requiring external services

### **Coverage Settings**
- **Target Coverage**: 80%+
- **Coverage Reports**: HTML, XML, Terminal
- **Excluded Files**: Tests, migrations, settings

## 📊 Test Reports

### **Coverage Report**
- **HTML Report**: `tests/reports/coverage_html/index.html`
- **XML Report**: `tests/reports/coverage.xml`
- **Terminal Report**: Displayed during test execution

### **Test Results**
- **JUnit XML**: `tests/reports/junit.xml`
- **JSON Summary**: `tests/reports/test_summary.json`

### **Opening Reports**
```bash
# Open coverage report in browser (Windows)
start tests/reports/coverage_html/index.html

# Open coverage report in browser (macOS)
open tests/reports/coverage_html/index.html

# Open coverage report in browser (Linux)
xdg-open tests/reports/coverage_html/index.html
```

## 🛠️ Writing New Tests

### **Unit Test Template**
```python
import pytest
from unittest.mock import Mock, patch
from src.your_module import YourClass

class TestYourClass:
    """Test cases for YourClass"""
    
    def test_your_method_success(self):
        """Test successful method execution"""
        # Arrange
        instance = YourClass()
        
        # Act
        result = instance.your_method("test_input")
        
        # Assert
        assert result is not None
        assert result == "expected_output"
    
    def test_your_method_failure(self):
        """Test method failure handling"""
        instance = YourClass()
        
        with pytest.raises(ValueError):
            instance.your_method("invalid_input")
```

### **Integration Test Template**
```python
import pytest
from unittest.mock import patch

@pytest.mark.integration
class TestYourIntegration:
    """Integration tests for your component"""
    
    def test_complete_workflow(self, mock_services):
        """Test complete workflow integration"""
        # Setup
        # Execute
        # Verify
        pass
```

## 🚨 Troubleshooting

### **Common Issues**

1. **Import Errors**
   ```bash
   # Solution: Set PYTHONPATH
   export PYTHONPATH=$PWD/src:$PYTHONPATH  # Linux/macOS
   set PYTHONPATH=%CD%\src;%PYTHONPATH%    # Windows
   ```

2. **Missing Dependencies**
   ```bash
   # Solution: Install test requirements
   pip install -r requirements-test.txt
   ```

3. **Test Timeouts**
   ```bash
   # Solution: Increase timeout or use --timeout flag
   pytest tests/ --timeout=300
   ```

4. **Coverage Issues**
   ```bash
   # Solution: Check coverage configuration in pytest.ini
   pytest tests/ --cov=src --cov-report=term-missing
   ```

### **Debug Mode**
```bash
# Run tests with detailed output
pytest tests/ -v --tb=long --capture=no

# Run specific test with debugging
pytest tests/unit/test_tools.py::TestSearchTool::test_search_tool_success -v -s
```

## 📈 Quality Metrics

### **Current Targets**
- **Test Coverage**: 80%+
- **Test Pass Rate**: 95%+
- **Response Time**: < 8 seconds for complex queries
- **Vietnamese Accuracy**: 90%+
- **Error Recovery**: 95%+

### **Continuous Improvement**
- Add new tests for new features
- Maintain high coverage percentage
- Regular performance benchmarking
- Update test data and scenarios
- Review and refactor test code

## 🤝 Contributing

### **Adding New Tests**
1. Create test file in appropriate directory
2. Follow naming convention: `test_*.py`
3. Use appropriate pytest markers
4. Include docstrings and comments
5. Update this README if needed

### **Test Review Checklist**
- [ ] Tests cover happy path and edge cases
- [ ] Appropriate mocking for external dependencies
- [ ] Clear test names and descriptions
- [ ] Proper assertions and error handling
- [ ] Performance considerations
- [ ] Vietnamese language support where applicable

---

**For questions or support**: Contact the development team or refer to the main project documentation.
