"""
E-commerce AI Product Advisor Chatbot with ReAct Agent
Main package initialization for AI Product Advisor system
"""

__version__ = "1.0.0"
__title__ = "E-commerce AI Product Advisor"
__description__ = "AI-powered product advisor chatbot with ReAct agent for e-commerce platforms"
__author__ = "AI Product Advisor Team"

# Core modules
from . import config
from . import services 
from . import tools
from . import agents
from . import prompts
from . import utils
from . import ui

__all__ = [
    "config",
    "services", 
    "tools",
    "agents", 
    "prompts",
    "utils",
    "ui"
]
