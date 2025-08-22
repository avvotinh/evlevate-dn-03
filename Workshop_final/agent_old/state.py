"""
State definitions for the LangGraph Agent
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Enhanced state for LangGraph agent with conversation history"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_input: str
    session_id: Optional[str]
    current_step: str
    intent: str
    tools_used: List[str]
    search_results: Optional[Dict[str, Any]]
    comparison_results: Optional[Dict[str, Any]]
    recommendation_results: Optional[Dict[str, Any]]
    review_results: Optional[Dict[str, Any]]
    context_data: Optional[str]
    final_response: Optional[str]
    iteration_count: int
    error_count: int
    reasoning_steps: List[Dict[str, Any]]
    # Memory-related fields for context continuity
    conversation_history: List[Dict[str, str]]
    previous_search_results: Optional[List[Dict[str, Any]]]
    previous_products: Optional[List[str]]
    context_references: Optional[Dict[str, Any]]
