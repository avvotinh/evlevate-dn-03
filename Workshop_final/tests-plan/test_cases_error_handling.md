# 🚨 Error Handling Testing - Detailed Test Cases

## 📋 Overview
This document contains comprehensive error handling test cases for the E-commerce AI Product Advisor Chatbot, focusing on graceful degradation, error recovery, and user-friendly error messaging.

## 🎯 Error Handling Test Objectives
- **Graceful Degradation**: System continues functioning despite component failures
- **Error Recovery**: Automatic and manual recovery mechanisms
- **User Experience**: Clear, helpful error messages in Vietnamese
- **System Stability**: No crashes or data corruption during errors
- **Logging and Monitoring**: Proper error tracking and alerting

---

## 🔌 Service Dependency Error Tests

### TC-ERROR-001: Azure OpenAI Service Unavailable
**Priority**: High  
**Category**: External Service Failure  

**Description**: Test behavior when Azure OpenAI service is unavailable

**Error Simulation**:
- Network connectivity issues
- API endpoint unreachable
- Authentication failures
- Rate limit exceeded
- Service maintenance

**Test Steps**:
1. Mock Azure OpenAI service failure
2. Send user query to agent
3. Verify error detection
4. Check fallback mechanisms
5. Validate user error message

**Expected Results**:
- Error detected and logged
- Fallback response provided
- User receives helpful message in Vietnamese
- System remains stable
- Retry mechanism activated

**Error Message Example**:
```
"⚠️ Dịch vụ AI tạm thời không khả dụng. Tôi sẽ thử lại trong giây lát. 
Bạn có thể thử đặt câu hỏi khác hoặc chờ một chút."
```

**Fallback Behavior**:
- Use cached responses for common queries
- Provide generic helpful suggestions
- Maintain conversation context
- Enable manual retry option

---

### TC-ERROR-002: Pinecone Database Connection Failure
**Priority**: High  
**Category**: Database Error  

**Description**: Test handling of Pinecone vector database failures

**Error Scenarios**:
- Database connection timeout
- Index not found
- Query execution failure
- Authentication errors
- Network partitioning

**Test Steps**:
1. Simulate Pinecone connection failure
2. Execute search query
3. Verify graceful error handling
4. Check alternative data sources
5. Test recovery mechanisms

**Expected Results**:
- Database error caught and handled
- Alternative search methods attempted
- User informed of limited functionality
- System continues operating
- Connection retry logic activated

**Fallback Strategy**:
```python
def handle_pinecone_error(error):
    logger.error(f"Pinecone error: {error}")
    
    # Try alternative data source
    try:
        return search_local_cache(query)
    except:
        return {
            "success": False,
            "error": "Tạm thời không thể tìm kiếm sản phẩm. Vui lòng thử lại sau.",
            "fallback_suggestions": [
                "Thử tìm kiếm với từ khóa khác",
                "Xem danh mục sản phẩm phổ biến",
                "Liên hệ hỗ trợ để được tư vấn trực tiếp"
            ]
        }
```

---

### TC-ERROR-003: Network Connectivity Issues
**Priority**: High  
**Category**: Network Error  

**Description**: Test behavior during network connectivity problems

**Network Scenarios**:
- Complete network loss
- Intermittent connectivity
- Slow network responses
- DNS resolution failures
- Proxy/firewall blocking

**Test Steps**:
1. Simulate network connectivity issues
2. Attempt various operations
3. Verify timeout handling
4. Check retry mechanisms
5. Test offline functionality

**Expected Results**:
- Network errors detected promptly
- Appropriate timeout values enforced
- Retry logic with exponential backoff
- Offline mode activated if available
- Clear user communication

---

## 🛠️ Tool Error Handling Tests

### TC-ERROR-004: Search Tool Failure Recovery
**Priority**: High  
**Category**: Tool Error  

**Description**: Test search tool error handling and recovery

**Error Conditions**:
- Invalid search parameters
- Empty result sets
- Malformed query strings
- Database query failures
- Timeout errors

**Test Steps**:
1. Send invalid search parameters
2. Verify parameter validation
3. Test empty result handling
4. Check timeout recovery
5. Validate error propagation

**Expected Results**:
- Invalid parameters rejected gracefully
- Empty results handled with suggestions
- Timeouts trigger retry logic
- Errors don't crash agent
- User receives actionable feedback

**Search Error Handling**:
```python
def handle_search_error(query, error):
    if "timeout" in str(error).lower():
        return {
            "success": False,
            "error": "Tìm kiếm mất nhiều thời gian hơn dự kiến. Đang thử lại...",
            "retry": True
        }
    elif "invalid" in str(error).lower():
        return {
            "success": False,
            "error": "Yêu cầu tìm kiếm không hợp lệ. Bạn có thể thử lại với từ khóa khác?",
            "suggestions": ["laptop", "điện thoại", "máy tính bảng"]
        }
```

---

### TC-ERROR-005: Compare Tool Error Scenarios
**Priority**: Medium  
**Category**: Tool Error  

**Description**: Test comparison tool error handling

**Error Cases**:
- Products not found for comparison
- Insufficient data for comparison
- Comparison timeout
- Invalid product identifiers
- Data format errors

**Test Steps**:
1. Request comparison of non-existent products
2. Compare products with missing data
3. Test comparison timeout scenarios
4. Send invalid product IDs
5. Verify error message quality

**Expected Results**:
- Missing products handled gracefully
- Partial comparisons provided when possible
- Timeouts handled with retry options
- Invalid IDs trigger helpful suggestions
- Clear error explanations provided

---

### TC-ERROR-006: Recommendation Tool Failures
**Priority**: Medium  
**Category**: Tool Error  

**Description**: Test recommendation engine error handling

**Error Scenarios**:
- No products match criteria
- Insufficient user preference data
- Recommendation algorithm failure
- Budget constraint conflicts
- Category mismatch errors

**Test Steps**:
1. Request recommendations with impossible criteria
2. Test with minimal user data
3. Simulate algorithm failures
4. Create budget-feature conflicts
5. Verify suggestion quality

**Expected Results**:
- Impossible criteria explained clearly
- Alternative suggestions provided
- Algorithm failures handled gracefully
- Conflicts resolved with user guidance
- Helpful recommendations despite errors

---

## 🧠 Agent State Error Tests

### TC-ERROR-007: Memory Corruption Recovery
**Priority**: High  
**Category**: State Management  

**Description**: Test recovery from corrupted agent state

**Corruption Scenarios**:
- Invalid session data
- Corrupted conversation history
- Missing state components
- Inconsistent state transitions
- Memory overflow conditions

**Test Steps**:
1. Corrupt agent state data
2. Attempt to continue conversation
3. Verify state validation
4. Test recovery mechanisms
5. Check data integrity restoration

**Expected Results**:
- Corrupted state detected
- State validation prevents crashes
- Recovery mechanisms restore functionality
- User experience minimally impacted
- Data integrity maintained

**State Recovery Logic**:
```python
def validate_and_recover_state(state):
    try:
        # Validate required state components
        required_keys = ["messages", "session_id", "intent", "tools_used"]
        for key in required_keys:
            if key not in state:
                logger.warning(f"Missing state key: {key}")
                state[key] = get_default_value(key)
        
        # Validate data types
        if not isinstance(state["messages"], list):
            state["messages"] = []
        
        return state
    except Exception as e:
        logger.error(f"State recovery failed: {e}")
        return create_fresh_state()
```

---

### TC-ERROR-008: Session Management Errors
**Priority**: Medium  
**Category**: Session Error  

**Description**: Test session management error scenarios

**Session Errors**:
- Session ID conflicts
- Expired sessions
- Session storage failures
- Concurrent session access
- Session data corruption

**Test Steps**:
1. Create conflicting session IDs
2. Access expired sessions
3. Simulate storage failures
4. Test concurrent access
5. Corrupt session data

**Expected Results**:
- Session conflicts resolved automatically
- Expired sessions handled gracefully
- Storage failures don't crash system
- Concurrent access managed safely
- Corrupted sessions recovered or reset

---

## 🔄 Recovery Mechanism Tests

### TC-ERROR-009: Automatic Error Recovery
**Priority**: High  
**Category**: Recovery  

**Description**: Test automatic error recovery mechanisms

**Recovery Scenarios**:
- Service reconnection after failure
- State restoration after corruption
- Tool retry after timeout
- Cache fallback activation
- Graceful degradation modes

**Test Steps**:
1. Trigger various error conditions
2. Monitor automatic recovery attempts
3. Verify recovery success rates
4. Test recovery time limits
5. Check user notification during recovery

**Expected Results**:
- Recovery attempts made automatically
- High success rate for transient errors
- Recovery time limits enforced
- Users informed of recovery progress
- System stability maintained

**Recovery Framework**:
```python
class ErrorRecoveryManager:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 1.0
        self.recovery_strategies = {
            "network_error": self.recover_network,
            "service_error": self.recover_service,
            "state_error": self.recover_state
        }
    
    async def attempt_recovery(self, error_type, context):
        strategy = self.recovery_strategies.get(error_type)
        if not strategy:
            return False
        
        for attempt in range(self.max_retries):
            try:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                result = await strategy(context)
                if result:
                    logger.info(f"Recovery successful after {attempt + 1} attempts")
                    return True
            except Exception as e:
                logger.warning(f"Recovery attempt {attempt + 1} failed: {e}")
        
        return False
```

---

### TC-ERROR-010: Manual Error Recovery
**Priority**: Medium  
**Category**: Recovery  

**Description**: Test manual error recovery options

**Manual Recovery Options**:
- User-initiated retry buttons
- Session reset functionality
- Agent switching during errors
- Manual fallback mode activation
- Error reporting mechanisms

**Test Steps**:
1. Trigger errors requiring manual intervention
2. Present recovery options to user
3. Test each recovery mechanism
4. Verify recovery effectiveness
5. Check user experience quality

**Expected Results**:
- Clear recovery options presented
- Manual recovery mechanisms work
- User can resolve most error conditions
- Recovery options are intuitive
- System state properly restored

---

## 📊 Error Logging and Monitoring Tests

### TC-ERROR-011: Error Logging Completeness
**Priority**: Medium  
**Category**: Monitoring  

**Description**: Verify comprehensive error logging

**Logging Requirements**:
- Error type and severity
- Timestamp and context
- Stack traces for debugging
- User session information
- Recovery attempt results

**Test Steps**:
1. Trigger various error types
2. Check log file completeness
3. Verify log format consistency
4. Test log rotation and archival
5. Validate sensitive data handling

**Expected Results**:
- All errors logged with sufficient detail
- Log format consistent and parseable
- Sensitive data properly masked
- Log files managed efficiently
- Debugging information preserved

**Log Format Example**:
```json
{
    "timestamp": "2025-08-23T10:30:45Z",
    "level": "ERROR",
    "component": "search_tool",
    "error_type": "database_connection",
    "message": "Pinecone connection timeout",
    "session_id": "session_123",
    "user_query": "tìm laptop Dell",
    "stack_trace": "...",
    "recovery_attempted": true,
    "recovery_success": false
}
```

---

### TC-ERROR-012: Error Alerting and Notifications
**Priority**: Medium  
**Category**: Monitoring  

**Description**: Test error alerting mechanisms

**Alert Scenarios**:
- Critical system errors
- High error rate thresholds
- Service degradation alerts
- Recovery failure notifications
- Performance degradation warnings

**Test Steps**:
1. Configure alert thresholds
2. Trigger alert conditions
3. Verify alert delivery
4. Test alert escalation
5. Check alert resolution tracking

**Expected Results**:
- Alerts triggered at correct thresholds
- Alert delivery mechanisms work
- Escalation procedures followed
- Alert resolution tracked
- False positive rate minimized

---

## 🧪 Error Testing Automation

### Error Injection Framework
```python
import random
import asyncio
from unittest.mock import patch

class ErrorInjectionFramework:
    def __init__(self):
        self.error_scenarios = {
            "network_error": self.inject_network_error,
            "service_error": self.inject_service_error,
            "database_error": self.inject_database_error,
            "timeout_error": self.inject_timeout_error
        }
    
    def inject_network_error(self, probability=0.1):
        """Randomly inject network errors"""
        if random.random() < probability:
            raise ConnectionError("Simulated network error")
    
    def inject_service_error(self, service_name, probability=0.05):
        """Inject service-specific errors"""
        if random.random() < probability:
            raise Exception(f"Simulated {service_name} service error")
    
    async def inject_timeout_error(self, delay=10):
        """Simulate timeout conditions"""
        await asyncio.sleep(delay)
        raise TimeoutError("Simulated timeout error")
    
    @contextmanager
    def chaos_testing(self, error_rate=0.1):
        """Enable chaos testing with random errors"""
        with patch('requests.get', side_effect=self.random_error_generator):
            yield
    
    def random_error_generator(self, *args, **kwargs):
        if random.random() < 0.1:
            raise random.choice([
                ConnectionError("Network error"),
                TimeoutError("Request timeout"),
                Exception("Service unavailable")
            ])
        return original_requests_get(*args, **kwargs)
```

### Error Recovery Testing
```python
class ErrorRecoveryTest:
    def test_service_recovery_cycle(self):
        """Test complete error-recovery cycle"""
        # Inject error
        with patch('src.services.llm_service.call_api') as mock_api:
            mock_api.side_effect = ConnectionError("Service unavailable")
            
            # Attempt operation
            response = agent.chat("Tìm laptop Dell")
            
            # Verify error handling
            assert response["success"] is False
            assert "không khả dụng" in response["error"]
            
            # Simulate service recovery
            mock_api.side_effect = None
            mock_api.return_value = {"intent": "search"}
            
            # Retry operation
            response = agent.chat("Thử lại")
            assert response["success"] is True
    
    def test_cascading_error_prevention(self):
        """Test prevention of cascading errors"""
        error_count = 0
        
        def error_counter(*args, **kwargs):
            nonlocal error_count
            error_count += 1
            if error_count > 3:
                pytest.fail("Too many cascading errors")
            raise Exception("Simulated error")
        
        with patch('src.tools.search_tool.run', side_effect=error_counter):
            response = agent.chat("Tìm laptop")
            
            # System should handle error gracefully
            assert response["success"] is False
            assert error_count <= 3
```

---

## 📋 Error Test Execution Matrix

| Test Case | Priority | Error Type | Recovery | Automation | Status |
|-----------|----------|------------|----------|------------|--------|
| TC-ERROR-001 | High | Service | Auto | Yes | ⏳ Pending |
| TC-ERROR-002 | High | Database | Auto/Manual | Yes | ⏳ Pending |
| TC-ERROR-003 | High | Network | Auto | Yes | ⏳ Pending |
| TC-ERROR-004 | High | Tool | Auto | Yes | ⏳ Pending |
| TC-ERROR-005 | Medium | Tool | Manual | Yes | ⏳ Pending |
| TC-ERROR-006 | Medium | Tool | Auto/Manual | Yes | ⏳ Pending |
| TC-ERROR-007 | High | State | Auto | Yes | ⏳ Pending |
| TC-ERROR-008 | Medium | Session | Auto | Yes | ⏳ Pending |
| TC-ERROR-009 | High | Recovery | Auto | Yes | ⏳ Pending |
| TC-ERROR-010 | Medium | Recovery | Manual | Partial | ⏳ Pending |
| TC-ERROR-011 | Medium | Logging | N/A | Yes | ⏳ Pending |
| TC-ERROR-012 | Medium | Alerting | N/A | Yes | ⏳ Pending |

---

**Error Handling Success Criteria**:
- 95%+ error recovery success rate
- No system crashes during error conditions
- User-friendly error messages in Vietnamese
- Error resolution time < 30 seconds
- Complete error logging and monitoring

**Next**: All test case documents completed. Ready for test execution phase.
