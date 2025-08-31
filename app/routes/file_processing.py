from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import List, Optional
from ..text_extractor import extract_text_from_file
from ..generators import FlashcardGenerator, QuizGenerator, ExerciseGenerator
from ..utils import (
    validate_language,
    validate_difficulty,
    validate_file_type,
    translate_text,
    translate_generated_content,
)
from ..logger import logger
from ..generators.document_all_content_generator import generate_document_content

router = APIRouter()

# Initialize generators (kept for backward compatibility, but not used in main flow)
flashcard_generator = FlashcardGenerator()
quiz_generator = QuizGenerator()
exercise_generator = ExerciseGenerator()

def get_card_types(card_types: Optional[List[str]] = Form(None)):
    """Get card types from form data with validation."""
    if card_types is None:
        return ["flashcard"]
    
    valid_types = [ct for ct in card_types if ct in ["flashcard", "exercise", "quiz"]]
    return valid_types if valid_types else ["flashcard"]

@router.post("/process-file")
async def process_file(
    file: UploadFile = File(...),
    language: str = Form("en"),
    card_types: List[str] = Depends(get_card_types),
    difficulty: str = Form("beginner")
):
    """
    Process uploaded document and generate flashcards, exercises, and quizzes.
    
    Args:
        file: The uploaded file (PDF, DOCX, or PPTX)
        language: The language of the document (en, si, ta)
        card_types: List of card types to generate (flashcard, exercise, quiz)
        difficulty: The difficulty level (beginner, intermediate, advanced)
    
    Returns:
        JSON response containing generated content
    """
    logger.info(f"Processing file: {file.filename}")
    logger.debug(f"Parameters: language={language}, card_types={card_types}, difficulty={difficulty}")
    
    try:
        # Validate parameters
        if not validate_language(language):
            raise HTTPException(status_code=400, detail="Unsupported language")
        
        difficulty = validate_difficulty(difficulty)
        
        # Validate file type
        file_extension = file.filename.split(".")[-1].lower()
        if not validate_file_type(file_extension):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read and process file
        content = await file.read()
        text = extract_text_from_file(content, file_extension)
        
        # Note: We no longer translate the input text here
        # The AI will generate content in English first, then we'll translate the output
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found in the document")
        
        # Generate all content in English first (regardless of requested language)
        all_content = generate_document_content(text, "en", difficulty)
        
        # Now translate the generated content to the requested language if needed
        if language != "en":
            logger.info(f"Translating generated content to {language}")
            all_content = translate_generated_content(all_content, language)
        
        # Validate that we actually got content
        generated_content = {}
        total_items = 0
        
        if "flashcard" in card_types:
            flashcards = all_content.get("flashcards", [])
            if isinstance(flashcards, list) and len(flashcards) > 0:
                generated_content["flashcards"] = flashcards
                total_items += len(flashcards)
        
        if "quiz" in card_types:
            quizzes = all_content.get("quizzes", [])
            if isinstance(quizzes, list) and len(quizzes) > 0:
                generated_content["quizzes"] = quizzes
                total_items += len(quizzes)
        
        if "exercise" in card_types:
            exercises = all_content.get("exercises", [])
            if isinstance(exercises, list) and len(exercises) > 0:
                generated_content["exercises"] = exercises
                total_items += len(exercises)
        
        # Check if we actually generated any content
        if total_items == 0:
            logger.warning(f"No content generated for {file.filename}. Requested types: {card_types}")
            raise HTTPException(
                status_code=422, 
                detail=f"Failed to generate content. Please try again or check if the document contains sufficient text."
            )
        
        logger.info(f"Successfully processed {file.filename}. Generated {total_items} items: {list(generated_content.keys())}")
        return {"generated_content": generated_content}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") 