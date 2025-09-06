import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

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

# OpenRouter API config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Google Gemini API config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# AI Model Priority Configuration
# Configurable priority order for AI services
# Options: "openrouter", "gemini", "local", "rule_based"
# Default: openrouter -> gemini -> local -> rule_based
AI_MODEL_PRIORITY = os.getenv("AI_MODEL_PRIORITY", "openrouter,gemini,local,rule_based").split(",")

# Clean up any whitespace from the priority list
AI_MODEL_PRIORITY = [model.strip().lower() for model in AI_MODEL_PRIORITY]

# Validate priority configuration
VALID_MODEL_TYPES = {"openrouter", "gemini", "local", "rule_based"}
AI_MODEL_PRIORITY = [model for model in AI_MODEL_PRIORITY if model in VALID_MODEL_TYPES]

# Ensure we have at least one fallback if list is empty or invalid
if not AI_MODEL_PRIORITY:
    AI_MODEL_PRIORITY = ["openrouter", "gemini", "local", "rule_based"]

# Multiple OpenRouter models to try in order (only working free tier models)
OPENROUTER_MODELS_TO_TRY = [
    "deepseek/deepseek-chat-v3-0324:free",  # Primary model - confirmed working
    "google/gemma-2-9b-it:free",  # Alternative - confirmed working
]

ENABLE_OPENROUTER = bool(OPENROUTER_API_KEY) and os.getenv("ENABLE_OPENROUTER", "true").lower() == "true"
ENABLE_GEMINI = bool(GEMINI_API_KEY) and os.getenv("ENABLE_GEMINI", "true").lower() == "true"
FALLBACK_TO_LOCAL = os.getenv("FALLBACK_TO_LOCAL", "true").lower() == "true"
# Disable rule-based fallback for document processing to avoid irrelevant content
ENABLE_RULE_BASED_FALLBACK = os.getenv("ENABLE_RULE_BASED_FALLBACK", "false").lower() == "true"

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
    "deepseek-ai/deepseek-coder-6.7b-instruct",
    "deepseek-ai/deepseek-llm-7b-chat",
    "microsoft/DialoGPT-large",
    "google/flan-t5-large",
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
SUPPORTED_FILE_TYPES = ["pdf", "docx", "pptx", "txt"]

# Content generation limits
GENERATION_LIMITS = {
    "flashcards": 10,
    "quizzes": 8,
    "exercises": 10,
    "text_chunks": 5
}

# Model generation parameters
GENERATION_PARAMS = {
    "max_length": 400,
    "temperature": 0.8,
    "top_p": 0.9,
    "no_repeat_ngram_size": 3,
    "do_sample": True,
    "top_k": 50
} 