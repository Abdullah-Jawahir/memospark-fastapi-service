import os
from pathlib import Path
from typing import Dict, Any

# Project root and directories
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "model_cache"

# Create necessary directories
LOG_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Set environment variables for model caching
os.environ['TRANSFORMERS_CACHE'] = str(CACHE_DIR)
os.environ['HF_HOME'] = str(CACHE_DIR)
os.environ['HF_DATASETS_CACHE'] = str(CACHE_DIR)

# Model configurations
MODEL_CONFIGS = {
    "question_generation": {
        "name": "microsoft/DialoGPT-medium",
        "alternative": "google/flan-t5-base"
    },
    "text_generation": {
        "name": "microsoft/DialoGPT-small",
        "alternative": "google/flan-t5-large"
    }
}

# Models to try in order of preference
MODELS_TO_TRY = [
    "google/flan-t5-base",
    "microsoft/DialoGPT-medium",
    "google/flan-t5-small",
]

# Supported languages and their prompts
LANGUAGE_PROMPTS = {
    "en": {
        "flashcard": "Create a clear question and answer from this text:\n\nText: {}\n\nQuestion:",
        "quiz": "Create a multiple choice question with 4 options from this text:\n\nText: {}\n\nQuestion: "
    },
    "si": {
        "flashcard": "මෙම පෙළෙන් පැහැදිලි ප්‍රශ්නයක් සහ පිළිතුරක් සාදන්න:\n\nපෙළ: {}\n\nප්‍රශ්නය:",
        "quiz": "මෙම පෙළෙන් විකල්ප 4ක් සහිත බහුවරණ ප්‍රශ්නයක් සාදන්න:\n\nපෙළ: {}\n\nප්‍රශ්නය: "
    },
    "ta": {
        "flashcard": "இந்த உரையிலிருந்து தெளிவான கேள்வி மற்றும் பதிலை உருவாக்கவும்:\n\nஉரை: {}\n\nகேள்வி:",
        "quiz": "இந்த உரையிலிருந்து 4 விருப்பங்களுடன் பல தேர்வு கேள்வியை உருவாக்கவும்:\n\nஉரை: {}\n\nகேள்வி: "
    }
}

# Supported file types
SUPPORTED_FILE_TYPES = ["pdf", "docx", "pptx"]

# Content generation limits
GENERATION_LIMITS = {
    "flashcards": 10,
    "quizzes": 8,
    "exercises": 10,
    "text_chunks": 5
}

# Model generation parameters
GENERATION_PARAMS = {
    "max_length": 200,
    "temperature": 0.7,
    "top_p": 0.9,
    "no_repeat_ngram_size": 2
} 