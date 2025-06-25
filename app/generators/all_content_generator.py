from ..models import model_manager
from ..config import GENERATION_LIMITS
from ..logger import logger

def generate_all_content(text: str, language: str = "en", difficulty: str = "beginner") -> dict:
    """
    Generate flashcards, quizzes, and exercises in a single OpenRouter request.
    Returns a dict with keys: flashcards, quizzes, exercises.
    """
    prompt = f"""
You are an educational content generator. Given the following text, generate:

1. {GENERATION_LIMITS['flashcards']} flashcards (Q&A pairs)
2. {GENERATION_LIMITS['quizzes']} multiple choice quiz questions (each with 4 options and the correct answer)
3. {GENERATION_LIMITS['exercises']} exercises (mix of fill-in-the-blank, true/false, short answer, and matching)

All content must be in the language: {language}.
Difficulty: {difficulty}.

Text:
{text[:2000]}

Format your response as JSON with keys: flashcards, quizzes, exercises. Each should be a list of objects. Example:
{
  "flashcards": [ {"question": "...", "answer": "..."}, ... ],
  "quizzes": [ {"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}, ... ],
  "exercises": [ {"type": "fill_blank", "instruction": "...", ...}, ... ]
}
"""
    try:
        response = model_manager.generate_text(prompt, max_length=2000)
        import json
        # Try to extract the JSON from the response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response[start:end]
            data = json.loads(json_str)
            return {
                "flashcards": data.get("flashcards", []),
                "quizzes": data.get("quizzes", []),
                "exercises": data.get("exercises", []),
            }
        else:
            logger.error("Could not find JSON in OpenRouter response")
            return {"flashcards": [], "quizzes": [], "exercises": []}
    except Exception as e:
        logger.error(f"Error in generate_all_content: {e}")
        return {"flashcards": [], "quizzes": [], "exercises": []} 