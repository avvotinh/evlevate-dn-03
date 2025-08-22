"""
Simple logging utilities for E-commerce AI Product Advisor Chatbot
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "ecommerce_ai_advisor", level: str = "INFO") -> logging.Logger:
    """
    Setup a simple logger for the application
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Create logs directory and file handler (optional)
    try:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            logs_dir / "app.log", 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    return logger


class Logger:
    """Simple logger wrapper for easy use"""
    
    def __init__(self, module_name: str):
        self.logger = setup_logger(f"ecommerce_ai_advisor.{module_name}")
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str, error: Exception = None):
        """Log error message"""
        if error:
            self.logger.error(f"{message}: {str(error)}")
        else:
            self.logger.error(message)
    
    def critical(self, message: str, error: Exception = None):
        """Log critical message"""
        if error:
            self.logger.critical(f"{message}: {str(error)}")
        else:
            self.logger.critical(message)


def get_logger(module_name: str) -> Logger:
    """Get a logger for a specific module"""
    return Logger(module_name)


# Performance tracking decorator
def track_time(func):
    """Simple decorator to track function execution time"""
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger = get_logger(func.__module__ or "unknown")
            logger.info(f"Function '{func.__name__}' executed in {execution_time:.3f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger = get_logger(func.__module__ or "unknown")
            logger.error(f"Function '{func.__name__}' failed after {execution_time:.3f}s", error=e)
            raise
    
    return wrapper


# Initialize main logger
main_logger = setup_logger()
main_logger.info("✅ Simple logging system initialized")
