#!/usr/bin/env python3
"""
Test the complete fallback pipeline: OpenRouter → Gemini → Local → Rule-based
"""

import sys
import os
import asyncio
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging to see the fallback behavior
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from app.config import OPENROUTER_MODELS_TO_TRY, OPENROUTER_API_KEY, GEMINI_API_KEY
try:
    from app.config import USE_RULE_BASED_FALLBACK
except ImportError:
    USE_RULE_BASED_FALLBACK = False  # Default value if not defined
from app.models import ModelManager

async def test_fallback_pipeline():
    """Test the complete fallback pipeline."""
    print("🧪 Testing Complete Fallback Pipeline")
    print("=" * 60)
    
    # Configuration status
    print("📋 Configuration Status:")
    print(f"  🔑 OpenRouter API Key: {'✅ Set' if OPENROUTER_API_KEY else '❌ Missing'}")
    print(f"  🌟 Gemini API Key: {'✅ Set' if GEMINI_API_KEY else '❌ Missing'}")
    print(f"  📝 Rule-based fallback: {'✅ Enabled' if USE_RULE_BASED_FALLBACK else '❌ Disabled'}")
    print(f"  🤖 OpenRouter models: {len(OPENROUTER_MODELS_TO_TRY)} configured")
    
    for i, model in enumerate(OPENROUTER_MODELS_TO_TRY, 1):
        print(f"      {i}. {model}")
    
    print("\n" + "=" * 60)
    
    # Initialize model manager
    print("🚀 Initializing ModelManager...")
    manager = ModelManager()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Simple Question",
            "prompt": "What is 2+2? Answer in one word.",
            "max_length": 50
        },
        {
            "name": "Content Generation", 
            "prompt": "Generate a short flashcard question about photosynthesis.",
            "max_length": 100
        }
    ]
    
    print("\n🎯 Testing Scenarios:")
    print("-" * 40)
    
    for scenario in test_scenarios:
        print(f"\n📝 Test: {scenario['name']}")
        print(f"   Prompt: {scenario['prompt']}")
        print(f"   Max length: {scenario['max_length']}")
        print("   " + "-" * 30)
        
        try:
            # Test the complete pipeline
            result = manager.generate_text(scenario['prompt'], scenario['max_length'])
            
            if result:
                print(f"   ✅ SUCCESS: Generated {len(result)} characters")
                print(f"   📄 Result: {result[:150]}{'...' if len(result) > 150 else ''}")
            else:
                print(f"   ❌ FAILED: No result generated")
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("   - This test verifies the complete fallback chain")
    print("   - OpenRouter models should be tried first")
    print("   - If OpenRouter fails, Gemini should be attempted")
    print("   - Check the logs above for the exact fallback sequence")
    print("   - Look for emoji indicators: 🔄 (OpenRouter), 🌟 (Gemini), 🏠 (Local), 📝 (Rule-based)")

if __name__ == "__main__":
    asyncio.run(test_fallback_pipeline())
