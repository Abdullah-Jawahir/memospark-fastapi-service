from ..models import model_manager
from ..config import GENERATION_LIMITS
from ..logger import logger
import json
import re

def generate_all_content(text: str, language: str = "en", difficulty: str = "beginner") -> dict:
    """
    Generate flashcards, quizzes, and exercises in a single OpenRouter request.
    Returns a dict with keys: flashcards, quizzes, exercises.
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            prompt = f"""
You are an educational content generator. Given the following text, generate:

1. {GENERATION_LIMITS['flashcards']} flashcards (Q&A pairs)
2. {GENERATION_LIMITS['quizzes']} multiple choice quiz questions (each with 4 options and the correct answer)
3. {GENERATION_LIMITS['exercises']} exercises (mix of fill-in-the-blank, true/false, short answer, and matching)

All content must be in the language: {language}.
Difficulty: {difficulty}.

Text:
{text[:2000]}

IMPORTANT: Return ONLY valid JSON. No additional text before or after the JSON object.
Format your response as JSON with keys: flashcards, quizzes, exercises. Each should be a list of objects. Example:
{{
  "flashcards": [ {{"question": "...", "answer": "..."}}, ... ],
  "quizzes": [ {{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}}, ... ],
  "exercises": [
    {{"type": "fill_blank", "instruction": "...", ...}},
    {{"type": "matching", "instruction": "...", "concepts": ["Hinge joint", "Ball-and-socket joint"], "definitions": ["Elbow", "Hip"]}},
    ...
  ]
}}
"""
            response = model_manager.generate_text(prompt, max_length=2000)
            
            if not response or not response.strip():
                logger.warning(f"Empty response from model (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error("All attempts failed - empty response")
                    return {"flashcards": [], "quizzes": [], "exercises": []}
            
            # Try to extract the JSON from the response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                logger.warning(f"Could not find JSON brackets in response (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error("All attempts failed - no JSON found")
                    return {"flashcards": [], "quizzes": [], "exercises": []}
            
            json_str = response[start:end]
            
            # Clean up common JSON issues
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
            
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as json_error:
                logger.warning(f"JSON parsing error (attempt {attempt + 1}/{max_retries}): {json_error}")
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error(f"All attempts failed - JSON parsing error: {json_error}")
                    logger.error(f"Problematic JSON string: {json_str[:200]}...")
                    return {"flashcards": [], "quizzes": [], "exercises": []}
            
            # Validate and process the data
            quizzes = data.get("quizzes", [])
            if not isinstance(quizzes, list):
                quizzes = []
            else:
                for quiz in quizzes:
                    if isinstance(quiz, dict):
                        if "difficulty" not in quiz:
                            quiz["difficulty"] = difficulty
                        if "type" not in quiz:
                            quiz["type"] = "Quiz"
            
            exercises = data.get("exercises", [])
            if not isinstance(exercises, list):
                exercises = []
            else:
                for exercise in exercises:
                    if isinstance(exercise, dict):
                        if "difficulty" not in exercise:
                            exercise["difficulty"] = difficulty
                        if "type" not in exercise:
                            exercise["type"] = "Exercise"
            
            flashcards = data.get("flashcards", [])
            if not isinstance(flashcards, list):
                flashcards = []
            else:
                for flashcard in flashcards:
                    if isinstance(flashcard, dict):
                        if "difficulty" not in flashcard:
                            flashcard["difficulty"] = difficulty
                        if "type" not in flashcard:
                            flashcard["type"] = "Flashcard"
            
            # Check if we got any content
            total_items = len(flashcards) + len(quizzes) + len(exercises)
            if total_items == 0:
                logger.warning(f"No content generated (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error("All attempts failed - no content generated")
                    return {"flashcards": [], "quizzes": [], "exercises": []}
            
            # Success! Log what we generated
            logger.info(f"Generated content (attempt {attempt + 1}): {len(flashcards)} flashcards, {len(quizzes)} quizzes, {len(exercises)} exercises")
            
            return {
                "flashcards": flashcards,
                "quizzes": quizzes,
                "exercises": exercises,
            }
            
        except Exception as e:
            logger.warning(f"Error in generate_all_content (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                continue
            else:
                logger.error(f"All attempts failed: {e}")
                return {"flashcards": [], "quizzes": [], "exercises": []}
    
    # If we get here, all retries failed
    return {"flashcards": [], "quizzes": [], "exercises": []} 