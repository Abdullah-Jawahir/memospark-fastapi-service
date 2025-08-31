from fastapi import APIRouter, HTTPException, Form
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..generators.flashcard_generator import FlashcardGenerator
from ..generators.topic_content_generator import TopicContentGenerator
from ..models import model_manager
from ..logger import logger
import time
import asyncio

router = APIRouter()

# Initialize generators
flashcard_generator = FlashcardGenerator()
topic_content_generator = TopicContentGenerator()

class SearchFlashcardRequest(BaseModel):
    """Request model for search-based flashcard generation."""
    topic: str
    description: Optional[str] = None
    difficulty: str = "beginner"
    count: int = 10

class SearchFlashcardResponse(BaseModel):
    """Response model for search-based flashcard generation."""
    topic: str
    description: Optional[str]
    flashcards: List[Dict[str, Any]]
    total_count: int
    difficulty: str
    message: str

@router.post("/search-flashcards", response_model=SearchFlashcardResponse)
async def search_and_generate_flashcards(request: SearchFlashcardRequest):
    """
    Generate flashcards based on a search topic and description.
    
    This endpoint is designed to work with Laravel's queue system.
    It processes the request asynchronously and returns the result
    when complete.
    
    Args:
        request: SearchFlashcardRequest containing topic, description, difficulty, and count
        
    Returns:
        SearchFlashcardResponse containing generated flashcards and metadata
    """
    logger.info(f"Generating flashcards for topic: {request.topic}")
    
    try:
        # Validate input
        if not request.topic or len(request.topic.strip()) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Topic must be at least 3 characters long"
            )
        
        if request.count < 1 or request.count > 20:
            raise HTTPException(
                status_code=400, 
                detail="Count must be between 1 and 20"
            )
        
        # Validate difficulty
        valid_difficulties = ["beginner", "intermediate", "advanced"]
        if request.difficulty not in valid_difficulties:
            request.difficulty = "beginner"
        
        # Add minimum processing time to ensure proper queue behavior
        start_time = time.time()
        
        # Generate educational content about the topic using the topic content generator
        topic_content = topic_content_generator.generate_topic_content(
            topic=request.topic,
            description=request.description,
            difficulty=request.difficulty
        )
        
        if not topic_content:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate content for the topic"
            )
        
        # Generate flashcards from the topic content in a single call
        flashcards = flashcard_generator.generate_flashcards(
            text=topic_content,
            language="en",  # Always generate in English as per requirements
            difficulty=request.difficulty,
            count=request.count
        )
        
        if not flashcards:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate valid flashcards for the topic"
            )
        
        # Ensure minimum processing time for queue system compatibility
        elapsed_time = time.time() - start_time
        min_processing_time = 2.0  # Minimum 2 seconds to ensure proper queue behavior
        
        if elapsed_time < min_processing_time:
            remaining_time = min_processing_time - elapsed_time
            await asyncio.sleep(remaining_time)
        
        logger.info(f"Successfully generated {len(flashcards)} flashcards for topic: {request.topic}")
        
        return SearchFlashcardResponse(
            topic=request.topic,
            description=request.description,
            flashcards=flashcards,
            total_count=len(flashcards),
            difficulty=request.difficulty,
            message=f"Successfully generated {len(flashcards)} flashcards for '{request.topic}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating flashcards for topic '{request.topic}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while generating flashcards: {str(e)}"
        )

@router.get("/search-flashcards/topics", response_model=List[str])
async def get_suggested_topics():
    """
    Get a list of suggested educational topics for flashcard generation.
    
    Returns:
        List of suggested topics that users can search for
    """
    suggested_topics = [
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
    
    return suggested_topics

@router.get("/search-flashcards/health")
async def search_flashcards_health():
    """
    Health check endpoint for the search flashcards service.
    
    Returns:
        Health status of the search flashcards functionality
    """
    try:
        # Test if the flashcard generator is working
        test_text = "This is a test text for health check."
        test_flashcards = flashcard_generator.generate_flashcards(test_text, "en", "beginner", 2)
        
        return {
            "status": "healthy",
            "service": "search-flashcards",
            "flashcard_generator": "working" if test_flashcards else "not_working",
            "model_manager": "available" if model_manager else "not_available"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "search-flashcards",
            "error": str(e)
        }
