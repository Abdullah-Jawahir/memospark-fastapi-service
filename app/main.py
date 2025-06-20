from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from pptx import Presentation
import io
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import List, Dict, Any
import logging
import os
from pathlib import Path
from datetime import datetime
import re

# Configure logging with file handler
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler
log_file = LOG_DIR / f"fastapi_errors_{datetime.now().strftime('%Y%m%d')}.log"
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.ERROR)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Set custom cache directory for Hugging Face models
CACHE_DIR = PROJECT_ROOT / "model_cache"
CACHE_DIR.mkdir(exist_ok=True)

os.environ['TRANSFORMERS_CACHE'] = str(CACHE_DIR)
os.environ['HF_HOME'] = str(CACHE_DIR)
os.environ['HF_DATASETS_CACHE'] = str(CACHE_DIR)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the model and tokenizer - using a better model for text generation
MODEL_NAME = "google/flan-t5-small"  # Better for instruction following
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=str(CACHE_DIR))
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, cache_dir=str(CACHE_DIR))
    logger.info("Model and tokenizer loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model and tokenizer: {str(e)}")
    raise

# Initialize question generation pipeline as backup
try:
    question_generator = pipeline(
        "text2text-generation",
        model="google/flan-t5-small",
        tokenizer=tokenizer,
        device=-1  # Use CPU
    )
    logger.info("Question generation pipeline loaded successfully")
except Exception as e:
    logger.error(f"Failed to load question generation pipeline: {str(e)}")
    question_generator = None

def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]]+', ' ', text)
    
    # Fix common OCR issues
    text = re.sub(r'(\w)\|(\w)', r'\1l\2', text)  # Fix common OCR 'l' -> '|' issue
    text = re.sub(r'(\w)0(\w)', r'\1o\2', text)   # Fix common OCR 'o' -> '0' issue
    
    return text

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in doc:
            page_text = page.get_text()
            text += page_text + "\n"
        doc.close()
        
        # Clean the extracted text
        text = clean_text(text)
        
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=400, detail="Error processing PDF file")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        doc = DocxDocument(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text.strip() + "\n"
        
        # Clean the extracted text
        text = clean_text(text)
        
        logger.info(f"Successfully extracted {len(text)} characters from DOCX")
        return text
    except Exception as e:
        error_msg = f"Error extracting text from DOCX: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=400, detail="Error processing DOCX file")

def extract_text_from_pptx(file_content: bytes) -> str:
    """Extract text from PPTX file."""
    try:
        prs = Presentation(io.BytesIO(file_content))
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text += shape.text.strip() + "\n"
        
        # Clean the extracted text
        text = clean_text(text)
        
        logger.info(f"Successfully extracted {len(text)} characters from PPTX")
        return text
    except Exception as e:
        error_msg = f"Error extracting text from PPTX: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=400, detail="Error processing PPTX file")

def generate_simple_flashcards(text: str, language: str = "en") -> List[Dict[str, Any]]:
    """Generate simple flashcards using text processing when model fails."""
    try:
        # Split text into sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        flashcards = []
        for i, sentence in enumerate(sentences[:10]):  # Limit to 10 sentences
            # Create a simple question-answer pair
            words = sentence.split()
            if len(words) > 5:
                # Take first few words as question context
                question_words = words[:min(5, len(words)//2)]
                question = f"What is described by: {' '.join(question_words)}..."
                answer = sentence
                
                flashcards.append({
                    "question": question,
                    "answer": answer,
                    "type": "Q&A",
                    "difficulty": "Easy"
                })
        
        return flashcards
    except Exception as e:
        logger.error(f"Error in simple flashcard generation: {str(e)}")
        return []

def generate_flashcards(text: str, language: str = "en") -> List[Dict[str, Any]]:
    """Generate flashcards from text using Flan-T5 model with proper prompting."""
    try:
        # Clean and prepare the text
        text = text.strip()
        if len(text) < 50:
            logger.warning("Text is too short to generate meaningful flashcards")
            return []
        
        # Split text into smaller chunks for better processing
        max_chunk_size = 800
        chunks = []
        for i in range(0, len(text), max_chunk_size):
            chunk = text[i:i + max_chunk_size]
            if len(chunk.strip()) > 100:  # Only process chunks with sufficient content
                chunks.append(chunk.strip())
        
        if not chunks:
            logger.warning("No valid text chunks found for flashcard generation")
            return generate_simple_flashcards(text, language)
        
        flashcards = []
        
        for chunk in chunks:
            # Create a clear, structured prompt for the model
            if language == "en":
                prompt = f"""Generate 2-3 flashcards from this text. For each flashcard, provide:
Question: [Write a clear question about a key concept]
Answer: [Provide a concise answer]

Text: {chunk}

Generate flashcards:"""
            elif language == "si":
                prompt = f"""Generate 2-3 flashcards from this text in Sinhala. For each flashcard, provide:
Question: [Write a clear question about a key concept in Sinhala]
Answer: [Provide a concise answer in Sinhala]

Text: {chunk}

Generate flashcards:"""
            elif language == "ta":
                prompt = f"""Generate 2-3 flashcards from this text in Tamil. For each flashcard, provide:
Question: [Write a clear question about a key concept in Tamil]
Answer: [Provide a concise answer in Tamil]

Text: {chunk}

Generate flashcards:"""
            else:
                prompt = f"""Generate 2-3 flashcards from this text. For each flashcard, provide:
Question: [Write a clear question about a key concept]
Answer: [Provide a concise answer]

Text: {chunk}

Generate flashcards:"""
            
            try:
                # Tokenize the input
                inputs = tokenizer(
                    prompt, 
                    return_tensors="pt", 
                    max_length=1024, 
                    truncation=True,
                    padding=True
                )
                
                # Generate response
                with torch.no_grad():
                    outputs = model.generate(
                        inputs["input_ids"],
                        max_length=400,
                        num_return_sequences=1,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                        no_repeat_ngram_size=2
                    )
                
                # Decode the generated text
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Extract the generated part (after the prompt)
                if "Generate flashcards:" in generated_text:
                    generated_part = generated_text.split("Generate flashcards:")[-1].strip()
                else:
                    generated_part = generated_text.strip()
                
                # Parse the generated flashcards
                flashcard_blocks = generated_part.split("Question:")
                
                for block in flashcard_blocks[1:]:  # Skip the first empty block
                    if "Answer:" in block:
                        try:
                            # Split by "Answer:" to separate question and answer
                            parts = block.split("Answer:", 1)
                            if len(parts) == 2:
                                question = parts[0].strip()
                                answer = parts[1].strip()
                                
                                # Clean up the question and answer
                                question = question.strip()
                                answer = answer.strip()
                                
                                # Remove any remaining formatting
                                question = re.sub(r'^\d+\.\s*', '', question)  # Remove numbering
                                answer = re.sub(r'^\d+\.\s*', '', answer)      # Remove numbering
                                
                                # Validate that we have meaningful content
                                if (len(question) > 10 and len(answer) > 5 and 
                                    not question.startswith("<") and not answer.startswith("<") and
                                    "Question:" not in question and "Answer:" not in answer):
                                    
                                    flashcards.append({
                                        "question": question,
                                        "answer": answer,
                                        "type": "Q&A",
                                        "difficulty": "Medium"
                                    })
                        except Exception as parse_error:
                            logger.warning(f"Failed to parse flashcard block: {block[:100]}... Error: {str(parse_error)}")
                            continue
                    
            except Exception as chunk_error:
                logger.warning(f"Error processing chunk: {str(chunk_error)}")
                continue
        
        # If model-generated flashcards are insufficient, use fallback
        if len(flashcards) < 3:
            logger.info("Model generated insufficient flashcards, trying pipeline method")
            pipeline_flashcards = generate_flashcards_with_pipeline(text, language)
            if pipeline_flashcards:
                flashcards.extend(pipeline_flashcards)
            else:
                logger.info("Pipeline method failed, using simple fallback")
                fallback_flashcards = generate_simple_flashcards(text, language)
                flashcards.extend(fallback_flashcards)
        
        # Remove duplicates based on question content
        unique_flashcards = []
        seen_questions = set()
        for card in flashcards:
            question_key = card["question"][:50].lower()  # Use first 50 chars as key
            if question_key not in seen_questions:
                seen_questions.add(question_key)
                unique_flashcards.append(card)
        
        # Limit total flashcards
        if len(unique_flashcards) > 10:
            unique_flashcards = unique_flashcards[:10]
        
        logger.info(f"Successfully generated {len(unique_flashcards)} flashcards using Flan-T5 model")
        return unique_flashcards
        
    except Exception as e:
        error_msg = f"Error generating flashcards: {str(e)}"
        logger.error(error_msg, exc_info=True)
        # Try pipeline method first, then fallback
        logger.info("Attempting pipeline flashcard generation")
        pipeline_flashcards = generate_flashcards_with_pipeline(text, language)
        if pipeline_flashcards:
            return pipeline_flashcards
        else:
            logger.info("Pipeline method failed, using simple fallback")
            return generate_simple_flashcards(text, language)

def generate_flashcards_with_pipeline(text: str, language: str = "en") -> List[Dict[str, Any]]:
    """Generate flashcards using the question generation pipeline."""
    if question_generator is None:
        return []
    
    try:
        # Split text into sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        
        flashcards = []
        for sentence in sentences[:5]:  # Limit to 5 sentences
            try:
                # Generate a question from the sentence
                if language == "en":
                    prompt = f"Generate a question about this: {sentence}"
                elif language == "si":
                    prompt = f"Generate a question in Sinhala about this: {sentence}"
                elif language == "ta":
                    prompt = f"Generate a question in Tamil about this: {sentence}"
                else:
                    prompt = f"Generate a question about this: {sentence}"
                
                result = question_generator(prompt, max_length=100, num_return_sequences=1)
                question = result[0]['generated_text'].strip()
                
                # Clean up the question
                question = re.sub(r'^\d+\.\s*', '', question)  # Remove numbering
                
                if len(question) > 10 and not question.startswith("<"):
                    flashcards.append({
                        "question": question,
                        "answer": sentence,
                        "type": "Q&A",
                        "difficulty": "Medium"
                    })
                    
            except Exception as e:
                logger.warning(f"Error generating question for sentence: {str(e)}")
                continue
        
        return flashcards
    except Exception as e:
        logger.error(f"Error in pipeline flashcard generation: {str(e)}")
        return []

@app.post("/process-file")
async def process_file(file: UploadFile = File(...), language: str = "en"):
    """
    Process uploaded document and generate flashcards.
    
    Args:
        file: The uploaded file (PDF, DOCX, or PPTX)
        language: The language of the document (en, si, ta)
    
    Returns:
        JSON response containing generated flashcards
    """
    # Log request details
    logger.info(f"Processing file: {file.filename}, language: {language}, size: {file.size} bytes")
    
    try:
        if language not in ["en", "si", "ta"]:
            error_msg = f"Unsupported language: {language}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail="Unsupported language")
        
        # Read file content
        content = await file.read()
        
        # Determine file type and extract text
        file_extension = file.filename.split(".")[-1].lower()
        text = ""
        
        if file_extension == "pdf":
            text = extract_text_from_pdf(content)
        elif file_extension == "docx":
            text = extract_text_from_docx(content)
        elif file_extension == "pptx":
            text = extract_text_from_pptx(content)
        else:
            error_msg = f"Unsupported file type: {file_extension}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        if not text.strip():
            error_msg = "No text content found in the document"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail="No text content found in the document")
        
        # Generate flashcards
        flashcards = generate_flashcards(text, language)
        
        logger.info(f"Successfully processed file {file.filename} and generated {len(flashcards)} flashcards")
        return {"generated_cards": flashcards}
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already logged
        raise
    except Exception as e:
        error_msg = f"Unexpected error processing file {file.filename}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# Add middleware to log all requests and responses
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Response: {response.status_code} - Processed in {process_time:.3f}s")
        
        return response
    except Exception as e:
        # Log any unhandled exceptions
        error_msg = f"Unhandled exception in request {request.method} {request.url}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 