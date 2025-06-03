from src.common.db import SessionLocal
from src.config import config
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.embedding_generation.generators import (
    len_safe_get_averaged_embedding,
)
from src.core.infrastructure.database.embeddings.repository import (
    ProductEmbeddingRepository,
)
from src.core.similarity_search.models import (
    SimilaritySearchResponse,
    SimilaritySearchResult,
)


class SimilaritySearchService:
    """Service for finding semantically similar products using embeddings."""

    def __init__(self) -> None:
        self.session = SessionLocal()
        self.embedding_repo = ProductEmbeddingRepository(self.session)
        self.facet_repo = FacetIdentificationRepository(self.session)

    def find_similar_products(
        self,
        product_key: str,
        limit: int = config.SIMILARITY_DEFAULT_LIMIT,
        max_distance: float = config.SIMILARITY_DEFAULT_DISTANCE,
    ) -> SimilaritySearchResponse:
        """
        Find products similar to the given product key.

        The specified product must have an embedding in the database.
        """
        if not 1 <= limit <= config.SIMILARITY_MAX_LIMIT:
            raise ValueError(
                f"Limit must be between 1 and {config.SIMILARITY_MAX_LIMIT}"
            )

        if (
            not config.SIMILARITY_MIN_DISTANCE
            <= max_distance
            <= config.SIMILARITY_MAX_DISTANCE
        ):
            raise ValueError(
                f"Maximum distance must be between "
                f"{config.SIMILARITY_MIN_DISTANCE} "
                f"and {config.SIMILARITY_MAX_DISTANCE}"
            )

        similar_products = self.embedding_repo.find_similar_products_by_key(
            product_key=product_key,
            limit=limit,
            distance_threshold=max_distance,
        )

        results = []
        for similar_product in similar_products:
            product_details = self.facet_repo.get_product_details(
                similar_product.product_key
            )
            results.append(
                SimilaritySearchResult(
                    product=product_details,
                    similarity_score=similar_product.distance,
                )
            )

        return SimilaritySearchResponse(
            results=results,
            total_results=len(results),
        )

    async def find_similar_products_for_description(
        self,
        description: str,
        limit: int = config.SIMILARITY_DEFAULT_LIMIT,
        max_distance: float = config.SIMILARITY_DEFAULT_DISTANCE,
    ) -> SimilaritySearchResponse:
        """
        Find semantic product matches using a raw text description.
        """
        if not 1 <= limit <= config.SIMILARITY_MAX_LIMIT:
            raise ValueError(
                f"Limit must be between 1 and {config.SIMILARITY_MAX_LIMIT}"
            )

        if (
            not config.SIMILARITY_MIN_DISTANCE
            <= max_distance
            <= config.SIMILARITY_MAX_DISTANCE
        ):
            raise ValueError(
                f"Maximum distance must be between "
                f"{config.SIMILARITY_MIN_DISTANCE} "
                f"and {config.SIMILARITY_MAX_DISTANCE}"
            )

        embedding = await len_safe_get_averaged_embedding(description)

        similar_products = (
            self.embedding_repo.find_similar_products_by_embedding(
                embedding=embedding,
                limit=limit,
                distance_threshold=max_distance,
            )
        )

        results = []
        for similar_product in similar_products:
            product_details = self.facet_repo.get_product_details(
                similar_product.product_key
            )
            results.append(
                SimilaritySearchResult(
                    product=product_details,
                    similarity_score=similar_product.distance,
                )
            )

        return SimilaritySearchResponse(
            results=results,
            total_results=len(results),
        )

    def __del__(self) -> None:
        self.session.close()
