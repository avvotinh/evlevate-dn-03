"""
Agent Manager for handling ProductAdvisorAgent instances
"""

from typing import List

from src.utils.logger import get_logger

logger = get_logger("agent_manager")


class AgentManager:
    """Improved agent manager with better session handling"""
    
    def __init__(self):
        # Import here to avoid circular imports
        from .product_advisor_agent import ProductAdvisorAgent
        self.agent = ProductAdvisorAgent()
        logger.info("✅ LangGraph Agent Manager initialized")
    
    def get_agent(self, session_id: str = "default"):
        """Get agent instance"""
        return self.agent
    
    def clear_session(self, session_id: str) -> bool:
        """Clear specific session - limited by LangGraph MemorySaver"""
        logger.info(f"⚠️ Individual session clearing not supported by MemorySaver")
        return False
    
    def clear_all_sessions(self) -> bool:
        """Clear all sessions by recreating agent"""
        try:
            from .product_advisor_agent import ProductAdvisorAgent
            self.agent = ProductAdvisorAgent()
            logger.info("✅ All sessions cleared by recreating agent")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing all sessions: {e}")
            return False
    
    def get_active_sessions(self) -> List[str]:
        """Get active sessions - not available with MemorySaver"""
        logger.info("ℹ️ Session tracking handled internally by LangGraph")
        return []


# Global instance
agent_manager = AgentManager()

def get_agent_manager() -> AgentManager:
    """Get agent manager instance"""
    return agent_manager
