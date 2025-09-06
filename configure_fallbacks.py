#!/usr/bin/env python3
"""
Configuration script to disable rule-based fallbacks for document processing.
This prevents the generation of irrelevant content when OpenRouter models are rate-limited.
"""

import os
from pathlib import Path

def configure_for_quality_content():
    """Configure the service to prioritize content quality over quantity."""
    
    env_file = Path(__file__).parent / ".env"
    
    # Read existing .env file if it exists
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Set recommended configuration for quality content
    env_vars['ENABLE_OPENROUTER'] = 'true'
    env_vars['ENABLE_GEMINI'] = 'true'  # Enable Gemini as fallback
    env_vars['FALLBACK_TO_LOCAL'] = 'false'  # Disable local model fallback for better quality
    env_vars['ENABLE_RULE_BASED_FALLBACK'] = 'false'  # Disable rule-based fallback
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.write("# FastAPI Document Processing Configuration\n")
        f.write("# Updated by configure_fallbacks.py for quality content\n\n")
        
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Configuration updated for quality content generation!")
    print(f"✅ Updated {env_file}")
    print("\nSettings applied:")
    print("- ✅ OpenRouter API enabled (better AI models)")
    print("- ✅ Gemini API enabled (fallback when OpenRouter fails)")
    print("- ❌ Local model fallback disabled (prevents poor quality)")
    print("- ❌ Rule-based fallback disabled (prevents irrelevant content)")
    print("\nRecommendations:")
    print("1. Get an OpenRouter API key for higher rate limits: https://openrouter.ai/")
    print("2. Get a Gemini API key for additional fallback: https://aistudio.google.com/")
    print("3. Add your API keys to .env:")
    print("   OPENROUTER_API_KEY=your_openrouter_key_here")
    print("   GEMINI_API_KEY=your_gemini_key_here")
    print("4. Restart your FastAPI service: uvicorn app.main:app --reload --port 8001")

def configure_for_fallbacks():
    """Configure the service to always generate content (may be lower quality)."""
    
    env_file = Path(__file__).parent / ".env"
    
    # Read existing .env file if it exists
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Set configuration for maximum content generation
    env_vars['ENABLE_OPENROUTER'] = 'true'
    env_vars['FALLBACK_TO_LOCAL'] = 'true'  # Enable local model fallback
    env_vars['ENABLE_RULE_BASED_FALLBACK'] = 'true'  # Enable rule-based fallback
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.write("# FastAPI Document Processing Configuration\n")
        f.write("# Updated by configure_fallbacks.py for maximum content\n\n")
        
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Configuration updated for maximum content generation!")
    print(f"✅ Updated {env_file}")
    print("\nSettings applied:")
    print("- ✅ OpenRouter API enabled")
    print("- ✅ Local model fallback enabled")
    print("- ✅ Rule-based fallback enabled")
    print("\nWarning: This may generate irrelevant content when AI models fail!")

if __name__ == "__main__":
    print("FastAPI Document Processing Configuration")
    print("=" * 50)
    print("\nChoose configuration mode:")
    print("1. Quality Mode (recommended) - Only high-quality AI-generated content")
    print("2. Fallback Mode - Always generate content (may be irrelevant)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        configure_for_quality_content()
    elif choice == "2":
        configure_for_fallbacks()
    else:
        print("❌ Invalid choice. Please run the script again and choose 1 or 2.")
