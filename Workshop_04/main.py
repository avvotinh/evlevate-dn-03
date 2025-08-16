#!/usr/bin/env python3
"""
Main entry point for E-commerce AI Product Advisor Chatbot with ReAct Agent
Run this script to start the Streamlit application with ReAct agent integration.
"""

import sys
import os

# Add the src directory to Python path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the ReAct Agent application."""
    try:
        print("🚀 Starting AI Product Advisor with ReAct Agent...")
        print("🤖 Initializing ReAct Agent components...")
        
        # Import and run the Streamlit app
        from src.ui.app import main as run_app
        run_app()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        print("\nFor ReAct Agent support, ensure you have:")
        print("- langchain (for ReAct pattern)")
        print("- All tool dependencies")
        
    except Exception as e:
        print(f"❌ Error starting ReAct Agent application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
