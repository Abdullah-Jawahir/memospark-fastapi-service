# Search Flashcards Feature

## Overview

The Search Flashcards feature allows users to generate educational flashcards based on any topic without needing to upload documents. Users can search for educational topics, provide descriptions, and receive AI-generated flashcards in English.

## Features

- **Topic-based Search**: Search for any educational topic
- **AI Content Generation**: Generate comprehensive educational content about topics
- **Flashcard Creation**: Automatically create flashcards from generated content
- **Difficulty Levels**: Support for beginner, intermediate, and advanced levels
- **Customizable Count**: Generate 1-20 flashcards per topic
- **Suggested Topics**: Pre-defined list of educational topics
- **Health Monitoring**: Service health check endpoints

## Architecture

### Components

1. **TopicContentGenerator** (`app/generators/topic_content_generator.py`)
   - Generates comprehensive educational content about topics
   - Adjusts complexity based on difficulty level
   - Provides fallback content generation

2. **SearchFlashcardsRouter** (`app/routes/search_flashcards.py`)
   - Handles HTTP requests for search functionality
   - Manages input validation and error handling
   - Coordinates between content generation and flashcard creation

3. **FlashcardGenerator** (existing)
   - Creates flashcards from generated content
   - Ensures consistent flashcard structure

### API Endpoints

- `POST /api/v1/search-flashcards` - Generate flashcards from topic
- `GET /api/v1/search-flashcards/topics` - Get suggested topics
- `GET /api/v1/search-flashcards/health` - Service health check

## Installation & Setup

### Prerequisites

- Python 3.8+
- FastAPI
- Required AI models (configured in `config.py`)

### Setup Steps

1. **Ensure Dependencies**: The feature uses existing dependencies
2. **Model Configuration**: Verify AI models are properly configured
3. **Service Integration**: The feature is automatically integrated into the main FastAPI app

### Configuration

The feature uses existing configuration from `config.py`:
- Model settings
- Generation parameters
- Language prompts

## Usage

### Basic Usage

```python
from app.generators.topic_content_generator import TopicContentGenerator
from app.generators.flashcard_generator import FlashcardGenerator

# Initialize generators
topic_generator = TopicContentGenerator()
flashcard_generator = FlashcardGenerator()

# Generate content for a topic
content = topic_generator.generate_topic_content(
    topic="Quantum Physics",
    description="Basic principles and concepts",
    difficulty="intermediate"
)

# Generate flashcards from content
flashcards = flashcard_generator.generate_flashcards(
    text=content,
    language="en",
    difficulty="intermediate"
)
```

### API Usage

```bash
# Generate flashcards
curl -X POST "http://localhost:8001/api/v1/search-flashcards" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning",
    "description": "Introduction to basic concepts",
    "difficulty": "beginner",
    "count": 10
  }'

# Get suggested topics
curl -X GET "http://localhost:8001/api/v1/search-flashcards/topics"

# Check health
curl -X GET "http://localhost:8001/api/v1/search-flashcards/health"
```

## Frontend Integration

### JavaScript Integration

```javascript
class SearchFlashcardsAPI {
    constructor(baseURL = 'http://localhost:8001/api/v1') {
        this.baseURL = baseURL;
    }

    async generateFlashcards(request) {
        const response = await fetch(`${this.baseURL}/search-flashcards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });
        return await response.json();
    }
}

// Usage
const api = new SearchFlashcardsAPI();
const result = await api.generateFlashcards({
    topic: 'Python Programming',
    difficulty: 'beginner',
    count: 5
});
```

### React Component Example

See `frontend_integration_example.js` for a complete React component implementation.

## Testing

### Run Tests

```bash
cd fastapi-service
python test_search_flashcards.py
```

### Test Coverage

The test suite covers:
- Topic content generation
- Flashcard creation
- End-to-end functionality
- Error handling

## Error Handling

### Common Errors

1. **Topic Too Short**: Minimum 3 characters required
2. **Invalid Count**: Must be between 1-20
3. **Generation Failure**: AI model fails to generate content
4. **Model Unavailable**: Required models not loaded

### Error Responses

```json
{
  "detail": "Error description message"
}
```

## Performance Considerations

### Response Times

- **Content Generation**: 5-15 seconds (topic complexity dependent)
- **Flashcard Creation**: 2-5 seconds
- **Total Response**: 7-20 seconds

### Optimization Tips

1. **Content Caching**: Cache popular topics
2. **Async Processing**: Consider implementing background processing
3. **Progress Updates**: Provide real-time feedback to users

## Security

### Current State

- No authentication required
- Input validation implemented
- No rate limiting

### Recommendations

1. **Authentication**: Implement user authentication
2. **Rate Limiting**: Add request rate limiting
3. **Input Sanitization**: Enhance input validation
4. **API Keys**: Consider API key authentication

## Monitoring

### Health Checks

- Service availability
- Model status
- Flashcard generator status

### Logging

- Request/response logging
- Error logging
- Performance metrics

## Troubleshooting

### Common Issues

1. **Models Not Loading**
   - Check model configuration
   - Verify model cache directory
   - Check available memory

2. **Content Generation Fails**
   - Verify AI model status
   - Check prompt formatting
   - Review error logs

3. **Flashcard Creation Issues**
   - Validate generated content
   - Check flashcard generator configuration
   - Review parsing logic

### Debug Mode

Enable debug logging in `logger.py` for detailed troubleshooting.

## Future Enhancements

### Planned Features

1. **Topic Caching**: Cache generated content
2. **User Preferences**: Save user settings
3. **Topic Categories**: Organize by subject
4. **Content Validation**: Quality scoring
5. **Multi-language**: Support beyond English

### API Improvements

1. **Batch Processing**: Generate multiple topics
2. **Content Templates**: Predefined content structures
3. **Export Options**: Multiple output formats
4. **Progress Tracking**: Real-time generation status

## Contributing

### Development Guidelines

1. **Code Style**: Follow existing code patterns
2. **Testing**: Add tests for new features
3. **Documentation**: Update API documentation
4. **Error Handling**: Implement proper error handling

### Testing New Features

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test API endpoints
3. **End-to-End Tests**: Test complete workflows

## Support

### Documentation

- API Documentation: `SEARCH_FLASHCARDS_API.md`
- Frontend Integration: `frontend_integration_example.js`
- Test Suite: `test_search_flashcards.py`

### Issues

Report issues through the project's issue tracking system.

### Questions

For questions about implementation or usage, refer to the documentation or create an issue.
