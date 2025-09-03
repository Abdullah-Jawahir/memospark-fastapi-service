# Search Flashcards API Documentation

## Overview

The Search Flashcards API allows users to generate educational flashcards based on any topic without needing to upload documents. Users can search for educational topics, provide descriptions, and receive AI-generated flashcards in English.

## Base URL

```
http://localhost:8001/api/v1
```

## Endpoints

### 1. Generate Flashcards from Topic

**POST** `/search-flashcards`

Generates flashcards based on a search topic and optional description.

#### Request Body

```json
{
  "topic": "string (required, min 3 characters)",
  "description": "string (optional)",
  "difficulty": "string (optional, default: 'beginner')",
  "count": "integer (optional, default: 10, range: 1-20)"
}
```

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` | string | Yes | - | The educational topic to search for (minimum 3 characters) |
| `description` | string | No | null | Additional context or description about the topic |
| `difficulty` | string | No | "beginner" | Difficulty level: "beginner", "intermediate", or "advanced" |
| `count` | integer | No | 10 | Number of flashcards to generate (1-20) |

#### Response

**Success Response (200 OK)**

```json
{
  "topic": "Machine Learning",
  "description": "Introduction to basic concepts",
  "flashcards": [
    {
      "question": "What is machine learning?",
      "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
      "type": "Q&A",
      "difficulty": "beginner"
    },
    {
      "question": "What are the three main types of machine learning?",
      "answer": "The three main types are supervised learning, unsupervised learning, and reinforcement learning.",
      "type": "Q&A",
      "difficulty": "beginner"
    }
  ],
  "total_count": 2,
  "difficulty": "beginner",
  "message": "Successfully generated 2 flashcards for 'Machine Learning'"
}
```

**Error Responses**

- **400 Bad Request**: Invalid input parameters
- **500 Internal Server Error**: Server-side generation failure

#### Example Usage

```bash
curl -X POST "http://localhost:8001/api/v1/search-flashcards" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Quantum Physics",
    "description": "Basic principles and concepts",
    "difficulty": "intermediate",
    "count": 15
  }'
```

### 2. Get Suggested Topics

**GET** `/search-flashcards/topics`

Returns a list of suggested educational topics for flashcard generation.

#### Response

**Success Response (200 OK)**

```json
[
  "Mathematics",
  "Physics",
  "Chemistry",
  "Biology",
  "History",
  "Geography",
  "Literature",
  "Computer Science",
  "Economics",
  "Psychology",
  "Philosophy",
  "Art History",
  "Music Theory",
  "Foreign Languages",
  "Environmental Science",
  "Astronomy",
  "Anatomy",
  "World Religions",
  "Political Science",
  "Sociology"
]
```

#### Example Usage

```bash
curl -X GET "http://localhost:8001/api/v1/search-flashcards/topics"
```

### 3. Health Check

**GET** `/search-flashcards/health`

Checks the health status of the search flashcards service.

#### Response

**Success Response (200 OK)**

```json
{
  "status": "healthy",
  "service": "search-flashcards",
  "flashcard_generator": "working",
  "model_manager": "available"
}
```

**Unhealthy Response (200 OK)**

```json
{
  "status": "unhealthy",
  "service": "search-flashcards",
  "error": "Model loading failed"
}
```

#### Example Usage

```bash
curl -X GET "http://localhost:8001/api/v1/search-flashcards/health"
```

## Flashcard Structure

Each generated flashcard follows this structure:

```json
{
  "question": "string - The question or prompt",
  "answer": "string - The answer or explanation",
  "type": "string - Always 'Q&A' for search-based flashcards",
  "difficulty": "string - The difficulty level used during generation"
}
```

## Difficulty Levels

- **beginner**: Basic concepts, simple explanations, fundamental principles
- **intermediate**: Detailed concepts, examples, connections between ideas
- **advanced**: Complex concepts, advanced theories, practical applications, research insights

## Content Generation

The system uses AI models to:

1. **Generate Topic Content**: Create comprehensive educational content about the requested topic
2. **Create Flashcards**: Extract key concepts and create question-answer pairs
3. **Ensure Quality**: Validate content length and relevance before returning results

## Error Handling

### Common Error Scenarios

1. **Topic Too Short**: Topic must be at least 3 characters long
2. **Invalid Count**: Count must be between 1 and 20
3. **Generation Failure**: AI model fails to generate content
4. **Model Unavailable**: Required AI models are not loaded

### Error Response Format

```json
{
  "detail": "Error description message"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. However, consider implementing rate limiting for production use.

## Authentication

Currently, no authentication is required. Consider implementing user authentication for production use.

## Testing

Use the provided test script to verify functionality:

```bash
cd fastapi-service
python test_search_flashcards.py
```

## Integration with Frontend

### Frontend Implementation Steps

1. **Search Interface**: Create a search bar for topic input
2. **Description Field**: Optional text area for additional context
3. **Difficulty Selection**: Dropdown for beginner/intermediate/advanced
4. **Count Selection**: Slider or input for number of flashcards (1-20)
5. **Results Display**: Show generated flashcards with study options
6. **Study Integration**: Connect to existing study page functionality

### Example Frontend Flow

```
User Input → API Call → Flashcard Generation → Results Display → Study Integration
```

## Performance Considerations

- **Content Generation**: May take 5-15 seconds depending on topic complexity
- **Flashcard Creation**: Additional 2-5 seconds for flashcard generation
- **Caching**: Consider implementing caching for popular topics
- **Async Processing**: For better UX, consider implementing async processing with progress updates

## Future Enhancements

1. **Topic Caching**: Cache generated content for popular topics
2. **User Preferences**: Save user's preferred difficulty and count settings
3. **Topic Categories**: Organize topics by subject area
4. **Content Validation**: Implement content quality scoring
5. **Multi-language Support**: Extend beyond English content generation
6. **Progress Tracking**: Track user's study progress with generated flashcards
