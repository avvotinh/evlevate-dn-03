"""
Pytest configuration and shared fixtures for all tests
"""

import os
import sys
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test configuration - Set all required environment variables
os.environ["TEST_MODE"] = "true"
os.environ["AZURE_OPENAI_API_KEY"] = "test_key_12345"
os.environ["PINECONE_API_KEY"] = "test_key_12345"
os.environ["AZURE_OPENAI_API_ENDPOINT"] = "https://test.openai.azure.com/"
os.environ["AZURE_OPENAI_EMBEDDING_API_KEY"] = "test_embedding_key_12345"
os.environ["AZURE_OPENAI_LLM_API_KEY"] = "test_llm_key_12345"
os.environ["PINECONE_INDEX_NAME"] = "test-index"


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "test_mode": True,
        "mock_services": True,
        "test_data_path": os.path.join(os.path.dirname(__file__), "fixtures"),
        "timeout": 30,
        "max_retries": 3
    }


@pytest.fixture
def sample_products():
    """Sample product data for testing"""
    return [
        {
            "id": "laptop_dell_xps_13",
            "name": "Dell XPS 13",
            "brand": "Dell",
            "category": "laptop",
            "price": 25000000,
            "currency": "VND",
            "specifications": {
                "processor": "Intel Core i7-1165G7",
                "ram": "16GB LPDDR4x",
                "storage": "512GB SSD",
                "display": "13.3 inch FHD+"
            },
            "features": ["Ultrabook", "Long Battery Life", "Premium Design"],
            "rating": 4.5,
            "review_count": 128,
            "availability": "in_stock"
        },
        {
            "id": "iphone_15_pro",
            "name": "iPhone 15 Pro",
            "brand": "Apple",
            "category": "smartphone",
            "price": 28000000,
            "currency": "VND",
            "specifications": {
                "processor": "A17 Pro",
                "ram": "8GB",
                "storage": "128GB",
                "display": "6.1 inch Super Retina XDR"
            },
            "features": ["Pro Camera System", "Titanium Design", "Action Button"],
            "rating": 4.7,
            "review_count": 256,
            "availability": "in_stock"
        }
    ]


@pytest.fixture
def sample_reviews():
    """Sample review data for testing"""
    return [
        {
            "id": "review_1",
            "product_id": "laptop_dell_xps_13",
            "rating": 5,
            "title": "Excellent laptop for work",
            "content": "Great performance and battery life. Perfect for programming.",
            "sentiment": "positive",
            "helpful_count": 15
        },
        {
            "id": "review_2", 
            "product_id": "iphone_15_pro",
            "rating": 4,
            "title": "Good phone but expensive",
            "content": "Camera quality is amazing but price is quite high.",
            "sentiment": "mixed",
            "helpful_count": 8
        }
    ]


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    mock_service = Mock()
    mock_service.classify_intent.return_value = {
        "intent": "search",
        "confidence": 0.9,
        "parameters": {"query": "laptop Dell"}
    }
    mock_service.generate_response.return_value = {
        "response": "Tôi đã tìm thấy một số laptop Dell phù hợp với yêu cầu của bạn.",
        "success": True
    }
    mock_service.health_check.return_value = True
    return mock_service


@pytest.fixture
def mock_pinecone_service():
    """Mock Pinecone service for testing"""
    mock_service = Mock()
    mock_service.search_products.return_value = [
        {
            "id": "laptop_dell_xps_13",
            "name": "Dell XPS 13",
            "price": 25000000,
            "similarity_score": 0.95
        }
    ]
    mock_service.upsert_products.return_value = True
    mock_service.health_check.return_value = True
    mock_service.get_index_stats.return_value = {"total_vector_count": 100}
    return mock_service


@pytest.fixture
def mock_search_tool():
    """Mock search tool for testing"""
    mock_tool = Mock()
    mock_tool.name = "search_products"
    mock_tool.description = "Search for products"
    mock_tool.run.return_value = json.dumps({
        "success": True,
        "products": [
            {
                "name": "Dell XPS 13",
                "price": 25000000,
                "category": "laptop"
            }
        ],
        "total_found": 1
    })
    return mock_tool


@pytest.fixture
def mock_compare_tool():
    """Mock compare tool for testing"""
    mock_tool = Mock()
    mock_tool.name = "compare_products"
    mock_tool.description = "Compare multiple products"
    mock_tool.run.return_value = json.dumps({
        "success": True,
        "comparison_table": {
            "Dell XPS 13": {"price": 25000000, "rating": 4.5},
            "MacBook Air": {"price": 30000000, "rating": 4.6}
        },
        "recommendation": "Dell XPS 13 offers better value for money"
    })
    return mock_tool


@pytest.fixture
def mock_recommend_tool():
    """Mock recommend tool for testing"""
    mock_tool = Mock()
    mock_tool.name = "recommend_products"
    mock_tool.description = "Recommend products based on preferences"
    mock_tool.run.return_value = json.dumps({
        "success": True,
        "recommendations": [
            {
                "name": "Dell XPS 13",
                "score": 0.95,
                "reason": "Perfect match for your requirements"
            }
        ],
        "total_recommendations": 1
    })
    return mock_tool


@pytest.fixture
def mock_review_tool():
    """Mock review tool for testing"""
    mock_tool = Mock()
    mock_tool.name = "get_reviews"
    mock_tool.description = "Get product reviews and analysis"
    mock_tool.run.return_value = json.dumps({
        "success": True,
        "reviews": [
            {
                "rating": 5,
                "content": "Excellent laptop",
                "sentiment": "positive"
            }
        ],
        "average_rating": 4.5,
        "sentiment_summary": "Overall positive"
    })
    return mock_tool


@pytest.fixture
def mock_tool_manager(mock_search_tool, mock_compare_tool, mock_recommend_tool, mock_review_tool):
    """Mock tool manager with all tools"""
    mock_manager = Mock()
    mock_manager.get_all_tools.return_value = [
        mock_search_tool, mock_compare_tool, mock_recommend_tool, mock_review_tool
    ]
    mock_manager.get_tool.side_effect = lambda name: {
        "search": mock_search_tool,
        "compare": mock_compare_tool,
        "recommend": mock_recommend_tool,
        "review": mock_review_tool
    }.get(name)
    mock_manager.get_tool_names.return_value = ["search", "compare", "recommend", "review"]
    return mock_manager


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history for testing"""
    return [
        {"role": "user", "content": "Xin chào"},
        {"role": "assistant", "content": "Xin chào! Tôi có thể giúp gì cho bạn?"},
        {"role": "user", "content": "Tìm laptop Dell"},
        {"role": "assistant", "content": "Tôi đã tìm thấy một số laptop Dell phù hợp..."}
    ]


@pytest.fixture
def sample_agent_state():
    """Sample agent state for testing"""
    return {
        "messages": [],
        "user_input": "Tìm laptop Dell",
        "session_id": "test_session_123",
        "current_step": "search",
        "intent": "search",
        "tools_used": [],
        "search_results": None,
        "comparison_results": None,
        "recommendation_results": None,
        "review_results": None,
        "context_data": None,
        "final_response": None,
        "iteration_count": 0,
        "error_count": 0,
        "reasoning_steps": [],
        "conversation_history": [],
        "previous_search_results": None,
        "previous_products": None,
        "context_references": None
    }


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    mock_config = Mock()
    mock_config.PINECONE_API_KEY = "test_pinecone_key"
    mock_config.PINECONE_INDEX_NAME = "test-index"
    mock_config.AZURE_OPENAI_API_ENDPOINT = "https://test.openai.azure.com/"
    mock_config.AZURE_OPENAI_API_VERSION = "2024-07-01-preview"
    mock_config.AZURE_OPENAI_EMBEDDING_API_KEY = "test_embedding_key"
    mock_config.AZURE_OPENAI_LLM_API_KEY = "test_llm_key"
    mock_config.DEFAULT_TOP_K = 5
    mock_config.TEMPERATURE = 0.7
    mock_config.MAX_TOKENS = 1000
    return mock_config


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Set test mode
    os.environ["TEST_MODE"] = "true"

    # Mock external services by default - make them always succeed
    with patch('src.services.pinecone_service.Pinecone') as mock_pinecone, \
         patch('src.services.llm_service.AzureOpenAI') as mock_azure_openai, \
         patch('openai.AzureOpenAI') as mock_openai:

        # Setup successful mocks
        mock_pinecone.return_value = Mock()
        mock_azure_openai.return_value = Mock()
        mock_openai.return_value = Mock()

        yield


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "ui: UI tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "external: Tests requiring external services")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to integration tests
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
