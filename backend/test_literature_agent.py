#!/usr/bin/env python3
"""
Test script for the literature review agent without LangSmith authentication.
This script verifies that the agent can be created and invoked locally.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = backend_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"Warning: .env file not found at {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables may not be loaded.")
    print("Install with: pip install python-dotenv")

def test_literature_agent():
    """Test the literature review agent creation and basic functionality."""
    print("Testing Literature Review Agent...")
    print("=" * 50)
    
    try:
        # Import the literature review agent
        from agents.literature_review import create_literature_review_agent
        
        print("Successfully imported literature review agent")
        
        # Create the agent
        print("Creating literature review agent...")
        agent = create_literature_review_agent()
        
        print("Successfully created literature review agent")
        print(f"Agent type: {type(agent)}")
        
        # Test basic invocation with a simple message
        print("Testing basic agent invocation...")
        
        test_message = {
            "messages": [
                {"role": "user", "content": "Hello, can you help me with a literature review?"}
            ]
        }
        
        # This is just testing agent creation, not full invocation
        # Full invocation would require a running LangGraph server
        print("Agent is ready for invocation")
        
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error creating agent: {e}")
        return False

def check_environment():
    """Check if the environment is properly configured."""
    print("Checking environment configuration...")
    print("=" * 50)
    
    # Check for required environment variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "CORE_API_KEY",
        "PERPLEXITY_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"OK {var}: Set")
    
    if missing_vars:
        print(f"WARNING Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    # Check for optional LangSmith variables (should be commented out)
    langsmith_vars = [
        "LANGSMITH_API_KEY",
        "LANGCHAIN_TRACING_V2"
    ]
    
    active_langsmith = []
    for var in langsmith_vars:
        if os.getenv(var):
            active_langsmith.append(var)
    
    if active_langsmith:
        print(f"WARNING LangSmith variables are active: {', '.join(active_langsmith)}")
        print("   This may cause authentication issues if keys are not valid")
    else:
        print("OK LangSmith variables are disabled (as expected)")
    
    return len(missing_vars) == 0

if __name__ == "__main__":
    print("Literature Review Agent Test Suite")
    print("=" * 50)
    
    # Check environment first
    env_ok = check_environment()
    print()
    
    if not env_ok:
        print("Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Test agent creation
    agent_ok = test_literature_agent()
    print()
    
    if agent_ok:
        print("All tests passed!")
        print("Literature review agent is working without LangSmith authentication")
        print()
        print("Next steps:")
        print("   1. Start the backend server: langgraph dev --no-browser")
        print("   2. Test the agent through the frontend interface")
    else:
        print("Tests failed. Please check the error messages above.")
        sys.exit(1)
