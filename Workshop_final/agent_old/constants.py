"""
Constants for the LangGraph Agent
"""

from dataclasses import dataclass
from typing import List


@dataclass
class AgentConstants:
    """Constants for the LangGraph Agent"""
    MAX_CONVERSATION_HISTORY: int = 5
    MAX_PRODUCTS_TO_EXTRACT: int = 3
    DEFAULT_MAX_RESULTS: int = 3
    VALID_INTENTS: List[str] = None
    
    def __post_init__(self):
        if self.VALID_INTENTS is None:
            self.VALID_INTENTS = ["greeting", "search", "compare", "recommend", "review", "direct"]
