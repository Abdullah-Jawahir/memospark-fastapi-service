#!/usr/bin/env python3
"""
Test script to verify the content generation fixes.
Run this to test if the JSON parsing and validation issues are resolved.
"""

import os
import sys
sys.path.append('app')

from app.generators.all_content_generator import generate_all_content

def test_content_generation():
    """Test the content generation with various scenarios."""
    
    print("🧪 Testing Content Generation Fixes")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid JSON Response",
            "text": "Python is a programming language. It is used for web development, data science, and automation.",
            "language": "en",
            "difficulty": "beginner"
        },
        {
            "name": "Empty Text",
            "text": "",
            "language": "en", 
            "difficulty": "beginner"
        },
        {
            "name": "Short Text",
            "text": "Hello world.",
            "language": "en",
            "difficulty": "beginner"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Text: {test_case['text'][:50]}...")
        
        try:
            result = generate_all_content(
                test_case['text'], 
                test_case['language'], 
                test_case['difficulty']
            )
            
            # Check results
            flashcards = result.get('flashcards', [])
            quizzes = result.get('quizzes', [])
            exercises = result.get('exercises', [])
            
            total_items = len(flashcards) + len(quizzes) + len(exercises)
            
            if total_items > 0:
                print(f"✅ Success! Generated {total_items} items:")
                print(f"   - {len(flashcards)} flashcards")
                print(f"   - {len(quizzes)} quizzes") 
                print(f"   - {len(exercises)} exercises")
                
                # Show first item as example
                if flashcards:
                    print(f"   Sample flashcard: {flashcards[0].get('question', 'N/A')[:50]}...")
                elif quizzes:
                    print(f"   Sample quiz: {quizzes[0].get('question', 'N/A')[:50]}...")
                elif exercises:
                    print(f"   Sample exercise: {exercises[0].get('instruction', 'N/A')[:50]}...")
            else:
                print("❌ No content generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🔍 Testing JSON Parsing Edge Cases...")
    
    # Test JSON cleanup
    test_json = '{"flashcards": [{"question": "test?", "answer": "test"},], "quizzes": [], "exercises": []}'
    print(f"Test JSON with trailing comma: {test_json}")
    
    import re
    cleaned = re.sub(r',\s*}', '}', test_json)
    cleaned = re.sub(r',\s*]', ']', cleaned)
    print(f"Cleaned JSON: {cleaned}")
    
    try:
        import json
        parsed = json.loads(cleaned)
        print(f"✅ JSON parsing successful: {len(parsed.get('flashcards', []))} flashcards")
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")

if __name__ == "__main__":
    test_content_generation()
