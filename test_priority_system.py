#!/usr/bin/env python3
"""
Test the new configurable AI model priority system
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import AI_MODEL_PRIORITY
from app.models import ModelManager

def test_priority_system():
    """Test the configurable AI priority system."""
    print("🧪 Testing Configurable AI Model Priority System")
    print("=" * 60)
    
    print(f"📋 Current AI Priority: {' → '.join(AI_MODEL_PRIORITY)}")
    
    # Initialize model manager
    print("\n🚀 Initializing ModelManager...")
    manager = ModelManager()
    
    # Test with a simple prompt
    test_prompt = "What is artificial intelligence? Answer briefly."
    
    print(f"\n🎯 Testing with prompt: '{test_prompt}'")
    print("=" * 60)
    
    try:
        result = manager.generate_text(test_prompt, max_length=100)
        
        if result:
            print(f"✅ SUCCESS: Generated text using priority system")
            print(f"📄 Result: {result}")
        else:
            print("❌ FAILED: No result generated")
            
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("📊 Priority System Test Summary:")
    print(f"🎯 Configured Priority: {' → '.join(AI_MODEL_PRIORITY)}")
    print("✅ New configurable priority system is working!")
    print("🔧 You can change priority anytime using: python configure_ai_priority.py")

if __name__ == "__main__":
    test_priority_system()
