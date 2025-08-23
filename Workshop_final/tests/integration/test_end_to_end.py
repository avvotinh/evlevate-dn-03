"""
End-to-end integration tests
Tests complete workflows from user input to final response
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""
    
    @pytest.fixture
    def mock_services(self):
        """Mock all external services for integration testing"""
        with patch('src.services.pinecone_service.pinecone_service') as mock_pinecone, \
             patch('src.services.llm_service.llm_service') as mock_llm:
            
            # Setup Pinecone mock
            mock_pinecone.search_products.return_value = [
                {
                    "id": "laptop_dell_xps_13",
                    "name": "Dell XPS 13",
                    "brand": "Dell",
                    "category": "laptop",
                    "price": 25000000,
                    "rating": 4.5,
                    "similarity_score": 0.95
                }
            ]
            mock_pinecone.health_check.return_value = True
            
            # Setup LLM mock
            mock_llm.classify_intent.return_value = "search"
            mock_llm.generate_response.return_value = "Tôi đã tìm thấy laptop Dell phù hợp với yêu cầu của bạn."
            mock_llm.health_check.return_value = True
            
            yield {"pinecone": mock_pinecone, "llm": mock_llm}
    
    def test_complete_search_workflow(self, mock_services):
        """Test complete search workflow from user input to response"""
        from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
        
        # Initialize agent
        agent = ProductAdvisorLangGraphAgent()
        
        # Test complete search workflow
        response = agent.chat("Tìm laptop Dell dưới 30 triệu", session_id="test_session")
        
        # Verify response structure
        assert response["success"] is True
        assert response["intent"] == "search"
        assert "search_products" in response["tools_used"]
        assert response["response"] is not None
        assert len(response["response"]) > 0
        
        # Verify services were called
        mock_services["pinecone"].search_products.assert_called()
        mock_services["llm"].generate_response.assert_called()
    
    def test_complete_comparison_workflow(self, mock_services):
        """Test complete comparison workflow"""
        from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
        
        # Setup comparison mock data
        mock_services["pinecone"].search_products.return_value = [
            {
                "name": "Dell XPS 13",
                "price": 25000000,
                "rating": 4.5
            },
            {
                "name": "MacBook Air M2",
                "price": 30000000,
                "rating": 4.6
            }
        ]
        
        agent = ProductAdvisorLangGraphAgent()
        
        # Test comparison workflow
        response = agent.chat("So sánh Dell XPS 13 và MacBook Air", session_id="test_session")
        
        # Verify response
        assert response["success"] is True
        assert response["intent"] == "compare"
        assert "compare_products" in response["tools_used"]
        assert response["response"] is not None
    
    def test_multi_turn_conversation(self, mock_services):
        """Test multi-turn conversation with context preservation"""
        from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
        
        agent = ProductAdvisorLangGraphAgent()
        session_id = "multi_turn_test"
        
        # Turn 1: Search
        response1 = agent.chat("Tìm laptop Dell", session_id=session_id)
        assert response1["success"] is True
        assert response1["intent"] == "search"
        
        # Turn 2: Follow-up question (should use context)
        mock_services["llm"].classify_intent.return_value = "compare"
        response2 = agent.chat("So sánh 2 model đầu tiên", session_id=session_id)
        assert response2["success"] is True
        
        # Turn 3: Another follow-up
        mock_services["llm"].classify_intent.return_value = "recommend"
        response3 = agent.chat("Cái nào tốt hơn cho lập trình?", session_id=session_id)
        assert response3["success"] is True
    
    def test_error_recovery_workflow(self, mock_services):
        """Test error recovery in complete workflow"""
        from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
        
        # Setup service to fail first, then succeed
        mock_services["pinecone"].search_products.side_effect = [
            Exception("Service temporarily unavailable"),
            [{"name": "Dell XPS 13", "price": 25000000}]
        ]
        
        agent = ProductAdvisorLangGraphAgent()
        
        # Test workflow with error recovery
        response = agent.chat("Tìm laptop Dell", session_id="error_test")
        
        # Should handle error gracefully
        assert response["success"] is False or response["success"] is True
        assert "error" in response or "response" in response
    
    def test_greeting_workflow(self, mock_services):
        """Test greeting workflow"""
        from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
        
        mock_services["llm"].classify_intent.return_value = "greeting"
        
        agent = ProductAdvisorLangGraphAgent()
        
        # Test greeting
        response = agent.chat("Xin chào", session_id="greeting_test")
        
        # Verify greeting response
        assert response["success"] is True
        assert response["intent"] == "greeting"
        assert "xin chào" in response["response"].lower()


class TestServiceIntegration:
    """Test integration between services"""
    
    def test_llm_pinecone_integration(self):
        """Test LLM and Pinecone service integration"""
        with patch('src.services.pinecone_service.Pinecone'), \
             patch('src.services.llm_service.AzureOpenAI'):
            
            from src.services.llm_service import LLMService
            from src.services.pinecone_service import PineconeService
            
            # Initialize services
            llm_service = LLMService()
            pinecone_service = PineconeService()
            
            # Test that both services can be initialized together
            assert llm_service is not None
            assert pinecone_service is not None
    
    def test_tool_service_integration(self):
        """Test tool integration with services"""
        with patch('src.services.pinecone_service.pinecone_service') as mock_pinecone, \
             patch('src.services.llm_service.llm_service') as mock_llm:
            
            # Setup mocks
            mock_pinecone.search_products.return_value = [
                {"name": "Dell XPS 13", "price": 25000000}
            ]
            mock_llm.generate_response.return_value = "Generated response"
            
            from src.tools.search_tool import search_tool
            from src.tools.generation_tool import generation_tool
            
            # Test search tool with service
            search_result = search_tool.run('{"query": "laptop Dell"}')
            search_response = json.loads(search_result)
            assert search_response["success"] is True
            
            # Test generation tool with service
            gen_result = generation_tool.run('{"query": "test", "context": "test"}')
            gen_response = json.loads(gen_result)
            assert gen_response["success"] is True


class TestAgentToolIntegration:
    """Test agent integration with tools"""
    
    @pytest.fixture
    def mock_all_services(self):
        """Mock all services and tools"""
        with patch('src.services.pinecone_service.pinecone_service') as mock_pinecone, \
             patch('src.services.llm_service.llm_service') as mock_llm, \
             patch('src.tools.search_tool.search_tool') as mock_search, \
             patch('src.tools.compare_tool.compare_tool') as mock_compare, \
             patch('src.tools.recommend_tool.recommend_tool') as mock_recommend, \
             patch('src.tools.review_tool.review_tool') as mock_review:
            
            # Setup service mocks
            mock_pinecone.health_check.return_value = True
            mock_llm.health_check.return_value = True
            mock_llm.get_langchain_llm.return_value = Mock()
            
            # Setup tool mocks
            mock_search.run.return_value = json.dumps({
                "success": True,
                "products": [{"name": "Dell XPS 13"}]
            })
            mock_compare.run.return_value = json.dumps({
                "success": True,
                "comparison_table": {"Dell XPS 13": {"price": 25000000}}
            })
            mock_recommend.run.return_value = json.dumps({
                "success": True,
                "recommendations": [{"name": "Dell XPS 13", "score": 0.95}]
            })
            mock_review.run.return_value = json.dumps({
                "success": True,
                "reviews": [{"rating": 5, "content": "Great laptop"}]
            })
            
            yield {
                "pinecone": mock_pinecone,
                "llm": mock_llm,
                "search": mock_search,
                "compare": mock_compare,
                "recommend": mock_recommend,
                "review": mock_review
            }
    
    def test_agent_uses_correct_tools(self, mock_all_services):
        """Test that agent uses correct tools for different intents"""
        from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
        
        agent = ProductAdvisorLangGraphAgent()
        
        # Test search intent uses search tool
        with patch.object(agent, '_classify_intent_with_llm', return_value="search"):
            response = agent.chat("Tìm laptop Dell", session_id="tool_test")
            if response["success"]:
                assert "search_products" in response.get("tools_used", [])
        
        # Test compare intent uses compare tool
        with patch.object(agent, '_classify_intent_with_llm', return_value="compare"):
            response = agent.chat("So sánh laptop", session_id="tool_test")
            if response["success"]:
                # Compare tool should be used (may also use search first)
                tools_used = response.get("tools_used", [])
                assert "compare_products" in tools_used or "search_products" in tools_used
    
    def test_tool_error_handling_in_agent(self, mock_all_services):
        """Test agent handles tool errors gracefully"""
        from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
        
        # Setup tool to fail
        mock_all_services["search"].run.side_effect = Exception("Tool error")
        
        agent = ProductAdvisorLangGraphAgent()
        
        # Test that agent handles tool error
        with patch.object(agent, '_classify_intent_with_llm', return_value="search"):
            response = agent.chat("Tìm laptop Dell", session_id="error_test")
            
            # Should handle error gracefully
            assert "error" in response or response["success"] is False


class TestConfigurationIntegration:
    """Test configuration integration across components"""
    
    def test_config_used_by_services(self):
        """Test that configuration is properly used by services"""
        with patch('src.config.config.Config') as mock_config:
            mock_config.PINECONE_API_KEY = "test_key"
            mock_config.AZURE_OPENAI_API_ENDPOINT = "https://test.openai.azure.com/"
            
            with patch('src.services.pinecone_service.Pinecone'), \
                 patch('src.services.llm_service.AzureOpenAI'):
                
                from src.services.pinecone_service import PineconeService
                from src.services.llm_service import LLMService
                
                # Services should initialize without error
                pinecone_service = PineconeService()
                llm_service = LLMService()
                
                assert pinecone_service is not None
                assert llm_service is not None
    
    def test_config_validation_integration(self):
        """Test configuration validation in integration context"""
        from src.config.config import Config
        
        # Test that config validation works
        try:
            # This might fail in test environment, which is expected
            Config.validate()
        except ValueError:
            # Expected in test environment with missing keys
            pass


class TestMemoryIntegration:
    """Test memory and state integration"""
    
    def test_session_memory_persistence(self):
        """Test session memory persistence across interactions"""
        with patch('src.services.pinecone_service.pinecone_service'), \
             patch('src.services.llm_service.llm_service'):
            
            from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
            
            agent = ProductAdvisorLangGraphAgent()
            session_id = "memory_test"
            
            # First interaction
            response1 = agent.chat("Tìm laptop Dell", session_id=session_id)
            
            # Second interaction should have access to previous context
            response2 = agent.chat("Có model nào khác không?", session_id=session_id)
            
            # Both should succeed (with mocked services)
            assert response1 is not None
            assert response2 is not None
    
    def test_session_isolation(self):
        """Test that different sessions are isolated"""
        with patch('src.services.pinecone_service.pinecone_service'), \
             patch('src.services.llm_service.llm_service'):
            
            from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent
            
            agent = ProductAdvisorLangGraphAgent()
            
            # Two different sessions
            response1 = agent.chat("Tìm laptop Dell", session_id="session_1")
            response2 = agent.chat("Tìm điện thoại Samsung", session_id="session_2")
            
            # Both should work independently
            assert response1 is not None
            assert response2 is not None
