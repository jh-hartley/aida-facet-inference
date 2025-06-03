import logging

from src.common.clock import clock
from src.common.db import SessionLocal
from src.core.embedding.generators import len_safe_get_averaged_embedding
from src.core.infrastructure.database.embeddings.models import ProductEmbedding
from src.core.infrastructure.database.embeddings.repository import (
    ProductEmbeddingRepository,
)

logger = logging.getLogger(__name__)


async def update_embedding(
    product_key: str,
    description: str,
    found_embedding: ProductEmbedding,
) -> ProductEmbedding:
    """
    Update an existing embedding for a product and return the updated
    ProductEmbedding object.
    """
    with SessionLocal() as session:
        embedding_repo = ProductEmbeddingRepository(session)
        now = clock.now()
        embedding = await len_safe_get_averaged_embedding(description)
        embedding_obj = ProductEmbedding(
            product_key=product_key,
            product_description=description,
            embedding=embedding,
            created_at=found_embedding.created_at,
            updated_at=now,
        )
        embedding_repo.update(embedding_obj)
        logger.debug(f"Updated embedding for product {product_key}")
        session.commit()
        return embedding_obj
