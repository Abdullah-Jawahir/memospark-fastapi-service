import random
from typing import List, Dict, Any
from ..utils import extract_key_concepts
from ..logger import logger
from ..models import model_manager
from ..config import GENERATION_LIMITS

class ExerciseGenerator:
    """Generates various types of exercises from text content."""
    
    def generate_exercises(self, text: str, language: str = "en", difficulty: str = "beginner") -> List[Dict[str, Any]]:
        """Generate various types of exercises from text using the model."""
        try:
            text = text.strip()
            if len(text) < 50:
                return []
            exercises = []
            # 1. Fill-in-the-blank
            fill_prompt = (
                f"Generate {GENERATION_LIMITS['exercises']//2} fill-in-the-blank exercises from the following text. "
                "Each should have a sentence with a blank (______) and the correct answer.\nText:\n"
                f"{text[:1200]}\nFormat: Sentence with blank | Answer"
            )
            fill_output = model_manager.generate_text(fill_prompt, max_length=600)
            exercises.extend(self._parse_fill_blank(fill_output, difficulty, language))
            # 2. True/False
            tf_prompt = (
                f"Generate {GENERATION_LIMITS['exercises']//2} true/false statements from the following text. "
                "Each should be a factual statement and its answer (True/False).\nText:\n"
                f"{text[:1200]}\nFormat: Statement | Answer"
            )
            tf_output = model_manager.generate_text(tf_prompt, max_length=600)
            exercises.extend(self._parse_true_false(tf_output, difficulty, language))
            # 3. Short Answer
            sa_prompt = (
                f"Generate 2 short answer questions from the following text. "
                "Each should have a question and a concise answer.\nText:\n"
                f"{text[:1200]}\nFormat: Question | Answer"
            )
            sa_output = model_manager.generate_text(sa_prompt, max_length=400)
            exercises.extend(self._parse_short_answer(sa_output, difficulty, language))
            # 4. Matching
            match_prompt = (
                "Generate a matching exercise from the following text. "
                "List 4 concepts and their definitions.\nText:\n"
                f"{text[:1200]}\nFormat: Concept | Definition (one per line)"
            )
            match_output = model_manager.generate_text(match_prompt, max_length=400)
            match_ex = self._parse_matching(match_output, difficulty, language)
            if match_ex:
                exercises.append(match_ex)
            # Fallback to rule-based if all fail
            if not exercises:
                return self._generate_rule_based_exercises(text, language, difficulty)
            return exercises[:GENERATION_LIMITS['exercises']]
        except Exception as e:
            logger.error(f"Error generating exercises: {str(e)}")
            return self._generate_rule_based_exercises(text, language, difficulty)

    def _parse_fill_blank(self, output: str, difficulty: str, language: str):
        exercises = []
        for line in output.split('\n'):
            if '|' in line:
                sent, ans = line.split('|', 1)
                sent = sent.strip().replace('_____', '______')
                ans = ans.strip()
                # Clean answer
                ans = self._clean_answer(ans)
                if '______' in sent and len(ans) > 1:
                    exercises.append({
                        'type': 'fill_blank',
                        'instruction': self._get_instruction('fill_blank', language),
                        'exercise_text': sent,
                        'answer': ans,
                        'difficulty': difficulty
                    })
        return exercises

    def _parse_true_false(self, output: str, difficulty: str, language: str):
        exercises = []
        for line in output.split('\n'):
            if '|' in line:
                sent, ans = line.split('|', 1)
                sent = sent.strip()
                ans = ans.strip()
                ans = self._clean_answer(ans)
                if ans.lower() in ['true', 'false']:
                    exercises.append({
                        'type': 'true_false',
                        'instruction': self._get_instruction('true_false', language),
                        'exercise_text': sent,
                        'answer': ans.capitalize(),
                        'difficulty': difficulty
                    })
        return exercises

    def _parse_short_answer(self, output: str, difficulty: str, language: str):
        exercises = []
        for line in output.split('\n'):
            if '|' in line:
                q, ans = line.split('|', 1)
                q = q.strip()
                ans = ans.strip()
                ans = self._clean_answer(ans)
                if len(q) > 10 and len(ans) > 1:
                    exercises.append({
                        'type': 'short_answer',
                        'instruction': self._get_instruction('short_answer', language),
                        'exercise_text': q,
                        'answer': ans,
                        'difficulty': difficulty
                    })
        return exercises

    def _parse_matching(self, output: str, difficulty: str, language: str):
        concepts = []
        definitions = []
        answer = {}
        for line in output.split('\n'):
            if '|' in line:
                concept, definition = line.split('|', 1)
                concept = concept.strip()
                definition = definition.strip()
                definition = self._clean_answer(definition)
                if len(concept) > 1 and len(definition) > 5:
                    concepts.append(concept)
                    definitions.append(definition)
                    answer[concept] = definition
        if len(concepts) >= 2:
            return {
                'type': 'matching',
                'instruction': self._get_instruction('matching', language),
                'concepts': concepts,
                'definitions': definitions,
                'answer': answer,
                'difficulty': difficulty
            }
        return None

    def _clean_answer(self, ans: str) -> str:
        import re
        ans = re.sub(r'^[A-D]\)\s*', '', ans)
        ans = re.sub(r'\*\*|\*', '', ans).strip()
        ans = re.split(r'---|These questions|Let me know|\\n', ans)[0].strip()
        ans = re.sub(r'^(Answer:|Correct answer:|Your answer:)', '', ans, flags=re.IGNORECASE).strip()
        return ans

    def _get_instruction(self, typ, language):
        if typ == 'fill_blank':
            if language == 'si':
                return "පහත වාක්‍යයේ හිස් තැන පුරවන්න:"
            elif language == 'ta':
                return "பின்வரும் வாக்கியத்தில் காலி இடத்தை நிரப்பவும்:"
            else:
                return "Fill in the blank in the following sentence:"
        elif typ == 'true_false':
            if language == 'si':
                return "පහත ප්‍රකාශනය සත්‍ය ද අසත්‍ය ද?"
            elif language == 'ta':
                return "பின்வரும் கூற்று உண்மையா பொய்யா?"
            else:
                return "Is the following statement true or false?"
        elif typ == 'short_answer':
            return "Answer the following question:"
        elif typ == 'matching':
            if language == 'si':
                return "පහත සංකල්ප සහ අර්ථ දැක්වීම් ගලපන්න:"
            elif language == 'ta':
                return "பின்வரும் கருத்துகள் மற்றும் வரையறைகளை பொருத்தவும்:"
            else:
                return "Match the following concepts with their definitions:"
        return ""

    def _generate_rule_based_exercises(self, text: str, language: str, difficulty: str):
        # fallback to old rule-based logic if model fails
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        key_concepts = extract_key_concepts(text)
        exercises = []
        exercises.extend(self._generate_fill_blank_exercises(sentences, language, difficulty))
        exercises.extend(self._generate_true_false_exercises(sentences, language, difficulty))
        exercises.extend(self._generate_short_answer_exercises(key_concepts, sentences, language, difficulty))
        matching_exercise = self._generate_matching_exercise(key_concepts, sentences, language, difficulty)
        if matching_exercise:
            exercises.append(matching_exercise)
        return exercises
    
    def _generate_fill_blank_exercises(self, sentences: List[str], language: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate fill in the blank exercises."""
        exercises = []
        
        for i, sentence in enumerate(sentences[:3]):
            try:
                words = sentence.split()
                if len(words) > 8:
                    # Remove important words (nouns, adjectives)
                    important_words = [w for w in words if len(w) > 4 and w.isalpha()]
                    if important_words:
                        word_to_blank = random.choice(important_words)
                        exercise_text = sentence.replace(word_to_blank, "______")
                        # Ensure the blank is not at the very start or end
                        if exercise_text.startswith('______') or exercise_text.endswith('______'):
                            continue
                        # Ensure the answer is not truncated
                        if len(word_to_blank) < 2 or word_to_blank[-1] in ',;:':
                            continue
                        if language == "si":
                            instruction = "පහත වාක්‍යයේ හිස් තැන පුරවන්න:"
                        elif language == "ta":
                            instruction = "பின்வரும் வாக்கியத்தில் காலி இடத்தை நிரப்பவும்:"
                        else:
                            instruction = "Fill in the blank in the following sentence:"
                        
                        exercises.append({
                            "type": "fill_blank",
                            "instruction": instruction,
                            "exercise_text": exercise_text,
                            "answer": word_to_blank,
                            "difficulty": difficulty
                        })
            except Exception as e:
                continue
        
        return exercises
    
    def _generate_true_false_exercises(self, sentences: List[str], language: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate true/false exercises."""
        exercises = []
        
        for i, sentence in enumerate(sentences[3:6]):
            try:
                # Only use sentences that are likely to be factual and complete
                if len(sentence) < 20 or sentence[-1] in ',;:':
                    continue
                if language == "si":
                    instruction = "පහත ප්‍රකාශනය සත්‍ය ද අසත්‍ය ද?"
                elif language == "ta":
                    instruction = "பின்வரும் கூற்று உண்மையா பொய்யா?"
                else:
                    instruction = "Is the following statement true or false?"
                
                exercises.append({
                    "type": "true_false",
                    "instruction": instruction,
                    "exercise_text": sentence,
                    "answer": "True",  # Assuming text content is factual
                    "difficulty": difficulty
                })
            except Exception as e:
                continue
        
        return exercises
    
    def _generate_short_answer_exercises(self, key_concepts: List[str], sentences: List[str], language: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate short answer exercises."""
        exercises = []
        
        for concept in key_concepts[:2]:
            try:
                if language == "si":
                    question = f"'{concept}' ගැන කෙටියෙන් පැහැදිලි කරන්න."
                elif language == "ta":
                    question = f"'{concept}' பற்றி சுருக்கமாக விளக்கவும்."
                else:
                    question = f"Briefly explain '{concept}'."
                
                # Find relevant sentence containing the concept, ensure it's not truncated
                relevant_sentence = next((s for s in sentences if concept.lower() in s.lower() and len(s) > 20 and s[-1] not in ',;:'), None)
                if not relevant_sentence:
                    continue
                exercises.append({
                    "type": "short_answer",
                    "instruction": "Answer the following question:",
                    "exercise_text": question,
                    "answer": relevant_sentence,
                    "difficulty": difficulty
                })
            except Exception as e:
                continue
        
        return exercises
    
    def _generate_matching_exercise(self, key_concepts: List[str], sentences: List[str], language: str, difficulty: str) -> Dict[str, Any]:
        """Generate matching exercise."""
        try:
            if len(key_concepts) < 4:
                return None
            
            # Create matching pairs
            concepts_subset = key_concepts[:4]
            definitions = []
            
            for concept in concepts_subset:
                # Find sentence containing the concept, ensure it's not truncated
                definition = next((s for s in sentences if concept.lower() in s.lower() and len(s) > 20 and s[-1] not in ',;:'), f"Related to {concept}")
                definitions.append(definition[:100] + "..." if len(definition) > 100 else definition)
            
            if language == "si":
                instruction = "පහත සංකල්ප සහ අර්ථ දැක්වීම් ගලපන්න:"
            elif language == "ta":
                instruction = "பின்வரும் கருத்துகள் மற்றும் வரையறைகளை பொருத்தவும்:"
            else:
                instruction = "Match the following concepts with their definitions:"
            
            return {
                "type": "matching",
                "instruction": instruction,
                "concepts": concepts_subset,
                "definitions": definitions,
                "answer": dict(zip(concepts_subset, definitions)),
                "difficulty": difficulty
            }
        except Exception as e:
            logger.warning(f"Error creating matching exercise: {str(e)}")
            return None 