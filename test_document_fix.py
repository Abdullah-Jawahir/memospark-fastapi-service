#!/usr/bin/env python3
"""
Test script to verify that document processing fixes are working correctly.
This tests the improved rate limiting and disabled rule-based fallbacks.
"""

import requests
import json
import time
from pathlib import Path

API_BASE_URL = "http://localhost:8001"

def test_document_processing():
    """Test document processing with a sample file."""
    
    print("Testing Document Processing Fixes")
    print("=" * 50)
    
    # Create a test document content
    test_content = """
    Human Anatomy Basics
    
    The human skeletal system is composed of 206 bones in adults. The skeletal system provides 
    support for the body, protects internal organs, and enables movement through the attachment 
    of muscles. The longest bone in the human body is the femur, located in the thigh.
    
    The muscular system works closely with the skeletal system. There are three types of muscle 
    tissue: skeletal muscle (voluntary), smooth muscle (involuntary), and cardiac muscle (found 
    only in the heart). Muscle contraction occurs when actin and myosin filaments slide past 
    each other, shortening the muscle fibers.
    
    The circulatory system is responsible for transporting oxygen, nutrients, hormones, and 
    other essential substances throughout the body, while also removing waste products. The 
    three main components are the heart, blood vessels (arteries, veins, and capillaries), 
    and blood. Red blood cells contain hemoglobin, which binds to oxygen in the lungs and 
    carries it to the body's tissues.
    """
    
    # Save test content to a temporary file
    test_file = Path("test_anatomy.txt")
    test_file.write_text(test_content)
    
    try:
        print(f"1. Uploading test document: {test_file.name}")
        print(f"   Content length: {len(test_content)} characters")
        print(f"   Testing rate limiting improvements...")
        
        # Prepare the API request
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'text/plain')}
            data = {
                'language': 'en',
                'card_types': ['flashcard', 'quiz', 'exercise'],
                'difficulty': 'beginner'
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/v1/process-file",
                files=files,
                data=data,
                timeout=120  # 2 minute timeout
            )
            end_time = time.time()
        
        print(f"2. Request completed in {end_time - start_time:.1f} seconds")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            generated_content = result.get('generated_content', {})
            
            print("\n✅ SUCCESS - Content generated successfully!")
            print(f"   Flashcards: {len(generated_content.get('flashcards', []))}")
            print(f"   Quizzes: {len(generated_content.get('quizzes', []))}")
            print(f"   Exercises: {len(generated_content.get('exercises', []))}")
            
            # Check content quality
            print("\n3. Quality Check:")
            check_content_quality(generated_content)
            
        elif response.status_code == 422:
            print("\n⚠️  EXPECTED - Content generation failed due to rate limits")
            print("   This is the new expected behavior - no irrelevant content generated")
            print("   Try again in a few minutes when rate limits reset")
            
        else:
            print(f"\n❌ ERROR - Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except requests.exceptions.Timeout:
        print("\n⏱️  TIMEOUT - Request took longer than 2 minutes")
        print("   This may indicate rate limiting or model loading")
        
    except Exception as e:
        print(f"\n❌ ERROR - {str(e)}")
    
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

def check_content_quality(generated_content):
    """Check if generated content is relevant to the test document."""
    
    # Keywords that should appear in anatomy-related content
    anatomy_keywords = [
        'skeletal', 'bone', 'muscle', 'heart', 'blood', 'tissue', 
        'body', 'organ', 'femur', 'anatomy', 'circulatory', 'oxygen'
    ]
    
    # Generic keywords that indicate rule-based generation (bad)
    generic_keywords = [
        'main concepts', 'important principles', 'fundamental', 
        'various concepts', 'topic covers', 'subject matter'
    ]
    
    total_items = 0
    relevant_items = 0
    generic_items = 0
    
    for content_type, items in generated_content.items():
        for item in items:
            total_items += 1
            
            # Check question and answer content
            text_to_check = ""
            if 'question' in item:
                text_to_check += item['question'].lower() + " "
            if 'answer' in item:
                text_to_check += str(item['answer']).lower() + " "
            if 'instruction' in item:
                text_to_check += item['instruction'].lower() + " "
            
            # Check for anatomy relevance
            if any(keyword in text_to_check for keyword in anatomy_keywords):
                relevant_items += 1
                print(f"   ✅ Relevant {content_type}: {item.get('question', item.get('instruction', 'N/A'))[:60]}...")
            
            # Check for generic content (rule-based fallback)
            elif any(keyword in text_to_check for keyword in generic_keywords):
                generic_items += 1
                print(f"   ❌ Generic {content_type}: {item.get('question', item.get('instruction', 'N/A'))[:60]}...")
            
            else:
                print(f"   ⚠️  Unclear {content_type}: {item.get('question', item.get('instruction', 'N/A'))[:60]}...")
    
    print(f"\n   Quality Summary:")
    print(f"   - Total items: {total_items}")
    print(f"   - Relevant items: {relevant_items}")
    print(f"   - Generic items: {generic_items}")
    
    if generic_items > 0:
        print(f"   ⚠️  WARNING: Found {generic_items} generic items - rule-based fallback may still be active")
    elif relevant_items > 0:
        print(f"   ✅ EXCELLENT: All content appears relevant to the document")
    else:
        print(f"   ❓ UNCLEAR: Content relevance could not be determined")

if __name__ == "__main__":
    print("Make sure your FastAPI service is running on http://localhost:8001")
    print("Press Enter to start the test...")
    input()
    test_document_processing()
