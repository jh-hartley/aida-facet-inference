import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers.base_router import base_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_middleware(app: FastAPI):
    """Configure CORS and other middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For local development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def setup_exception_handlers(app: FastAPI):
    """Configure global exception handlers."""
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AIDA Facet Inference API",
        description="API for inferring product facets using LLMs",
        version="0.1.0"
    )

    setup_middleware(app)
    setup_exception_handlers(app)

    app.include_router(base_router())

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 