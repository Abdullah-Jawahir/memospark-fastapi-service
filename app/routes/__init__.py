from .file_processing import router as file_processing_router
from .health import router as health_router
from .search_flashcards import router as search_flashcards_router

__all__ = ['file_processing_router', 'health_router', 'search_flashcards_router'] 