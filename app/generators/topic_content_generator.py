from typing import Optional, Dict, Any
from ..models import model_manager
from ..logger import logger

class TopicContentGenerator:
    """Generates educational content from topics for flashcard creation."""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def generate_topic_content(self, topic: str, description: Optional[str] = None, difficulty: str = "beginner") -> str:
        """
        Generate comprehensive educational content about a topic.
        
        Args:
            topic: The educational topic to generate content about
            description: Optional additional context or description
            difficulty: The difficulty level (beginner, intermediate, advanced)
            
        Returns:
            Generated educational content as a string
        """
        try:
            # Create a comprehensive prompt for the topic
            prompt = self._create_topic_prompt(topic, description, difficulty)
            
            # Generate content using the AI model
            content = self._generate_content(prompt)
            
            if not content or len(content.strip()) < 100:
                logger.warning(f"Generated content too short for topic '{topic}', trying fallback")
                content = self._generate_fallback_content(topic, description, difficulty)
            
            return content.strip() if content else ""
            
        except Exception as e:
            logger.error(f"Error generating topic content for '{topic}': {str(e)}")
            return ""
    
    def _create_topic_prompt(self, topic: str, description: Optional[str] = None, difficulty: str = "beginner") -> str:
        """Create a comprehensive prompt for topic-based content generation."""
        
        # Adjust complexity based on difficulty
        complexity_guide = {
            "beginner": "basic concepts, simple explanations, fundamental principles",
            "intermediate": "detailed concepts, examples, connections between ideas",
            "advanced": "complex concepts, advanced theories, practical applications, research insights"
        }
        
        complexity = complexity_guide.get(difficulty, complexity_guide["beginner"])
        
        base_prompt = f"""You are an expert educator. Create comprehensive, structured educational content about: {topic}

Difficulty Level: {difficulty.title()}
Focus on: {complexity}

Create content that covers these key areas:

1. **Core Definition**: What is {topic}? Provide a clear, concise explanation.
2. **Key Concepts**: List and explain the main ideas, principles, and components.
3. **Important Facts**: Include essential information, statistics, and details that learners should know.
4. **Examples**: Provide concrete, real-world examples and applications.
5. **Related Concepts**: Explain how this topic connects to other fields and subjects.
6. **Practical Applications**: Describe how this knowledge is used in practice.
7. **Common Misconceptions**: Address what people often misunderstand about {topic}.
8. **Historical Context**: When and how did this topic develop? (if applicable)

"""
        
        if description:
            base_prompt += f"Additional Context: {description}\n\n"
        
        base_prompt += f"""Requirements:
- Write in clear, educational language suitable for {difficulty} level learners
- Use specific examples and concrete details
- Structure the content logically with clear sections
- Make the content engaging and easy to understand
- Ensure all information is accurate and educational
- Write content that can be easily converted into flashcards

Format the response as clear, structured educational content. Each section should contain specific, testable information."""

        return base_prompt
    
    def _generate_content(self, prompt: str) -> str:
        """Generate content using the AI model."""
        try:
            # Generate content with appropriate length for comprehensive coverage
            content = self.model_manager.generate_text(prompt, max_length=800)
            return content
            
        except Exception as e:
            logger.error(f"Error in primary content generation: {str(e)}")
            return ""
    
    def _generate_fallback_content(self, topic: str, description: Optional[str] = None, difficulty: str = "beginner") -> str:
        """Generate fallback content when primary generation fails."""
        try:
            # Simpler, more direct prompt
            fallback_prompt = f"""Create educational content about {topic}.
            
Difficulty: {difficulty}

Please provide:
1. A clear definition of {topic}
2. Key points and concepts
3. Examples and explanations
4. Important facts to remember

Make this content educational and suitable for creating flashcards.
Keep it clear and structured."""

            if description:
                fallback_prompt += f"\n\nAdditional context: {description}"
            
            content = self.model_manager.generate_text(fallback_prompt, max_length=500)
            return content
            
        except Exception as e:
            logger.error(f"Error in fallback content generation: {str(e)}")
            return ""
    
    def generate_topic_summary(self, topic: str, content: str) -> Dict[str, Any]:
        """
        Generate a summary of the topic content for better organization.
        
        Args:
            topic: The topic name
            content: The generated content
            
        Returns:
            Dictionary containing topic summary information
        """
        try:
            summary_prompt = f"""Given this content about {topic}, create a structured summary:

Content: {content[:500]}...

Please provide:
1. Main theme or focus
2. Key learning objectives
3. Difficulty level assessment
4. Estimated study time
5. Prerequisites (if any)

Format as a clear, structured response."""

            summary = self.model_manager.generate_text(summary_prompt, max_length=300)
            
            return {
                "topic": topic,
                "main_theme": self._extract_main_theme(summary),
                "learning_objectives": self._extract_learning_objectives(summary),
                "difficulty_assessment": self._extract_difficulty_assessment(summary),
                "estimated_study_time": self._extract_study_time(summary),
                "prerequisites": self._extract_prerequisites(summary),
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error generating topic summary: {str(e)}")
            return {
                "topic": topic,
                "main_theme": "Educational content",
                "learning_objectives": ["Learn about the topic"],
                "difficulty_assessment": "Moderate",
                "estimated_study_time": "15-30 minutes",
                "prerequisites": [],
                "content_length": len(content)
            }
    
    def _extract_main_theme(self, summary: str) -> str:
        """Extract main theme from summary."""
        try:
            if "Main theme:" in summary:
                return summary.split("Main theme:")[1].split("\n")[0].strip()
            elif "Main theme" in summary:
                return summary.split("Main theme")[1].split("\n")[0].strip()
            return "Educational content"
        except:
            return "Educational content"
    
    def _extract_learning_objectives(self, summary: str) -> list:
        """Extract learning objectives from summary."""
        try:
            if "learning objectives:" in summary.lower():
                obj_section = summary.split("learning objectives:")[1].split("\n")[0]
                return [obj.strip() for obj in obj_section.split(",") if obj.strip()]
            return ["Learn about the topic"]
        except:
            return ["Learn about the topic"]
    
    def _extract_difficulty_assessment(self, summary: str) -> str:
        """Extract difficulty assessment from summary."""
        try:
            if "difficulty" in summary.lower():
                diff_section = summary.split("difficulty")[1].split("\n")[0]
                return diff_section.strip()
            return "Moderate"
        except:
            return "Moderate"
    
    def _extract_study_time(self, summary: str) -> str:
        """Extract estimated study time from summary."""
        try:
            if "study time" in summary.lower():
                time_section = summary.split("study time")[1].split("\n")[0]
                return time_section.strip()
            return "15-30 minutes"
        except:
            return "15-30 minutes"
    
    def _extract_prerequisites(self, summary: str) -> list:
        """Extract prerequisites from summary."""
        try:
            if "prerequisites" in summary.lower():
                prereq_section = summary.split("prerequisites")[1].split("\n")[0]
                return [prereq.strip() for prereq in prereq_section.split(",") if prereq.strip()]
            return []
        except:
            return []
