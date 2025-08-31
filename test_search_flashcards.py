#!/usr/bin/env python3
"""
Test script for the new search flashcards functionality.
This script tests the topic content generation and flashcard creation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.generators.topic_content_generator import TopicContentGenerator
from app.generators.flashcard_generator import FlashcardGenerator
from app.logger import logger

def test_topic_content_generation():
    """Test the topic content generation functionality."""
    print("Testing Topic Content Generation...")
    print("=" * 50)
    
    try:
        # Initialize the topic content generator
        topic_generator = TopicContentGenerator()
        
        # Test topics
        test_topics = [
            "Python Programming",
            "Quantum Physics",
            "World War II",
            "Photosynthesis"
        ]
        
        for topic in test_topics:
            print(f"\nTesting topic: {topic}")
            print("-" * 30)
            
            # Generate content
            content = topic_generator.generate_topic_content(
                topic=topic,
                description=f"Basic concepts and fundamentals of {topic}",
                difficulty="beginner"
            )
            
            if content:
                print(f"✓ Content generated successfully")
                print(f"Content length: {len(content)} characters")
                print(f"First 200 chars: {content[:200]}...")
                
                # Generate summary
                summary = topic_generator.generate_topic_summary(topic, content)
                print(f"✓ Summary generated: {summary['main_theme']}")
                
            else:
                print(f"✗ Failed to generate content for {topic}")
        
        print("\n" + "=" * 50)
        print("Topic Content Generation Test Completed!")
        
    except Exception as e:
        print(f"Error in topic content generation test: {str(e)}")
        logger.error(f"Test error: {str(e)}")

def test_flashcard_generation():
    """Test the flashcard generation from topic content."""
    print("\nTesting Flashcard Generation...")
    print("=" * 50)
    
    try:
        # Initialize generators
        topic_generator = TopicContentGenerator()
        flashcard_generator = FlashcardGenerator()
        
        # Test with a specific topic
        test_topic = "Machine Learning"
        print(f"Testing flashcard generation for: {test_topic}")
        
        # Generate topic content
        content = topic_generator.generate_topic_content(
            topic=test_topic,
            description="Introduction to basic machine learning concepts",
            difficulty="beginner"
        )
        
        if content:
            print(f"✓ Topic content generated ({len(content)} characters)")
            
            # Generate flashcards from the content
            flashcards = flashcard_generator.generate_flashcards(
                text=content,
                language="en",
                difficulty="beginner"
            )
            
            if flashcards:
                print(f"✓ Generated {len(flashcards)} flashcards")
                
                # Display first few flashcards
                for i, flashcard in enumerate(flashcards[:3]):
                    print(f"\nFlashcard {i+1}:")
                    print(f"Question: {flashcard['question']}")
                    print(f"Answer: {flashcard['answer']}")
                    print(f"Type: {flashcard['type']}")
                    print(f"Difficulty: {flashcard['difficulty']}")
            else:
                print("✗ Failed to generate flashcards")
        else:
            print("✗ Failed to generate topic content")
        
        print("\n" + "=" * 50)
        print("Flashcard Generation Test Completed!")
        
    except Exception as e:
        print(f"Error in flashcard generation test: {str(e)}")
        logger.error(f"Test error: {str(e)}")

def test_end_to_end():
    """Test the complete end-to-end functionality."""
    print("\nTesting End-to-End Functionality...")
    print("=" * 50)
    
    try:
        # Initialize generators
        topic_generator = TopicContentGenerator()
        flashcard_generator = FlashcardGenerator()
        
        # Test with a simple topic
        test_topic = "Solar System"
        print(f"Testing complete flow for: {test_topic}")
        
        # Step 1: Generate topic content
        print("Step 1: Generating topic content...")
        content = topic_generator.generate_topic_content(
            topic=test_topic,
            difficulty="beginner"
        )
        
        if not content:
            print("✗ Failed at step 1: Topic content generation")
            return
        
        print(f"✓ Step 1 completed: {len(content)} characters generated")
        
        # Step 2: Generate flashcards
        print("Step 2: Generating flashcards...")
        flashcards = flashcard_generator.generate_flashcards(
            text=content,
            language="en",
            difficulty="beginner"
        )
        
        if not flashcards:
            print("✗ Failed at step 2: Flashcard generation")
            return
        
        print(f"✓ Step 2 completed: {len(flashcards)} flashcards generated")
        
        # Step 3: Generate summary
        print("Step 3: Generating topic summary...")
        summary = topic_generator.generate_topic_summary(test_topic, content)
        
        print(f"✓ Step 3 completed: Summary generated")
        print(f"   Main theme: {summary['main_theme']}")
        print(f"   Learning objectives: {summary['learning_objectives']}")
        print(f"   Difficulty: {summary['difficulty_assessment']}")
        print(f"   Study time: {summary['estimated_study_time']}")
        
        print("\n" + "=" * 50)
        print("End-to-End Test Completed Successfully!")
        print(f"Final result: {len(flashcards)} flashcards ready for study!")
        
    except Exception as e:
        print(f"Error in end-to-end test: {str(e)}")
        logger.error(f"Test error: {str(e)}")

if __name__ == "__main__":
    print("Search Flashcards Functionality Test Suite")
    print("=" * 60)
    
    # Run tests
    test_topic_content_generation()
    test_flashcard_generation()
    test_end_to_end()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
