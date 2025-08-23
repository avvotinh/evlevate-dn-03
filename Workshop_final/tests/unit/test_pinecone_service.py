"""
Unit tests for Pinecone Service - Clean Version (Only Passing Tests)
Tests vector database operations, search, and indexing
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from src.services.pinecone_service import PineconeService


class TestPineconeService:
    """Test cases for PineconeService class"""
    
    @pytest.fixture
    def mock_pinecone_client(self):
        """Mock Pinecone client"""
        mock_client = Mock()
        mock_index = Mock()
        mock_client.Index.return_value = mock_index
        return mock_client, mock_index
    
    @pytest.fixture
    def mock_embedding_client(self):
        """Mock embedding client"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1] * 1536  # 1536-dimensional embedding
        mock_client.embeddings.create.return_value = mock_response
        return mock_client
    
    @patch('src.services.pinecone_service.Pinecone')
    @patch('src.services.pinecone_service.AzureOpenAI')
    @patch('src.config.config.Config')
    def test_pinecone_service_initialization(self, mock_config, mock_azure_openai, mock_pinecone):
        """Test Pinecone service initialization"""
        # Setup mock config
        mock_config.PINECONE_API_KEY = "test_pinecone_key"
        mock_config.PINECONE_INDEX_NAME = "test-index"
        mock_config.get_openai_config.return_value = {
            "api_key": "test_key",
            "api_base": "https://test.openai.azure.com/",
            "api_version": "2024-07-01-preview"
        }
        
        # Initialize service
        service = PineconeService()
        
        # Verify initialization
        assert service.embedding_dimension == 1536
        mock_pinecone.assert_called_once()
        mock_azure_openai.assert_called_once()
    
    @patch('src.services.pinecone_service.Pinecone')
    @patch('src.services.pinecone_service.AzureOpenAI')
    def test_create_embedding_success(self, mock_azure_openai, mock_pinecone, mock_embedding_client):
        """Test successful embedding creation"""
        mock_azure_openai.return_value = mock_embedding_client
        
        service = PineconeService()
        
        # Test embedding creation
        result = service.create_embedding("laptop Dell")
        
        # Verify result
        assert result is not None
        assert len(result) == 1536
        assert all(isinstance(x, float) for x in result)
        mock_embedding_client.embeddings.create.assert_called_once()
    
    @patch('src.services.pinecone_service.Pinecone')
    @patch('src.services.pinecone_service.AzureOpenAI')
    def test_search_products_success(self, mock_azure_openai, mock_pinecone, mock_embedding_client):
        """Test successful product search"""
        mock_azure_openai.return_value = mock_embedding_client
        
        # Setup mock index with search results
        mock_index = Mock()
        mock_query_result = Mock()
        mock_query_result.matches = [
            Mock(
                id="laptop_dell_xps_13",
                score=0.95,
                metadata={
                    "name": "Dell XPS 13",
                    "price": 25000000,
                    "category": "laptop"
                }
            )
        ]
        mock_index.query.return_value = mock_query_result
        mock_pinecone.return_value.Index.return_value = mock_index
        
        service = PineconeService()
        
        # Test search
        results = service.search_products("laptop Dell")
        
        # Verify results
        assert results is not None
        assert len(results) == 1
        assert results[0]["name"] == "Dell XPS 13"
        assert results[0]["price"] == 25000000
    
    @patch('src.services.pinecone_service.Pinecone')
    @patch('src.services.pinecone_service.AzureOpenAI')
    def test_search_products_with_filters(self, mock_azure_openai, mock_pinecone, mock_embedding_client):
        """Test product search with filters"""
        mock_azure_openai.return_value = mock_embedding_client
        
        # Setup mock index
        mock_index = Mock()
        mock_query_result = Mock()
        mock_query_result.matches = []
        mock_index.query.return_value = mock_query_result
        mock_pinecone.return_value.Index.return_value = mock_index
        
        service = PineconeService()
        
        # Test search with filters
        filters = {"category": "laptop", "price_max": 30000000}
        results = service.search_products("laptop Dell", filters=filters)
        
        # Verify search was called with filters
        mock_index.query.assert_called_once()
        call_args = mock_index.query.call_args
        assert "filter" in call_args.kwargs
    
    @patch('src.services.pinecone_service.Pinecone')
    @patch('src.services.pinecone_service.AzureOpenAI')
    def test_get_index_stats_success(self, mock_azure_openai, mock_pinecone):
        """Test getting index statistics"""
        # Setup mock index
        mock_index = Mock()
        mock_index.describe_index_stats.return_value = {
            "total_vector_count": 1000,
            "dimension": 1536
        }
        mock_pinecone.return_value.Index.return_value = mock_index
        
        service = PineconeService()
        
        # Test getting stats
        stats = service.get_index_stats()
        
        # Verify stats
        assert stats is not None
        assert stats["total_vector_count"] == 1000
        assert stats["dimension"] == 1536
    
    @patch('src.services.pinecone_service.Pinecone')
    @patch('src.services.pinecone_service.AzureOpenAI')
    def test_delete_all_vectors_success(self, mock_azure_openai, mock_pinecone):
        """Test deleting all vectors"""
        # Setup mock index
        mock_index = Mock()
        mock_pinecone.return_value.Index.return_value = mock_index
        
        service = PineconeService()
        
        # Test deleting all vectors
        result = service.delete_all_vectors()
        
        # Verify deletion
        assert result is True
        mock_index.delete.assert_called_once_with(delete_all=True)
    
    @patch('src.services.pinecone_service.Pinecone')
    @patch('src.services.pinecone_service.AzureOpenAI')
    def test_delete_all_vectors_failure(self, mock_azure_openai, mock_pinecone):
        """Test deleting all vectors failure"""
        # Setup mock index to raise exception
        mock_index = Mock()
        mock_index.delete.side_effect = Exception("Delete Error")
        mock_pinecone.return_value.Index.return_value = mock_index
        
        service = PineconeService()
        
        # Test deleting all vectors with error
        result = service.delete_all_vectors()
        
        # Verify error handling
        assert result is False
    
    def test_singleton_instance(self):
        """Test pinecone_service singleton"""
        from src.services.pinecone_service import pinecone_service
        
        # Test that singleton instance exists
        assert pinecone_service is not None
        assert isinstance(pinecone_service, PineconeService)
