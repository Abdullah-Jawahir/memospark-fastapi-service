from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import List, Optional
from ..text_extractor import extract_text_from_file
from ..generators import FlashcardGenerator, QuizGenerator, ExerciseGenerator
from ..utils import (
    validate_language,
    validate_difficulty,
    validate_file_type,
    translate_text,
)
from ..logger import logger

router = APIRouter()

# Initialize generators
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
        
        # Translate text if needed
        lang_map = {"en": "en", "si": "si", "ta": "ta"}
        if language in lang_map and language != "en":
            text = translate_text(text, lang_map[language])
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found in the document")
        
        # Generate requested content types
        generated_content = {}
        
        if "flashcard" in card_types:
            logger.info("Generating flashcards...")
            flashcards = flashcard_generator.generate_flashcards(text, language, difficulty)
            generated_content["flashcards"] = flashcards
        
        if "quiz" in card_types:
            logger.info("Generating quizzes...")
            quizzes = quiz_generator.generate_quizzes(text, language, difficulty)
            generated_content["quizzes"] = quizzes
        
        if "exercise" in card_types:
            logger.info("Generating exercises...")
            exercises = exercise_generator.generate_exercises(text, language, difficulty)
            generated_content["exercises"] = exercises
        
        logger.info(f"Successfully processed {file.filename}. Generated: {list(generated_content.keys())}")
        return {"generated_content": generated_content}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") 