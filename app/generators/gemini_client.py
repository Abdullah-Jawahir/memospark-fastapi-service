"""
Google Gemini API integration for FastAPI document processing.
This serves as a fallback when OpenRouter models are rate-limited.

The Gemini free tier includes:
- Gemini 1.5 Flash: Fast, efficient model good for content generation
- Gemini 1.5 Pro: More capable model for complex tasks
- 15 requests per minute, 1,500 requests per day (generous limits)
"""

import requests
import json
import time
from typing import Optional, Dict, Any
from ..logger import logger
from ..config import GENERATION_PARAMS

class GeminiAPIClient:
    """Client for Google Gemini API with rate limiting and error handling."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.models_to_try = [
            "gemini-2.0-flash",      # Primary - 15 RPM, 1M TPM, 200 RPD
            "gemini-2.0-flash-lite", # Secondary - 30 RPM, 1M TPM, 200 RPD  
            "gemini-2.5-flash-lite", # Tertiary - 15 RPM, 250K TPM, 1,000 RPD
            "gemini-2.5-flash",      # Fallback - 10 RPM, 250K TPM, 250 RPD
        ]
        self.last_request_time = 0
        self.min_request_interval = 2.5  # 2.5 seconds between requests for better rate limits (up to 30/min for 2.0-flash-lite)
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            logger.info(f"Rate limiting: waiting {wait_time:.1f}s before Gemini API call")
            time.sleep(wait_time)
    
    def generate_text(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """
        Generate text using Gemini API with fallback between models.
        
        Args:
            prompt: The prompt to send to Gemini
            max_tokens: Maximum tokens to generate (Gemini uses different limits)
            
        Returns:
            Generated text or None if all models fail
        """
        for model_name in self.models_to_try:
            try:
                logger.info(f"Trying Gemini model: {model_name}")
                
                # Respect rate limits
                self._wait_for_rate_limit()
                
                # Prepare the request
                url = f"{self.base_url}/{model_name}:generateContent"
                headers = {
                    "Content-Type": "application/json",
                }
                
                # Gemini API format
                data = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": GENERATION_PARAMS["temperature"],
                        "topK": GENERATION_PARAMS["top_k"],
                        "topP": GENERATION_PARAMS["top_p"],
                        "maxOutputTokens": min(max_tokens, 8192),  # Gemini limit
                        "stopSequences": [],
                    },
                    "safetySettings": [
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        }
                    ]
                }
                
                # Add API key to URL
                url += f"?key={self.api_key}"
                
                # Make the request
                response = requests.post(
                    url,
                    headers=headers,
                    data=json.dumps(data),
                    timeout=60
                )
                
                self.last_request_time = time.time()
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"Gemini rate limited on {model_name}, trying next model...")
                    continue
                
                # Handle other errors
                if response.status_code != 200:
                    logger.warning(f"Gemini API error on {model_name}: {response.status_code} - {response.text}")
                    continue
                
                # Parse successful response
                result = response.json()
                
                if "candidates" not in result or not result["candidates"]:
                    logger.warning(f"No candidates in Gemini response from {model_name}")
                    continue
                
                candidate = result["candidates"][0]
                
                if "content" not in candidate or "parts" not in candidate["content"]:
                    logger.warning(f"Invalid response structure from {model_name}")
                    continue
                
                # Extract the generated text
                generated_text = candidate["content"]["parts"][0].get("text", "")
                
                if not generated_text.strip():
                    logger.warning(f"Empty response from {model_name}")
                    continue
                
                logger.info(f"Successfully generated text using Gemini {model_name}")
                return generated_text.strip()
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout with Gemini {model_name}")
                continue
            except Exception as e:
                logger.warning(f"Error with Gemini {model_name}: {str(e)}")
                continue
        
        # All models failed
        logger.error("All Gemini models failed")
        return None
    
    def test_connection(self) -> bool:
        """Test if the API key works and Gemini is accessible."""
        try:
            response = self.generate_text("Test: Generate the word 'Hello'", max_tokens=10)
            return response is not None and "hello" in response.lower()
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False


def create_gemini_client(api_key: Optional[str] = None) -> Optional[GeminiAPIClient]:
    """
    Create and test a Gemini API client.
    
    Args:
        api_key: Gemini API key, if None will try to get from environment
        
    Returns:
        GeminiAPIClient instance if successful, None otherwise
    """
    import os
    
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.warning("No Gemini API key provided")
        return None
    
    try:
        client = GeminiAPIClient(api_key)
        logger.info("Testing Gemini API connection...")
        
        if client.test_connection():
            logger.info("✅ Gemini API connection successful")
            return client
        else:
            logger.warning("❌ Gemini API connection test failed")
            return None
            
    except Exception as e:
        logger.error(f"Failed to create Gemini client: {e}")
        return None
