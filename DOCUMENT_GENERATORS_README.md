# Document Generators System

## Overview

This document explains the new document generators system that was created to fix the main document processing functionality while keeping the search flashcard functionality intact.

## Problem

The original `flashcard_generator.py` file was modified to support search flashcard generation, but these changes broke the main document processing and flashcard generation functionality. The system was failing to generate proper JSON responses, causing the `/api/v1/process-file` endpoint to return 422 errors.

## Solution

We created a separate set of document-specific generators that are dedicated to handling document processing:

1. **`DocumentFlashcardGenerator`** - Generates flashcards from document text
2. **`DocumentQuizGenerator`** - Generates quiz questions from document text  
3. **`DocumentExerciseGenerator`** - Generates exercises from document text
4. **`DocumentAllContentGenerator`** - Coordinates all three generators

## Architecture

### File Structure

```
app/generators/
├── flashcard_generator.py          # Original - for search functionality
├── document_flashcard_generator.py # NEW - for document processing
├── document_quiz_generator.py      # NEW - for document processing
├── document_exercise_generator.py  # NEW - for document processing
├── document_all_content_generator.py # NEW - coordinates all document generators
└── all_content_generator.py        # Original - kept as fallback
```

### Generator Hierarchy

```
DocumentAllContentGenerator
├── DocumentFlashcardGenerator
├── DocumentQuizGenerator
└── DocumentExerciseGenerator
    └── Fallback to AI-based generation
    └── Fallback to rule-based generation
```

## Features

### Multiple Fallback Strategies

Each document generator implements a three-tier fallback system:

1. **Structured JSON Generation** - Tries to generate content using structured prompts
2. **Simple Format Generation** - Falls back to simpler Q&A format prompts
3. **Rule-based Generation** - Final fallback using pattern matching and text analysis

### Robust Error Handling

- Graceful degradation when AI models fail
- Automatic retry mechanisms
- Comprehensive logging for debugging
- Fallback to rule-based content generation

### Language Support

- English (primary generation language)
- Sinhala (si) - with localized content
- Tamil (ta) - with localized content

## Usage

### In File Processing Route

The main document processing route now uses the new generators:

```python
from ..generators.document_all_content_generator import generate_document_content

# Generate all content in English first
all_content = generate_document_content(text, "en", difficulty)

# Translate to requested language if needed
if language != "en":
    all_content = translate_generated_content(all_content, language)
```

### Direct Generator Usage

You can also use individual generators directly:

```python
from .document_flashcard_generator import DocumentFlashcardGenerator

generator = DocumentFlashcardGenerator()
flashcards = generator.generate_flashcards(text, "en", "beginner", 10)
```

## Testing

Run the test script to verify the generators work correctly:

```bash
cd memo-spark-be/fastapi-service
python test_document_generators.py
```

This will test:
- Individual generator functionality
- Combined generation
- Language support
- Error handling
- Fallback mechanisms

## Configuration

The generators use the same configuration as the original system:

- `GENERATION_LIMITS` from `config.py`
- Model manager from `models.py`
- Logging from `logger.py`

## Benefits

1. **Separation of Concerns** - Search and document generation are now separate
2. **Improved Reliability** - Multiple fallback strategies ensure content generation
3. **Better Error Handling** - Graceful degradation when AI models fail
4. **Maintainability** - Clear separation makes debugging and updates easier
5. **Backward Compatibility** - Original search functionality remains intact

## Migration Notes

- The original `flashcard_generator.py` is unchanged and continues to work for search
- The file processing route now uses `generate_document_content()` instead of `generate_all_content()`
- All existing API endpoints remain the same
- No changes needed in the frontend or other services

## Troubleshooting

### Common Issues

1. **No content generated** - Check logs for fallback generation attempts
2. **JSON parsing errors** - Generators automatically fall back to simpler formats
3. **Model failures** - System automatically tries alternative models and fallback strategies

### Debugging

Enable detailed logging to see which generation strategy is being used:

```python
logger.setLevel(logging.DEBUG)
```

### Performance

The new generators may be slightly slower due to multiple fallback attempts, but they are much more reliable. The trade-off is worth it for production document processing.

## Future Improvements

1. **Caching** - Cache generated content to avoid regeneration
2. **Quality Metrics** - Add quality scoring for generated content
3. **Custom Prompts** - Allow customization of generation prompts
4. **Batch Processing** - Optimize for multiple document processing
5. **Content Validation** - Add more sophisticated content validation rules
