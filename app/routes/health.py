from fastapi import APIRouter
from datetime import datetime
from ..models import model_manager

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    model_info = model_manager.get_model_info()
    return {
        "status": "healthy",
        "model": model_info["model_name"],
        "model_type": model_info["model_type"],
        "pipeline_loaded": model_info["pipeline_loaded"],
        "timestamp": datetime.now().isoformat()
    } 