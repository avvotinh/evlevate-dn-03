"""
Agents module for E-commerce AI Product Advisor  
Contains ReAct agent implementation for product advisory
"""

from .react_agent import ProductAdvisorReActAgent, get_agent_manager

__all__ = [
    "ProductAdvisorReActAgent",
    "get_agent_manager"
]
