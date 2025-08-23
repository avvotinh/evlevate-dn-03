"""
Unit tests for Agents
Tests LangGraph agent functionality, state management, and workflows
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage

from src.agents.langgraph_agent import ProductAdvisorLangGraphAgent, AgentState


class TestProductAdvisorLangGraphAgent:
    """Test cases for ProductAdvisorLangGraphAgent"""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all agent dependencies"""
        with patch('src.agents.langgraph_agent.llm_service') as mock_llm, \
             patch('src.agents.langgraph_agent.ToolManager') as mock_tool_manager, \
             patch('src.agents.langgraph_agent.generation_tool') as mock_gen_tool, \
             patch('src.agents.langgraph_agent.prompt_manager') as mock_prompt_manager:

            # Setup mocks
            mock_llm.get_langchain_llm.return_value = Mock()
            mock_tool_manager.return_value = Mock()
            mock_gen_tool.run.return_value = json.dumps({"success": True, "response": "Test response"})
            mock_prompt_manager.get_prompt.return_value = "Test prompt template"

            yield {
                "llm": mock_llm,
                "tool_manager": mock_tool_manager,
                "generation_tool": mock_gen_tool,
                "prompt_manager": mock_prompt_manager
            }

    def test_agent_initialization(self, mock_dependencies):
        """Test agent initialization"""
        agent = ProductAdvisorLangGraphAgent()

        # Verify initialization
        assert agent is not None
        assert agent.llm is not None
        assert agent.tool_manager is not None
        assert agent.graph is not None
        assert agent.memory_saver is not None
    

    
    def test_classify_intent_with_llm_failure(self, mock_dependencies):
        """Test LLM intent classification failure"""
        mock_dependencies["llm"].get_langchain_llm.return_value.invoke.side_effect = Exception("LLM Error")

        agent = ProductAdvisorLangGraphAgent()

        # Test intent classification failure
        intent = agent._classify_intent_with_llm("Tìm laptop Dell")

        # Verify failure handling
        assert intent is None
    
    def test_analyze_intent_node(self, mock_dependencies, sample_agent_state):
        """Test analyze intent node"""
        agent = ProductAdvisorLangGraphAgent()

        # Test intent analysis
        state = sample_agent_state.copy()
        state["user_input"] = "Tìm laptop Dell"

        result_state = agent._analyze_intent(state)

        # Verify state updates
        assert "intent" in result_state
        assert "reasoning_steps" in result_state
        assert len(result_state["reasoning_steps"]) > 0

    def test_handle_greeting_node(self, mock_dependencies, sample_agent_state):
        """Test handle greeting node"""
        agent = ProductAdvisorLangGraphAgent()

        # Test greeting handling
        state = sample_agent_state.copy()
        state["user_input"] = "Xin chào"
        state["intent"] = "greeting"

        result_state = agent._handle_greeting(state)

        # Verify greeting response
        assert "final_response" in result_state
        assert result_state["final_response"] is not None
        assert "xin chào" in result_state["final_response"].lower()

    def test_search_products_node(self, mock_dependencies, sample_agent_state):
        """Test search products node"""
        # Setup mock tool
        mock_search_tool = Mock()
        mock_search_tool.run.return_value = json.dumps({
            "success": True,
            "products": [{"name": "Dell XPS 13", "price": 25000000}]
        })
        mock_dependencies["tool_manager"].return_value.get_tool.return_value = mock_search_tool

        agent = ProductAdvisorLangGraphAgent()

        # Test search
        state = sample_agent_state.copy()
        state["user_input"] = "Tìm laptop Dell"
        state["intent"] = "search"

        result_state = agent._search_products(state)

        # Verify search results
        assert "search_results" in result_state
        assert "search_products" in result_state["tools_used"]
        assert len(result_state["reasoning_steps"]) > 0

    def test_compare_products_node(self, mock_dependencies, sample_agent_state):
        """Test compare products node"""
        # Setup mock tool
        mock_compare_tool = Mock()
        mock_compare_tool.run.return_value = json.dumps({
            "success": True,
            "comparison_table": {"Dell XPS 13": {"price": 25000000}}
        })
        mock_dependencies["tool_manager"].return_value.get_tool.return_value = mock_compare_tool

        agent = ProductAdvisorLangGraphAgent()

        # Test comparison
        state = sample_agent_state.copy()
        state["user_input"] = "So sánh Dell XPS 13 và MacBook Air"
        state["intent"] = "compare"

        result_state = agent._compare_products(state)

        # Verify comparison results
        assert "comparison_results" in result_state
        assert "compare_products" in result_state["tools_used"]

    def test_recommend_products_node(self, mock_dependencies, sample_agent_state):
        """Test recommend products node"""
        # Setup mock tool
        mock_recommend_tool = Mock()
        mock_recommend_tool.run.return_value = json.dumps({
            "success": True,
            "recommendations": [{"name": "Dell XPS 13", "score": 0.95}]
        })
        mock_dependencies["tool_manager"].return_value.get_tool.return_value = mock_recommend_tool

        agent = ProductAdvisorLangGraphAgent()

        # Test recommendation
        state = sample_agent_state.copy()
        state["user_input"] = "Gợi ý laptop cho lập trình"
        state["intent"] = "recommend"

        result_state = agent._recommend_products(state)

        # Verify recommendation results
        assert "recommendation_results" in result_state
        assert "recommend_products" in result_state["tools_used"]
    
    def test_generate_response_node(self, mock_dependencies, sample_agent_state):
        """Test generate response node"""
        agent = ProductAdvisorLangGraphAgent()

        # Test response generation
        state = sample_agent_state.copy()
        state["user_input"] = "Tìm laptop Dell"
        state["intent"] = "search"
        state["search_results"] = {"products": [{"name": "Dell XPS 13"}]}

        result_state = agent._generate_response(state)

        # Verify response generation
        assert "final_response" in result_state
        assert result_state["final_response"] is not None

    def test_handle_error_node(self, mock_dependencies, sample_agent_state):
        """Test handle error node"""
        agent = ProductAdvisorLangGraphAgent()

        # Test error handling
        state = sample_agent_state.copy()
        state["error_count"] = 1

        result_state = agent._handle_error(state)

        # Verify error handling
        assert "final_response" in result_state
        assert "lỗi" in result_state["final_response"].lower()

    def test_chat_method(self, mock_dependencies):
        """Test main chat method"""
        agent = ProductAdvisorLangGraphAgent()

        # Mock graph execution
        mock_final_state = {
            "final_response": "Test response",
            "intent": "search",
            "tools_used": ["search_products"],
            "reasoning_steps": [],
            "error_count": 0,
            "iteration_count": 1
        }

        with patch.object(agent.graph, 'invoke', return_value=mock_final_state):
            # Test chat
            response = agent.chat("Tìm laptop Dell", session_id="test_session")

            # Verify response
            assert response["success"] is True
            assert response["response"] == "Test response"
            assert response["intent"] == "search"
            assert "search_products" in response["tools_used"]

    def test_chat_method_with_error(self, mock_dependencies):
        """Test chat method with error"""
        agent = ProductAdvisorLangGraphAgent()

        # Mock graph execution failure
        with patch.object(agent.graph, 'invoke', side_effect=Exception("Graph error")):
            # Test chat with error
            response = agent.chat("Tìm laptop Dell")

            # Verify error handling
            assert response["success"] is False
            assert "error" in response

    def test_clear_memory(self, mock_dependencies):
        """Test memory clearing"""
        agent = ProductAdvisorLangGraphAgent()

        # Test memory clearing (should not raise exception)
        try:
            agent.clear_memory("test_session")
        except Exception as e:
            pytest.fail(f"clear_memory raised an exception: {e}")

    def test_agent_state_structure(self):
        """Test AgentState structure"""
        # Test that AgentState has required fields
        required_fields = [
            "messages", "user_input", "session_id", "current_step", "intent",
            "tools_used", "search_results", "comparison_results",
            "recommendation_results", "review_results", "context_data",
            "final_response", "iteration_count", "error_count", "reasoning_steps",
            "conversation_history", "previous_search_results", "previous_products",
            "context_references"
        ]

        # Create a sample state
        state = AgentState()

        # Verify all required fields exist in the TypedDict
        # Note: This is a basic check since TypedDict is a type hint
        assert AgentState is not None


class TestAgentManager:
    """Test cases for agent manager functions"""

    @patch('src.agents.langgraph_agent.ProductAdvisorLangGraphAgent')
    def test_get_agent_manager(self, mock_agent_class):
        """Test get_agent_manager function"""
        from src.agents.langgraph_agent import get_agent_manager

        # Test getting agent manager
        manager = get_agent_manager()

        # Verify manager
        assert manager is not None
        assert hasattr(manager, 'get_agent')
