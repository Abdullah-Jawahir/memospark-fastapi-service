import re
from typing import List, Dict, Any
from ..models import model_manager
from ..utils import extract_key_concepts, split_text_into_chunks
from ..config import LANGUAGE_PROMPTS, GENERATION_LIMITS
from ..logger import logger

class FlashcardGenerator:
    """Generates flashcards from text content."""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def generate_flashcards(self, text: str, language: str = "en", difficulty: str = "beginner") -> List[Dict[str, Any]]:
        """Generate flashcards from text using improved prompting and parsing."""
        try:
            text = text.strip()
            if len(text) < 50:
                logger.warning("Text is too short to generate meaningful flashcards")
                return []
            
            # Extract key concepts for better question generation
            key_concepts = extract_key_concepts(text)
            
            # Split text into meaningful chunks
            chunks = split_text_into_chunks(text)
            
            flashcards = []
            base_prompt = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS["en"])["flashcard"]
            
            for i, chunk in enumerate(chunks[:GENERATION_LIMITS["text_chunks"]]):
                try:
                    # Use key concepts to generate focused questions
                    if key_concepts and i < len(key_concepts):
                        concept = key_concepts[i]
                        focused_prompt = f"{base_prompt.format(chunk)} What is {concept}?"
                    else:
                        focused_prompt = base_prompt.format(chunk)
                    
                    generated = self.model_manager.generate_text(focused_prompt, max_length=150)
                    
                    if generated and len(generated.strip()) > 10:
                        # Try to parse question and answer
                        question, answer = self._parse_flashcard_response(generated, language, chunk)
                        
                        if question and answer:
                            flashcards.append({
                                "question": question,
                                "answer": answer,
                                "type": "Q&A",
                                "difficulty": difficulty
                            })
                        
                except Exception as e:
                    logger.warning(f"Error generating flashcard for chunk {i}: {str(e)}")
                    continue
            
            # If model failed, generate rule-based flashcards
            if not flashcards:
                flashcards = self._generate_rule_based_flashcards(text, language, difficulty)
            
            logger.info(f"Generated {len(flashcards)} flashcards")
            return flashcards[:GENERATION_LIMITS["flashcards"]]
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            return self._generate_rule_based_flashcards(text, language, difficulty)
    
    def _parse_flashcard_response(self, generated: str, language: str, chunk: str) -> tuple:
        """Parse the generated response to extract question and answer."""
        lines = generated.strip().split('\n')
        question = ""
        answer = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith(('Question:', 'ප්‍රශ්නය:', 'கேள்வி:')):
                question = line.split(':', 1)[1].strip()
            elif line.startswith(('Answer:', 'පිළිතුර:', 'பதில்:')):
                answer = line.split(':', 1)[1].strip()
            elif not question and len(line) > 10 and line.endswith('?'):
                question = line
            elif question and not answer and len(line) > 10:
                answer = line
        
        # If parsing failed, create from the chunk
        if not question:
            if language == "si":
                question = f"මෙම කරුණ ගැන කුමක් කිව හැකිද: {chunk[:100]}...?"
            elif language == "ta":
                question = f"இந்த விஷயத்தைப் பற்றி என்ன சொல்லலாம்: {chunk[:100]}...?"
            else:
                question = f"What can you tell me about: {chunk[:100]}...?"
        
        if not answer:
            answer = chunk[:200] + "..." if len(chunk) > 200 else chunk
        
        # Clean up and validate
        question = re.sub(r'\s+', ' ', question).strip()
        answer = re.sub(r'\s+', ' ', answer).strip()
        
        if len(question) > 10 and len(answer) > 10:
            return question, answer
        
        return "", ""
    
    def _generate_rule_based_flashcards(self, text: str, language: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate flashcards using rule-based approach when model fails."""
        flashcards = []
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        for i, sentence in enumerate(sentences[:8]):
            try:
                if language == "si":
                    question = f"'{sentence[:50]}...' යන්නෙන් අදහස් කරන්නේ කුමක්ද?"
                elif language == "ta":
                    question = f"'{sentence[:50]}...' என்பதன் பொருள் என்ன?"
                else:
                    question = f"What does '{sentence[:50]}...' refer to?"
                
                flashcards.append({
                    "question": question,
                    "answer": sentence,
                    "type": "Q&A",
                    "difficulty": difficulty
                })
            except Exception as e:
                continue
        
        return flashcards 