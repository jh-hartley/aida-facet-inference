import asyncio
import logging
import random
import traceback

from tqdm import tqdm

from src.common.db import SessionLocal
from src.common.logs import setup_logging
from src.core.domain.models import ProductDetails
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.embedding.uow.create_embedding import create_embedding
from src.core.embedding.uow.update_embedding import update_embedding
from src.core.infrastructure.database.embeddings.repository import (
    ProductEmbeddingRepository,
)

logger = logging.getLogger(__name__)
setup_logging()

semaphore = asyncio.Semaphore(5)

MAX_RETRIES = 5
INITIAL_BACKOFF = 2  # seconds
MAX_BACKOFF = 60  # seconds


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


async def _embed_product_description(product_key: str) -> str:
    """
    Create or update embedding for a single product.

    Returns status string.
    """
    async with semaphore:
        attempt = 0
        backoff = INITIAL_BACKOFF
        while attempt < MAX_RETRIES:
            try:
                with SessionLocal() as session:
                    facet_repo = FacetIdentificationRepository(session)
                    product_details = facet_repo.get_product_details(
                        product_key
                    )
                    description = _get_product_description(product_details)
                    embedding_repo = ProductEmbeddingRepository(session)
                    found_embedding = embedding_repo.find(product_key)

                if found_embedding is not None:
                    if found_embedding.product_description == description:
                        logger.debug(
                            f"Skipped embedding for product {product_key} "
                            "(description unchanged)"
                        )
                        return "skipped"
                    # Update existing embedding
                    try:
                        await update_embedding(
                            product_key, description, found_embedding
                        )
                        return "updated"
                    except Exception as e:
                        logger.error(f"Failed to update embedding: {e}")
                        return "error"

                # Create new embedding
                try:
                    await create_embedding(product_key, description)
                    return "created"
                except Exception as e:
                    logger.error(f"Failed to create embedding: {e}")
                    return "error"

            except Exception as e:
                error_str = str(e)
                if (
                    "429" in error_str
                    or "rate limit" in error_str.lower()
                    or "insufficient_quota" in error_str
                    or "timeout" in error_str.lower()
                ):
                    attempt += 1
                    logger.warning(
                        f"Rate limit or timeout for product {product_key} "
                        f"(attempt {attempt}/{MAX_RETRIES}). "
                        f"Retrying in {backoff:.1f} seconds..."
                    )
                    await asyncio.sleep(backoff + random.uniform(0, 1))
                    backoff = min(backoff * 2, MAX_BACKOFF)
                    continue

                logger.error(
                    f"Failed to process product {product_key}: {str(e)}\n"
                    f"{traceback.format_exc()}"
                )
                return "error"

        logger.error(
            f"Failed to process product {product_key} after {MAX_RETRIES} "
            "retries due to rate limits/timeouts."
        )
        return "error"


async def create_embeddings_for_products() -> None:
    """
    Create or update embeddings for all products.
    """
    with SessionLocal() as session:
        product_details = FacetIdentificationRepository(
            session
        ).get_all_product_details()
        product_keys = [
            product_details.product_key for product_details in product_details
        ]
        logger.info(f"Found {len(product_keys)} product keys to embed.")

    results = {"created": 0, "updated": 0, "skipped": 0, "error": 0}

    for key in tqdm(product_keys, desc="Embedding products", unit="product"):
        status = await _embed_product_description(key)
        if status == "created":
            results["created"] += 1
        elif status == "updated":
            results["updated"] += 1
        elif status == "skipped":
            results["skipped"] += 1
        else:
            results["error"] += 1

    logger.info(f"Processed {len(product_keys)} products: {results}")


async def embed_single_product(product_key: str) -> None:
    """Embed or update a single product by key"""
    status = await _embed_product_description(product_key)
    logger.info(f"Product {product_key} embedding status: {status}")


if __name__ == "__main__":
    asyncio.run(create_embeddings_for_products())
