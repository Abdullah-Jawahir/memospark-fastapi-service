import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
from .config import MODELS_TO_TRY, CACHE_DIR, GENERATION_PARAMS, OPENROUTER_API_KEY, OPENROUTER_API_URL, OPENROUTER_MODEL, OPENROUTER_MODELS_TO_TRY, ENABLE_OPENROUTER, ENABLE_GEMINI, FALLBACK_TO_LOCAL
from .logger import logger
import re
import requests
import json

class ModelManager:
    """Manages the loading and usage of AI models or OpenRouter API."""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.current_model_name = None
        self.question_generator = None
        self.use_openrouter = ENABLE_OPENROUTER
        self.gemini_client = None
        
        # Initialize Gemini client if enabled
        if ENABLE_GEMINI:
            self._init_gemini_client()
        
        if not self.use_openrouter:
            self._load_best_model()
            self._setup_pipeline()
    
    def _init_gemini_client(self):
        """Initialize Gemini API client as fallback."""
        try:
            from .generators.gemini_client import create_gemini_client
            self.gemini_client = create_gemini_client()
            if self.gemini_client:
                logger.info("Gemini client initialized successfully")
            else:
                logger.warning("Failed to initialize Gemini client")
        except Exception as e:
            logger.warning(f"Could not initialize Gemini client: {e}")
            self.gemini_client = None
    
    def _load_best_model(self):
        """Load the best available model for text generation tasks."""
        for model_name in MODELS_TO_TRY:
            try:
                logger.info(f"Attempting to load model: {model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=str(CACHE_DIR))
                if "flan-t5" in model_name:
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=str(CACHE_DIR))
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=str(CACHE_DIR))
                self.current_model_name = model_name
                logger.info(f"Successfully loaded model: {model_name}")
                return
            except Exception as e:
                logger.warning(f"Failed to load {model_name}: {str(e)}")
                continue
        raise Exception("Failed to load any suitable model")
    
    def _setup_pipeline(self):
        """Setup the question generation pipeline."""
        try:
            self.question_generator = pipeline(
                "text2text-generation" if self.current_model_name and "flan-t5" in self.current_model_name else "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1  # Use CPU
            )
            logger.info("Question generation pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load question generation pipeline: {str(e)}")
            self.question_generator = None
    
    def _ensure_local_model_loaded(self):
        """Ensure a local model is loaded if needed."""
        if not self.current_model_name or not self.model or not self.tokenizer:
            logger.info("Loading local model for fallback...")
            try:
                self._load_best_model()
                self._setup_pipeline()
                logger.info("Local model loaded successfully for fallback")
                return True
            except Exception as e:
                logger.error(f"Failed to load local model for fallback: {str(e)}")
                return False
        return True

    def generate_text(self, prompt: str, max_length: int | None = None) -> str:
        """Generate text using OpenRouter API if available, otherwise local model."""
        if max_length is None:
            max_length = GENERATION_PARAMS["max_length"]
        
        # At this point, max_length is guaranteed to be an int
        assert isinstance(max_length, int), "max_length must be an int at this point"
        
        if self.use_openrouter:
            result = self._generate_text_openrouter(prompt, max_length)
            
            # If OpenRouter fails, try Gemini before local fallback
            if not result and self.gemini_client:
                logger.info("OpenRouter failed, trying Gemini API...")
                result = self._generate_text_gemini(prompt, max_length)
                if result:
                    logger.info("Gemini API fallback successful")
                    return result
                else:
                    logger.warning("Gemini API fallback also failed")
            
            # If both OpenRouter and Gemini fail, try local model if enabled
            if not result and FALLBACK_TO_LOCAL:
                logger.info("All cloud APIs failed, falling back to local model")
                if self._ensure_local_model_loaded():
                    local_result = self._generate_text_local(prompt, max_length)
                    if local_result:
                        logger.info("Local model fallback successful")
                        return local_result
                    else:
                        logger.error("Local model fallback also failed")
                        return ""
                else:
                    logger.error("Cannot fallback to local model - failed to load")
                    return ""
            return result
        else:
            # Direct local model usage
            if not self.current_model_name or not self.model or not self.tokenizer:
                if not self._ensure_local_model_loaded():
                    logger.error("Failed to load local model")
                    return ""
            return self._generate_text_local(prompt, max_length)
    
    def _generate_text_gemini(self, prompt: str, max_length: int) -> str:
        """Generate text using Gemini API."""
        if not self.gemini_client:
            logger.warning("Gemini client not available")
            return ""
        
        try:
            result = self.gemini_client.generate_text(prompt, max_length)
            return result if result else ""
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return ""
    
    def _generate_text_openrouter(self, prompt: str, max_length: int) -> str:
        """Generate text using OpenRouter API with multi-model fallback."""
        max_retries_per_model = 2  # Give each model 2 chances
        retry_delay = 5  # Wait 5 seconds between retries to be respectful of rate limits
        
        # Try each OpenRouter model in order
        for model_index, model_name in enumerate(OPENROUTER_MODELS_TO_TRY):
            logger.info(f"Trying OpenRouter model {model_index + 1}/{len(OPENROUTER_MODELS_TO_TRY)}: {model_name}")
            
            for attempt in range(max_retries_per_model):
                try:
                    headers = {
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant for educational content generation."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_length,
                        "temperature": GENERATION_PARAMS["temperature"],
                        "top_p": GENERATION_PARAMS["top_p"]
                    }
                    
                    response = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(data), timeout=60)
                    
                    if response.status_code == 429:  # Rate limited
                        if attempt < max_retries_per_model - 1:
                            logger.warning(f"Rate limited on {model_name}. Waiting {retry_delay} seconds before retry...")
                            import time
                            time.sleep(retry_delay)
                            continue
                        else:
                            logger.warning(f"Rate limited on {model_name}. Trying next model...")
                            break  # Move to next model after exhausting retries
                    
                    try:
                        response.raise_for_status()
                    except requests.HTTPError as e:
                        logger.error(f"OpenRouter API error on {model_name}: {e}. Response content: {response.text}")
                        if attempt < max_retries_per_model - 1:
                            logger.warning(f"Retrying {model_name}... (attempt {attempt + 1}/{max_retries_per_model})")
                            import time
                            time.sleep(retry_delay)
                            continue
                        else:
                            logger.warning(f"Failed on {model_name}. Trying next model...")
                            break  # Try next model
                    
                    # Success! Extract and return the response
                    result = response.json()
                    reply = result["choices"][0]["message"]["content"]
                    logger.info(f"Successfully generated text using {model_name}")
                    return self._clean_generated_text(reply)
                    
                except Exception as e:
                    logger.error(f"Error with {model_name} (attempt {attempt + 1}): {str(e)}")
                    if attempt < max_retries_per_model - 1:
                        logger.warning(f"Retrying {model_name}... (attempt {attempt + 1}/{max_retries_per_model})")
                        continue
                    else:
                        logger.warning(f"Failed on {model_name}. Trying next model...")
                        break  # Try next model
        
        # If we get here, all OpenRouter models failed
        logger.error("All OpenRouter models failed. Falling back to local model.")
        if FALLBACK_TO_LOCAL:
            return self._generate_text_local(prompt, max_length)
        else:
            return ""
    
    def _generate_text_local(self, prompt: str, max_length: int) -> str:
        try:
            # Check if we have a loaded model
            if not self.current_model_name or not self.model or not self.tokenizer:
                logger.error("No local model loaded. Cannot generate text locally.")
                return ""
            
            # Handle different model types with appropriate prompts
            if self.current_model_name and "deepseek" in self.current_model_name:
                formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            elif self.current_model_name and "flan-t5" in self.current_model_name:
                formatted_prompt = prompt
            else:
                formatted_prompt = f"Instruction: {prompt}\n\nResponse:"
            
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                max_length=1024,
                truncation=True,
                padding=True
            )
            
            with torch.no_grad():
                if self.current_model_name and "flan-t5" in self.current_model_name:
                    outputs = self.model.generate(
                        inputs["input_ids"],
                        max_length=max_length,
                        num_return_sequences=1,
                        temperature=GENERATION_PARAMS["temperature"],
                        top_p=GENERATION_PARAMS["top_p"],
                        top_k=GENERATION_PARAMS["top_k"],
                        do_sample=GENERATION_PARAMS["do_sample"],
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        no_repeat_ngram_size=GENERATION_PARAMS["no_repeat_ngram_size"]
                    )
                else:
                    outputs = self.model.generate(
                        inputs["input_ids"],
                        max_length=len(inputs["input_ids"][0]) + max_length,
                        num_return_sequences=1,
                        temperature=GENERATION_PARAMS["temperature"],
                        top_p=GENERATION_PARAMS["top_p"],
                        top_k=GENERATION_PARAMS["top_k"],
                        do_sample=GENERATION_PARAMS["do_sample"],
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        no_repeat_ngram_size=GENERATION_PARAMS["no_repeat_ngram_size"]
                    )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            if not self.current_model_name or "flan-t5" not in self.current_model_name:
                generated_text = generated_text[len(formatted_prompt):].strip()
            generated_text = self._clean_generated_text(generated_text)
            logger.info(f"Successfully generated text using local model: {self.current_model_name}")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error in local model generation: {str(e)}")
            return ""
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean up generated text by removing unwanted tokens and formatting."""
        unwanted_tokens = [
            "<|im_end|>", "<|endoftext|>", "<|endofmask|>",
            "Instruction:", "Response:", "User:", "Assistant:"
        ]
        for token in unwanted_tokens:
            text = text.replace(token, "")
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        return text
    
    def get_model_info(self) -> dict:
        """Get information about the current model or API usage."""
        if self.use_openrouter:
            return {
                "model_name": OPENROUTER_MODEL,
                "model_type": "openrouter_api",
                "pipeline_loaded": True
            }
        else:
            return {
                "model_name": self.current_model_name,
                "model_type": "seq2seq" if self.current_model_name and "flan-t5" in self.current_model_name else "causal",
                "pipeline_loaded": self.question_generator is not None
            }

# Global model manager instance
model_manager = ModelManager() 