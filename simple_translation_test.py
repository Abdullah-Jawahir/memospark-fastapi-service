#!/usr/bin/env python3
"""
Simple test script for translation functionality.
This script tests the core translation logic using deep-translator.
"""

def test_basic_translation():
    """Test basic translation functionality."""
    
    print("Testing translation functionality with deep-translator...")
    print("=" * 50)
    
    try:
        from deep_translator import GoogleTranslator
        
        # Test English to Sinhala
        print("\n1. Testing English to Sinhala:")
        english_text = "What is the capital of France?"
        translator = GoogleTranslator(source='en', target='si')
        sinhala_text = translator.translate(english_text)
        print(f"  English: {english_text}")
        print(f"  Sinhala: {sinhala_text}")
        print("  ✓ Sinhala translation successful")
        
        # Test English to Tamil
        print("\n2. Testing English to Tamil:")
        translator = GoogleTranslator(source='en', target='ta')
        tamil_text = translator.translate(english_text)
        print(f"  English: {english_text}")
        print(f"  Tamil: {tamil_text}")
        print("  ✓ Tamil translation successful")
        
        # Test another sentence
        print("\n3. Testing another sentence:")
        english_text2 = "Education is the key to success."
        translator = GoogleTranslator(source='en', target='si')
        sinhala_text2 = translator.translate(english_text2)
        print(f"  English: {english_text2}")
        print(f"  Sinhala: {sinhala_text2}")
        print("  ✓ Additional translation successful")
        
    except ImportError:
        print("✗ deep-translator library not installed")
        print("  Please install it with: pip install deep-translator")
    except Exception as e:
        print(f"✗ Translation failed: {e}")
        print("  This might be due to network issues or API limitations")
    
    print("\n" + "=" * 50)
    print("Translation test completed!")

if __name__ == "__main__":
    test_basic_translation()
