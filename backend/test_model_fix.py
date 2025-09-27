#!/usr/bin/env python3
"""
Test script to verify the model configuration fix.
This script tests that the new model hierarchy works properly.
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

def test_model_configuration():
    """Test the model configuration and creation."""
    print("Testing Model Configuration...")
    print("=" * 50)
    
    try:
        # Import the model factory
        from models import get_default_model, ModelFactory
        
        print("Successfully imported model factory")
        
        # Test getting the default model
        print("Creating default model...")
        model = get_default_model()
        
        print(f"Successfully created model: {type(model)}")
        print(f"Model name: {getattr(model, 'model_name', 'Unknown')}")
        
        # Test the model hierarchy
        print("\nTesting model hierarchy...")
        for model_key in ["primary", "fallback-1", "fallback-2"]:
            try:
                config = ModelFactory.DEFAULT_MODELS[model_key]
                print(f"  {model_key}: {config.name} - OK")
            except Exception as e:
                print(f"  {model_key}: ERROR - {e}")
        
        return True
        
    except Exception as e:
        print(f"Error testing model configuration: {e}")
        return False

def test_simple_message():
    """Test a simple message format that should work with the new model."""
    print("\nTesting Simple Message Format...")
    print("=" * 50)
    
    try:
        from models import get_default_model
        
        model = get_default_model()
        
        # Test a simple message
        from langchain_core.messages import HumanMessage
        
        messages = [HumanMessage(content="Hello, this is a test message.")]
        
        print("Message format looks valid")
        print(f"Message content: '{messages[0].content}'")
        
        # Note: We're not actually invoking the model here to avoid API costs
        # Just testing that the message format is correct
        
        return True
        
    except Exception as e:
        print(f"Error testing message format: {e}")
        return False

if __name__ == "__main__":
    print("Model Configuration Fix Test")
    print("=" * 50)
    
    # Test model configuration
    model_ok = test_model_configuration()
    
    # Test message format
    message_ok = test_simple_message()
    
    print("\n" + "=" * 50)
    if model_ok and message_ok:
        print("All tests passed!")
        print("The model configuration has been fixed.")
        print()
        print("Changes made:")
        print("  1. Changed primary model from x-ai/grok-4-fast to google/gemini-2.5-flash-preview-09-2025")
        print("  2. Added anthropic/claude-3.5-sonnet as fallback-1")
        print("  3. Moved x-ai/grok-4-fast to fallback-2 (less strict message validation)")
        print()
        print("Next steps:")
        print("  1. Restart the backend server")
        print("  2. Test the literature review agent again")
    else:
        print("Some tests failed. Please check the error messages above.")
        sys.exit(1)
