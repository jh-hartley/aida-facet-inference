from pydantic import BaseModel, Field

from src.core.domain.models import ProductDetails


class SimilaritySearchResult(BaseModel):
    """Represents a single result from a similarity search."""

    product: ProductDetails
    similarity_score: float = Field(ge=0, le=1)


class SimilaritySearchResponse(BaseModel):
    """Response containing multiple similarity search results."""

    results: list[SimilaritySearchResult]
    total_results: int
