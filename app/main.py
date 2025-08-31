from fastapi import FastAPI
from .routes import file_processing_router, health_router, search_flashcards_router
from .middleware import setup_cors, log_requests_middleware
from .logger import logger

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Memo Spark Backend",
        description="AI-powered document processing and content generation service",
        version="1.0.0"
    )
    
    # Setup middleware
    setup_cors(app)
    app.middleware("http")(log_requests_middleware)
    
    # Include routers
    app.include_router(file_processing_router, prefix="/api/v1", tags=["file-processing"])
    app.include_router(health_router, tags=["health"])
    app.include_router(search_flashcards_router, prefix="/api/v1", tags=["search-flashcards"])
    
    logger.info("FastAPI application created successfully")
    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 