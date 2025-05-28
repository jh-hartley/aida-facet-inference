from fastapi import APIRouter

from src.api.routers.facet_inference import facet_inference_router


def base_router() -> APIRouter:
    """Create base router with all API routes."""

    router = APIRouter()

    router.include_router(facet_inference_router())

    return router
