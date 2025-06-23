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
    """Translate text to the target language using googletrans."""
    if target_language == "en":
        return text
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, dest=target_language)
        return result.text
    except Exception as e:
        # If translation fails, return original text
        print(f"Translation error: {e}")
        return text 