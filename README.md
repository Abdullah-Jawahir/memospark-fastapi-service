# Memo Spark Backend

A FastAPI-based service for AI-powered document processing and educational content generation.

## Project Structure

The project has been refactored into a clean, modular structure:

```
fastapi-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # New simplified main application
│   ├── config.py                # Configuration settings
│   ├── logger.py                # Logging configuration
│   ├── utils.py                 # Utility functions
│   ├── models.py                # AI model management
│   ├── text_extractor.py        # Document text extraction
│   ├── middleware.py            # CORS and request logging
│   ├── generators/              # Content generation modules
│   │   ├── __init__.py
│   │   ├── flashcard_generator.py
│   │   ├── quiz_generator.py
│   │   └── exercise_generator.py
│   └── routes/                  # API route modules
│       ├── __init__.py
│       ├── file_processing.py
│       └── health.py
├── logs/                        # Application logs
├── model_cache/                 # Hugging Face model cache
├── requirements.txt
└── README.md
```

## Key Improvements

### 1. **Modular Architecture**
- **Separation of Concerns**: Each module has a specific responsibility
- **Maintainability**: Easier to maintain and extend individual components
- **Testability**: Each module can be tested independently

### 2. **Configuration Management**
- **Centralized Config**: All settings in `config.py`
- **Environment Variables**: Proper model caching configuration
- **Language Support**: Multi-language prompt configurations

### 3. **Model Management**
- **ModelManager Class**: Encapsulates model loading and generation
- **Fallback Strategy**: Multiple model options with automatic fallback
- **Error Handling**: Robust error handling for model operations

### 4. **Content Generation**
- **Specialized Generators**: Separate classes for each content type
- **Rule-based Fallbacks**: When AI models fail, use rule-based generation
- **Multi-language Support**: Support for English, Sinhala, and Tamil

### 5. **API Organization**
- **Route Modules**: Organized by functionality
- **Middleware**: Centralized CORS and logging
- **Health Checks**: Dedicated health monitoring endpoint

## Modules Overview

### Core Modules

#### `config.py`
- Project paths and directories
- Model configurations
- Language prompts
- Generation parameters
- File type validation

#### `logger.py`
- Centralized logging setup
- File and console handlers
- Configurable log levels

#### `utils.py`
- Text cleaning and processing
- Key concept extraction
- Text chunking
- Validation functions

#### `models.py`
- `ModelManager` class for AI model handling
- Automatic model loading with fallbacks
- Text generation with proper error handling

#### `text_extractor.py`
- Document text extraction (PDF, DOCX, PPTX)
- File type-specific extraction logic
- Error handling for each file type

### Content Generators

#### `generators/flashcard_generator.py`
- `FlashcardGenerator` class
- AI-powered question-answer generation
- Rule-based fallback generation
- Multi-language support

#### `generators/quiz_generator.py`
- `QuizGenerator` class
- Multiple choice quiz generation
- Distractor generation
- Question formatting

#### `generators/exercise_generator.py`
- `ExerciseGenerator` class
- Multiple exercise types (fill-blank, true/false, short answer, matching)
- Language-specific instructions

### API Routes

#### `routes/file_processing.py`
- Main file processing endpoint
- Parameter validation
- Content generation orchestration

#### `routes/health.py`
- Health check endpoint
- Model status information

#### `middleware.py`
- CORS configuration
- Request/response logging
- Performance monitoring

## Usage

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main_new
```

### API Endpoints

#### Health Check
```http
GET /health
```

#### File Processing
```http
POST /api/v1/process-file
Content-Type: multipart/form-data

Parameters:
- file: Document file (PDF, DOCX, PPTX)
- language: "en", "si", or "ta"
- card_types: ["flashcard", "quiz", "exercise"]
- difficulty: "beginner", "intermediate", "advanced"
```

## Benefits of the New Structure

1. **Maintainability**: Each component is focused and easier to maintain
2. **Scalability**: Easy to add new content types or file formats
3. **Testing**: Modular structure enables better unit testing
4. **Documentation**: Clear separation makes the codebase self-documenting
5. **Error Handling**: Centralized error handling and logging
6. **Configuration**: Easy to modify settings without touching code
7. **Performance**: Better resource management and caching

## Migration from Old Structure

The old `main.py` file has been preserved for reference. To use the new structure:

1. Use `app/main_new.py` instead of `app/main.py`
2. All functionality remains the same
3. API endpoints are now under `/api/v1/` prefix
4. Better error messages and logging

## Future Enhancements

With this modular structure, it's easy to add:

- New content generation types
- Additional file format support
- More language support
- Advanced caching strategies
- Database integration
- User authentication
- Rate limiting
- Advanced analytics 