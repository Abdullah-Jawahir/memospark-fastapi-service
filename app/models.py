import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
from .config import MODELS_TO_TRY, CACHE_DIR, GENERATION_PARAMS
from .logger import logger

class ModelManager:
    """Manages the loading and usage of AI models."""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.current_model_name = None
        self.question_generator = None
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
        """Generate text using the loaded model."""
        if max_length is None:
            max_length = GENERATION_PARAMS["max_length"]
        
        try:
            inputs = self.tokenizer(
                prompt,
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
                        do_sample=True,
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
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        no_repeat_ngram_size=GENERATION_PARAMS["no_repeat_ngram_size"]
                    )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # For non-T5 models, remove the input prompt from output
            if "flan-t5" not in self.current_model_name:
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
        except Exception as e:
            logger.error(f"Error in model generation: {str(e)}")
            return ""
    
    def get_model_info(self) -> dict:
        """Get information about the current model."""
        return {
            "model_name": self.current_model_name,
            "model_type": "seq2seq" if "flan-t5" in self.current_model_name else "causal",
            "pipeline_loaded": self.question_generator is not None
        }

# Global model manager instance
model_manager = ModelManager() 