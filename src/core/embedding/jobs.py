import asyncio
import logging

from src.core.embedding.generators import len_safe_get_averaged_embedding
from src.core.embedding.models import ProductEmbedding
from src.core.embedding.repository import ProductEmbeddingRepository
from src.core.models import ProductDetails
from src.core.repositories import FacetIdentificationRepository
from src.db.connection import SessionLocal
from src.log_utils import setup_logging
from src.utils.clock import clock

logger = logging.getLogger(__name__)
setup_logging()

semaphore = asyncio.Semaphore(100)


def _get_product_description(product_details: ProductDetails) -> str:
    """Convert product details into a text description for embedding"""
    description_parts = [
        f"Product: {product_details.product_name}",
        f"Product Code ({product_details.code_type}): "
        f"{product_details.product_code}",
        f"Categories: {', '.join(product_details.categories)}",
    ]

    if product_details.attributes:
        description_parts.append("Attributes:")
        for attr in product_details.attributes:
            description_parts.append(f"- {attr.attribute}: {attr.value}")

    if product_details.product_description:
        description_parts.append("Descriptions:")
        for desc in product_details.product_description:
            description_parts.append(f"- {desc.descriptor}: {desc.value}")

    return "\n".join(description_parts)


async def _create_embedding(product_key: str) -> None:
    """Create embedding for a single product"""
    async with semaphore:
        try:
            with SessionLocal() as session:
                facet_repo = FacetIdentificationRepository(session)
                product_details = facet_repo.get_product_details(product_key)

                description = _get_product_description(product_details)
                embedding = await len_safe_get_averaged_embedding(description)

                embedding_repo = ProductEmbeddingRepository(session)
                embedding_repo.create(
                    ProductEmbedding(
                        product_key=product_key,
                        embedding=embedding,
                        created_at=clock.now(),
                    )
                )
                session.commit()

            logger.debug(f"Created embedding for product {product_key}")

        except Exception as e:
            logger.error(f"Failed to process product {product_key}: {str(e)}")


async def create_embeddings_for_products() -> None:
    """Create embeddings for all products that need them"""
    with SessionLocal() as session:
        product_keys = FacetIdentificationRepository(
            session
        ).get_products_with_gaps()

        embedding_repo = ProductEmbeddingRepository(session)
        product_keys = [
            key for key in product_keys if not embedding_repo.exists(key)
        ]

    tasks = [_create_embedding(key) for key in product_keys]
    await asyncio.gather(*tasks)
    logger.info(f"Processed {len(product_keys)} products")


if __name__ == "__main__":
    asyncio.run(create_embeddings_for_products())
