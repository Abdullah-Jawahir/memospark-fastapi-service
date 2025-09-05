# 🚀 MemoSpark FastAPI Service - AI Content Generation Engine

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a699?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python)
![Transformers](https://img.shields.io/badge/🤗_Transformers-4.26+-yellow?style=flat)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

**AI-powered document processing and educational content generation service**

[🏠 Main Repository](https://github.com/Abdullah-Jawahir/memo-spark) • [🔧 Laravel Service](https://github.com/Abdullah-Jawahir/memospark-laravel-service) • [📖 Documentation](https://github.com/Abdullah-Jawahir/memospark-fastapi-service/wiki)

</div>

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🧠 AI Capabilities](#-ai-capabilities)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [📚 API Documentation](#-api-documentation)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [🔍 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👨‍💻 Author](#-author)

## 🌟 Overview

The MemoSpark FastAPI Service is the core AI engine that powers intelligent document processing and educational content generation. Built with FastAPI and leveraging state-of-the-art transformer models, this service converts static documents into dynamic learning materials through advanced natural language processing.

### 🎯 Core Responsibilities

- **📄 Document Processing**: Extract and process text from PDF, DOCX, and PPTX files
- **🤖 AI Content Generation**: Create flashcards, quizzes, and exercises using transformer models
- **🌍 Multi-language Support**: Generate content in English, Sinhala, and Tamil
- **📊 Intelligent Analysis**: Extract key concepts and optimize content difficulty
- **⚡ High Performance**: Asynchronous processing with model caching and optimization

## ✨ Key Features

### 🔧 Document Processing

- **Multi-format Support**: PDF, Word documents (DOCX), PowerPoint presentations (PPTX)
- **Advanced Text Extraction**: Clean text extraction with formatting preservation
- **Content Analysis**: Automatic key concept identification and text chunking
- **Metadata Extraction**: Document properties and structural information

### 🤖 AI-Powered Generation

- **Smart Flashcards**: Context-aware question-answer pairs with multiple difficulty levels
- **Interactive Quizzes**: Multiple-choice questions with distractor generation
- **Adaptive Exercises**: Various exercise types tailored to content and user preferences
- **Quality Assurance**: Built-in validation and fallback mechanisms

### 🌐 Language Intelligence

- **Multilingual Processing**: Native support for English, Sinhala (සිංහල), Tamil (தமிழ்)
- **Context-Aware Translation**: Intelligent content adaptation for different languages
- **Cultural Localization**: Region-specific educational content formatting

### ⚡ Performance & Reliability

- **Model Caching**: Efficient model loading and memory management
- **Async Processing**: Non-blocking document processing
- **Error Handling**: Comprehensive error recovery and logging
- **Scalable Architecture**: Designed for high-throughput operations

## 🧠 AI Capabilities

### 🤖 Transformer Models

- **Primary Models**: DistilGPT-2, GPT-2 variants for text generation
- **Backup Models**: Rule-based fallback for reliability
- **Model Management**: Automatic model selection and fallback strategies
- **Optimization**: Memory-efficient model loading and inference

### 📊 Content Intelligence

- **Key Concept Extraction**: Automatic identification of important topics
- **Difficulty Assessment**: Content complexity analysis and adaptation
- **Context Understanding**: Semantic relationship analysis
- **Quality Scoring**: Generated content validation and filtering

### 🎯 Adaptive Learning

- **Personalization**: Content difficulty adjustment based on user preferences
- **Learning Patterns**: Intelligent content sequencing
- **Progress Tracking**: Performance-based content optimization
- **Feedback Integration**: Continuous improvement through user interaction data

## 🛠️ Tech Stack

### Core Framework

- **🚀 FastAPI** - Modern, fast web framework for building APIs
- **🐍 Python 3.8+** - Core programming language
- **📡 Uvicorn** - ASGI server for high-performance async support

### AI & Machine Learning

- **🤗 Transformers** - State-of-the-art NLP models
- **🔥 PyTorch** - Deep learning framework
- **📊 NumPy** - Numerical computing
- **🔤 Sentence Transformers** - Semantic text embeddings

### Document Processing

- **📄 PyMuPDF** - PDF text extraction and processing
- **📝 python-docx** - Word document manipulation
- **📊 python-pptx** - PowerPoint presentation processing
- **🔍 Pydantic** - Data validation and serialization

### Language & Translation

- **🌐 deep-translator** - Multi-language translation support
- **🔤 Text Processing Libraries** - Custom language-specific processing

### Development & Operations

- **📋 Logging** - Comprehensive application logging
- **🔧 Configuration Management** - Environment-based settings
- **🧪 Testing Framework** - Comprehensive test suite
- **📊 Monitoring** - Performance and health monitoring

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Git** for version control
- **4GB+ RAM** (recommended for model operations)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Abdullah-Jawahir/memospark-fastapi-service.git
   cd memospark-fastapi-service
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download AI models (first run)**

   ```bash
   python -c "from transformers import pipeline; pipeline('text-generation', model='distilgpt2')"
   ```

5. **Start the server**

   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

6. **Verify installation**
   Open `http://localhost:8001/docs` for interactive API documentation

### Environment Setup

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your-openrouter-key-here
ENABLE_OPENROUTER=true
FALLBACK_TO_LOCAL=false
```

```
memospark-fastapi-service/
├── app/                        # Main application package
│   ├── __init__.py            # Package initialization
│   ├── main.py                # FastAPI application and routes
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging configuration
│   ├── middleware.py          # CORS and request logging
│   ├── models.py              # AI model management
│   ├── text_extractor.py      # Document processing utilities
│   ├── utils.py               # General utility functions
│   ├── generators/            # Content generation modules
│   │   ├── __init__.py
│   │   ├── flashcard_generator.py  # Flashcard generation logic
│   │   ├── quiz_generator.py       # Quiz generation logic
│   │   └── exercise_generator.py   # Exercise generation logic
│   └── routes/                # API route modules
│       ├── __init__.py
│       ├── file_processing.py      # Document upload endpoints
│       └── health.py              # Health check endpoints
├── logs/                      # Application logs
│   └── fastapi_errors_*.log   # Error logs by date
├── model_cache/              # Hugging Face model cache
│   └── transformers/         # Cached transformer models
├── tests/                    # Test suite
│   ├── test_flashcards.py    # Flashcard generation tests
│   ├── test_quiz.py          # Quiz generation tests
│   └── test_document.py      # Document processing tests
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── Dockerfile               # Container configuration
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

The service uses environment variables for configuration. Create a `.env` file:

```bash
# Copy example configuration
cp .env.example .env
```

### Core Settings

```python
# app/config.py
class Settings:
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # AI Model Configuration
    MODEL_CACHE_DIR: str = "./model_cache"
    PRIMARY_MODEL: str = "distilgpt2"
    FALLBACK_MODEL: str = "gpt2"
    
    # Processing Limits
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    CHUNK_SIZE: int = 512
    MAX_CHUNKS: int = 10
    
    # Language Support
    SUPPORTED_LANGUAGES: list = ["en", "si", "ta"]
    DEFAULT_LANGUAGE: str = "en"
```

### Model Configuration

```python
# Model fallback strategy
MODEL_HIERARCHY = [
    "distilgpt2",           # Primary: Fast, efficient
    "gpt2",                 # Secondary: More capable
    "rule_based"            # Fallback: Always available
]
```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI JSON**: `http://localhost:8001/openapi.json`

### Core Endpoints

#### 📄 Document Processing

```http
POST /process-file
Content-Type: multipart/form-data

Parameters:
- file: File (PDF, DOCX, PPTX)
- language: str = "en" | "si" | "ta"
- difficulty: str = "beginner" | "intermediate" | "advanced"
- card_types: List[str] = ["flashcards", "quizzes", "exercises"]

Response:
{
  "flashcards": [...],
  "quizzes": [...],
  "exercises": [...],
  "metadata": {...}
}
```

#### 🏥 Health Check

```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0",
  "models_loaded": ["distilgpt2", "gpt2"],
  "memory_usage": "2.1GB"
}
```

#### 🎯 Content Generation

```http
POST /generate-flashcards
Content-Type: application/json

{
  "text": "Your content here...",
  "language": "en",
  "difficulty": "intermediate",
  "count": 5
}

Response:
{
  "flashcards": [
    {
      "question": "What is...?",
      "answer": "The answer is...",
      "type": "Q&A",
      "difficulty": "intermediate",
      "confidence": 0.85
    }
  ]
}
```

### Error Handling

```json
{
  "error": {
    "code": "PROCESSING_ERROR",
    "message": "Failed to process document",
    "details": "Unsupported file format",
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req-12345"
  }
}
```

### Rate Limiting

- **File Upload**: 10 requests per minute
- **Text Processing**: 100 requests per minute
- **Health Check**: Unlimited

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test categories
python -m pytest tests/test_flashcards.py
python -m pytest tests/test_document.py
```

### Test Structure

```python
# tests/test_flashcards.py
import pytest
from app.generators.flashcard_generator import generate_flashcards

@pytest.mark.asyncio
async def test_flashcard_generation():
    text = "Python is a programming language."
    result = await generate_flashcards(text, "en", "beginner")
    
    assert len(result) > 0
    assert "question" in result[0]
    assert "answer" in result[0]
```

### Manual Testing

```bash
# Test document upload
curl -X POST "http://localhost:8000/process-file" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_document.pdf" \
  -F "language=en" \
  -F "difficulty=intermediate"

# Test health endpoint
curl -X GET "http://localhost:8000/health"
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs model_cache

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run with Docker
docker build -t memospark-fastapi .
docker run -p 8000:8000 -v $(pwd)/model_cache:/app/model_cache memospark-fastapi
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./model_cache:/app/model_cache
      - ./logs:/app/logs
    environment:
      - DEBUG=False
      - MODEL_CACHE_DIR=/app/model_cache
    restart: unless-stopped
```

### Production Deployment

#### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Environment Configuration

```bash
# Production environment variables
export DEBUG=False
export LOG_LEVEL=INFO
export MODEL_CACHE_DIR=/opt/memospark/models
export MAX_WORKERS=4
```

### Monitoring & Logging

```python
# Health monitoring endpoint
@app.get("/metrics")
async def get_metrics():
    return {
        "requests_total": request_counter,
        "models_loaded": len(loaded_models),
        "memory_usage": get_memory_usage(),
        "uptime": get_uptime(),
        "error_rate": calculate_error_rate()
    }
```

## 🔍 Troubleshooting

### Common Issues

#### Model Loading Errors

```bash
# Issue: Model download fails
Error: ConnectionError: Unable to download model

# Solution: Check internet connection and model cache
rm -rf model_cache/
python -c "from transformers import pipeline; pipeline('text-generation', model='distilgpt2')"
```

#### Memory Issues

```bash
# Issue: Out of memory errors
RuntimeError: CUDA out of memory

# Solution: Reduce model size or batch size
export MAX_CHUNKS=5
export CHUNK_SIZE=256
```

#### File Processing Errors

```bash
# Issue: PDF processing fails
Error: Failed to extract text from PDF

# Solution: Check file integrity and format
python -c "import fitz; doc = fitz.open('your_file.pdf'); print(len(doc))"
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG

# Start with debug output
uvicorn app.main:app --reload --log-level debug
```

### Performance Optimization

```python
# Model caching optimization
@lru_cache(maxsize=3)
def load_model(model_name: str):
    return pipeline('text-generation', model=model_name)

# Memory management
import gc
gc.collect()  # Force garbage collection
```

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/memospark-fastapi-service.git
cd memospark-fastapi-service

# Create development environment
python -m venv dev-env
source dev-env/bin/activate  # or dev-env\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Code Standards

- **Type Hints**: All functions must have type annotations
- **Docstrings**: Use Google-style docstrings
- **Testing**: Minimum 80% code coverage
- **Linting**: Follow Black and flake8 standards

```python
# Example function with proper typing and docstring
from typing import List, Dict, Any

async def generate_flashcards(
    text: str, 
    language: str = "en", 
    difficulty: str = "beginner"
) -> List[Dict[str, Any]]:
    """Generate flashcards from input text.
    
    Args:
        text: The input text to process
        language: Target language for generation
        difficulty: Difficulty level for content
        
    Returns:
        List of dictionaries containing flashcard data
        
    Raises:
        ValueError: If text is empty or invalid
        ModelError: If AI model fails to generate content
    """
    pass
```

### Pull Request Process

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make Changes and Test**

   ```bash
   python -m pytest
   python -m black app/
   python -m flake8 app/
   ```

3. **Commit Changes**

   ```bash
   git commit -m "feat: add amazing feature"
   ```

4. **Push and Create PR**

   ```bash
   git push origin feature/amazing-feature
   ```

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Abdullah Jawahir

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👨‍💻 Author

<div align="center">

### **Abdullah Jawahir**

*AI Engineer & Full-Stack Developer*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Abdullah_Jawahir-blue?style=flat&logo=linkedin)](https://linkedin.com/in/abdullah-jawahir)
[![GitHub](https://img.shields.io/badge/GitHub-Abdullah_Jawahir-black?style=flat&logo=github)](https://github.com/Abdullah-Jawahir)
[![Email](https://img.shields.io/badge/Email-Contact_Me-red?style=flat&logo=gmail)](mailto:abdullahjawahir@gmail.com)

---

**🚀 Building the future of AI-powered education**

*Made with ❤️ and cutting-edge AI technology*

---

### 🌟 Related Projects

- **[MemoSpark Frontend](https://github.com/Abdullah-Jawahir/memo-spark)** - React-based user interface
- **[MemoSpark Laravel Service](https://github.com/Abdullah-Jawahir/memospark-laravel-service)** - Data management and user services

</div>

---

<div align="center">

**⭐ If this project helped you, please give it a star! ⭐**

**🔧 Found a bug? [Report it here](https://github.com/Abdullah-Jawahir/memospark-fastapi-service/issues)**

**💡 Have an idea? [Share it with us](https://github.com/Abdullah-Jawahir/memospark-fastapi-service/issues)**

</div>

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
