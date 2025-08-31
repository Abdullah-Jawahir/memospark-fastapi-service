from fastapi import APIRouter, HTTPException, Form
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..generators.flashcard_generator import FlashcardGenerator
from ..generators.topic_content_generator import TopicContentGenerator
from ..models import model_manager
from ..logger import logger
import time
import asyncio
import re

router = APIRouter()

# Initialize generators
flashcard_generator = FlashcardGenerator()
topic_content_generator = TopicContentGenerator()

def clean_flashcard_text(text: str) -> str:
    """
    Clean and format flashcard text to remove markdown and formatting artifacts.
    
    Args:
        text: Raw text from AI model
        
    Returns:
        Clean, formatted text suitable for flashcards
    """
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'#{1,6}\s*', '', text)  # Remove headers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic
    text = re.sub(r'`(.*?)`', r'\1', text)  # Remove code blocks
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove links
    
    # Remove incomplete sentences and fragments
    text = re.sub(r'\.{3,}', '.', text)  # Replace multiple dots with single dot
    text = re.sub(r'\.{2,}$', '.', text)  # Remove trailing dots
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    text = text.strip()
    
    # Remove common AI artifacts
    text = re.sub(r'Flashcard:\s*', '', text)
    text = re.sub(r'Q:\s*', '', text)
    text = re.sub(r'A:\s*', '', text)
    text = re.sub(r'Question:\s*', '', text)
    text = re.sub(r'Answer:\s*', '', text)
    
    # Remove specific artifacts from your example
    text = re.sub(r'### \*\*.*?\*\*.*?\n#### \*\*.*?\*\*.*?\n', '', text)
    text = re.sub(r'Core Definition\*\*\s*\n\*\*Flashcard:\s*\n\*\*Q:\s*', '', text)
    text = re.sub(r'Key Concepts\*\*\s*\n\*\*Flashcard:\s*\n\*\*Q:\s*', '', text)
    text = re.sub(r'What does \'.*?\' refer to\?', '', text)
    
    # Remove incomplete text fragments
    text = re.sub(r'\.{2,}$', '.', text)  # Remove trailing dots
    text = re.sub(r'\(e\.g\.,?.*?\)', '', text)  # Remove incomplete examples
    text = re.sub(r',.*?\.{2,}', '.', text)  # Remove trailing incomplete phrases
    
    # Ensure proper sentence endings
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
    
    # Final cleanup - remove any remaining artifacts
    text = re.sub(r'\s+', ' ', text)  # Clean up any remaining multiple spaces
    text = text.strip()
    
    return text

def format_flashcard_pair(question: str, answer: str) -> tuple[str, str]:
    """
    Format a question-answer pair to ensure they're clean and meaningful.
    
    Args:
        question: Raw question text
        answer: Raw answer text
        
    Returns:
        Tuple of (clean_question, clean_answer)
    """
    # Clean the texts
    clean_q = clean_flashcard_text(question)
    clean_a = clean_flashcard_text(answer)
    
    # Skip if either text is too short or meaningless
    if len(clean_q) < 10 or len(clean_a) < 10:
        return "", ""
    
    # Skip if question contains common artifacts
    if any(artifact in clean_q.lower() for artifact in ['what does', 'refer to', '###', '**']):
        return "", ""
    
    # Skip if answer contains common artifacts
    if any(artifact in clean_a.lower() for artifact in ['###', '**', 'flashcard:', 'q:', 'a:']):
        return "", ""
    
    # Ensure question ends with question mark
    if clean_q and not clean_q.endswith('?'):
        clean_q += '?'
    
    # Ensure answer doesn't end with question mark
    if clean_a and clean_a.endswith('?'):
        clean_a = clean_a[:-1] + '.'
    
    # Ensure answer is a complete sentence
    if clean_a and not clean_a.endswith(('.', '!', '?')):
        clean_a += '.'
    
    return clean_q, clean_a

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
        # This prevents the job from completing too quickly and ensures
        # the frontend can properly track progress
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
        
        # Generate flashcards from the topic content
        raw_flashcards = flashcard_generator.generate_flashcards(
            text=topic_content,
            language="en",  # Always generate in English as per requirements
            difficulty=request.difficulty
        )
        
        # Clean and format flashcards
        cleaned_flashcards = []
        for flashcard in raw_flashcards[:request.count * 2]:  # Process more to account for filtering
            # Clean the question and answer
            clean_question, clean_answer = format_flashcard_pair(
                flashcard.get('question', ''),
                flashcard.get('answer', '')
            )
            
            # Only include flashcards with meaningful content
            if clean_question and clean_answer and len(clean_question) > 10 and len(clean_answer) > 10:
                cleaned_flashcards.append({
                    'question': clean_question,
                    'answer': clean_answer,
                    'type': flashcard.get('type', 'Q&A'),
                    'difficulty': flashcard.get('difficulty', request.difficulty)
                })
                
                # Stop if we have enough flashcards
                if len(cleaned_flashcards) >= request.count:
                    break
        
        # If we don't have enough cleaned flashcards, try to generate more
        if len(cleaned_flashcards) < request.count:
            logger.warning(f"Only got {len(cleaned_flashcards)} clean flashcards, attempting to generate more")
            
            # Try to process more raw flashcards
            for flashcard in raw_flashcards[request.count * 2:]:
                if len(cleaned_flashcards) >= request.count:
                    break
                    
                clean_question, clean_answer = format_flashcard_pair(
                    flashcard.get('question', ''),
                    flashcard.get('answer', '')
                )
                
                if clean_question and clean_answer:
                    cleaned_flashcards.append({
                        'question': clean_question,
                        'answer': clean_answer,
                        'type': flashcard.get('type', 'Q&A'),
                        'difficulty': flashcard.get('difficulty', request.difficulty)
                    })
        
        if not cleaned_flashcards:
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
        
        logger.info(f"Successfully generated {len(cleaned_flashcards)} cleaned flashcards for topic: {request.topic}")
        
        return SearchFlashcardResponse(
            topic=request.topic,
            description=request.description,
            flashcards=cleaned_flashcards,
            total_count=len(cleaned_flashcards),
            difficulty=request.difficulty,
            message=f"Successfully generated {len(cleaned_flashcards)} flashcards for '{request.topic}'"
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
        test_flashcards = flashcard_generator.generate_flashcards(test_text, "en", "beginner")
        
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
