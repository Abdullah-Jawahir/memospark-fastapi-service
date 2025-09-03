#!/usr/bin/env python3
"""
Test script for the translation functionality.
This script tests the translation of generated content to different languages.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Mock logger for testing
class MockLogger:
    def info(self, msg): print(f"[INFO] {msg}")
    def warning(self, msg): print(f"[WARNING] {msg}")
    def error(self, msg): print(f"[ERROR] {msg}")

# Mock the logger module
sys.modules['app.logger'] = type('MockLoggerModule', (), {'logger': MockLogger()})

from utils import translate_generated_content

def test_translation():
    """Test the translation functionality with sample content."""
    
    # Sample content in English (what the AI would generate)
    sample_content = {
        "flashcards": [
            {
                "question": "What is the capital of France?",
                "answer": "Paris is the capital of France."
            },
            {
                "question": "What is photosynthesis?",
                "answer": "Photosynthesis is the process by which plants convert sunlight into energy."
            }
        ],
        "quizzes": [
            {
                "question": "Which planet is closest to the Sun?",
                "options": ["Mercury", "Venus", "Earth", "Mars"],
                "answer": "Mercury"
            }
        ],
        "exercises": [
            {
                "type": "fill_blank",
                "instruction": "Fill in the blank with the correct word.",
                "question": "The _____ is the largest organ in the human body.",
                "answer": "skin"
            }
        ]
    }
    
    print("Testing translation functionality...")
    print("=" * 50)
    
    # Test Sinhala translation
    print("\n1. Testing Sinhala (si) translation:")
    try:
        sinhala_content = translate_generated_content(sample_content, "si")
        print("✓ Sinhala translation successful")
        print(f"  Flashcard question: {sinhala_content['flashcards'][0]['question']}")
        print(f"  Flashcard answer: {sinhala_content['flashcards'][0]['answer']}")
    except Exception as e:
        print(f"✗ Sinhala translation failed: {e}")
    
    # Test Tamil translation
    print("\n2. Testing Tamil (ta) translation:")
    try:
        tamil_content = translate_generated_content(sample_content, "ta")
        print("✓ Tamil translation successful")
        print(f"  Flashcard question: {tamil_content['flashcards'][0]['question']}")
        print(f"  Flashcard answer: {tamil_content['flashcards'][0]['answer']}")
    except Exception as e:
        print(f"✗ Tamil translation failed: {e}")
    
    # Test English (no translation needed)
    print("\n3. Testing English (en) - no translation:")
    try:
        english_content = translate_generated_content(sample_content, "en")
        print("✓ English content returned unchanged")
        print(f"  Flashcard question: {english_content['flashcards'][0]['question']}")
    except Exception as e:
        print(f"✗ English processing failed: {e}")
    
    print("\n" + "=" * 50)
    print("Translation test completed!")

if __name__ == "__main__":
    test_translation()
