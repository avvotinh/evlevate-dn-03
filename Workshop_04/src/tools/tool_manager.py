"""
Tool Manager for E-commerce AI Product Advisor
Centralizes all tools for easy integration with LangGraph agents.
"""

from typing import List
from langchain.tools import BaseTool

from .search_tool import search_tool
from .compare_tool import compare_tool
from .recommend_tool import recommend_tool
from .rag_generation_tool import rag_generation_tool

from src.utils.logger import get_logger

logger = get_logger("tool_manager")


class ToolManager:
    """Manages all available tools for the chatbot"""
    
    def __init__(self):
        """Initialize tool manager with all available tools"""
        self._tools = {
            "search": search_tool,
            "compare": compare_tool,
            "recommend": recommend_tool,
            "answer_with_context": rag_generation_tool
        }
        
        logger.info(f"✅ ToolManager initialized with {len(self._tools)} tools")
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all available tools as a list"""
        return list(self._tools.values())
    
    def get_tool(self, tool_name: str) -> BaseTool:
        """Get a specific tool by name"""
        return self._tools.get(tool_name)
    
    def get_tool_names(self) -> List[str]:
        """Get names of all available tools"""
        return list(self._tools.keys())
    
    def describe_tools(self) -> dict:
        """Get descriptions of all tools"""
        descriptions = {}
        for name, tool in self._tools.items():
            descriptions[name] = {
                "name": tool.name,
                "description": tool.description,
                "schema": tool.args_schema.schema() if tool.args_schema else None
            }
        return descriptions


# Global tool manager instance
tool_manager = ToolManager()

# Export tools for easy import
__all__ = [
    "tool_manager",
    "search_tool", 
    "compare_tool", 
    "recommend_tool",
    "rag_generation_tool"
]
