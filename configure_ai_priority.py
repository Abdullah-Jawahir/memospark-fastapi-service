#!/usr/bin/env python3
"""
AI Model Priority Configuration Tool
Configure the order in which AI models are tried for text generation.
"""

import os
from pathlib import Path

def get_current_priority():
    """Get the current AI model priority configuration."""
    current = os.getenv("AI_MODEL_PRIORITY", "openrouter,gemini,local,rule_based")
    return current.split(",")

def set_priority(priority_list):
    """Set a new AI model priority configuration."""
    priority_string = ",".join(priority_list)
    
    # Check if .env file exists, if not create it
    env_file = Path(".env")
    
    if env_file.exists():
        # Read existing .env content
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add AI_MODEL_PRIORITY
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("AI_MODEL_PRIORITY="):
                lines[i] = f"AI_MODEL_PRIORITY={priority_string}\n"
                updated = True
                break
        
        # If not found, add it
        if not updated:
            lines.append(f"AI_MODEL_PRIORITY={priority_string}\n")
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(lines)
    else:
        # Create new .env file
        with open(env_file, 'w') as f:
            f.write(f"AI_MODEL_PRIORITY={priority_string}\n")
    
    print(f"✅ AI Model Priority set to: {' → '.join(priority_list)}")
    print(f"📝 Updated .env file with: AI_MODEL_PRIORITY={priority_string}")

def main():
    """Main configuration interface."""
    print("🤖 AI Model Priority Configuration Tool")
    print("=" * 50)
    
    current_priority = get_current_priority()
    print(f"📋 Current Priority: {' → '.join(current_priority)}")
    
    print("\n🎯 Available AI Services:")
    print("  1. openrouter - OpenRouter API (free tier models)")
    print("  2. gemini     - Google Gemini API")
    print("  3. local      - Local transformer models")
    print("  4. rule_based - Rule-based generation")
    
    print("\n🔧 Preset Configurations:")
    presets = {
        "1": {
            "name": "Gemini First (Recommended for quality)",
            "priority": ["gemini", "openrouter", "local", "rule_based"]
        },
        "2": {
            "name": "OpenRouter First (Current default)",
            "priority": ["openrouter", "gemini", "local", "rule_based"]
        },
        "3": {
            "name": "Local First (Privacy focused)",
            "priority": ["local", "gemini", "openrouter", "rule_based"]
        },
        "4": {
            "name": "Cloud Only (No local fallback)",
            "priority": ["gemini", "openrouter"]
        },
        "5": {
            "name": "Gemini Only",
            "priority": ["gemini"]
        },
        "6": {
            "name": "OpenRouter Only",
            "priority": ["openrouter"]
        }
    }
    
    for key, preset in presets.items():
        print(f"  {key}. {preset['name']}")
        print(f"     Priority: {' → '.join(preset['priority'])}")
    
    print("  7. Custom configuration")
    print("  8. Exit without changes")
    
    choice = input("\n🎯 Select configuration (1-8): ").strip()
    
    if choice in presets:
        set_priority(presets[choice]["priority"])
        print(f"\n🚀 Configuration applied! Restart your FastAPI service to use the new priority.")
    elif choice == "7":
        print("\n🔧 Custom Configuration")
        print("Enter AI services in priority order, separated by commas")
        print("Available: openrouter, gemini, local, rule_based")
        custom = input("Priority order: ").strip()
        
        if custom:
            custom_list = [service.strip().lower() for service in custom.split(",")]
            valid_services = {"openrouter", "gemini", "local", "rule_based"}
            custom_list = [service for service in custom_list if service in valid_services]
            
            if custom_list:
                set_priority(custom_list)
                print(f"\n🚀 Custom configuration applied! Restart your FastAPI service to use the new priority.")
            else:
                print("❌ No valid services provided!")
        else:
            print("❌ No configuration provided!")
    elif choice == "8":
        print("👋 Exiting without changes.")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
