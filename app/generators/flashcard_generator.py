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
            logger.info(f"Starting flashcard generation: text_length={len(text)}, language={language}, difficulty={difficulty}, count={count}")
            
            text = text.strip()
            if len(text) < 50:
                logger.warning("Text is too short to generate meaningful flashcards")
                return []
            
            # Generate all flashcards in a single API call
            logger.info("Calling single-call flashcard generation...")
            flashcards = self._generate_flashcards_single_call(text, language, difficulty, count)
            logger.info(f"Single-call generation returned {len(flashcards)} flashcards")
            
            # If AI generation failed, try rule-based generation
            if not flashcards:
                logger.info("AI generation failed, trying rule-based generation...")
                flashcards = self._generate_rule_based_flashcards(text, language, difficulty, count)
                logger.info(f"Rule-based generation returned {len(flashcards)} flashcards")
            
            # Clean and validate flashcards
            logger.info("Cleaning and validating flashcards...")
            cleaned_flashcards = self._clean_and_validate_flashcards(flashcards, count)
            
            logger.info(f"Generated {len(cleaned_flashcards)} cleaned flashcards")
            return cleaned_flashcards
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            logger.info("Falling back to rule-based flashcard generation...")
            return self._generate_rule_based_flashcards(text, language, difficulty, count)
    
    def _generate_flashcards_single_call(self, text: str, language: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate all flashcards in a single API call with a comprehensive prompt."""
        
        # Create a comprehensive prompt for generating multiple flashcards
        prompt = self._create_comprehensive_flashcard_prompt(text, language, difficulty, count)
        logger.debug(f"Generated prompt length: {len(prompt)} characters")
        
        try:
            # Generate content with appropriate length for multiple flashcards
            max_length = min(count * 100, 800)  # Reduced max length to prevent short responses
            logger.info(f"Calling AI model with max_length={max_length}...")
            
            # Add retry logic for the AI model call
            generated_content = None
            for attempt in range(3):
                try:
                    generated_content = self.model_manager.generate_text(prompt, max_length=max_length)
                    if generated_content and len(generated_content.strip()) > 50:  # Ensure minimum content length
                        break
                    else:
                        logger.warning(f"AI model returned insufficient content on attempt {attempt + 1}: length={len(generated_content) if generated_content else 0}")
                except Exception as e:
                    logger.warning(f"AI model call failed on attempt {attempt + 1}: {str(e)}")
                    if attempt < 2:  # Don't sleep on last attempt
                        import time
                        time.sleep(1)
            
            if not generated_content or len(generated_content.strip()) < 50:
                logger.error("All AI model attempts failed or returned insufficient content")
                logger.error(f"Prompt length: {len(prompt)}")
                logger.error(f"Text length: {len(text)}")
                logger.error(f"Max length requested: {max_length}")
                logger.error(f"Generated content length: {len(generated_content) if generated_content else 0}")
                return []
            
            logger.info(f"AI model returned content length: {len(generated_content)} characters")
            logger.debug(f"Generated content preview: {generated_content[:500]}...")
            
            # Parse the generated content to extract flashcards
            logger.info("Parsing generated content for flashcards...")
            flashcards = self._parse_multiple_flashcards(generated_content, count)
            
            logger.info(f"Parsing completed, extracted {len(flashcards)} flashcards")
            return flashcards
            
        except Exception as e:
            logger.error(f"Error in single-call flashcard generation: {str(e)}", exc_info=True)
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
        
        # Generic, focused prompt for any topic
        prompt = f"""Create {count} educational flashcards about the given topic.

{lang_instruction}
Difficulty: {difficulty}
Focus: {complexity}

Based on this content:
{text[:800]}...

Generate {count} flashcards in this exact format:
Q: [Clear, specific question about the topic]
A: [Complete, informative answer]

Q: [Another clear question]
A: [Complete answer]

Make questions relevant to the topic content and ensure answers are educational and complete."""

        return prompt
    
    def _parse_multiple_flashcards(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse generated content to extract multiple flashcards."""
        flashcards = []
        
        # Add debug logging
        logger.info(f"Parsing flashcard content, expected: {expected_count}, content length: {len(content)}")
        logger.debug(f"Content preview: {content[:300]}...")
        
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
        
        logger.info(f"Primary parsing found {len(flashcards)} flashcards")
        
        # If parsing failed, try alternative parsing methods
        if len(flashcards) < expected_count:
            logger.info(f"Primary parsing insufficient, trying alternative methods. Need {expected_count - len(flashcards)} more")
            additional_flashcards = self._parse_alternative_format(content, expected_count - len(flashcards))
            flashcards.extend(additional_flashcards)
            logger.info(f"Alternative parsing added {len(additional_flashcards)} flashcards")
        
        # Final validation and cleaning
        cleaned_flashcards = []
        for fc in flashcards:
            if fc["question"].strip() and fc["answer"].strip() and len(fc["question"]) > 5 and len(fc["answer"]) > 5:
                cleaned_flashcards.append(fc)
        
        logger.info(f"Final cleaned flashcards: {len(cleaned_flashcards)} out of {len(flashcards)} parsed")
        
        return cleaned_flashcards[:expected_count]
    
    def _parse_alternative_format(self, content: str, needed_count: int) -> List[Dict[str, Any]]:
        """Alternative parsing method for different response formats."""
        flashcards = []
        
        logger.debug(f"Trying alternative parsing for {needed_count} flashcards")
        
        # Method 1: Look for question-answer pairs in various formats
        lines = content.split('\n')
        current_qa = {"question": "", "answer": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for question indicators (ends with ? or starts with question words)
            if (re.search(r'\?$', line) and len(line) > 10) or \
               re.match(r'^(What|How|Why|When|Where|Which|Who|Can|Do|Does|Is|Are|Will|Would|Could|Should)', line, re.IGNORECASE):
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
            
            # Check for answer indicators (not a question, longer than 10 chars)
            elif current_qa["question"] and not current_qa["answer"] and len(line) > 10 and not re.search(r'\?$', line):
                current_qa["answer"] = line
        
        # Add the last flashcard if we have one
        if current_qa["question"] and current_qa["answer"]:
            flashcards.append({
                "question": current_qa["question"],
                "answer": current_qa["answer"],
                "type": "Q&A",
                "difficulty": "beginner"
            })
        
        logger.debug(f"Method 1 found {len(flashcards)} flashcards")
        
        # Method 2: If still not enough, try to split by sentences and create Q&A pairs
        if len(flashcards) < needed_count:
            remaining_needed = needed_count - len(flashcards)
            logger.debug(f"Method 1 insufficient, trying Method 2 for {remaining_needed} more")
            
            # Split content into sentences
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            for i in range(0, min(len(sentences) - 1, remaining_needed), 2):
                if i + 1 < len(sentences):
                    question = sentences[i]
                    answer = sentences[i + 1]
                    
                    # Make sure we have a question format
                    if not question.endswith('?'):
                        question = question + "?"
                    
                    flashcards.append({
                        "question": question,
                        "answer": answer,
                        "type": "Q&A",
                        "difficulty": "beginner"
                    })
                    
                    if len(flashcards) >= needed_count:
                        break
        
        logger.debug(f"Alternative parsing total: {len(flashcards)} flashcards")
        return flashcards
    
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
    
    def _generate_rule_based_flashcards(self, text: str, language: str, difficulty: str, count: int = 10) -> List[Dict[str, Any]]:
        """Generate flashcards using rule-based approach when AI model fails."""
        logger.info("Using rule-based flashcard generation as fallback")
        
        flashcards = []
        
        # Extract key concepts and topics from the generated text
        key_concepts = self._extract_key_concepts_from_text(text)
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        
        # Create concept-based questions
        for i, concept in enumerate(key_concepts[:min(count//2, len(key_concepts))]):
            if language == "si":
                question = f"'{concept}' යන්නෙන් අදහස් කරන්නේ කුමක්ද?"
            elif language == "ta":
                question = f"'{concept}' என்பதன் பொருள் என்ன?"
            else:
                question = f"What is '{concept}'?"
            
            # Find relevant content from the generated text
            relevant_content = self._find_relevant_content(text, concept)
            answer = relevant_content if relevant_content else f"Information about {concept}"
            
            flashcards.append({
                "question": question,
                "answer": answer,
                "type": "Q&A",
                "difficulty": difficulty
            })
        
        # Generate sentence-based questions from the content
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
        
        # If still not enough, create generic educational questions
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
        
        logger.info(f"Rule-based generation created {len(flashcards)} generic flashcards")
        return flashcards[:count]
    
    def _extract_key_concepts_from_text(self, text: str) -> List[str]:
        """Extract key concepts from text for rule-based flashcard generation."""
        try:
            # Simple keyword extraction based on capitalization and frequency
            import re
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            
            # Count word frequency
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Filter out short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and return top concepts
            key_concepts = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [concept[0] for concept in key_concepts[:10]]
        except Exception:
            return ["Topic", "Concept", "Principle", "Theory", "Method"]
    
    def _find_relevant_content(self, text: str, concept: str) -> str:
        """Find relevant content from the generated text that explains the concept."""
        try:
            # Look for sentences containing the concept
            sentences = text.split('.')
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if concept.lower() in sentence_lower:
                    if len(sentence.strip()) > 20:
                        return sentence.strip()
            
            return ""
        except Exception:
            return "" 