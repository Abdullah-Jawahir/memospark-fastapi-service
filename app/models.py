import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
from .config import MODELS_TO_TRY, CACHE_DIR, GENERATION_PARAMS, OPENROUTER_API_KEY, OPENROUTER_API_URL, OPENROUTER_MODEL
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
        self.use_openrouter = bool(OPENROUTER_API_KEY)
        if not self.use_openrouter:
            self._load_best_model()
            self._setup_pipeline()
    
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
                "text2text-generation" if "flan-t5" in self.current_model_name else "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1  # Use CPU
            )
            logger.info("Question generation pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load question generation pipeline: {str(e)}")
            self.question_generator = None
    
    def generate_text(self, prompt: str, max_length: int = None) -> str:
        """Generate text using OpenRouter API if available, otherwise local model."""
        if max_length is None:
            max_length = GENERATION_PARAMS["max_length"]
        
        if self.use_openrouter:
            return self._generate_text_openrouter(prompt, max_length)
        else:
            return self._generate_text_local(prompt, max_length)
    
    def _generate_text_openrouter(self, prompt: str, max_length: int) -> str:
        """Generate text using OpenRouter API (DeepSeek model)."""
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant for educational quiz generation."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_length,
                "temperature": GENERATION_PARAMS["temperature"],
                "top_p": GENERATION_PARAMS["top_p"]
            }
            response = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(data), timeout=60)
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(f"OpenRouter API error: {e}. Response content: {response.text}")
                return ""
            result = response.json()
            # Extract the assistant's reply
            reply = result["choices"][0]["message"]["content"]
            return self._clean_generated_text(reply)
        except Exception as e:
            logger.error(f"Error in OpenRouter API generation: {str(e)}")
            return ""
    
    def _generate_text_local(self, prompt: str, max_length: int) -> str:
        try:
            # Handle different model types with appropriate prompts
            if "deepseek" in self.current_model_name:
                formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            elif "flan-t5" in self.current_model_name:
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
                if "flan-t5" in self.current_model_name:
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
            if "flan-t5" not in self.current_model_name:
                generated_text = generated_text[len(formatted_prompt):].strip()
            generated_text = self._clean_generated_text(generated_text)
            return generated_text
        except Exception as e:
            logger.error(f"Error in model generation: {str(e)}")
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
                "model_type": "seq2seq" if "flan-t5" in self.current_model_name else "causal",
                "pipeline_loaded": self.question_generator is not None
            }

# Global model manager instance
model_manager = ModelManager() 