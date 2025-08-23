# 🤖 Agent Testing - Detailed Test Cases

## 📋 Overview
This document contains comprehensive test cases for both ReAct Agent and LangGraph Agent implementations in the E-commerce AI Product Advisor Chatbot.

## 🎯 Test Scope
- **LangGraph Agent**: Primary agent with state management and graph workflows
- **ReAct Agent**: Legacy agent for comparison and fallback
- **Agent State Management**: Memory persistence and context handling
- **Intent Classification**: Understanding user requests and routing
- **Tool Orchestration**: Proper tool selection and execution

---

## 🧪 Test Cases

### TC-AGENT-001: LangGraph Agent Initialization
**Priority**: High  
**Category**: Functional  

**Description**: Verify LangGraph agent initializes correctly with all components

**Prerequisites**:
- Environment variables configured
- Dependencies installed
- Sample data loaded in Pinecone

**Test Steps**:
1. Import LangGraph agent module
2. Initialize agent manager
3. Get agent instance
4. Verify agent state structure
5. Check tool manager integration

**Expected Results**:
- Agent initializes without errors
- All tools are loaded (search, compare, recommend, review)
- State graph is properly constructed
- Memory saver is configured
- Session management is ready

**Validation Criteria**:
```python
assert agent is not None
assert len(agent.tool_manager.get_all_tools()) == 4
assert agent.memory_saver is not None
assert agent.graph is not None
```

---

### TC-AGENT-002: Basic Chat Functionality
**Priority**: High  
**Category**: Functional  

**Description**: Test basic chat interaction with simple queries

**Test Data**:
- Input: "Xin chào"
- Input: "Tìm laptop Dell"
- Input: "Cảm ơn"

**Test Steps**:
1. Start new chat session
2. Send greeting message
3. Send product search request
4. Send closing message
5. Verify responses are appropriate

**Expected Results**:
- Greeting response is welcoming and informative
- Product search triggers search tool
- Closing response is polite
- All responses are in Vietnamese
- Response time < 8 seconds

**Pass Criteria**:
- All responses are contextually appropriate
- No errors or exceptions
- Proper Vietnamese language usage

---

### TC-AGENT-003: Intent Classification Accuracy
**Priority**: High  
**Category**: Functional  

**Description**: Verify agent correctly identifies user intents

**Test Data**:
```python
test_intents = [
    ("Tìm laptop gaming", "search"),
    ("So sánh iPhone 15 và Samsung S24", "compare"),
    ("Gợi ý điện thoại dưới 10 triệu", "recommend"),
    ("Đánh giá MacBook Air M2", "review"),
    ("Cảm ơn bạn", "general"),
    ("Laptop nào tốt nhất?", "recommend")
]
```

**Test Steps**:
1. For each test case:
   - Send user input to agent
   - Capture intent classification result
   - Verify correct intent is identified
   - Check appropriate tool is selected

**Expected Results**:
- Intent classification accuracy > 90%
- Correct tools are invoked for each intent
- Ambiguous intents trigger clarification

**Validation**:
```python
for input_text, expected_intent in test_intents:
    result = agent.chat(input_text)
    assert result["intent"] == expected_intent
```

---

### TC-AGENT-004: Multi-turn Conversation Context
**Priority**: High  
**Category**: Functional  

**Description**: Test conversation context preservation across multiple turns

**Test Scenario**:
```
Turn 1: "Tìm laptop Dell dưới 20 triệu"
Turn 2: "Có những model nào?"
Turn 3: "So sánh 2 model đầu tiên"
Turn 4: "Model nào tốt hơn cho lập trình?"
```

**Test Steps**:
1. Start new session with session_id
2. Execute conversation turns sequentially
3. Verify context is maintained
4. Check reference resolution ("2 model đầu tiên")
5. Validate personalized recommendations

**Expected Results**:
- Each turn builds on previous context
- References are resolved correctly
- Recommendations become more specific
- Session state persists between turns

**Context Validation**:
- Previous search results are referenced
- Product names are resolved from context
- User preferences are accumulated

---

### TC-AGENT-005: Session Memory Persistence
**Priority**: High  
**Category**: Functional  

**Description**: Verify session memory persists across application restarts

**Test Steps**:
1. Start conversation with session_id="test_session"
2. Perform product search
3. Save session state
4. Restart agent/application
5. Continue conversation with same session_id
6. Reference previous search results

**Expected Results**:
- Session state is restored correctly
- Previous conversation history is available
- Context references work across restarts
- No data loss occurs

**Validation**:
```python
# Before restart
result1 = agent.chat("Tìm laptop Dell", session_id="test_session")

# After restart
agent = get_new_agent_instance()
result2 = agent.chat("So sánh chúng", session_id="test_session")
assert "Dell" in result2["response"]  # Context preserved
```

---

### TC-AGENT-006: Error Handling and Recovery
**Priority**: High  
**Category**: Error Handling  

**Description**: Test agent behavior when tools fail or return errors

**Test Scenarios**:
1. Pinecone service unavailable
2. LLM service timeout
3. Invalid tool parameters
4. Empty search results
5. Malformed user input

**Test Steps**:
1. Mock service failures
2. Send requests that trigger each error
3. Verify graceful error handling
4. Check fallback mechanisms
5. Validate error messages are user-friendly

**Expected Results**:
- No application crashes
- User-friendly error messages in Vietnamese
- Fallback suggestions provided
- Agent continues functioning after errors
- Error count is tracked in state

---

### TC-AGENT-007: Tool Selection Logic
**Priority**: Medium  
**Category**: Functional  

**Description**: Verify agent selects appropriate tools based on user input

**Test Cases**:
```python
tool_selection_tests = [
    ("Tìm laptop HP", ["search_tool"]),
    ("So sánh iPhone và Samsung", ["search_tool", "compare_tool"]),
    ("Gợi ý điện thoại tốt", ["recommend_tool"]),
    ("Đánh giá MacBook", ["search_tool", "review_tool"]),
    ("Laptop nào phù hợp với tôi?", ["recommend_tool"])
]
```

**Test Steps**:
1. For each test case, send input to agent
2. Monitor tool execution sequence
3. Verify correct tools are called
4. Check tool parameters are extracted correctly
5. Validate tool results are used appropriately

**Expected Results**:
- Correct tools selected for each query type
- Tools called in logical sequence
- Parameters extracted accurately
- Results integrated properly

---

### TC-AGENT-008: Performance Benchmarking
**Priority**: Medium  
**Category**: Performance  

**Description**: Measure agent response times for different query types

**Test Scenarios**:
- Simple search: "Tìm laptop Dell"
- Complex comparison: "So sánh 3 laptop gaming tốt nhất"
- Recommendation: "Gợi ý điện thoại phù hợp với sinh viên"
- Multi-tool query: "Tìm và so sánh iPhone mới nhất"

**Performance Targets**:
- Simple queries: < 5 seconds
- Complex queries: < 8 seconds
- Multi-tool queries: < 10 seconds
- Memory usage: < 500MB per session

**Measurement Points**:
- Total response time
- Individual tool execution time
- LLM API call duration
- Database query time
- Memory consumption

---

### TC-AGENT-009: Concurrent Session Handling
**Priority**: Medium  
**Category**: Performance  

**Description**: Test agent handling multiple concurrent sessions

**Test Setup**:
- 5 concurrent sessions
- Different conversation flows per session
- Mixed query types
- Session isolation verification

**Test Steps**:
1. Start 5 parallel sessions
2. Execute different conversations simultaneously
3. Verify session isolation
4. Check memory usage scaling
5. Validate response quality consistency

**Expected Results**:
- Sessions don't interfere with each other
- Response quality maintained across all sessions
- Memory usage scales linearly
- No session data leakage

---

### TC-AGENT-010: Vietnamese Language Handling
**Priority**: High  
**Category**: Functional  

**Description**: Verify proper Vietnamese language processing

**Test Cases**:
- Diacritics: "Tìm điện thoại có màn hình đẹp"
- Colloquial: "Cho tôi xem laptop xịn xò"
- Technical terms: "Laptop có CPU Intel Core i7"
- Mixed language: "Tìm iPhone 15 Pro Max"

**Validation Points**:
- Correct intent understanding
- Proper parameter extraction
- Vietnamese response generation
- Technical term recognition
- Cultural context awareness

**Expected Results**:
- 90%+ accuracy in Vietnamese understanding
- Responses maintain Vietnamese language
- Technical terms handled correctly
- Cultural nuances respected

---

## 📊 Test Execution Matrix

| Test Case | Priority | Automation | Status | Notes |
|-----------|----------|------------|--------|-------|
| TC-AGENT-001 | High | Yes | ⏳ Pending | Core functionality |
| TC-AGENT-002 | High | Yes | ⏳ Pending | Basic chat flow |
| TC-AGENT-003 | High | Yes | ⏳ Pending | Intent accuracy critical |
| TC-AGENT-004 | High | Partial | ⏳ Pending | Manual validation needed |
| TC-AGENT-005 | High | Yes | ⏳ Pending | Memory persistence |
| TC-AGENT-006 | High | Yes | ⏳ Pending | Error scenarios |
| TC-AGENT-007 | Medium | Yes | ⏳ Pending | Tool selection logic |
| TC-AGENT-008 | Medium | Yes | ⏳ Pending | Performance benchmarks |
| TC-AGENT-009 | Medium | Yes | ⏳ Pending | Concurrency testing |
| TC-AGENT-010 | High | Partial | ⏳ Pending | Language validation |

## 🔧 Test Automation Framework

### Unit Test Structure
```python
import pytest
from src.agents.langgraph_agent import get_agent_manager

class TestLangGraphAgent:
    @pytest.fixture
    def agent(self):
        return get_agent_manager().get_agent()
    
    def test_agent_initialization(self, agent):
        assert agent is not None
        # Additional assertions...
    
    def test_basic_chat(self, agent):
        response = agent.chat("Xin chào")
        assert response["success"] is True
        # Additional validations...
```

### Integration Test Setup
```python
@pytest.mark.integration
class TestAgentIntegration:
    def test_multi_turn_conversation(self):
        # Multi-turn conversation test
        pass
    
    def test_session_persistence(self):
        # Session memory test
        pass
```

---

**Next**: Continue with tool-specific test cases in `test_cases_tools.md`
