# 🖥️ UI Testing - Detailed Test Cases

## 📋 Overview
This document contains comprehensive UI test cases for the Streamlit-based E-commerce AI Product Advisor Chatbot interface, focusing on user experience, functionality, and visual presentation.

## 🎯 UI Test Scope
- **Streamlit Interface**: Main chat interface and components
- **Agent Selection**: ReAct vs LangGraph agent switching
- **Message Display**: Chat history and response formatting
- **Vietnamese Language**: Text rendering and input handling
- **Responsive Design**: Layout adaptation and usability
- **Error Handling**: User-friendly error message display
- **Session Management**: UI state persistence

---

## 💬 Chat Interface Tests

### TC-UI-001: Basic Chat Interface Functionality
**Priority**: High  
**Category**: Functional  

**Description**: Test core chat interface functionality

**Test Steps**:
1. Launch Streamlit application
2. Verify chat interface loads correctly
3. Test message input field
4. Send test message
5. Verify response display
6. Check chat history preservation

**Expected Results**:
- Chat interface loads without errors
- Input field accepts Vietnamese text
- Messages display in correct order
- Chat history preserved during session
- Proper message formatting applied

**UI Elements to Validate**:
- Message input text area
- Send button functionality
- Chat history container
- Welcome message display
- Agent status indicator

**Visual Validation**:
```python
def test_chat_interface_elements():
    # Streamlit testing framework
    assert st.session_state.get("messages") is not None
    assert len(st.session_state.messages) >= 1  # Welcome message
    
    # Check UI components exist
    assert "chat_input" in st.session_state
    assert "agent_type" in st.session_state
```

---

### TC-UI-002: Message Display and Formatting
**Priority**: High  
**Category**: Visual  

**Description**: Verify proper message display and formatting

**Test Scenarios**:
- User messages (right-aligned, blue background)
- Assistant messages (left-aligned, gray background)
- Long messages with text wrapping
- Messages with special characters
- Messages with markdown formatting
- Vietnamese diacritics display

**Test Steps**:
1. Send various message types
2. Verify visual formatting
3. Check text alignment
4. Test markdown rendering
5. Validate Vietnamese character display

**Expected Results**:
- User and assistant messages visually distinct
- Proper text alignment and colors
- Markdown formatting rendered correctly
- Vietnamese characters display properly
- Long messages wrap appropriately

**Message Format Examples**:
```
User: "Tìm laptop Dell có SSD 512GB"
Assistant: "Tôi đã tìm thấy **3 laptop Dell** phù hợp:
1. **Dell XPS 13** - 25,000,000 VND
2. **Dell Inspiron 15** - 18,500,000 VND
..."
```

---

### TC-UI-003: Agent Selection Interface
**Priority**: High  
**Category**: Functional  

**Description**: Test agent selection functionality

**Test Steps**:
1. Locate agent selection dropdown/radio buttons
2. Verify both ReAct and LangGraph options available
3. Switch between agent types
4. Test conversation with each agent
5. Verify agent-specific behavior

**Expected Results**:
- Agent selection controls visible and functional
- Both agent types selectable
- Agent switching works without errors
- Different agents show distinct behavior
- Selection persists during session

**Agent Selection Validation**:
```python
def test_agent_selection():
    # Test agent options
    agent_options = ["ReAct Agent", "LangGraph Agent"]
    assert st.session_state.get("agent_type") in agent_options
    
    # Test agent switching
    for agent_type in agent_options:
        st.session_state.agent_type = agent_type
        # Verify agent initialization
        assert get_current_agent() is not None
```

---

### TC-UI-004: Vietnamese Language Support
**Priority**: High  
**Category**: Localization  

**Description**: Test Vietnamese language input and display

**Test Cases**:
- Vietnamese input with diacritics: "Tìm điện thoại có màn hình đẹp"
- Mixed Vietnamese-English: "Laptop gaming RTX 4060 giá rẻ"
- Special Vietnamese characters: "Đánh giá iPhone 15 Pro Max"
- Long Vietnamese sentences
- Vietnamese technical terms

**Test Steps**:
1. Input Vietnamese text with various diacritics
2. Verify text displays correctly in input field
3. Send message and check display in chat
4. Verify agent response in Vietnamese
5. Test copy-paste functionality

**Expected Results**:
- All Vietnamese characters input correctly
- Diacritics preserved in display
- Agent responds in proper Vietnamese
- No character encoding issues
- Copy-paste works with Vietnamese text

---

### TC-UI-005: Responsive Design and Layout
**Priority**: Medium  
**Category**: Visual  

**Description**: Test UI responsiveness across different screen sizes

**Screen Sizes to Test**:
- Desktop (1920x1080)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667)

**Test Steps**:
1. Load application on different screen sizes
2. Verify layout adaptation
3. Test chat interface usability
4. Check text readability
5. Validate button accessibility

**Expected Results**:
- Layout adapts to screen size
- Chat interface remains usable
- Text remains readable
- All controls accessible
- No horizontal scrolling required

---

## 🎨 Visual and UX Tests

### TC-UI-006: Welcome Message and Onboarding
**Priority**: Medium  
**Category**: User Experience  

**Description**: Test initial user experience and welcome flow

**Test Steps**:
1. Start fresh session
2. Verify welcome message display
3. Check feature explanation
4. Test example queries
5. Validate onboarding flow

**Expected Results**:
- Welcome message appears immediately
- Features clearly explained
- Example queries provided
- Professional and friendly tone
- Clear call-to-action

**Welcome Message Content Validation**:
- Greeting in Vietnamese
- Feature list (search, compare, recommend, review)
- Example usage scenarios
- Agent selection explanation

---

### TC-UI-007: Loading States and Progress Indicators
**Priority**: Medium  
**Category**: User Experience  

**Description**: Test loading states during agent processing

**Test Scenarios**:
- Simple query processing
- Complex multi-tool queries
- Long-running operations
- Error scenarios
- Network delays

**Test Steps**:
1. Send query requiring processing time
2. Verify loading indicator appears
3. Check progress messages
4. Test user interaction during loading
5. Validate completion indication

**Expected Results**:
- Loading indicator shows immediately
- Progress messages keep user informed
- User can't send duplicate requests
- Clear completion indication
- Smooth transition to results

**Loading State Examples**:
```
"🔍 Đang tìm kiếm sản phẩm..."
"⚖️ Đang so sánh các sản phẩm..."
"💡 Đang tạo gợi ý cho bạn..."
"✅ Hoàn thành!"
```

---

### TC-UI-008: Error Message Display
**Priority**: High  
**Category**: Error Handling  

**Description**: Test error message presentation to users

**Error Scenarios**:
- Network connectivity issues
- Service unavailable errors
- Invalid input handling
- Timeout errors
- Unexpected system errors

**Test Steps**:
1. Simulate various error conditions
2. Verify error messages display
3. Check message clarity and helpfulness
4. Test error recovery options
5. Validate user guidance

**Expected Results**:
- Error messages in Vietnamese
- Clear explanation of issue
- Helpful recovery suggestions
- Professional tone maintained
- No technical jargon exposed

**Error Message Examples**:
```
❌ "Không thể kết nối đến dịch vụ. Vui lòng thử lại sau."
⚠️ "Không tìm thấy sản phẩm phù hợp. Hãy thử điều chỉnh yêu cầu."
🔧 "Hệ thống đang bảo trì. Vui lòng quay lại sau 5 phút."
```

---

## 🔄 Session and State Management Tests

### TC-UI-009: Session State Persistence
**Priority**: High  
**Category**: State Management  

**Description**: Test UI state persistence across interactions

**Test Steps**:
1. Start conversation with multiple messages
2. Refresh browser page
3. Verify chat history preservation
4. Test agent selection persistence
5. Check session continuity

**Expected Results**:
- Chat history preserved after refresh
- Agent selection maintained
- Session ID consistent
- No data loss occurs
- Smooth user experience

**State Persistence Validation**:
```python
def test_session_persistence():
    # Check session state keys
    required_keys = ["messages", "agent_type", "session_id"]
    for key in required_keys:
        assert key in st.session_state
    
    # Verify message history
    assert len(st.session_state.messages) > 0
    assert st.session_state.messages[0]["role"] == "assistant"
```

---

### TC-UI-010: Multi-Tab Session Isolation
**Priority**: Medium  
**Category**: State Management  

**Description**: Test session isolation across browser tabs

**Test Steps**:
1. Open application in first tab
2. Start conversation
3. Open application in second tab
4. Start different conversation
5. Verify sessions don't interfere

**Expected Results**:
- Each tab maintains separate session
- No data leakage between tabs
- Independent conversation flows
- Proper session identification
- No conflicts or errors

---

## 📱 Accessibility and Usability Tests

### TC-UI-011: Keyboard Navigation
**Priority**: Medium  
**Category**: Accessibility  

**Description**: Test keyboard-only navigation

**Test Steps**:
1. Navigate using only keyboard
2. Test tab order through interface
3. Verify Enter key sends messages
4. Test keyboard shortcuts
5. Check focus indicators

**Expected Results**:
- Logical tab order maintained
- Enter key sends messages
- All controls keyboard accessible
- Clear focus indicators
- No keyboard traps

---

### TC-UI-012: Text Readability and Contrast
**Priority**: Medium  
**Category**: Accessibility  

**Description**: Test text readability and color contrast

**Test Steps**:
1. Check text contrast ratios
2. Test with different font sizes
3. Verify readability in various lighting
4. Test color-blind accessibility
5. Validate text scaling

**Expected Results**:
- Contrast ratios meet WCAG standards
- Text readable at various sizes
- Good visibility in different lighting
- Color-blind friendly design
- Text scales properly

---

## 🧪 UI Test Automation Framework

### Streamlit Testing Setup
```python
import streamlit as st
from streamlit.testing.v1 import AppTest
import pytest

class StreamlitUITest:
    def __init__(self):
        self.app_test = AppTest.from_file("src/ui/app.py")
    
    def test_initial_load(self):
        """Test initial application load"""
        self.app_test.run()
        
        # Check welcome message
        assert len(self.app_test.chat_message) > 0
        welcome_msg = self.app_test.chat_message[0]
        assert "Xin chào" in welcome_msg.children[0].value
        
        # Check agent selection
        assert self.app_test.selectbox[0].label == "Chọn Agent"
        
    def test_message_sending(self):
        """Test sending and receiving messages"""
        self.app_test.run()
        
        # Send test message
        test_message = "Tìm laptop Dell"
        self.app_test.chat_input[0].set_value(test_message).run()
        
        # Verify message appears in chat
        messages = self.app_test.chat_message
        assert any(test_message in msg.children[0].value for msg in messages)
        
    def test_agent_switching(self):
        """Test switching between agents"""
        self.app_test.run()
        
        # Switch to LangGraph agent
        self.app_test.selectbox[0].select("LangGraph Agent").run()
        
        # Verify agent change
        assert st.session_state.get("agent_type") == "LangGraph Agent"
```

### Visual Regression Testing
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class VisualRegressionTest:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.base_url = "http://localhost:8501"
    
    def test_chat_interface_layout(self):
        """Test chat interface visual layout"""
        self.driver.get(self.base_url)
        time.sleep(3)  # Wait for load
        
        # Take screenshot
        self.driver.save_screenshot("chat_interface_baseline.png")
        
        # Check key elements exist
        chat_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='stChatInput']")
        assert chat_input.is_displayed()
        
        # Check agent selector
        agent_selector = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='stSelectbox']")
        assert agent_selector.is_displayed()
    
    def test_message_display(self):
        """Test message display formatting"""
        self.driver.get(self.base_url)
        time.sleep(3)
        
        # Send test message
        chat_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='stChatInput'] textarea")
        chat_input.send_keys("Tìm laptop Dell")
        chat_input.submit()
        
        # Wait for response
        time.sleep(5)
        
        # Take screenshot of conversation
        self.driver.save_screenshot("message_display_test.png")
        
        # Verify message elements
        messages = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='stChatMessage']")
        assert len(messages) >= 2  # Welcome + user message + response
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.driver.quit()
```

### Performance UI Testing
```python
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UIPerformanceTest:
    def test_page_load_time(self):
        """Test initial page load performance"""
        start_time = time.time()
        
        self.driver.get(self.base_url)
        
        # Wait for chat interface to be ready
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stChatInput']"))
        )
        
        load_time = time.time() - start_time
        assert load_time < 5.0  # Page should load within 5 seconds
    
    def test_message_response_time(self):
        """Test message response time in UI"""
        self.driver.get(self.base_url)
        time.sleep(3)
        
        # Send message and measure response time
        start_time = time.time()
        
        chat_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='stChatInput'] textarea")
        chat_input.send_keys("Xin chào")
        chat_input.submit()
        
        # Wait for response to appear
        WebDriverWait(self.driver, 15).until(
            lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "[data-testid='stChatMessage']")) >= 3
        )
        
        response_time = time.time() - start_time
        assert response_time < 10.0  # Response should appear within 10 seconds
```

---

## 📊 UI Test Execution Matrix

| Test Case | Priority | Automation | Browser Support | Status |
|-----------|----------|------------|-----------------|--------|
| TC-UI-001 | High | Yes | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-002 | High | Yes | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-003 | High | Yes | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-004 | High | Partial | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-005 | Medium | Manual | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-006 | Medium | Yes | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-007 | Medium | Yes | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-008 | High | Yes | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-009 | High | Yes | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-010 | Medium | Manual | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-011 | Medium | Manual | Chrome, Firefox, Edge | ⏳ Pending |
| TC-UI-012 | Medium | Manual | Chrome, Firefox, Edge | ⏳ Pending |

---

**UI Testing Tools**:
- **Streamlit Testing**: Built-in testing framework
- **Selenium WebDriver**: Browser automation
- **Pytest**: Test framework and assertions
- **Visual Regression**: Screenshot comparison
- **Accessibility**: WAVE, axe-core tools

**Next**: Continue with error handling test cases in `test_cases_error_handling.md`
