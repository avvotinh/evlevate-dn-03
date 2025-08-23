# 🛠️ Tools Testing - Detailed Test Cases

## 📋 Overview
This document contains comprehensive test cases for all 5 core tools in the E-commerce AI Product Advisor Chatbot:
- **Search Tool**: Semantic product search
- **Compare Tool**: Product comparison
- **Recommend Tool**: Smart recommendations  
- **Review Tool**: Review analysis
- **Generation Tool**: Contextual response generation

---

## 🔍 Search Tool Test Cases

### TC-SEARCH-001: Basic Product Search
**Priority**: High  
**Category**: Functional  

**Description**: Test basic product search functionality

**Test Data**:
```json
{
    "query": "laptop Dell",
    "metadata": {
        "max_results": 5,
        "include_reviews": true
    }
}
```

**Test Steps**:
1. Initialize search tool
2. Execute search with test data
3. Parse JSON response
4. Validate product results
5. Check response structure

**Expected Results**:
- Returns 1-5 Dell laptop products
- Each product has required fields (name, price, specs)
- Response includes success status
- Results are relevant to query
- Response time < 3 seconds

**Validation**:
```python
result = search_tool.run(json.dumps(test_data))
response = json.loads(result)
assert response["success"] is True
assert len(response["products"]) > 0
assert "Dell" in response["products"][0]["name"]
```

---

### TC-SEARCH-002: Advanced Filtering
**Priority**: High  
**Category**: Functional  

**Description**: Test search with price and category filters

**Test Data**:
```json
{
    "query": "laptop gaming",
    "metadata": {
        "price_min": 15000000,
        "price_max": 30000000,
        "category": "laptop",
        "brand": "ASUS",
        "max_results": 3
    }
}
```

**Test Steps**:
1. Execute filtered search
2. Verify all results match filters
3. Check price range compliance
4. Validate brand filtering
5. Confirm result count limit

**Expected Results**:
- All products are ASUS laptops
- Prices between 15-30 million VND
- Maximum 3 results returned
- Gaming-related features highlighted
- Filters applied correctly

---

### TC-SEARCH-003: Empty Results Handling
**Priority**: Medium  
**Category**: Error Handling  

**Description**: Test behavior when no products match search criteria

**Test Data**:
```json
{
    "query": "laptop giá 1 triệu",
    "metadata": {
        "price_max": 1000000
    }
}
```

**Test Steps**:
1. Execute search with unrealistic criteria
2. Verify graceful handling of empty results
3. Check error message quality
4. Validate suggestions provided
5. Ensure no exceptions thrown

**Expected Results**:
- Returns empty product list
- Provides helpful error message
- Suggests alternative search criteria
- Maintains proper JSON structure
- No application crashes

---

### TC-SEARCH-004: Invalid Input Handling
**Priority**: Medium  
**Category**: Error Handling  

**Description**: Test search tool with invalid or malformed inputs

**Test Cases**:
- Empty query string
- Invalid JSON format
- Negative price values
- Extremely large max_results
- Special characters in query

**Expected Results**:
- Graceful error handling for all cases
- User-friendly error messages
- No system crashes
- Proper validation feedback

---

## ⚖️ Compare Tool Test Cases

### TC-COMPARE-001: Two Product Comparison
**Priority**: High  
**Category**: Functional  

**Description**: Compare two specific products side by side

**Test Data**:
```json
{
    "product_ids": ["iPhone 15", "Samsung Galaxy S24"],
    "comparison_aspects": ["giá", "camera", "hiệu năng", "pin"],
    "include_reviews": true
}
```

**Test Steps**:
1. Execute comparison with test data
2. Verify both products are found
3. Check comparison table structure
4. Validate all aspects are covered
5. Confirm review integration

**Expected Results**:
- Both products successfully compared
- Comparison table with all requested aspects
- Clear pros/cons for each product
- Review sentiment included
- Structured JSON response

**Validation**:
```python
result = compare_tool.run(json.dumps(test_data))
response = json.loads(result)
assert response["success"] is True
assert len(response["products_compared"]) == 2
assert "comparison_table" in response
```

---

### TC-COMPARE-002: Multiple Product Comparison
**Priority**: High  
**Category**: Functional  

**Description**: Compare 3+ products simultaneously

**Test Data**:
```json
{
    "product_ids": ["MacBook Air M2", "Dell XPS 13", "ThinkPad X1 Carbon"],
    "comparison_aspects": ["giá", "hiệu năng", "thiết kế", "pin"],
    "include_reviews": false
}
```

**Expected Results**:
- All 3 products compared successfully
- Comparison matrix format
- Clear differentiation between products
- Performance rankings provided
- Recommendation for best choice

---

### TC-COMPARE-003: Product Not Found Handling
**Priority**: Medium  
**Category**: Error Handling  

**Description**: Handle comparison when some products don't exist

**Test Data**:
```json
{
    "product_ids": ["iPhone 15", "NonExistent Product", "Samsung S24"],
    "comparison_aspects": ["giá", "camera"]
}
```

**Expected Results**:
- Comparison proceeds with found products
- Warning about missing products
- Partial comparison results provided
- Clear indication of which products were found

---

## 💡 Recommend Tool Test Cases

### TC-RECOMMEND-001: Budget-Based Recommendations
**Priority**: High  
**Category**: Functional  

**Description**: Generate recommendations based on budget constraints

**Test Data**:
```json
{
    "user_needs": "laptop cho sinh viên",
    "budget": 15000000,
    "preferences": {
        "category": "laptop",
        "usage": "học tập, giải trí",
        "brand_preference": "không"
    },
    "num_recommendations": 3
}
```

**Test Steps**:
1. Execute recommendation request
2. Verify all recommendations within budget
3. Check relevance to student needs
4. Validate explanation quality
5. Confirm recommendation count

**Expected Results**:
- 3 laptop recommendations
- All prices ≤ 15 million VND
- Student-appropriate features highlighted
- Clear explanations for each choice
- Ranked by suitability

---

### TC-RECOMMEND-002: Use Case Specific Recommendations
**Priority**: High  
**Category**: Functional  

**Description**: Recommendations for specific use cases

**Test Cases**:
- Gaming: High-performance requirements
- Business: Portability and battery life
- Creative work: Display and processing power
- Budget-conscious: Value for money

**Expected Results**:
- Recommendations match use case requirements
- Feature priorities align with needs
- Performance benchmarks provided
- Alternative options suggested

---

### TC-RECOMMEND-003: No Suitable Products Scenario
**Priority**: Medium  
**Category**: Error Handling  

**Description**: Handle cases where no products meet criteria

**Test Data**:
```json
{
    "user_needs": "laptop gaming cao cấp",
    "budget": 5000000,
    "preferences": {
        "category": "laptop",
        "performance": "high-end gaming"
    }
}
```

**Expected Results**:
- Clear explanation of constraint conflict
- Suggestions to adjust budget or requirements
- Alternative product categories offered
- Helpful guidance provided

---

## 📝 Review Tool Test Cases

### TC-REVIEW-001: Product Review Analysis
**Priority**: High  
**Category**: Functional  

**Description**: Analyze reviews for a specific product

**Test Data**:
```json
{
    "product_id": "iPhone 15 Pro Max",
    "analysis_type": "sentiment",
    "include_summary": true
}
```

**Test Steps**:
1. Execute review analysis
2. Verify sentiment analysis results
3. Check review summary quality
4. Validate key insights extraction
5. Confirm structured output

**Expected Results**:
- Overall sentiment score (positive/negative/neutral)
- Key positive and negative points
- Review summary in Vietnamese
- Confidence scores for analysis
- Actionable insights provided

---

### TC-REVIEW-002: Comparative Review Analysis
**Priority**: Medium  
**Category**: Functional  

**Description**: Compare reviews across multiple products

**Test Data**:
```json
{
    "product_ids": ["iPhone 15", "Samsung S24"],
    "comparison_focus": "camera quality",
    "include_ratings": true
}
```

**Expected Results**:
- Comparative review insights
- Focus area analysis (camera quality)
- Rating comparisons
- User preference trends
- Recommendation based on reviews

---

## 🎯 Generation Tool Test Cases

### TC-GENERATION-001: Contextual Response Generation
**Priority**: High  
**Category**: Functional  

**Description**: Generate contextual responses using tool results

**Test Data**:
```json
{
    "query": "Laptop nào tốt nhất cho lập trình?",
    "context": {
        "search_results": [...],
        "user_preferences": {...},
        "conversation_history": [...]
    }
}
```

**Test Steps**:
1. Provide query with rich context
2. Execute generation tool
3. Verify context integration
4. Check response relevance
5. Validate Vietnamese language quality

**Expected Results**:
- Response incorporates all context elements
- Specific product recommendations
- Technical reasoning provided
- Natural Vietnamese language
- Actionable advice given

---

### TC-GENERATION-002: Multi-Modal Response Generation
**Priority**: Medium  
**Category**: Functional  

**Description**: Generate responses combining multiple tool results

**Test Data**:
- Search results: List of laptops
- Comparison data: Feature comparison
- Review insights: User feedback
- Recommendation scores: Ranking data

**Expected Results**:
- Coherent response combining all data sources
- Structured presentation of information
- Clear recommendations with reasoning
- Proper source attribution

---

## 🔧 Tool Manager Test Cases

### TC-TOOLMGR-001: Tool Registration and Discovery
**Priority**: High  
**Category**: Functional  

**Description**: Verify all tools are properly registered and accessible

**Test Steps**:
1. Initialize ToolManager
2. Get list of all tools
3. Verify each tool is accessible
4. Check tool descriptions
5. Validate tool schemas

**Expected Results**:
- All 4 tools registered (search, compare, recommend, review)
- Each tool has proper name and description
- Tool schemas are valid
- Tools can be retrieved by name

**Validation**:
```python
tool_manager = ToolManager()
tools = tool_manager.get_all_tools()
assert len(tools) == 4
assert tool_manager.get_tool("search") is not None
```

---

### TC-TOOLMGR-002: Tool Execution Coordination
**Priority**: Medium  
**Category**: Integration  

**Description**: Test coordinated execution of multiple tools

**Test Scenario**:
1. Search for products
2. Compare top results
3. Generate recommendation
4. Analyze reviews

**Expected Results**:
- Tools execute in proper sequence
- Data flows correctly between tools
- No conflicts or interference
- Results are properly aggregated

---

## 📊 Tool Performance Benchmarks

### Performance Targets
| Tool | Target Response Time | Memory Usage | Success Rate |
|------|---------------------|--------------|--------------|
| Search | < 3 seconds | < 50MB | > 95% |
| Compare | < 5 seconds | < 100MB | > 90% |
| Recommend | < 4 seconds | < 75MB | > 85% |
| Review | < 3 seconds | < 50MB | > 90% |
| Generation | < 2 seconds | < 25MB | > 98% |

### Load Testing Scenarios
- **Concurrent Tool Usage**: 10 simultaneous tool executions
- **Large Dataset Processing**: 100+ products in comparison
- **Complex Queries**: Multi-criteria searches with filters
- **Extended Sessions**: 50+ tool calls in single session

---

## 🧪 Test Automation Framework

### Tool Test Base Class
```python
import pytest
import json
from src.tools.tool_manager import tool_manager

class BaseToolTest:
    @pytest.fixture
    def search_tool(self):
        return tool_manager.get_tool("search")
    
    @pytest.fixture
    def compare_tool(self):
        return tool_manager.get_tool("compare")
    
    def validate_json_response(self, response_str):
        """Validate tool response is valid JSON"""
        try:
            response = json.loads(response_str)
            assert "success" in response
            return response
        except json.JSONDecodeError:
            pytest.fail("Tool response is not valid JSON")
```

### Performance Testing
```python
import time
import psutil
import pytest

class TestToolPerformance:
    def test_search_performance(self, search_tool):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        result = search_tool.run('{"query": "laptop Dell"}')
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        assert (end_time - start_time) < 3.0  # < 3 seconds
        assert (end_memory - start_memory) < 50 * 1024 * 1024  # < 50MB
```

---

**Next**: Continue with integration test cases in `test_cases_integration.md`
