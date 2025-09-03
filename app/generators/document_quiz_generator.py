import re
import json
from typing import List, Dict, Any
from ..models import model_manager
from ..logger import logger

class DocumentQuizGenerator:
    """Generates quiz questions from document text content with robust JSON handling and fallbacks."""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def generate_quizzes(self, text: str, language: str = "en", difficulty: str = "beginner", count: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions from document text with multiple fallback strategies."""
        try:
            logger.info(f"Starting document quiz generation: text_length={len(text)}, language={language}, difficulty={difficulty}, count={count}")
            
            text = text.strip()
            if len(text) < 50:
                logger.warning("Text is too short to generate meaningful quiz questions")
                return []
            
            # Try structured JSON generation first
            quizzes = self._generate_structured_quizzes(text, language, difficulty, count)
            
            # If that fails, try simple format generation
            if not quizzes:
                logger.info("Structured generation failed, trying simple format generation...")
                quizzes = self._generate_simple_quizzes(text, language, difficulty, count)
            
            # If still no quizzes, use rule-based generation
            if not quizzes:
                logger.info("Simple generation failed, using rule-based generation...")
                quizzes = self._generate_rule_based_quizzes(text, language, difficulty, count)
            
            # Clean and validate quizzes
            cleaned_quizzes = self._clean_and_validate_quizzes(quizzes, count)
            
            logger.info(f"Generated {len(cleaned_quizzes)} cleaned quiz questions")
            return cleaned_quizzes
            
        except Exception as e:
            logger.error(f"Error generating quiz questions: {str(e)}")
            logger.info("Falling back to rule-based quiz generation...")
            return self._generate_rule_based_quizzes(text, language, difficulty, count)
    
    def _generate_structured_quizzes(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate quiz questions using structured JSON prompt."""
        
        prompt = f"""Generate exactly {count} multiple choice quiz questions from the following text.

Text: {text[:1500]}...

Requirements:
- Difficulty: {difficulty}
- Language: {language}
- Format: Each question must have 4 options (A, B, C, D) and the correct answer
- Questions should test understanding of key concepts
- All options should be plausible but only one correct

Return ONLY a valid JSON array with this exact format:
[
  {{
    "question": "What is the main concept discussed in this text?",
    "options": [
      "Option A description",
      "Option B description", 
      "Option C description",
      "Option D description"
    ],
    "answer": "Option A description",
    "type": "Multiple Choice",
    "difficulty": "{difficulty}"
  }},
  {{
    "question": "How does this concept work?",
    "options": [
      "Option A description",
      "Option B description",
      "Option C description", 
      "Option D description"
    ],
    "answer": "Option C description",
    "type": "Multiple Choice",
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
                quizzes = json.loads(json_str)
                if isinstance(quizzes, list):
                    logger.info(f"Successfully parsed {len(quizzes)} quiz questions from JSON")
                    return quizzes
                else:
                    logger.warning("Response is not a JSON array")
                    return []
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error in structured generation: {e}")
            return []
    
    def _generate_simple_quizzes(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate quiz questions using simple format prompt."""
        
        prompt = f"""Create {count} multiple choice quiz questions from this text:

{text[:1000]}...

Generate {count} questions in this format:
Q: [Question about the topic]
A) [Option A]
B) [Option B] 
C) [Option C]
D) [Option D]
Answer: [Correct option letter]

Q: [Another question]
A) [Option A]
B) [Option B]
C) [Option C] 
D) [Option D]
Answer: [Correct option letter]

Make sure each question has exactly 4 options and a clear answer."""

        try:
            response = self.model_manager.generate_text(prompt, max_length=2000)
            
            if not response or not response.strip():
                return []
            
            # Parse simple format
            quizzes = self._parse_simple_format(response, count)
            return quizzes
            
        except Exception as e:
            logger.error(f"Error in simple generation: {e}")
            return []
    
    def _parse_simple_format(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse simple Q&A format content into quiz questions."""
        quizzes = []
        
        # Split by Q: or Question:
        sections = re.split(r'(?:Q:|Question:)', content, flags=re.IGNORECASE)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Look for options and answer
            if len(quizzes) >= expected_count:
                break
                
            # Extract question (everything before first option)
            question_match = re.search(r'^(.+?)(?=A\)|A:|A\.)', section, re.DOTALL)
            if not question_match:
                continue
                
            question = question_match.group(1).strip()
            
            # Extract options
            options = []
            option_patterns = [
                r'(?:A\)|A:|A\.)\s*(.+?)(?=B\)|B:|B\.|Answer:|$)',
                r'(?:B\)|B:|B\.)\s*(.+?)(?=C\)|C:|C\.|Answer:|$)',
                r'(?:C\)|C:|C\.)\s*(.+?)(?=D\)|D:|D\.|Answer:|$)',
                r'(?:D\)|D:|D\.)\s*(.+?)(?=Answer:|$)'
            ]
            
            for pattern in option_patterns:
                match = re.search(pattern, section, re.DOTALL)
                if match:
                    option = match.group(1).strip()
                    if option and len(option) > 2:
                        options.append(option)
            
            # Extract answer
            answer_match = re.search(r'(?:Answer:|Answer)\s*([A-D])', section, re.IGNORECASE)
            if answer_match:
                answer_letter = answer_match.group(1).upper()
                answer_index = ord(answer_letter) - ord('A')
                
                if 0 <= answer_index < len(options) and len(options) == 4:
                    quizzes.append({
                        "question": question,
                        "options": options,
                        "answer": options[answer_index],
                        "type": "Multiple Choice",
                        "difficulty": "beginner"
                    })
        
        logger.info(f"Parsed {len(quizzes)} quiz questions from simple format")
        return quizzes
    
    def _generate_rule_based_quizzes(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate quiz questions using rule-based approach when AI fails."""
        logger.info("Using rule-based quiz generation as fallback")
        
        quizzes = []
        
        # Extract sentences and key concepts
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        key_concepts = self._extract_key_concepts(text)
        
        # Create concept-based questions
        for i, concept in enumerate(key_concepts[:min(count//2, len(key_concepts))]):
            if language == "si":
                question = f"'{concept}' යන්නෙන් අදහස් කරන්නේ කුමක්ද?"
                options = [
                    f"{concept} ගැන විස්තරයක්",
                    f"{concept} ගැන තොරතුරක්",
                    f"{concept} ගැන පැහැදිලි කිරීමක්",
                    f"{concept} ගැන විස්තරයක් නොවේ"
                ]
            elif language == "ta":
                question = f"'{concept}' என்பதன் பொருள் என்ன?"
                options = [
                    f"{concept} பற்றிய விளக்கம்",
                    f"{concept} பற்றிய தகவல்",
                    f"{concept} பற்றிய விளக்கம்",
                    f"{concept} பற்றிய விளக்கம் அல்ல"
                ]
            else:
                question = f"What is '{concept}'?"
                options = [
                    f"A key concept in this topic",
                    f"An important principle",
                    f"A fundamental theory",
                    f"None of the above"
                ]
            
            quizzes.append({
                "question": question,
                "options": options,
                "answer": options[0],  # First option is usually correct
                "type": "Multiple Choice",
                "difficulty": difficulty
            })
        
        # Generate sentence-based questions
        remaining_count = count - len(quizzes)
        for i, sentence in enumerate(sentences[:remaining_count]):
            if language == "si":
                question = f"මෙම කරුණ ගැන කුමක් කිව හැකිද: {sentence[:80]}...?"
                options = [
                    "මෙය වැදගත් කරුණකි",
                    "මෙය අවශ්‍ය නැත",
                    "මෙය ප්‍රශ්නයකි",
                    "මෙය පිළිතුරකි"
                ]
            elif language == "ta":
                question = f"இந்த விஷயத்தைப் பற்றி என்ன சொல்லலாம்: {sentence[:80]}...?"
                options = [
                    "இது முக்கியமான விஷயம்",
                    "இது தேவையில்லை",
                    "இது கேள்வி",
                    "இது பதில்"
                ]
            else:
                question = f"What can you tell me about: {sentence[:80]}...?"
                options = [
                    "This is an important point",
                    "This is not relevant",
                    "This is a question",
                    "This is an answer"
                ]
            
            quizzes.append({
                "question": question,
                "options": options,
                "answer": options[0],
                "type": "Multiple Choice",
                "difficulty": difficulty
            })
        
        # Fill remaining with generic questions
        while len(quizzes) < count:
            if language == "si":
                question = "මෙම විෂයයේ ප්‍රධාන සංකල්ප මොනවාද?"
                options = [
                    "විවිධ වැදගත් සංකල්ප සහ මූලධර්ම",
                    "එක් සංකල්පයක් පමණි",
                    "කිසිවක් නැත",
                    "සියල්ලම"
                ]
            elif language == "ta":
                question = "இந்த பாடத்தின் முக்கிய கருத்துக்கள் என்ன?"
                options = [
                    "பல்வேறு முக்கிய கருத்துக்கள் மற்றும் கொள்கைகள்",
                    "ஒரு கருத்து மட்டும்",
                    "எதுவும் இல்லை",
                    "அனைத்தும்"
                ]
            else:
                question = "What are the main concepts in this topic?"
                options = [
                    "Various important concepts and principles",
                    "Only one concept",
                    "Nothing specific",
                    "All of the above"
                ]
            
            quizzes.append({
                "question": question,
                "options": options,
                "answer": options[0],
                "type": "Multiple Choice",
                "difficulty": difficulty
            })
        
        logger.info(f"Rule-based generation created {len(quizzes)} quiz questions")
        return quizzes[:count]
    
    def _clean_and_validate_quizzes(self, quizzes: List[Dict[str, Any]], target_count: int) -> List[Dict[str, Any]]:
        """Clean and validate quiz questions."""
        cleaned_quizzes = []
        
        for quiz in quizzes:
            question = quiz.get('question', '').strip()
            options = quiz.get('options', [])
            answer = quiz.get('answer', '').strip()
            
            # Clean the question
            question = self._clean_text(question)
            
            # Clean options
            cleaned_options = []
            for option in options:
                if isinstance(option, str):
                    cleaned_option = self._clean_text(option)
                    if cleaned_option and len(cleaned_option) > 2:
                        cleaned_options.append(cleaned_option)
            
            # Clean answer
            answer = self._clean_text(answer)
            
            # Validate quality
            if self._is_valid_quiz(question, cleaned_options, answer):
                cleaned_quizzes.append({
                    "question": question,
                    "options": cleaned_options,
                    "answer": answer,
                    "type": "Multiple Choice",
                    "difficulty": quiz.get('difficulty', 'beginner')
                })
            
            if len(cleaned_quizzes) >= target_count:
                break
        
        return cleaned_quizzes
    
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
    
    def _is_valid_quiz(self, question: str, options: List[str], answer: str) -> bool:
        """Check if a quiz question meets quality standards."""
        if len(question) < 10:
            return False
        
        if len(options) != 4:
            return False
        
        for option in options:
            if len(option) < 2:
                return False
        
        if not answer or answer not in options:
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
