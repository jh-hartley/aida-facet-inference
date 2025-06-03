from src.common.db import SessionLocal
from src.config import config
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.embedding_generation.generators import len_safe_get_averaged_embedding
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
        
        Args:
            product_key (str): The key of the product to find similar products for.
            limit (int, optional): Maximum number of results to return.
                Defaults to config.SIMILARITY_DEFAULT_LIMIT.
            max_distance (float, optional): Maximum cosine distance (0-2).
                Products with distances above this will be excluded.
                Defaults to config.SIMILARITY_DEFAULT_DISTANCE.

        Returns:
            SimilaritySearchResponse: A response object containing the list
                of similar products and the total count.
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
        for similar_key, distance in similar_products:
            product_details = self.facet_repo.get_product_details(similar_key)
            results.append(
                SimilaritySearchResult(
                    product=product_details,
                    similarity_score=distance,
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
        Find products similar to the given description.
        
        Args:
            description (str): The product description to find similar products for.
            limit (int, optional): Maximum number of results to return.
                Defaults to config.SIMILARITY_DEFAULT_LIMIT.
            max_distance (float, optional): Maximum cosine distance (0-2).
                Products with distances above this will be excluded.
                Defaults to config.SIMILARITY_DEFAULT_DISTANCE.

        Returns:
            SimilaritySearchResponse: A response object containing the list
                of similar products and the total count.
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

        similar_products = self.embedding_repo.find_similar_products_by_embedding(
            embedding=embedding,
            limit=limit,
            distance_threshold=max_distance,
        )

        results = []
        for similar_key, distance in similar_products:
            product_details = self.facet_repo.get_product_details(similar_key)
            results.append(
                SimilaritySearchResult(
                    product=product_details,
                    similarity_score=distance,
                )
            )

        return SimilaritySearchResponse(
            results=results,
            total_results=len(results),
        )

    def __del__(self) -> None:
        self.session.close()
