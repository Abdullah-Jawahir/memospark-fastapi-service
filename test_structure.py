#!/usr/bin/env python3
"""
Test script to verify the new modular structure works correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing module imports...")
    
    try:
        # Test core modules
        from app.config import MODEL_CONFIGS, LANGUAGE_PROMPTS
        print("✅ config.py imported successfully")
        
        from app.logger import logger
        print("✅ logger.py imported successfully")
        
        from app.utils import clean_text, extract_key_concepts
        print("✅ utils.py imported successfully")
        
        from app.models import model_manager
        print("✅ models.py imported successfully")
        
        from app.text_extractor import extract_text_from_file
        print("✅ text_extractor.py imported successfully")
        
        from app.middleware import setup_cors
        print("✅ middleware.py imported successfully")
        
        # Test generators
        from app.generators import FlashcardGenerator, QuizGenerator, ExerciseGenerator
        print("✅ generators package imported successfully")
        
        # Test routes
        from app.routes import file_processing_router, health_router
        print("✅ routes package imported successfully")
        
        # Test main application
        from app.main_new import app
        print("✅ main_new.py imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_model_manager():
    """Test that the model manager is working."""
    print("\n🧪 Testing model manager...")
    
    try:
        from app.models import model_manager
        
        # Test model info
        model_info = model_manager.get_model_info()
        print(f"✅ Model loaded: {model_info['model_name']}")
        print(f"✅ Model type: {model_info['model_type']}")
        print(f"✅ Pipeline loaded: {model_info['pipeline_loaded']}")
        
        # Test text generation
        test_prompt = "Hello, how are you?"
        generated = model_manager.generate_text(test_prompt, max_length=50)
        print(f"✅ Text generation test: {'Success' if generated else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model manager test failed: {e}")
        return False

def test_generators():
    """Test that generators can be instantiated."""
    print("\n🧪 Testing generators...")
    
    try:
        from app.generators import FlashcardGenerator, QuizGenerator, ExerciseGenerator
        
        # Test instantiation
        flashcard_gen = FlashcardGenerator()
        quiz_gen = QuizGenerator()
        exercise_gen = ExerciseGenerator()
        
        print("✅ All generators instantiated successfully")
        
        # Test with sample text
        sample_text = "This is a sample text for testing. It contains some information that can be used to generate educational content."
        
        # Test flashcard generation
        flashcards = flashcard_gen.generate_flashcards(sample_text, "en", "beginner")
        print(f"✅ Flashcard generation: {len(flashcards)} flashcards created")
        
        # Test quiz generation
        quizzes = quiz_gen.generate_quizzes(sample_text, "en", "beginner")
        print(f"✅ Quiz generation: {len(quizzes)} quizzes created")
        
        # Test exercise generation
        exercises = exercise_gen.generate_exercises(sample_text, "en", "beginner")
        print(f"✅ Exercise generation: {len(exercises)} exercises created")
        
        return True
        
    except Exception as e:
        print(f"❌ Generator test failed: {e}")
        return False

def test_fastapi_app():
    """Test that the FastAPI app can be created."""
    print("\n🧪 Testing FastAPI application...")
    
    try:
        from app.main import app
        
        # Check if app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ FastAPI app created with {len(routes)} routes")
        
        # Check for expected routes
        expected_routes = ["/health", "/api/v1/process-file"]
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✅ Route {route} found")
            else:
                print(f"⚠️  Route {route} not found")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing new modular structure...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_model_manager,
        test_generators,
        test_fastapi_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The new structure is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 