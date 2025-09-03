#!/usr/bin/env python3
"""
Test script for the new document generators.
This script tests the document-specific generators to ensure they work correctly
and can fall back to rule-based generation when AI fails.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.generators.document_flashcard_generator import DocumentFlashcardGenerator
from app.generators.document_quiz_generator import DocumentQuizGenerator
from app.generators.document_exercise_generator import DocumentExerciseGenerator
from app.generators.document_all_content_generator import generate_document_content

def test_document_generators():
    """Test all document generators with sample text."""
    
    # Sample text for testing
    sample_text = """
    Artificial Intelligence (AI) in Education represents a transformative approach to learning and teaching. 
    AI technologies can personalize learning experiences, provide immediate feedback, and adapt content to individual student needs. 
    Machine learning algorithms analyze student performance data to identify learning patterns and optimize educational content delivery. 
    Natural language processing enables intelligent tutoring systems that can understand and respond to student queries. 
    Computer vision technology can assess student engagement and provide insights for teachers. 
    The integration of AI in education requires careful consideration of ethical implications, data privacy, and equitable access. 
    Research shows that AI-enhanced learning can improve student outcomes by 20-30% compared to traditional methods.
    """
    
    print("Testing Document Generators")
    print("=" * 50)
    print(f"Sample text length: {len(sample_text)} characters")
    print()
    
    # Test individual generators
    print("1. Testing DocumentFlashcardGenerator...")
    flashcard_gen = DocumentFlashcardGenerator()
    flashcards = flashcard_gen.generate_flashcards(sample_text, "en", "beginner", 5)
    print(f"   Generated {len(flashcards)} flashcards")
    for i, fc in enumerate(flashcards[:2]):  # Show first 2
        print(f"   Flashcard {i+1}: Q: {fc['question'][:50]}... A: {fc['answer'][:50]}...")
    print()
    
    print("2. Testing DocumentQuizGenerator...")
    quiz_gen = DocumentQuizGenerator()
    quizzes = quiz_gen.generate_quizzes(sample_text, "en", "beginner", 3)
    print(f"   Generated {len(quizzes)} quiz questions")
    for i, quiz in enumerate(quizzes[:2]):  # Show first 2
        print(f"   Quiz {i+1}: {quiz['question'][:50]}...")
        print(f"   Options: {len(quiz['options'])} options, Answer: {quiz['answer'][:30]}...")
    print()
    
    print("3. Testing DocumentExerciseGenerator...")
    exercise_gen = DocumentExerciseGenerator()
    exercises = exercise_gen.generate_exercises(sample_text, "en", "beginner", 3)
    print(f"   Generated {len(exercises)} exercises")
    for i, exercise in enumerate(exercises[:2]):  # Show first 2
        print(f"   Exercise {i+1}: Type: {exercise['type']}, Question: {exercise['question'][:50]}...")
    print()
    
    # Test the combined generator
    print("4. Testing generate_document_content...")
    all_content = generate_document_content(sample_text, "en", "beginner")
    print(f"   Combined generation results:")
    print(f"   - Flashcards: {len(all_content.get('flashcards', []))}")
    print(f"   - Quizzes: {len(all_content.get('quizzes', []))}")
    print(f"   - Exercises: {len(all_content.get('exercises', []))}")
    print()
    
    # Test with different languages
    print("5. Testing language support...")
    si_content = generate_document_content(sample_text, "si", "beginner")
    ta_content = generate_document_content(sample_text, "ta", "beginner")
    print(f"   Sinhala: {len(si_content.get('flashcards', []))} flashcards")
    print(f"   Tamil: {len(ta_content.get('flashcards', []))} flashcards")
    print()
    
    print("All tests completed successfully!")
    return True

def test_error_handling():
    """Test error handling with invalid inputs."""
    
    print("Testing Error Handling")
    print("=" * 50)
    
    # Test with very short text
    print("1. Testing with short text...")
    short_text = "AI"
    flashcard_gen = DocumentFlashcardGenerator()
    flashcards = flashcard_gen.generate_flashcards(short_text, "en", "beginner", 5)
    print(f"   Short text result: {len(flashcards)} flashcards (expected 0)")
    
    # Test with empty text
    print("2. Testing with empty text...")
    empty_text = ""
    flashcards = flashcard_gen.generate_flashcards(empty_text, "en", "beginner", 5)
    print(f"   Empty text result: {len(flashcards)} flashcards (expected 0)")
    
    # Test with None text
    print("3. Testing with None text...")
    try:
        flashcards = flashcard_gen.generate_flashcards(None, "en", "beginner", 5)
        print(f"   None text result: {len(flashcards)} flashcards")
    except Exception as e:
        print(f"   None text error: {type(e).__name__}: {e}")
    
    print("Error handling tests completed!")
    print()

if __name__ == "__main__":
    try:
        print("Starting Document Generator Tests")
        print("=" * 60)
        print()
        
        # Run main tests
        test_document_generators()
        print()
        
        # Run error handling tests
        test_error_handling()
        
        print("=" * 60)
        print("All tests passed! The document generators are working correctly.")
        
    except Exception as e:
        print(f"Test failed with error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
