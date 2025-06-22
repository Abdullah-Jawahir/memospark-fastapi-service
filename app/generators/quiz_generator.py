import random
import re
from typing import List, Dict, Any
from ..models import model_manager
from ..utils import extract_key_concepts
from ..config import LANGUAGE_PROMPTS, GENERATION_LIMITS
from ..logger import logger

class QuizGenerator:
    """Generates multiple choice quizzes from text content with meaningful questions."""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def generate_quizzes(self, text: str, language: str = "en", difficulty: str = "beginner") -> List[Dict[str, Any]]:
        """Generate meaningful multiple choice quizzes from text content."""
        try:
            text = text.strip()
            if len(text) < 200:
                return []
            
            # Extract key concepts and important information
            key_concepts = extract_key_concepts(text)
            
            # Generate quiz content using AI
            quiz_data = self._generate_quiz_content(text, key_concepts, language, difficulty)
            
            if not quiz_data:
                return []
            
            quizzes = []
            for quiz_item in quiz_data[:GENERATION_LIMITS["quizzes"]]:
                try:
                    quiz = {
                        "question": quiz_item["question"],
                        "options": quiz_item["options"],
                        "answer": quiz_item["correct_answer"],
                        "correct_answer_option": quiz_item["correct_answer"],
                        "type": "quiz",
                        "difficulty": difficulty
                    }
                    quizzes.append(quiz)
                except Exception as e:
                    logger.warning(f"Error processing quiz item: {str(e)}")
                    continue
            
            logger.info(f"Generated {len(quizzes)} meaningful quizzes")
            return quizzes
            
        except Exception as e:
            logger.error(f"Error generating quizzes: {str(e)}")
            return []
    
    def _generate_quiz_content(self, text: str, key_concepts: List[str], language: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate quiz questions and answers using AI model."""
        try:
            # Create a comprehensive prompt for quiz generation
            prompt = self._create_quiz_generation_prompt(text, key_concepts, language, difficulty)
            
            # Generate quiz content
            generated_content = self.model_manager.generate_text(prompt, max_length=800)
            
            # Parse the generated content
            quizzes = self._parse_generated_quizzes(generated_content, language)
            
            return quizzes
            
        except Exception as e:
            logger.error(f"Error in quiz content generation: {str(e)}")
            return []
    
    def _create_quiz_generation_prompt(self, text: str, key_concepts: List[str], language: str, difficulty: str) -> str:
        """Create a comprehensive prompt for generating meaningful quizzes."""
        
        if language == "si":
            return f"""පහත පෙළෙන් අර්ථවත් බහුවරණ ප්‍රශ්න 5ක් සාදන්න. එක් එක් ප්‍රශ්නයට විකල්ප 4ක් තිබිය යුතුය.

පෙළ:
{text[:1000]}

ප්‍රධාන සංකල්ප:
{', '.join(key_concepts[:10])}

උපදෙස්:
1. ප්‍රශ්න අර්ථවත් විය යුතුය
2. පිළිතුරු පෙළෙන් ගත හැකි නමුත් ප්‍රශ්න ආකෘතියෙන් නොවිය යුතුය
3. විකල්ප සියල්ලම තාර්කික විය යුතුය
4. එක් විකල්පයක් පමණක් නිවැරදි විය යුතුය

ආකෘතිය:
Q1: [ප්‍රශ්නය]
A) [විකල්පය]
B) [විකල්පය]
C) [විකල්පය]
D) [විකල්පය]
ANSWER: [නිවැරදි විකල්පය]"""
        
        elif language == "ta":
            return f"""கீழே உள்ள உரையிலிருந்து அர்த்தமுள்ள பல தேர்வு கேள்விகள் 5ஐ உருவாக்கவும். ஒவ்வொரு கேள்விக்கும் 4 விருப்பங்கள் இருக்க வேண்டும்.

உரை:
{text[:1000]}

முக்கிய கருத்துக்கள்:
{', '.join(key_concepts[:10])}

வழிமுறைகள்:
1. கேள்விகள் அர்த்தமுள்ளதாக இருக்க வேண்டும்
2. பதில்கள் உரையிலிருந்து எடுக்கப்படலாம் ஆனால் கேள்விகள் வடிவத்தில் இருக்கக்கூடாது
3. அனைத்து விருப்பங்களும் தர்க்கரீதியாக இருக்க வேண்டும்
4. ஒரு விருப்பம் மட்டும் சரியாக இருக்க வேண்டும்

வடிவம்:
Q1: [கேள்வி]
A) [விருப்பம்]
B) [விருப்பம்]
C) [விருப்பம்]
D) [விருப்பம்]
ANSWER: [சரியான விருப்பம்]"""
        
        else:
            return f"""Generate 5 meaningful multiple choice questions from the following text. Each question should have 4 options.

Text:
{text[:1000]}

Key concepts:
{', '.join(key_concepts[:10])}

Instructions:
1. Questions should be meaningful and test understanding
2. Answers can be derived from the text but questions should not be exact sentences from the text
3. All options should be logical and plausible
4. Only one option should be correct
5. Questions should test comprehension, not just memorization

Format:
Q1: [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
ANSWER: [Correct option]

Q2: [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
ANSWER: [Correct option]

Continue with Q3, Q4, Q5..."""
    
    def _parse_generated_quizzes(self, generated_content: str, language: str) -> List[Dict[str, Any]]:
        """Parse the generated quiz content into structured format."""
        quizzes = []
        
        try:
            # Split by question patterns
            if language == "si":
                question_pattern = r'Q(\d+):\s*(.+?)\s*A\)\s*(.+?)\s*B\)\s*(.+?)\s*C\)\s*(.+?)\s*D\)\s*(.+?)\s*ANSWER:\s*(.+?)(?=Q\d+:|$)'
            elif language == "ta":
                question_pattern = r'Q(\d+):\s*(.+?)\s*A\)\s*(.+?)\s*B\)\s*(.+?)\s*C\)\s*(.+?)\s*D\)\s*(.+?)\s*ANSWER:\s*(.+?)(?=Q\d+:|$)'
            else:
                question_pattern = r'Q(\d+):\s*(.+?)\s*A\)\s*(.+?)\s*B\)\s*(.+?)\s*C\)\s*(.+?)\s*D\)\s*(.+?)\s*ANSWER:\s*(.+?)(?=Q\d+:|$)'
            
            matches = re.findall(question_pattern, generated_content, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                try:
                    question_num, question, option_a, option_b, option_c, option_d, correct_answer = match
                    
                    # Clean up the text
                    question = question.strip()
                    options = [
                        option_a.strip(),
                        option_b.strip(),
                        option_c.strip(),
                        option_d.strip()
                    ]
                    correct_answer = correct_answer.strip()

                    # Remove option letters (e.g., 'A)', 'B)', etc.) at the start
                    correct_answer = re.sub(r'^[A-D]\)\s*', '', correct_answer)
                    # Remove Markdown bold/italics and extra asterisks
                    correct_answer = re.sub(r'\*\*|\*', '', correct_answer).strip()
                    # Remove any trailing commentary after '---' or similar
                    correct_answer = re.split(r'---|These questions|Let me know', correct_answer)[0].strip()
                    
                    # Validate that we have meaningful content
                    if (len(question) > 10 and 
                        all(len(opt) > 5 for opt in options) and 
                        len(correct_answer) > 1):
                        
                        quizzes.append({
                            "question": question,
                            "options": options,
                            "correct_answer": correct_answer
                        })
                
                except Exception as e:
                    logger.warning(f"Error parsing quiz match: {str(e)}")
                    continue
            
            # If parsing failed, try alternative parsing
            if not quizzes:
                quizzes = self._fallback_parsing(generated_content, language)
            
            return quizzes
            
        except Exception as e:
            logger.error(f"Error parsing generated quizzes: {str(e)}")
            return self._fallback_parsing(generated_content, language)
    
    def _fallback_parsing(self, generated_content: str, language: str) -> List[Dict[str, Any]]:
        """Fallback parsing method if the main parsing fails."""
        quizzes = []
        
        try:
            # Split by lines and look for question patterns
            lines = generated_content.split('\n')
            current_question = None
            current_options = []
            current_answer = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for question start
                if line.startswith('Q') and ':' in line:
                    # Save previous question if exists
                    if current_question and current_options and current_answer:
                        # Clean answer
                        ca = current_answer.strip()
                        ca = re.sub(r'^[A-D]\)\s*', '', ca)
                        ca = re.sub(r'\*\*|\*', '', ca).strip()
                        ca = re.split(r'---|These questions|Let me know', ca)[0].strip()
                        quizzes.append({
                            "question": current_question,
                            "options": current_options,
                            "correct_answer": ca
                        })
                    
                    # Start new question
                    current_question = line.split(':', 1)[1].strip()
                    current_options = []
                    current_answer = None
                
                # Check for options
                elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                    option = line.split(')', 1)[1].strip()
                    current_options.append(option)
                
                # Check for answer
                elif line.startswith('ANSWER:'):
                    current_answer = line.split(':', 1)[1].strip()
            
            # Add the last question
            if current_question and current_options and current_answer:
                ca = current_answer.strip()
                ca = re.sub(r'^[A-D]\)\s*', '', ca)
                ca = re.sub(r'\*\*|\*', '', ca).strip()
                ca = re.split(r'---|These questions|Let me know', ca)[0].strip()
                quizzes.append({
                    "question": current_question,
                    "options": current_options,
                    "correct_answer": ca
                })
            
            return quizzes
        
        except Exception as e:
            logger.error(f"Error in fallback parsing: {str(e)}")
            return [] 