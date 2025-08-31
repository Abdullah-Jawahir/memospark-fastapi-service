import re
from typing import List, Dict, Any
from ..models import model_manager
from ..logger import logger

class FlashcardGenerator:
    """Generates flashcards from text content using efficient single-call generation."""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def generate_flashcards(self, text: str, language: str = "en", difficulty: str = "beginner", count: int = 10) -> List[Dict[str, Any]]:
        """Generate flashcards from text using a single, well-structured prompt."""
        try:
            text = text.strip()
            if len(text) < 50:
                logger.warning("Text is too short to generate meaningful flashcards")
                return []
            
            # Generate all flashcards in a single API call
            flashcards = self._generate_flashcards_single_call(text, language, difficulty, count)
            
            # Clean and validate flashcards
            cleaned_flashcards = self._clean_and_validate_flashcards(flashcards, count)
            
            logger.info(f"Generated {len(cleaned_flashcards)} cleaned flashcards")
            return cleaned_flashcards
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            return self._generate_rule_based_flashcards(text, language, difficulty, count)
    
    def _generate_flashcards_single_call(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate all flashcards in a single API call with a comprehensive prompt."""
        
        # Create a comprehensive prompt for generating multiple flashcards
        prompt = self._create_comprehensive_flashcard_prompt(text, language, difficulty, count)
        
        try:
            # Generate content with appropriate length for multiple flashcards
            max_length = count * 200  # Allocate space for multiple flashcards
            generated_content = self.model_manager.generate_text(prompt, max_length=max_length)
            
            if not generated_content:
                logger.warning("Failed to generate flashcard content, using fallback")
                return []
            
            # Parse the generated content to extract flashcards
            flashcards = self._parse_multiple_flashcards(generated_content, count)
            
            return flashcards
            
        except Exception as e:
            logger.error(f"Error in single-call flashcard generation: {str(e)}")
            return []
    
    def _create_comprehensive_flashcard_prompt(self, text: str, language: str, difficulty: str, count: int) -> str:
        """Create a comprehensive prompt for generating multiple high-quality flashcards."""
        
        # Adjust complexity based on difficulty
        complexity_guide = {
            "beginner": "basic concepts, simple explanations, fundamental principles",
            "intermediate": "detailed concepts, examples, connections between ideas", 
            "advanced": "complex concepts, advanced theories, practical applications, research insights"
        }
        
        complexity = complexity_guide.get(difficulty, complexity_guide["beginner"])
        
        # Language-specific instructions
        lang_instructions = {
            "en": "Generate in English",
            "si": "Generate in Sinhala",
            "ta": "Generate in Tamil"
        }
        
        lang_instruction = lang_instructions.get(language, "Generate in English")
        
        prompt = f"""You are an expert educational content creator. Based on the following text, create {count} high-quality flashcards.

{lang_instruction}
Difficulty Level: {difficulty.title()}
Focus on: {complexity}

Text to create flashcards from:
{text[:1000]}...

Requirements for each flashcard:
1. Question: Clear, specific, and educational question that tests understanding
2. Answer: Complete, accurate, and informative answer
3. Both question and answer should be self-contained and meaningful
4. Questions should cover different aspects of the topic
5. Avoid vague or overly broad questions
6. Ensure answers are complete sentences, not fragments

Format each flashcard exactly as follows:
Q: [Question here]
A: [Answer here]

---

Generate exactly {count} flashcards. Make sure each question and answer pair is high-quality, educational, and relevant to the text provided."""

        return prompt
    
    def _parse_multiple_flashcards(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse generated content to extract multiple flashcards."""
        flashcards = []
        
        # Split content by flashcard separators
        # Look for patterns like "Q:", "Question:", "A:", "Answer:" or numbered patterns
        sections = re.split(r'(?:Q:|Question:|^\d+\.|^-\s*)', content, flags=re.MULTILINE)
        
        current_question = ""
        current_answer = ""
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Check if this section contains a question
            if re.search(r'\?$', section.strip()):
                # Save previous flashcard if we have one
                if current_question and current_answer:
                    flashcards.append({
                        "question": current_question.strip(),
                        "answer": current_answer.strip(),
                        "type": "Q&A",
                        "difficulty": "beginner"
                    })
                
                # Start new flashcard
                current_question = section.strip()
                current_answer = ""
                
            elif current_question and not current_answer:
                # This is likely the answer
                current_answer = section.strip()
                
                # Save the flashcard
                if current_question and current_answer:
                    flashcards.append({
                        "question": current_question.strip(),
                        "answer": current_answer.strip(),
                        "type": "Q&A",
                        "difficulty": "beginner"
                    })
                    current_question = ""
                    current_answer = ""
        
        # Handle the last flashcard if we have one
        if current_question and current_answer:
            flashcards.append({
                "question": current_question.strip(),
                "answer": current_answer.strip(),
                "type": "Q&A",
                "difficulty": "beginner"
            })
        
        # If parsing failed, try alternative parsing methods
        if len(flashcards) < expected_count:
            flashcards.extend(self._parse_alternative_format(content, expected_count - len(flashcards)))
        
        return flashcards[:expected_count]
    
    def _parse_alternative_format(self, content: str, needed_count: int) -> List[Dict[str, Any]]:
        """Alternative parsing method for different response formats."""
        flashcards = []
        
        # Look for question-answer pairs in various formats
        lines = content.split('\n')
        current_qa = {"question": "", "answer": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for question indicators
            if re.search(r'\?$', line) and len(line) > 10:
                if current_qa["question"] and current_qa["answer"]:
                    flashcards.append({
                        "question": current_qa["question"],
                        "answer": current_qa["answer"],
                        "type": "Q&A",
                        "difficulty": "beginner"
                    })
                    if len(flashcards) >= needed_count:
                        break
                
                current_qa = {"question": line, "answer": ""}
            
            # Check for answer indicators
            elif current_qa["question"] and not current_qa["answer"] and len(line) > 10:
                current_qa["answer"] = line
        
        # Add the last flashcard if we have one
        if current_qa["question"] and current_qa["answer"]:
            flashcards.append({
                "question": current_qa["question"],
                "answer": current_qa["answer"],
                "type": "Q&A",
                "difficulty": "beginner"
            })
        
        return flashcards[:needed_count]
    
    def _clean_and_validate_flashcards(self, flashcards: List[Dict[str, Any]], target_count: int) -> List[Dict[str, Any]]:
        """Clean and validate flashcards, ensuring quality and completeness."""
        cleaned_flashcards = []
        
        for flashcard in flashcards:
            question = flashcard.get('question', '').strip()
            answer = flashcard.get('answer', '').strip()
            
            # Clean the text
            question = self._clean_text(question)
            answer = self._clean_text(answer)
            
            # Validate quality
            if self._is_valid_flashcard(question, answer):
                cleaned_flashcards.append({
                    "question": question,
                    "answer": answer,
                    "type": "Q&A",
                    "difficulty": flashcard.get('difficulty', 'beginner')
                })
            
            if len(cleaned_flashcards) >= target_count:
                break
        
        return cleaned_flashcards
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing unwanted formatting and artifacts."""
        if not text:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'#{1,6}\s*', '', text)  # Remove headers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic
        text = re.sub(r'`(.*?)`', r'\1', text)  # Remove code blocks
        
        # Remove common AI artifacts
        text = re.sub(r'Flashcard:\s*', '', text)
        text = re.sub(r'Q:\s*', '', text)
        text = re.sub(r'A:\s*', '', text)
        text = re.sub(r'Question:\s*', '', text)
        text = re.sub(r'Answer:\s*', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove incomplete sentences and fragments
        text = re.sub(r'\.{3,}', '.', text)
        text = re.sub(r'\.{2,}$', '.', text)
        
        # Ensure proper sentence endings
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _is_valid_flashcard(self, question: str, answer: str) -> bool:
        """Check if a flashcard meets quality standards."""
        # Basic length checks
        if len(question) < 10 or len(answer) < 10:
            return False
        
        # Check for meaningful content
        if question.lower().startswith(('what does', 'refer to', '###', '**')):
            return False
        
        if answer.lower().startswith(('###', '**', 'flashcard:', 'q:', 'a:')):
            return False
        
        # Ensure question ends with question mark
        if not question.endswith('?'):
            return False
        
        # Ensure answer doesn't end with question mark
        if answer.endswith('?'):
            return False
        
        # Check for complete sentences
        if not answer.endswith(('.', '!', '?')):
            return False
        
        return True
    
    def _generate_rule_based_flashcards(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate flashcards using rule-based approach when model fails."""
        flashcards = []
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        for i, sentence in enumerate(sentences[:count * 2]):
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
                
                if len(flashcards) >= count:
                    break
                    
            except Exception as e:
                continue
        
        return flashcards[:count] 