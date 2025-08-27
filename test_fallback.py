#!/usr/bin/env python3
"""
Test script to verify the multi-model fallback strategy.
Run this to test if your fallback system is working correctly.
"""

import os
import sys
sys.path.append('app')

from app.models import model_manager
from app.config import OPENROUTER_MODELS_TO_TRY

def test_fallback_strategy():
    """Test the fallback strategy with a simple prompt."""
    
    print("🧪 Testing Multi-Model Fallback Strategy")
    print("=" * 50)
    
    # Test prompt
    test_prompt = "Generate a simple quiz question about Python programming."
    
    print(f"📝 Test Prompt: {test_prompt}")
    print(f"🔑 OpenRouter API Key: {'✅ Set' if os.getenv('OPENROUTER_API_KEY') else '❌ Not Set'}")
    print(f"🌐 OpenRouter Enabled: {'✅ Yes' if model_manager.use_openrouter else '❌ No'}")
    print(f"🔄 Fallback to Local: {'✅ Yes' if hasattr(model_manager, '_ensure_local_model_loaded') else '❌ No'}")
    
    print(f"\n📋 Available Models ({len(OPENROUTER_MODELS_TO_TRY)}):")
    for i, model in enumerate(OPENROUTER_MODELS_TO_TRY):
        print(f"  {i+1}. {model}")
    
    print(f"\n🚀 Current Model: {model_manager.current_model_name or 'None'}")
    print(f"🔧 Model Type: {'OpenRouter' if model_manager.use_openrouter else 'Local'}")
    
    print("\n🔄 Testing Generation...")
    try:
        result = model_manager.generate_text(test_prompt, max_length=100)
        if result:
            print(f"✅ Success! Generated {len(result)} characters")
            print(f"📄 Result: {result[:100]}...")
        else:
            print("❌ Failed to generate text")
    except Exception as e:
        print(f"❌ Error during generation: {e}")
    
    print("\n📊 Model Info:")
    try:
        info = model_manager.get_model_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"❌ Error getting model info: {e}")

if __name__ == "__main__":
    test_fallback_strategy()
