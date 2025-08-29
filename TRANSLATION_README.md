# Translation Functionality Documentation

## Overview

The Memo Spark Backend now supports multi-language content generation through a two-step process:

1. **AI Generation**: Content is always generated in English first using the AI model
2. **Translation**: Generated content is then translated to the requested language using external translation APIs

## Supported Languages

- **en**: English (default, no translation needed)
- **si**: Sinhala (සිංහල)
- **ta**: Tamil (தமிழ்)

## How It Works

### 1. Content Generation Flow

```
User Request (language: si/ta) → AI generates content in English → Translation to requested language → Response to frontend
```

### 2. Translation Process

The system uses a fallback approach for translation:

1. **Primary**: `googletrans` library (unofficial Google Translate wrapper)
2. **Fallback**: `deep-translator` library (more reliable alternative)
3. **Graceful degradation**: If both fail, original English content is returned

### 3. Content Types Translated

All generated content types are fully translated:

- **Flashcards**: Questions and answers
- **Quizzes**: Questions, options, and answers
- **Exercises**: Instructions, questions, answers, concepts, and definitions

## Implementation Details

### Key Functions

#### `translate_generated_content(content: dict, target_language: str) -> dict`

Translates the entire generated content structure to the target language.

**Parameters:**
- `content`: Dictionary containing flashcards, quizzes, and exercises
- `target_language`: Target language code (en, si, ta)

**Returns:**
- Translated content dictionary with the same structure

#### `translate_text(text: str, target_language: str) -> str`

Translates individual text strings with fallback support.

### Error Handling

- Translation failures are logged but don't crash the system
- If translation fails, original English content is returned
- Individual field translation failures don't affect other fields

## API Usage

### Request Format

```http
POST /api/v1/process-file
Content-Type: multipart/form-data

file: [PDF/DOCX/PPTX file]
language: si  # or "ta" for Tamil, "en" for English
card_types: ["flashcard", "quiz", "exercise"]
difficulty: "beginner"
```

### Response Format

The response format remains unchanged - only the content language changes:

```json
{
  "generated_content": {
    "flashcards": [
      {
        "question": "ප්‍රංශයේ අගනුවර කුමක්ද?",  // Translated to Sinhala
        "answer": "පැරිස් යනු ප්‍රංශයේ අගනුවරයි."
      }
    ],
    "quizzes": [...],
    "exercises": [...]
  }
}
```

## Installation

The required dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Dependencies

- `googletrans==4.0.0rc1` - Primary translation library
- `deep-translator` - Fallback translation library

## Testing

Run the translation test script to verify functionality:

```bash
python test_translation.py
```

This will test translation to Sinhala and Tamil with sample content.

## Benefits of This Approach

1. **Consistent Quality**: AI generates high-quality content in English
2. **Reliable Translation**: Professional translation APIs ensure accuracy
3. **Fallback Support**: Multiple translation services prevent failures
4. **No Format Changes**: Frontend receives the same response structure
5. **Language Flexibility**: Easy to add new languages in the future

## Future Enhancements

1. **Caching**: Cache translations to avoid repeated API calls
2. **More Languages**: Support for additional languages
3. **Translation Quality**: User feedback on translation quality
4. **Custom Models**: Fine-tuned translation models for educational content

## Troubleshooting

### Common Issues

1. **Translation API Failures**: Check internet connectivity and API rate limits
2. **Language Codes**: Ensure correct language codes (si, ta, en)
3. **Content Format**: Verify generated content structure before translation

### Logs

Translation activities are logged with appropriate levels:
- `INFO`: Successful translations
- `WARNING`: Translation failures with fallback
- `ERROR`: Complete translation system failures

## Performance Considerations

- Translation adds processing time (typically 1-3 seconds)
- Consider implementing translation caching for repeated content
- Monitor translation API usage and rate limits
