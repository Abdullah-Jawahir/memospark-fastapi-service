import random
from typing import List, Dict, Any
from ..utils import extract_key_concepts
from ..logger import logger

class ExerciseGenerator:
    """Generates various types of exercises from text content."""
    
    def generate_exercises(self, text: str, language: str = "en", difficulty: str = "beginner") -> List[Dict[str, Any]]:
        """Generate various types of exercises from text."""
        try:
            text = text.strip()
            if len(text) < 50:
                return []
            
            exercises = []
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
            key_concepts = extract_key_concepts(text)
            
            # Exercise Type 1: Fill in the blanks
            exercises.extend(self._generate_fill_blank_exercises(sentences, language, difficulty))
            
            # Exercise Type 2: True/False
            exercises.extend(self._generate_true_false_exercises(sentences, language, difficulty))
            
            # Exercise Type 3: Short Answer
            exercises.extend(self._generate_short_answer_exercises(key_concepts, sentences, language, difficulty))
            
            # Exercise Type 4: Matching
            matching_exercise = self._generate_matching_exercise(key_concepts, sentences, language, difficulty)
            if matching_exercise:
                exercises.append(matching_exercise)
            
            logger.info(f"Generated {len(exercises)} exercises")
            return exercises
            
        except Exception as e:
            logger.error(f"Error generating exercises: {str(e)}")
            return []
    
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
                        
                        if language == "si":
                            instruction = "පහත වාක්‍යයේ හිස් තැන පුරවන්න:"
                        elif language == "ta":
                            instruction = "பின்வரும் வாக்்யத்தில் கா்லி இடத்தை நிரப்பவும்:"
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
                
                # Find relevant sentence containing the concept
                relevant_sentence = next((s for s in sentences if concept.lower() in s.lower()), sentences[0])
                
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
                # Find sentence containing the concept
                definition = next((s for s in sentences if concept.lower() in s.lower()), f"Related to {concept}")
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