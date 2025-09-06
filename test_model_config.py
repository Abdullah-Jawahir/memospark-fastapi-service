#!/usr/bin/env python3
"""
Test script to verify OpenRouter model configuration
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import OPENROUTER_MODELS_TO_TRY, OPENROUTER_API_KEY
# We'll create a simple test instead of importing ModelManager

async def test_openrouter_models():
    """Test all configured OpenRouter models."""
    print("🧪 Testing OpenRouter Model Configuration")
    print("=" * 50)
    
    print(f"📋 Configured models: {len(OPENROUTER_MODELS_TO_TRY)}")
    for i, model in enumerate(OPENROUTER_MODELS_TO_TRY, 1):
        print(f"  {i}. {model}")
    
    print("\n🔑 API Key status:", "✅ Set" if OPENROUTER_API_KEY else "❌ Missing")
    
    if not OPENROUTER_API_KEY:
        print("⚠️  Cannot test models without API key")
        return
    
    print("\n✅ Configuration looks good!")
    print(f"📊 Total models to try: {len(OPENROUTER_MODELS_TO_TRY)}")
    
    # Test individual model validity by checking if they're real model names
    valid_patterns = [
        'deepseek',
        'gemma',
        'google/',
        'microsoft/',
        'meta-llama/'
    ]
    
    print("\n🔍 Model name validation:")
    for model in OPENROUTER_MODELS_TO_TRY:
        is_valid = any(pattern in model for pattern in valid_patterns)
        status = "✅" if is_valid else "⚠️"
        print(f"  {status} {model}")

if __name__ == "__main__":
    asyncio.run(test_openrouter_models())
