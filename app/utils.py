import re
from typing import List
from .logger import logger

def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\'\"]+', ' ', text)
    
    # Fix common OCR issues
    text = re.sub(r'(\w)\|(\w)', r'\1l\2', text)  # Fix common OCR 'l' -> '|' issue
    text = re.sub(r'(\w)0(\w)', r'\1o\2', text)   # Fix common OCR 'o' -> '0' issue
    
    return text

def extract_key_concepts(text: str, max_concepts: int = 10) -> List[str]:
    """Extract key concepts from text for better question generation."""
    # Simple keyword extraction based on capitalization and frequency
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    # Count word frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top concepts
    key_concepts = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [concept[0] for concept in key_concepts[:max_concepts]]

def split_text_into_chunks(text: str, max_chunk_length: int = 600) -> List[str]:
    """Split text into meaningful chunks for processing."""
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk + sentence) > max_chunk_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += ". " + sentence if current_chunk else sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def validate_language(language: str) -> bool:
    """Validate if the language is supported."""
    return language in ["en", "si", "ta"]

def validate_difficulty(difficulty: str) -> str:
    """Validate and return difficulty level."""
    valid_difficulties = ["beginner", "intermediate", "advanced"]
    return difficulty if difficulty in valid_difficulties else "beginner"

def validate_file_type(file_extension: str) -> bool:
    """Validate if the file type is supported."""
    from .config import SUPPORTED_FILE_TYPES
    return file_extension.lower() in SUPPORTED_FILE_TYPES

def translate_text(text: str, target_language: str) -> str:
    """Translate text to the target language using deep-translator."""
    if target_language == "en":
        return text
    
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target=target_language)
        return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        # If translation fails, return original text
        return text

def translate_generated_content(content: dict, target_language: str) -> dict:
    """
    Translate generated content (flashcards, quizzes, exercises) to the target language.
    
    Args:
        content: Dictionary containing flashcards, quizzes, and exercises
        target_language: Target language code (en, si, ta)
    
    Returns:
        Translated content dictionary
    """
    if target_language == "en":
        return content
    
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target=target_language)
    except Exception as e:
        logger.error(f"Translation library not available: {e}")
        # If translation library is not available, return original content
        return content
    
    translated_content = {}
    
    # Translate flashcards
    if "flashcards" in content and isinstance(content["flashcards"], list):
        translated_flashcards = []
        for flashcard in content["flashcards"]:
            if isinstance(flashcard, dict):
                translated_flashcard = flashcard.copy()
                if "question" in flashcard:
                    try:
                        translated_flashcard["question"] = translator.translate(flashcard["question"])
                    except Exception as e:
                        logger.warning(f"Failed to translate flashcard question: {e}")
                        translated_flashcard["question"] = flashcard["question"]
                
                if "answer" in flashcard:
                    try:
                        translated_flashcard["answer"] = translator.translate(flashcard["answer"])
                    except Exception as e:
                        logger.warning(f"Failed to translate flashcard answer: {e}")
                        translated_flashcard["answer"] = flashcard["answer"]
                
                translated_flashcards.append(translated_flashcard)
            else:
                translated_flashcards.append(flashcard)
        translated_content["flashcards"] = translated_flashcards
    
    # Translate quizzes
    if "quizzes" in content and isinstance(content["quizzes"], list):
        translated_quizzes = []
        for quiz in content["quizzes"]:
            if isinstance(quiz, dict):
                translated_quiz = quiz.copy()
                if "question" in quiz:
                    try:
                        translated_quiz["question"] = translator.translate(quiz["question"])
                    except Exception as e:
                        logger.warning(f"Failed to translate quiz question: {e}")
                        translated_quiz["question"] = quiz["question"]
                
                if "options" in quiz and isinstance(quiz["options"], list):
                    translated_options = []
                    for option in quiz["options"]:
                        try:
                            translated_options.append(translator.translate(option))
                        except Exception as e:
                            logger.warning(f"Failed to translate quiz option: {e}")
                            translated_options.append(option)
                    translated_quiz["options"] = translated_options
                
                if "answer" in quiz:
                    try:
                        translated_quiz["answer"] = translator.translate(quiz["answer"])
                    except Exception as e:
                        logger.warning(f"Failed to translate quiz answer: {e}")
                        translated_quiz["answer"] = quiz["answer"]
                
                translated_quizzes.append(translated_quiz)
            else:
                translated_quizzes.append(quiz)
        translated_content["quizzes"] = translated_quizzes
    
    # Translate exercises
    if "exercises" in content and isinstance(content["exercises"], list):
        translated_exercises = []
        for exercise in content["exercises"]:
            if isinstance(exercise, dict):
                translated_exercise = exercise.copy()
                if "instruction" in exercise:
                    try:
                        translated_exercise["instruction"] = translator.translate(exercise["instruction"])
                    except Exception as e:
                        logger.warning(f"Failed to translate exercise instruction: {e}")
                        translated_exercise["instruction"] = exercise["instruction"]
                
                if "question" in exercise:
                    try:
                        translated_exercise["question"] = translator.translate(exercise["question"])
                    except Exception as e:
                        logger.warning(f"Failed to translate exercise question: {e}")
                        translated_exercise["question"] = exercise["question"]
                
                if "answer" in exercise:
                    try:
                        translated_exercise["answer"] = translator.translate(exercise["answer"])
                    except Exception as e:
                        logger.warning(f"Failed to translate exercise answer: {e}")
                        translated_exercise["answer"] = exercise["answer"]
                
                if "concepts" in exercise and isinstance(exercise["concepts"], list):
                    translated_concepts = []
                    for concept in exercise["concepts"]:
                        try:
                            translated_concepts.append(translator.translate(concept))
                        except Exception as e:
                            logger.warning(f"Failed to translate exercise concept: {e}")
                            translated_concepts.append(concept)
                    translated_exercise["concepts"] = translated_concepts
                
                if "definitions" in exercise and isinstance(exercise["definitions"], list):
                    translated_definitions = []
                    for definition in exercise["definitions"]:
                        try:
                            translated_definitions.append(translator.translate(definition))
                        except Exception as e:
                            logger.warning(f"Failed to translate exercise definition: {e}")
                            translated_definitions.append(definition)
                    translated_exercise["definitions"] = translated_definitions
                
                translated_exercises.append(translated_exercise)
            else:
                translated_exercises.append(exercise)
        translated_content["exercises"] = translated_exercises
    
    return translated_content 