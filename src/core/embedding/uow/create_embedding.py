import logging

from src.common.clock import clock
from src.common.db import SessionLocal
from src.core.embedding.generators import len_safe_get_averaged_embedding
from src.core.infrastructure.database.embeddings.models import ProductEmbedding
from src.core.infrastructure.database.embeddings.repository import (
    ProductEmbeddingRepository,
)

logger = logging.getLogger(__name__)


async def create_embedding(
    product_key: str,
    description: str,
) -> ProductEmbedding:
    """
    Create a new embedding for a product and return the created
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
            created_at=now,
            updated_at=now,
        )
        embedding_repo.create(embedding_obj)
        logger.debug(f"Created embedding for product {product_key}")
        session.commit()
        return embedding_obj
