import random
from typing import List, Dict, Any
from ..models import model_manager
from ..utils import extract_key_concepts
from ..config import LANGUAGE_PROMPTS, GENERATION_LIMITS
from ..logger import logger

class QuizGenerator:
    """Generates multiple choice quizzes from text content."""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def generate_quizzes(self, text: str, language: str = "en", difficulty: str = "beginner") -> List[Dict[str, Any]]:
        """Generate multiple choice quizzes with improved accuracy."""
        try:
            text = text.strip()
            if len(text) < 100:
                return []
            
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
            key_concepts = extract_key_concepts(text)
            quizzes = []
            
            # Generate quiz prompts
            base_prompt = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS["en"])["quiz"]
            
            for i, sentence in enumerate(sentences[:6]):
                try:
                    if len(sentence.split()) < 8:
                        continue
                    
                    # Generate question using model
                    prompt = base_prompt.format(sentence)
                    generated = self.model_manager.generate_text(prompt, max_length=200)
                    
                    # Create options: 1 correct, 3 distractors
                    correct_answer = sentence
                    distractors = self._generate_distractors(sentences, i, language)
                    
                    options = distractors + [correct_answer]
                    random.shuffle(options)
                    
                    # Generate question
                    question = self._generate_question_text(sentence, language)
                    
                    quizzes.append({
                        "question": question,
                        "options": options,
                        "answer": correct_answer,
                        "correct_answer_option": correct_answer,
                        "type": "quiz",
                        "difficulty": difficulty
                    })
                    
                except Exception as e:
                    logger.warning(f"Error generating quiz {i}: {str(e)}")
                    continue
            
            logger.info(f"Generated {len(quizzes)} quizzes")
            return quizzes[:GENERATION_LIMITS["quizzes"]]
            
        except Exception as e:
            logger.error(f"Error generating quizzes: {str(e)}")
            return []
    
    def _generate_distractors(self, sentences: List[str], correct_index: int, language: str) -> List[str]:
        """Generate distractor options for quiz questions."""
        distractors = []
        
        # Get other sentences as distractors
        other_sentences = [s for j, s in enumerate(sentences) if j != correct_index and len(s.split()) > 5]
        random.shuffle(other_sentences)
        distractors = other_sentences[:3]
        
        # If not enough distractors, create some
        while len(distractors) < 3:
            if language == "si":
                distractors.append(f"වෙනත් සාධාරණ තොරතුර {len(distractors) + 1}")
            elif language == "ta":
                distractors.append(f"பிற பொதுவான தகவல் {len(distractors) + 1}")
            else:
                distractors.append(f"Other general information {len(distractors) + 1}")
        
        return distractors
    
    def _generate_question_text(self, sentence: str, language: str) -> str:
        """Generate question text based on the sentence and language."""
        words = sentence.split()
        
        if language == "si":
            return f"පහත සඳහන් කුමන කාරණය සත්‍ය ද? {' '.join(words[:8])}... ගැන"
        elif language == "ta":
            return f"பின்வருவனவற்றில் எது உண்மை? {' '.join(words[:8])}... பற்றி"
        else:
            return f"Which of the following is true about: {' '.join(words[:8])}...?" 