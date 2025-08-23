# 🔗 Integration Testing - Detailed Test Cases

## 📋 Overview
This document contains comprehensive integration test cases for the E-commerce AI Product Advisor Chatbot, focusing on component interactions, data flow, and end-to-end scenarios.

## 🎯 Integration Test Scope
- **Agent-Tool Integration**: LangGraph agent with all tools
- **Service Layer Integration**: LLM, Pinecone, and configuration services
- **UI-Backend Integration**: Streamlit frontend with agent backend
- **Database Integration**: Pinecone vector database connectivity
- **Memory Integration**: Session persistence and state management
- **API Integration**: Azure OpenAI and external service calls

---

## 🤖 Agent-Tool Integration Tests

### TC-INT-001: Complete Search-to-Response Flow
**Priority**: High  
**Category**: End-to-End  

**Description**: Test complete flow from user query to final response

**Test Scenario**:
```
User Input: "Tìm laptop Dell dưới 20 triệu có SSD"
Expected Flow: Intent Analysis → Search Tool → Generation Tool → Response
```

**Test Steps**:
1. Send user query to LangGraph agent
2. Monitor agent state transitions
3. Verify search tool is called with correct parameters
4. Check search results are retrieved from Pinecone
5. Validate generation tool creates contextual response
6. Confirm final response quality

**Expected Results**:
- Intent classified as "search"
- Search tool called with extracted parameters
- Pinecone returns relevant Dell laptops
- Generation tool creates Vietnamese response
- Response includes specific product recommendations
- Total response time < 8 seconds

**Validation Points**:
```python
response = agent.chat("Tìm laptop Dell dưới 20 triệu có SSD")
assert response["success"] is True
assert "search_products" in response["tools_used"]
assert "Dell" in response["response"]
assert response["intent"] == "search"
```

---

### TC-INT-002: Multi-Tool Orchestration
**Priority**: High  
**Category**: Workflow  

**Description**: Test agent coordinating multiple tools in sequence

**Test Scenario**:
```
User Input: "So sánh laptop gaming tốt nhất và gợi ý cho tôi"
Expected Flow: Intent → Search → Compare → Recommend → Generate
```

**Test Steps**:
1. Send complex query requiring multiple tools
2. Monitor tool execution sequence
3. Verify data flows between tools
4. Check intermediate results are preserved
5. Validate final integrated response

**Expected Results**:
- Multiple tools executed in logical order
- Search results feed into comparison
- Comparison results inform recommendations
- Final response integrates all tool outputs
- No data loss between tool calls

**Tool Sequence Validation**:
```python
response = agent.chat("So sánh laptop gaming tốt nhất và gợi ý cho tôi")
tools_used = response["tools_used"]
assert "search_products" in tools_used
assert "compare_products" in tools_used
assert "recommend_products" in tools_used
```

---

### TC-INT-003: Context Preservation Across Tools
**Priority**: High  
**Category**: State Management  

**Description**: Verify context is maintained across multiple tool calls

**Test Conversation**:
```
Turn 1: "Tìm laptop Dell XPS"
Turn 2: "So sánh chúng với MacBook"
Turn 3: "Cái nào tốt hơn cho thiết kế?"
```

**Test Steps**:
1. Execute first turn (search)
2. Store search results in agent state
3. Execute second turn (comparison with context)
4. Verify "chúng" resolves to Dell XPS models
5. Execute third turn (contextual recommendation)
6. Check design-specific analysis

**Expected Results**:
- Search results preserved in agent state
- Context references resolved correctly
- Comparison uses previous search results
- Final recommendation considers design use case
- Conversation coherence maintained

---

## 🗄️ Database Integration Tests

### TC-INT-004: Pinecone Vector Search Integration
**Priority**: High  
**Category**: Database  

**Description**: Test integration with Pinecone vector database

**Test Steps**:
1. Initialize Pinecone service
2. Execute semantic search query
3. Verify vector similarity calculations
4. Check metadata filtering
5. Validate result ranking

**Test Data**:
```python
search_params = {
    "query": "laptop cho lập trình Python",
    "filters": {"category": "laptop", "price_max": 25000000},
    "top_k": 5
}
```

**Expected Results**:
- Connection to Pinecone established
- Query vectorized using embeddings
- Semantic similarity search executed
- Metadata filters applied correctly
- Results ranked by relevance score

**Database Validation**:
```python
results = pinecone_service.search_products(**search_params)
assert len(results) <= 5
assert all(r["price"] <= 25000000 for r in results)
assert all(r["category"] == "laptop" for r in results)
```

---

### TC-INT-005: Data Consistency and Integrity
**Priority**: Medium  
**Category**: Database  

**Description**: Verify data consistency between JSON files and Pinecone

**Test Steps**:
1. Load sample data from JSON files
2. Query same products from Pinecone
3. Compare data consistency
4. Check for missing or corrupted data
5. Validate embedding quality

**Expected Results**:
- All JSON products exist in Pinecone
- Product attributes match between sources
- No data corruption or loss
- Embeddings properly generated
- Metadata accurately indexed

---

## 🌐 Service Layer Integration Tests

### TC-INT-006: LLM Service Integration
**Priority**: High  
**Category**: External API  

**Description**: Test integration with Azure OpenAI LLM service

**Test Components**:
- Intent classification calls
- Response generation calls
- Parameter extraction calls
- Error handling for API failures

**Test Steps**:
1. Configure LLM service with test credentials
2. Execute various LLM operations
3. Monitor API call patterns
4. Test rate limiting and retries
5. Validate response quality

**Expected Results**:
- All LLM operations complete successfully
- API calls properly authenticated
- Rate limiting respected
- Retries work for transient failures
- Response quality meets standards

**API Integration Validation**:
```python
llm_response = llm_service.classify_intent("Tìm laptop Dell")
assert llm_response["intent"] in ["search", "compare", "recommend"]
assert llm_response["confidence"] > 0.7
```

---

### TC-INT-007: Configuration Management Integration
**Priority**: Medium  
**Category**: Configuration  

**Description**: Test configuration loading and environment management

**Test Steps**:
1. Load configuration from various sources
2. Test environment variable override
3. Validate configuration validation
4. Check default value handling
5. Test configuration hot-reload

**Expected Results**:
- Configuration loads from all sources
- Environment variables take precedence
- Invalid configurations rejected
- Defaults applied appropriately
- Hot-reload works without restart

---

## 🖥️ UI-Backend Integration Tests

### TC-INT-008: Streamlit Frontend Integration
**Priority**: High  
**Category**: Frontend  

**Description**: Test Streamlit UI integration with agent backend

**Test Scenarios**:
- User message submission
- Agent response display
- Session management
- Error message handling
- Agent selection (ReAct vs LangGraph)

**Test Steps**:
1. Start Streamlit application
2. Submit test messages through UI
3. Verify backend agent processing
4. Check response display formatting
5. Test session persistence in UI

**Expected Results**:
- Messages submitted successfully to backend
- Agent responses displayed correctly
- Vietnamese text rendered properly
- Session state maintained in UI
- Error messages shown appropriately

---

### TC-INT-009: Real-time Response Streaming
**Priority**: Medium  
**Category**: Frontend  

**Description**: Test real-time response streaming in UI

**Test Steps**:
1. Submit complex query requiring multiple tools
2. Monitor response streaming
3. Check intermediate status updates
4. Verify final response assembly
5. Test user experience during processing

**Expected Results**:
- Processing status shown to user
- Intermediate updates displayed
- Final response assembled correctly
- No UI freezing during processing
- Smooth user experience maintained

---

## 🔄 Memory and State Integration Tests

### TC-INT-010: Session State Persistence
**Priority**: High  
**Category**: Memory  

**Description**: Test session state persistence across interactions

**Test Scenario**:
```python
session_id = "test_integration_session"
conversation_flow = [
    "Tìm laptop Dell",
    "Có model nào dưới 20 triệu?",
    "So sánh 2 model rẻ nhất",
    "Model nào tốt hơn?"
]
```

**Test Steps**:
1. Execute conversation flow with consistent session_id
2. Verify state accumulation after each turn
3. Check context references work correctly
4. Test session retrieval after delay
5. Validate memory cleanup

**Expected Results**:
- Session state grows with each interaction
- Context references resolved correctly
- Session retrievable after time delay
- Memory usage remains reasonable
- Old sessions cleaned up appropriately

---

### TC-INT-011: Cross-Session Data Isolation
**Priority**: Medium  
**Category**: Memory  

**Description**: Verify sessions don't interfere with each other

**Test Setup**:
- Session A: Laptop search conversation
- Session B: Smartphone search conversation
- Concurrent execution

**Test Steps**:
1. Start two parallel sessions
2. Execute different conversation flows
3. Verify no data leakage between sessions
4. Check session-specific context preservation
5. Validate independent state management

**Expected Results**:
- Sessions maintain separate contexts
- No data leakage between sessions
- Independent conversation flows
- Proper session isolation
- Concurrent processing works correctly

---

## 🚨 Error Handling Integration Tests

### TC-INT-012: Cascading Error Recovery
**Priority**: High  
**Category**: Error Handling  

**Description**: Test error recovery across integrated components

**Error Scenarios**:
1. Pinecone service unavailable
2. LLM API timeout
3. Invalid tool responses
4. Memory corruption
5. Configuration errors

**Test Steps**:
1. Simulate each error scenario
2. Monitor error propagation
3. Verify fallback mechanisms
4. Check graceful degradation
5. Test recovery procedures

**Expected Results**:
- Errors don't cascade through system
- Fallback mechanisms activate
- User receives helpful error messages
- System continues functioning
- Recovery possible after error resolution

---

### TC-INT-013: Data Validation Integration
**Priority**: Medium  
**Category**: Data Integrity  

**Description**: Test data validation across component boundaries

**Validation Points**:
- User input sanitization
- Tool parameter validation
- API response validation
- Database query validation
- Response format validation

**Expected Results**:
- Invalid data rejected at boundaries
- Proper error messages generated
- No data corruption occurs
- System remains stable
- Security vulnerabilities prevented

---

## 📊 Performance Integration Tests

### TC-INT-014: End-to-End Performance
**Priority**: High  
**Category**: Performance  

**Description**: Measure performance across integrated system

**Performance Metrics**:
- Total response time
- Component-wise latency
- Memory usage patterns
- Database query performance
- API call efficiency

**Test Scenarios**:
- Simple queries (baseline)
- Complex multi-tool queries
- High-frequency requests
- Large result sets
- Concurrent user simulation

**Performance Targets**:
- Simple queries: < 5 seconds
- Complex queries: < 10 seconds
- Memory usage: < 500MB per session
- Database queries: < 2 seconds
- API calls: < 3 seconds

---

### TC-INT-015: Scalability Integration
**Priority**: Medium  
**Category**: Scalability  

**Description**: Test system behavior under load

**Load Test Scenarios**:
- 10 concurrent users
- 100 requests per minute
- Extended session duration
- Large conversation history
- Peak usage simulation

**Expected Results**:
- System handles target load
- Response times remain acceptable
- Memory usage scales linearly
- No resource leaks
- Graceful degradation under overload

---

## 🧪 Integration Test Automation

### Test Environment Setup
```python
import pytest
from src.agents.langgraph_agent import get_agent_manager
from src.services.pinecone_service import pinecone_service
from src.services.llm_service import llm_service

@pytest.fixture(scope="session")
def integration_environment():
    """Setup integration test environment"""
    # Initialize services
    agent_manager = get_agent_manager()
    
    # Verify external service connectivity
    assert pinecone_service.health_check()
    assert llm_service.health_check()
    
    return {
        "agent": agent_manager.get_agent(),
        "pinecone": pinecone_service,
        "llm": llm_service
    }
```

### End-to-End Test Framework
```python
class TestEndToEndIntegration:
    def test_complete_conversation_flow(self, integration_environment):
        agent = integration_environment["agent"]
        
        # Execute complete conversation
        responses = []
        conversation = [
            "Tìm laptop Dell dưới 20 triệu",
            "So sánh 2 model đầu tiên",
            "Model nào tốt hơn cho lập trình?"
        ]
        
        session_id = "integration_test_session"
        for message in conversation:
            response = agent.chat(message, session_id=session_id)
            responses.append(response)
            assert response["success"] is True
        
        # Validate conversation coherence
        assert len(responses) == 3
        assert "Dell" in responses[0]["response"]
        assert "so sánh" in responses[1]["response"].lower()
        assert "lập trình" in responses[2]["response"].lower()
```

---

**Next**: Continue with performance test cases in `test_cases_performance.md`
