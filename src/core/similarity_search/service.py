from src.common.db import SessionLocal
from src.config import config
from src.core.domain.repositories import FacetIdentificationRepository
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
        similarity_threshold: float = config.SIMILARITY_DEFAULT_THRESHOLD,
    ) -> SimilaritySearchResponse:
        """
        Find products similar to the given product key.

        Args:
            product_key (str): The key of the product to find similar products
                for.
            limit (int, optional): Maximum number of results to return.
                Defaults to config.SIMILARITY_DEFAULT_LIMIT.
            similarity_threshold (float, optional): Minimum similarity score.
                Defaults to config.SIMILARITY_DEFAULT_THRESHOLD.

        Returns:
            SimilaritySearchResponse: A response object containing the list
                of similar products and the total count.
        """
        if not 1 <= limit <= config.SIMILARITY_MAX_LIMIT:
            raise ValueError(
                f"Limit must be between 1 and {config.SIMILARITY_MAX_LIMIT}"
            )

        if (
            not config.SIMILARITY_MIN_THRESHOLD
            <= similarity_threshold
            <= config.SIMILARITY_MAX_THRESHOLD
        ):
            raise ValueError(
                f"Similarity threshold must be between "
                f"{config.SIMILARITY_MIN_THRESHOLD} "
                f"and {config.SIMILARITY_MAX_THRESHOLD}"
            )

        source_embedding = self.embedding_repo.find(product_key)
        if not source_embedding:
            raise ValueError(f"No embedding found for product {product_key}")

        similar_products = self.embedding_repo.find_similar_products(
            embedding=source_embedding.embedding,
            limit=limit,
            distance_threshold=1 - similarity_threshold,
        )

        results = []
        for similar_key, distance in similar_products:
            if similar_key == product_key:
                continue

            product_details = self.facet_repo.get_product_details(similar_key)
            similarity_score = 1 - distance

            results.append(
                SimilaritySearchResult(
                    product=product_details,
                    similarity_score=similarity_score,
                )
            )

        return SimilaritySearchResponse(
            results=results,
            total_results=len(results),
        )

    def __del__(self) -> None:
        self.session.close()
