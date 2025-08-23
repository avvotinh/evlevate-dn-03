# ⚡ Performance Testing - Detailed Test Cases

## 📋 Overview
This document contains comprehensive performance test cases for the E-commerce AI Product Advisor Chatbot, focusing on response times, scalability, resource usage, and system limits.

## 🎯 Performance Test Objectives
- **Response Time**: Validate response times meet user expectations
- **Scalability**: Test system behavior under increasing load
- **Resource Usage**: Monitor memory, CPU, and network utilization
- **Throughput**: Measure maximum requests per second
- **Reliability**: Ensure consistent performance over time
- **Bottleneck Identification**: Find and document performance limitations

---

## ⏱️ Response Time Performance Tests

### TC-PERF-001: Baseline Response Time Measurement
**Priority**: High  
**Category**: Response Time  

**Description**: Establish baseline response times for different query types

**Test Scenarios**:
```python
baseline_queries = [
    ("Xin chào", "greeting", "< 2 seconds"),
    ("Tìm laptop Dell", "simple_search", "< 5 seconds"),
    ("So sánh iPhone 15 và Samsung S24", "comparison", "< 8 seconds"),
    ("Gợi ý laptop cho lập trình dưới 20 triệu", "recommendation", "< 10 seconds"),
    ("Tìm laptop gaming, so sánh 3 model tốt nhất", "complex_multi_tool", "< 12 seconds")
]
```

**Test Steps**:
1. Execute each query type 10 times
2. Measure total response time
3. Record component-wise latency
4. Calculate statistical metrics (mean, median, 95th percentile)
5. Identify performance outliers

**Expected Results**:
- All queries meet target response times
- 95% of requests complete within target
- Consistent performance across runs
- No significant outliers

**Performance Metrics**:
```python
def measure_response_time(query, expected_time):
    start_time = time.time()
    response = agent.chat(query)
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < expected_time
    return response_time, response
```

---

### TC-PERF-002: Component Latency Breakdown
**Priority**: High  
**Category**: Response Time  

**Description**: Measure latency of individual system components

**Components to Measure**:
- Intent classification: Target < 1 second
- Tool execution: Target < 3 seconds per tool
- Database queries: Target < 2 seconds
- LLM API calls: Target < 3 seconds
- Response generation: Target < 2 seconds

**Test Steps**:
1. Instrument code with timing measurements
2. Execute representative queries
3. Collect component-wise timing data
4. Identify bottleneck components
5. Analyze latency distribution

**Expected Results**:
- Each component meets latency targets
- Total latency equals sum of components
- Bottlenecks clearly identified
- Optimization opportunities documented

**Latency Measurement Framework**:
```python
import time
from contextlib import contextmanager

@contextmanager
def measure_latency(component_name):
    start = time.time()
    yield
    end = time.time()
    latency = end - start
    print(f"{component_name}: {latency:.3f}s")
    
# Usage in agent code
with measure_latency("Intent Classification"):
    intent = classify_intent(user_input)
```

---

### TC-PERF-003: Response Time Under Load
**Priority**: High  
**Category**: Load Testing  

**Description**: Measure response time degradation under increasing load

**Load Scenarios**:
- 1 concurrent user (baseline)
- 5 concurrent users
- 10 concurrent users
- 20 concurrent users
- 50 concurrent users (stress test)

**Test Steps**:
1. Start with single user baseline
2. Gradually increase concurrent users
3. Measure response time at each level
4. Monitor system resource usage
5. Identify breaking point

**Expected Results**:
- Response times remain acceptable up to 10 users
- Graceful degradation beyond capacity
- System doesn't crash under overload
- Resource usage scales predictably

---

## 🔄 Scalability Performance Tests

### TC-PERF-004: Concurrent User Scalability
**Priority**: High  
**Category**: Scalability  

**Description**: Test system behavior with multiple concurrent users

**Test Configuration**:
```python
concurrent_test_config = {
    "users": [1, 5, 10, 15, 20, 25],
    "duration": 300,  # 5 minutes per test
    "ramp_up": 60,    # 1 minute ramp-up
    "queries_per_user": 10
}
```

**Test Steps**:
1. Configure load testing framework
2. Execute concurrent user tests
3. Monitor system metrics during tests
4. Measure throughput and response times
5. Identify scalability limits

**Expected Results**:
- System handles 10 concurrent users smoothly
- Throughput increases linearly up to capacity
- Response times remain stable
- No resource leaks or memory issues

**Scalability Metrics**:
- Requests per second (RPS)
- Average response time
- 95th percentile response time
- Error rate percentage
- Resource utilization

---

### TC-PERF-005: Session Scalability
**Priority**: Medium  
**Category**: Scalability  

**Description**: Test memory usage with increasing number of sessions

**Test Scenarios**:
- 10 active sessions
- 50 active sessions
- 100 active sessions
- 500 active sessions
- 1000 active sessions

**Test Steps**:
1. Create multiple concurrent sessions
2. Execute conversations in each session
3. Monitor memory usage growth
4. Test session cleanup mechanisms
5. Measure session retrieval performance

**Expected Results**:
- Memory usage scales linearly with sessions
- Session cleanup works effectively
- Session retrieval remains fast
- No memory leaks detected

---

### TC-PERF-006: Long-Running Session Performance
**Priority**: Medium  
**Category**: Endurance  

**Description**: Test performance of extended conversations

**Test Configuration**:
- Session duration: 2 hours
- Messages per session: 100+
- Conversation complexity: Mixed query types
- Memory monitoring: Continuous

**Test Steps**:
1. Start long-running conversation session
2. Send messages at regular intervals
3. Monitor memory usage over time
4. Check response time degradation
5. Validate context preservation

**Expected Results**:
- Response times remain consistent
- Memory usage stabilizes after initial growth
- Context preservation works throughout
- No performance degradation over time

---

## 💾 Resource Usage Performance Tests

### TC-PERF-007: Memory Usage Profiling
**Priority**: High  
**Category**: Resource Usage  

**Description**: Profile memory usage patterns and identify leaks

**Memory Monitoring Points**:
- Agent initialization
- Tool execution
- Session creation
- Conversation processing
- Cleanup operations

**Test Steps**:
1. Set up memory profiling tools
2. Execute representative workloads
3. Monitor memory allocation patterns
4. Identify memory leaks
5. Test garbage collection effectiveness

**Expected Results**:
- Memory usage within acceptable limits
- No memory leaks detected
- Garbage collection works effectively
- Memory patterns are predictable

**Memory Profiling Tools**:
```python
import psutil
import tracemalloc

def profile_memory_usage():
    tracemalloc.start()
    process = psutil.Process()
    
    # Execute test workload
    initial_memory = process.memory_info().rss
    
    # ... test execution ...
    
    final_memory = process.memory_info().rss
    memory_growth = final_memory - initial_memory
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return {
        "memory_growth": memory_growth,
        "peak_usage": peak,
        "current_usage": current
    }
```

---

### TC-PERF-008: CPU Usage Optimization
**Priority**: Medium  
**Category**: Resource Usage  

**Description**: Monitor and optimize CPU usage patterns

**CPU Monitoring Scenarios**:
- Idle system baseline
- Single user interaction
- Multiple concurrent users
- Complex query processing
- Tool-intensive operations

**Test Steps**:
1. Monitor CPU usage during different scenarios
2. Identify CPU-intensive operations
3. Profile code execution paths
4. Test optimization strategies
5. Validate performance improvements

**Expected Results**:
- CPU usage remains reasonable under load
- No CPU-intensive blocking operations
- Efficient use of available cores
- Optimization opportunities identified

---

### TC-PERF-009: Network Performance Testing
**Priority**: Medium  
**Category**: Resource Usage  

**Description**: Test network usage and API call efficiency

**Network Monitoring Points**:
- Azure OpenAI API calls
- Pinecone database queries
- Streamlit UI communication
- External service dependencies

**Test Steps**:
1. Monitor network traffic patterns
2. Measure API call latency
3. Test network error handling
4. Optimize request batching
5. Validate retry mechanisms

**Expected Results**:
- Efficient network usage
- Minimal redundant API calls
- Proper error handling for network issues
- Optimized request patterns

---

## 🔥 Stress Testing

### TC-PERF-010: System Breaking Point
**Priority**: High  
**Category**: Stress Testing  

**Description**: Determine system limits and breaking points

**Stress Test Scenarios**:
- Maximum concurrent users
- Extreme query complexity
- Rapid-fire requests
- Resource exhaustion
- Service dependency failures

**Test Steps**:
1. Gradually increase system load
2. Monitor system behavior at limits
3. Identify failure modes
4. Test recovery mechanisms
5. Document breaking points

**Expected Results**:
- System fails gracefully at limits
- Clear error messages provided
- Recovery possible after overload
- No data corruption occurs

---

### TC-PERF-011: Database Performance Limits
**Priority**: High  
**Category**: Stress Testing  

**Description**: Test Pinecone database performance limits

**Database Stress Scenarios**:
- High-frequency queries
- Large result sets
- Complex filter combinations
- Concurrent query execution
- Index performance limits

**Test Steps**:
1. Execute high-volume database queries
2. Monitor query response times
3. Test concurrent query handling
4. Measure index performance
5. Identify database bottlenecks

**Expected Results**:
- Database handles expected query volume
- Query times remain acceptable
- Concurrent queries don't interfere
- Index performance is optimal

---

## 📊 Performance Benchmarking

### TC-PERF-012: Comparative Performance Analysis
**Priority**: Medium  
**Category**: Benchmarking  

**Description**: Compare ReAct Agent vs LangGraph Agent performance

**Comparison Metrics**:
- Response time differences
- Memory usage patterns
- Tool execution efficiency
- Conversation handling
- Error recovery performance

**Test Steps**:
1. Execute identical test suites on both agents
2. Measure performance metrics
3. Compare results statistically
4. Identify performance trade-offs
5. Document recommendations

**Expected Results**:
- Clear performance comparison
- Trade-offs documented
- Recommendations provided
- Both agents meet minimum requirements

---

### TC-PERF-013: Performance Regression Testing
**Priority**: Medium  
**Category**: Regression  

**Description**: Ensure performance doesn't degrade with updates

**Regression Test Suite**:
- Baseline performance measurements
- Automated performance tests
- Performance threshold validation
- Historical performance tracking

**Test Steps**:
1. Establish performance baselines
2. Run automated performance tests
3. Compare against historical data
4. Flag performance regressions
5. Validate performance improvements

**Expected Results**:
- No performance regressions detected
- Performance improvements validated
- Automated alerts for degradation
- Historical trends tracked

---

## 🛠️ Performance Test Automation

### Load Testing Framework
```python
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

class LoadTestFramework:
    def __init__(self, base_url, concurrent_users=10):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []
    
    async def execute_user_session(self, user_id, queries):
        """Simulate single user session"""
        session_results = []
        
        for query in queries:
            start_time = time.time()
            
            # Execute query (replace with actual agent call)
            response = await self.send_query(query)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            session_results.append({
                "user_id": user_id,
                "query": query,
                "response_time": response_time,
                "success": response.get("success", False)
            })
        
        return session_results
    
    async def run_load_test(self, test_queries, duration=300):
        """Run load test with multiple concurrent users"""
        tasks = []
        
        for user_id in range(self.concurrent_users):
            task = self.execute_user_session(user_id, test_queries)
            tasks.append(task)
        
        # Execute all user sessions concurrently
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_results = [item for sublist in results for item in sublist]
        
        return self.analyze_results(all_results)
    
    def analyze_results(self, results):
        """Analyze load test results"""
        response_times = [r["response_time"] for r in results]
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        
        return {
            "total_requests": len(results),
            "success_rate": success_rate,
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": sorted(response_times)[int(0.95 * len(response_times))]
        }
```

### Performance Monitoring
```python
import psutil
import time
from dataclasses import dataclass
from typing import List

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_percent: float
    memory_mb: float
    response_time: float
    active_sessions: int

class PerformanceMonitor:
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.monitoring = False
    
    def start_monitoring(self, interval=1.0):
        """Start continuous performance monitoring"""
        self.monitoring = True
        
        while self.monitoring:
            process = psutil.Process()
            
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=process.cpu_percent(),
                memory_mb=process.memory_info().rss / 1024 / 1024,
                response_time=0,  # Set by test framework
                active_sessions=0  # Set by session manager
            )
            
            self.metrics.append(metrics)
            time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
    
    def get_performance_report(self):
        """Generate performance report"""
        if not self.metrics:
            return "No performance data collected"
        
        cpu_avg = sum(m.cpu_percent for m in self.metrics) / len(self.metrics)
        memory_avg = sum(m.memory_mb for m in self.metrics) / len(self.metrics)
        memory_peak = max(m.memory_mb for m in self.metrics)
        
        return {
            "monitoring_duration": len(self.metrics),
            "cpu_average": cpu_avg,
            "memory_average_mb": memory_avg,
            "memory_peak_mb": memory_peak,
            "total_samples": len(self.metrics)
        }
```

---

**Performance Test Execution Schedule**:
- **Week 1**: Baseline measurements and component profiling
- **Week 2**: Load testing and scalability validation
- **Week 3**: Stress testing and limit identification
- **Week 4**: Optimization and regression testing

**Next**: Continue with UI test cases in `test_cases_ui.md`
