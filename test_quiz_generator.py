#!/usr/bin/env python3
"""
Test script for the improved quiz generator.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.generators.quiz_generator import QuizGenerator
from app.logger import logger

def test_quiz_generation():
    """Test the quiz generator with sample text."""
    
    # Sample text about English vocabulary building
    sample_text = """
    English Vocabulary Building Introduction
    
    Vocabulary is essential for effective communication and academic success in language learning. 
    A strong vocabulary enables learners to express ideas clearly, understand complex texts, and 
    engage in meaningful conversations.
    
    Contextual Learning
    
    Learning words in context improves retention over rote memorization. When students encounter 
    new words within meaningful sentences and paragraphs, they better understand usage, connotations, 
    and grammatical patterns. This approach helps learners remember words longer and use them correctly.
    
    Strategy: Read articles, novels, or academic texts; note unfamiliar words
    
    Reading extensively exposes learners to new vocabulary in natural contexts. When encountering 
    unfamiliar words, students should note them down with their context and look up definitions. 
    This method helps build vocabulary while improving reading comprehension.
    
    Word Formation
    
    Understanding word roots, prefixes, and suffixes aids vocabulary expansion. Many English words 
    share common roots from Latin and Greek. For example, the root "bene" means "good," appearing 
    in words like "benevolent," "benefit," and "beneficial." Learning these patterns helps learners 
    decode unfamiliar words and expand their vocabulary systematically.
    
    Synonyms and Antonyms
    
    Synonyms (similar meanings) and antonyms (opposite meanings) enrich expression. Learning word 
    relationships helps learners choose the most appropriate terms for different contexts and 
    express nuances in meaning.
    
    Collocations
    
    Collocations are words that commonly appear together. Examples include "make a decision" 
    (not "do a decision") and "heavy rain" (not "strong rain"). Learning these natural word 
    combinations improves fluency and makes speech sound more natural.
    
    Digital Tools
    
    Use digital tools like flashcards to track progress and enhance engagement. Modern vocabulary 
    apps offer spaced repetition algorithms, progress tracking, and interactive exercises that 
    make learning more efficient and enjoyable.
    
    Practice Activities
    
    Practice: Write sentences using new words
    Practice: Identify collocations in reading materials
    Activity: Create word maps linking synonyms and antonyms
    
    Example Sentence: Her benevolence was evident in her charitable actions
    
    Conclusion
    
    Consistent practice with contextual learning, word formation, and spaced repetition builds 
    a robust vocabulary. This document provides strategies and examples for building English 
    vocabulary, suitable for intermediate learners.
    """
    
    print("Testing improved quiz generator...")
    print("=" * 50)
    
    # Initialize quiz generator
    quiz_generator = QuizGenerator()
    
    # Generate quizzes
    quizzes = quiz_generator.generate_quizzes(sample_text, language="en", difficulty="intermediate")
    
    print(f"Generated {len(quizzes)} quizzes")
    print()
    
    # Display quizzes
    for i, quiz in enumerate(quizzes, 1):
        print(f"Quiz {i}:")
        print(f"Question: {quiz['question']}")
        print("Options:")
        for j, option in enumerate(quiz['options'], 1):
            marker = "✓" if option == quiz['correct_answer_option'] else " "
            print(f"  {chr(64+j)}) {marker} {option}")
        print(f"Correct Answer: {quiz['correct_answer_option']}")
        print("-" * 50)
        print()

if __name__ == "__main__":
    test_quiz_generation() 