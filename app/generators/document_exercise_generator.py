import re
import json
from typing import List, Dict, Any
from ..models import model_manager
from ..logger import logger

class DocumentExerciseGenerator:
    """Generates exercises from document text content with robust JSON handling and fallbacks."""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def generate_exercises(self, text: str, language: str = "en", difficulty: str = "beginner", count: int = 5) -> List[Dict[str, Any]]:
        """Generate exercises from document text with multiple fallback strategies."""
        try:
            logger.info(f"Starting document exercise generation: text_length={len(text)}, language={language}, difficulty={difficulty}, count={count}")
            
            text = text.strip()
            if len(text) < 50:
                logger.warning("Text is too short to generate meaningful exercises")
                return []
            
            # Try structured JSON generation first
            exercises = self._generate_structured_exercises(text, language, difficulty, count)
            
            # If that fails, try simple format generation
            if not exercises:
                logger.info("Structured generation failed, trying simple format generation...")
                exercises = self._generate_simple_exercises(text, language, difficulty, count)
            
            # If still no exercises, check if we have any AI fallbacks available
            if not exercises:
                logger.warning("All AI-based generation attempts failed.")
                # The ModelManager will have already tried OpenRouter -> Gemini -> Local
                # If we get here, all AI methods have been exhausted
                from ..config import ENABLE_RULE_BASED_FALLBACK
                if ENABLE_RULE_BASED_FALLBACK:
                    logger.info("Using rule-based generation as final fallback...")
                    exercises = self._generate_rule_based_exercises(text, language, difficulty, count)
                else:
                    logger.warning("Rule-based fallback disabled. Returning empty content to maintain quality.")
                    return []
            
            # Clean and validate exercises
            cleaned_exercises = self._clean_and_validate_exercises(exercises, count)
            
            logger.info(f"Generated {len(cleaned_exercises)} cleaned exercises")
            return cleaned_exercises
            
        except Exception as e:
            logger.error(f"Error generating exercises: {str(e)}")
            # Final fallback - only use rule-based if explicitly enabled
            from ..config import ENABLE_RULE_BASED_FALLBACK
            if ENABLE_RULE_BASED_FALLBACK:
                logger.info("Using rule-based generation as final fallback...")
                return self._generate_rule_based_exercises(text, language, difficulty, count)
            else:
                logger.warning("All generation methods failed. Returning empty content to maintain quality.")
                return []
    
    def _generate_structured_exercises(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate exercises using structured JSON prompt."""
        
        prompt = f"""Generate exactly {count} educational exercises from the following text.

Text: {text[:1500]}...

Requirements:
- Difficulty: {difficulty}
- Language: {language}
- Mix of exercise types: fill-in-the-blank, true/false, short answer, matching
- Each exercise should test understanding of key concepts
- Provide clear instructions and expected answers

Return ONLY a valid JSON array with this exact format:
[
  {{
    "type": "fill_blank",
    "instruction": "Fill in the blank: The main concept discussed is _____.",
    "question": "The main concept discussed is _____.",
    "answer": "artificial intelligence",
    "difficulty": "{difficulty}"
  }},
  {{
    "type": "true_false",
    "instruction": "Determine if the statement is true or false.",
    "question": "AI can completely replace human teachers.",
    "answer": "false",
    "difficulty": "{difficulty}"
  }},
  {{
    "type": "short_answer",
    "instruction": "Answer the following question in 2-3 sentences.",
    "question": "What are the benefits of using AI in education?",
    "answer": "AI in education provides personalized learning, immediate feedback, and adaptive content delivery.",
    "difficulty": "{difficulty}"
  }},
  {{
    "type": "matching",
    "instruction": "Match the concepts with their definitions.",
    "concepts": ["Machine Learning", "Deep Learning", "Neural Networks"],
    "definitions": ["A subset of AI that learns from data", "Advanced ML using neural networks", "Computing systems inspired by brains"],
    "answer": [["Machine Learning", "A subset of AI that learns from data"], ["Deep Learning", "Advanced ML using neural networks"], ["Neural Networks", "Computing systems inspired by brains"]],
    "difficulty": "{difficulty}"
  }}
]

IMPORTANT: Return ONLY the JSON array, no additional text or explanations."""

        try:
            response = self.model_manager.generate_text(prompt, max_length=2500)
            
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
            json_str = re.sub(r',\s*]', ']', json_str)
            json_str = re.sub(r',\s*}', '}', json_str)
            
            try:
                exercises = json.loads(json_str)
                if isinstance(exercises, list):
                    logger.info(f"Successfully parsed {len(exercises)} exercises from JSON")
                    return exercises
                else:
                    logger.warning("Response is not a JSON array")
                    return []
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error in structured generation: {e}")
            return []
    
    def _generate_simple_exercises(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate exercises using simple format prompt."""
        
        prompt = f"""Create {count} educational exercises from this text:

{text[:1000]}...

Generate {count} exercises in this format:
Type: fill_blank
Instruction: Fill in the blank
Question: The main concept is _____.
Answer: artificial intelligence

Type: true_false
Instruction: Determine if true or false
Question: AI can replace teachers completely.
Answer: false

Type: short_answer
Instruction: Answer in 2-3 sentences
Question: What are the benefits of AI in education?
Answer: AI provides personalized learning and immediate feedback.

Make sure each exercise has clear type, instruction, question, and answer."""

        try:
            response = self.model_manager.generate_text(prompt, max_length=2000)
            
            if not response or not response.strip():
                return []
            
            # Parse simple format
            exercises = self._parse_simple_format(response, count)
            return exercises
            
        except Exception as e:
            logger.error(f"Error in simple generation: {e}")
            return []
    
    def _parse_simple_format(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse simple format content into exercises."""
        exercises = []
        
        # Split by exercise separators
        sections = re.split(r'(?:Type:|Exercise:)', content, flags=re.IGNORECASE)
        
        for section in sections:
            section = section.strip()
            if not section or len(exercises) >= expected_count:
                break
            
            # Extract exercise components
            exercise_type = ""
            instruction = ""
            question = ""
            answer = ""
            
            # Extract type
            type_match = re.search(r'^([a-zA-Z_]+)', section)
            if type_match:
                exercise_type = type_match.group(1).strip()
            
            # Extract instruction
            instruction_match = re.search(r'(?:Instruction:|Instruction)\s*(.+?)(?=Question:|Question|$)', section, re.DOTALL)
            if instruction_match:
                instruction = instruction_match.group(1).strip()
            
            # Extract question
            question_match = re.search(r'(?:Question:|Question)\s*(.+?)(?=Answer:|Answer|$)', section, re.DOTALL)
            if question_match:
                question = question_match.group(1).strip()
            
            # Extract answer
            answer_match = re.search(r'(?:Answer:|Answer)\s*(.+?)$', section, re.DOTALL)
            if answer_match:
                answer = answer_match.group(1).strip()
            
            # Validate and create exercise
            if exercise_type and question and answer:
                exercise = {
                    "type": exercise_type,
                    "instruction": instruction or f"Complete this {exercise_type} exercise.",
                    "question": question,
                    "answer": answer,
                    "difficulty": "beginner"
                }
                
                # Handle special cases for matching exercises
                if exercise_type == "matching":
                    exercise["concepts"] = ["Concept 1", "Concept 2", "Concept 3"]
                    exercise["definitions"] = ["Definition 1", "Definition 2", "Definition 3"]
                    exercise["answer"] = [["Concept 1", "Definition 1"], ["Concept 2", "Definition 2"], ["Concept 3", "Definition 3"]]
                
                exercises.append(exercise)
        
        logger.info(f"Parsed {len(exercises)} exercises from simple format")
        return exercises
    
    def _generate_rule_based_exercises(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate exercises using rule-based approach when AI fails."""
        logger.info("Using rule-based exercise generation as fallback")
        
        exercises = []
        
        # Extract sentences and key concepts
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        key_concepts = self._extract_key_concepts(text)
        
        # Create fill-in-the-blank exercises
        fill_blank_count = min(count//3, len(key_concepts))
        for i, concept in enumerate(key_concepts[:fill_blank_count]):
            if language == "si":
                instruction = "හිස් තැන පුරවන්න"
                question = f"මෙම විෂයයේ ප්‍රධාන සංකල්පය වන්නේ _____ ය."
                answer = concept
            elif language == "ta":
                instruction = "வெற்று இடத்தை நிரப்பவும்"
                question = f"இந்த பாடத்தின் முக்கிய கருத்து _____ ஆகும்."
                answer = concept
            else:
                instruction = "Fill in the blank"
                question = f"The main concept in this topic is _____."
                answer = concept
            
            exercises.append({
                "type": "fill_blank",
                "instruction": instruction,
                "question": question,
                "answer": answer,
                "difficulty": difficulty
            })
        
        # Create true/false exercises
        true_false_count = min(count//3, len(sentences))
        for i, sentence in enumerate(sentences[:true_false_count]):
            if language == "si":
                instruction = "සත්‍ය හෝ අසත්‍ය බව තීරණය කරන්න"
                question = f"මෙම ප්‍රකාශනය සත්‍යය: {sentence[:80]}..."
                answer = "true" if i % 2 == 0 else "false"
            elif language == "ta":
                instruction = "சரி அல்லது தவறு என தீர்மானிக்கவும்"
                question = f"இந்த கூற்று சரி: {sentence[:80]}..."
                answer = "true" if i % 2 == 0 else "false"
            else:
                instruction = "Determine if true or false"
                question = f"This statement is true: {sentence[:80]}..."
                answer = "true" if i % 2 == 0 else "false"
            
            exercises.append({
                "type": "true_false",
                "instruction": instruction,
                "question": question,
                "answer": answer,
                "difficulty": difficulty
            })
        
        # Create short answer exercises
        remaining_count = count - len(exercises)
        for i in range(remaining_count):
            if language == "si":
                instruction = "2-3 වාක්‍ය තුළ පිළිතුරු දෙන්න"
                question = "මෙම විෂයයේ ප්‍රධාන සංකල්ප මොනවාද?"
                answer = "මෙම විෂයයේ ප්‍රධාන සංකල්ප සහ මූලධර්ම ඇතුළත් වේ."
            elif language == "ta":
                instruction = "2-3 வாக்கியங்களில் பதிலளிக்கவும்"
                question = "இந்த பாடத்தின் முக்கிய கருத்துக்கள் என்ன?"
                answer = "இந்த பாடத்தின் முக்கிய கருத்துக்கள் மற்றும் கொள்கைகள் அடங்கும்."
            else:
                instruction = "Answer in 2-3 sentences"
                question = "What are the main concepts in this topic?"
                answer = "This topic covers various important concepts and principles that are fundamental to understanding the subject matter."
            
            exercises.append({
                "type": "short_answer",
                "instruction": instruction,
                "question": question,
                "answer": answer,
                "difficulty": difficulty
            })
        
        logger.info(f"Rule-based generation created {len(exercises)} exercises")
        return exercises[:count]
    
    def _clean_and_validate_exercises(self, exercises: List[Dict[str, Any]], target_count: int) -> List[Dict[str, Any]]:
        """Clean and validate exercises."""
        cleaned_exercises = []
        
        for exercise in exercises:
            exercise_type = exercise.get('type', '').strip()
            instruction = exercise.get('instruction', '').strip()
            question = exercise.get('question', '').strip()
            answer = exercise.get('answer', '')
            
            # Clean the text
            instruction = self._clean_text(instruction)
            question = self._clean_text(question)
            
            # Handle different answer types
            if isinstance(answer, str):
                answer = self._clean_text(answer)
            elif isinstance(answer, list):
                # For matching exercises
                answer = [self._clean_text(str(item)) for item in answer if item]
            
            # Validate quality
            if self._is_valid_exercise(exercise_type, instruction, question, answer):
                cleaned_exercise = {
                    "type": exercise_type,
                    "instruction": instruction,
                    "question": question,
                    "answer": answer,
                    "difficulty": exercise.get('difficulty', 'beginner')
                }
                
                # Add special fields for matching exercises
                if exercise_type == "matching":
                    concepts = exercise.get('concepts', [])
                    definitions = exercise.get('definitions', [])
                    if concepts and definitions:
                        cleaned_exercise["concepts"] = [self._clean_text(str(c)) for c in concepts]
                        cleaned_exercise["definitions"] = [self._clean_text(str(d)) for d in definitions]
                
                cleaned_exercises.append(cleaned_exercise)
            
            if len(cleaned_exercises) >= target_count:
                break
        
        return cleaned_exercises
    
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
        text = re.sub(r'^(Type:|Instruction:|Question:|Answer:)\s*', '', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Ensure proper sentence endings
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _is_valid_exercise(self, exercise_type: str, instruction: str, question: str, answer: Any) -> bool:
        """Check if an exercise meets quality standards."""
        if not exercise_type or not instruction or not question:
            return False
        
        if len(instruction) < 5 or len(question) < 5:
            return False
        
        # Validate answer based on type
        if exercise_type == "fill_blank":
            if not isinstance(answer, str) or len(answer) < 2:
                return False
        elif exercise_type == "true_false":
            if not isinstance(answer, str) or answer.lower() not in ["true", "false"]:
                return False
        elif exercise_type == "short_answer":
            if not isinstance(answer, str) or len(answer) < 10:
                return False
        elif exercise_type == "matching":
            if not isinstance(answer, list) or len(answer) < 2:
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
