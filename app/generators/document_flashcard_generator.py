import re
import json
from typing import List, Dict, Any
from ..models import model_manager
from ..logger import logger

class DocumentFlashcardGenerator:
    """Generates flashcards from document text content with robust JSON handling and fallbacks."""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def generate_flashcards(self, text: str, language: str = "en", difficulty: str = "beginner", count: int = 10) -> List[Dict[str, Any]]:
        """Generate flashcards from document text with multiple fallback strategies."""
        try:
            logger.info(f"Starting document flashcard generation: text_length={len(text)}, language={language}, difficulty={difficulty}, count={count}")
            
            text = text.strip()
            if len(text) < 50:
                logger.warning("Text is too short to generate meaningful flashcards")
                return []
            
            # Try structured JSON generation first
            flashcards = self._generate_structured_flashcards(text, language, difficulty, count)
            
            # If that fails, try simple Q&A generation
            if not flashcards:
                logger.info("Structured generation failed, trying simple Q&A generation...")
                flashcards = self._generate_simple_flashcards(text, language, difficulty, count)
            
            # If still no flashcards, check if we have any AI fallbacks available
            if not flashcards:
                logger.warning("All AI-based generation attempts failed.")
                # The ModelManager will have already tried OpenRouter -> Gemini -> Local
                # If we get here, all AI methods have been exhausted
                from ..config import ENABLE_RULE_BASED_FALLBACK
                if ENABLE_RULE_BASED_FALLBACK:
                    logger.info("Using rule-based generation as final fallback...")
                    flashcards = self._generate_rule_based_flashcards(text, language, difficulty, count)
                else:
                    logger.warning("Rule-based fallback disabled. Returning empty content to maintain quality.")
                    return []
            
            # Clean and validate flashcards
            cleaned_flashcards = self._clean_and_validate_flashcards(flashcards, count)
            
            logger.info(f"Generated {len(cleaned_flashcards)} cleaned flashcards")
            return cleaned_flashcards
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            # Final fallback - only use rule-based if explicitly enabled
            from ..config import ENABLE_RULE_BASED_FALLBACK
            if ENABLE_RULE_BASED_FALLBACK:
                logger.info("Using rule-based generation as final fallback...")
                return self._generate_rule_based_flashcards(text, language, difficulty, count)
            else:
                logger.warning("All generation methods failed. Returning empty content to maintain quality.")
                return []
    
    def _generate_structured_flashcards(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate flashcards using structured JSON prompt."""
        
        prompt = f"""Generate exactly {count} educational flashcards from the following text.

Text: {text[:1500]}...

Requirements:
- Difficulty: {difficulty}
- Language: {language}
- Format: Each flashcard must have a clear question and comprehensive answer
- Questions should be specific and educational
- Answers should be informative and complete

Return ONLY a valid JSON array with this exact format:
[
  {{
    "question": "What is the main concept discussed in this text?",
    "answer": "The main concept is...",
    "type": "Q&A",
    "difficulty": "{difficulty}"
  }},
  {{
    "question": "How does this concept work?",
    "answer": "This concept works by...",
    "type": "Q&A", 
    "difficulty": "{difficulty}"
  }}
]

IMPORTANT: Return ONLY the JSON array, no additional text or explanations."""

        try:
            response = self.model_manager.generate_text(prompt, max_length=2000)
            
            if not response or not response.strip():
                logger.warning("Empty response from model")
                return []
            
            # Extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON array found in response")
                return []
            
            json_str = response[json_start:json_end]
            
            # Clean up common JSON issues
            json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas in objects
            
            try:
                flashcards = json.loads(json_str)
                if isinstance(flashcards, list):
                    logger.info(f"Successfully parsed {len(flashcards)} flashcards from JSON")
                    return flashcards
                else:
                    logger.warning("Response is not a JSON array")
                    return []
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error in structured generation: {e}")
            return []
    
    def _generate_simple_flashcards(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate flashcards using simple Q&A format prompt."""
        
        prompt = f"""Create {count} educational flashcards from this text:

{text[:1000]}...

Generate {count} flashcards in this simple format:
Q: [Question about the topic]
A: [Answer explaining the concept]

Q: [Another question]
A: [Another answer]

Make sure each question ends with a question mark and each answer is complete."""

        try:
            response = self.model_manager.generate_text(prompt, max_length=1500)
            
            if not response or not response.strip():
                return []
            
            # Parse Q&A format
            flashcards = self._parse_qa_format(response, count)
            return flashcards
            
        except Exception as e:
            logger.error(f"Error in simple generation: {e}")
            return []
    
    def _parse_qa_format(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse Q&A format content into flashcards."""
        flashcards = []
        
        # Split by Q: or Question:
        sections = re.split(r'(?:Q:|Question:)', content, flags=re.IGNORECASE)
        
        current_question = ""
        current_answer = ""
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Look for A: or Answer: to separate question and answer
            if re.search(r'(?:A:|Answer:)', section, re.IGNORECASE):
                parts = re.split(r'(?:A:|Answer:)', section, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()
                    
                    if question and answer and len(question) > 5 and len(answer) > 5:
                        flashcards.append({
                            "question": question,
                            "answer": answer,
                            "type": "Q&A",
                            "difficulty": "beginner"
                        })
                        
                        if len(flashcards) >= expected_count:
                            break
            else:
                # If no A: found, this might be just a question
                if not current_question and len(section) > 5:
                    current_question = section
        
        logger.info(f"Parsed {len(flashcards)} flashcards from Q&A format")
        return flashcards
    
    def _generate_rule_based_flashcards(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate flashcards using rule-based approach when AI fails."""
        logger.info("Using rule-based flashcard generation as fallback")
        
        flashcards = []
        
        # Extract sentences and key concepts
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        key_concepts = self._extract_key_concepts(text)
        
        # Create concept-based questions
        for i, concept in enumerate(key_concepts[:min(count//2, len(key_concepts))]):
            if language == "si":
                question = f"'{concept}' යන්නෙන් අදහස් කරන්නේ කුමක්ද?"
            elif language == "ta":
                question = f"'{concept}' என்பதன் பொருள் என்ன?"
            else:
                question = f"What is '{concept}'?"
            
            # Find relevant content
            relevant_content = self._find_relevant_content(text, concept)
            answer = relevant_content if relevant_content else f"Information about {concept}"
            
            flashcards.append({
                "question": question,
                "answer": answer,
                "type": "Q&A",
                "difficulty": difficulty
            })
        
        # Generate sentence-based questions
        remaining_count = count - len(flashcards)
        for i, sentence in enumerate(sentences[:remaining_count]):
            if language == "si":
                question = f"මෙම කරුණ ගැන කුමක් කිව හැකිද: {sentence[:100]}...?"
            elif language == "ta":
                question = f"இந்த விஷயத்தைப் பற்றி என்ன சொல்லலாம்: {sentence[:100]}...?"
            else:
                question = f"What can you tell me about: {sentence[:100]}...?"
            
            flashcards.append({
                "question": question,
                "answer": sentence,
                "type": "Q&A",
                "difficulty": difficulty
            })
        
        # Fill remaining with generic questions
        while len(flashcards) < count:
            if language == "si":
                question = "මෙම විෂයයේ ප්‍රධාන සංකල්ප මොනවාද?"
                answer = "මෙම විෂයයේ ප්‍රධාන සංකල්ප සහ මූලධර්ම ඇතුළත් වේ."
            elif language == "ta":
                question = "இந்த பாடத்தின் முக்கிய கருத்துக்கள் என்ன?"
                answer = "இந்த பாடத்தின் முக்கிய கருத்துக்கள் மற்றும் கொள்கைகள் அடங்கும்."
            else:
                question = "What are the main concepts in this topic?"
                answer = "This topic covers various important concepts and principles that are fundamental to understanding the subject matter."
            
            flashcards.append({
                "question": question,
                "answer": answer,
                "type": "Q&A",
                "difficulty": difficulty
            })
        
        logger.info(f"Rule-based generation created {len(flashcards)} flashcards")
        return flashcards[:count]
    
    def _clean_and_validate_flashcards(self, flashcards: List[Dict[str, Any]], target_count: int) -> List[Dict[str, Any]]:
        """Clean and validate flashcards."""
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
        """Clean text by removing unwanted formatting."""
        if not text:
            return ""
        
        # Remove markdown and formatting
        text = re.sub(r'#{1,6}\s*', '', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove common prefixes
        text = re.sub(r'^(Q:|A:|Question:|Answer:)\s*', '', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Ensure proper sentence endings
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _is_valid_flashcard(self, question: str, answer: str) -> bool:
        """Check if a flashcard meets quality standards."""
        if len(question) < 10 or len(answer) < 10:
            return False
        
        # Ensure question ends with question mark
        if not question.endswith('?'):
            return False
        
        # Ensure answer doesn't end with question mark
        if answer.endswith('?'):
            return False
        
        return True
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text."""
        try:
            # Extract capitalized words (potential concepts)
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            
            # Count frequency
            word_freq = {}
            for word in words:
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Return top concepts
            key_concepts = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [concept[0] for concept in key_concepts[:10]]
        except Exception:
            return ["Topic", "Concept", "Principle", "Theory", "Method"]
    
    def _find_relevant_content(self, text: str, concept: str) -> str:
        """Find relevant content explaining a concept."""
        try:
            sentences = text.split('.')
            for sentence in sentences:
                if concept.lower() in sentence.lower() and len(sentence.strip()) > 20:
                    return sentence.strip()
            return ""
        except Exception:
            return ""
