import logging

from tqdm import tqdm

from src.common.db import SessionLocal
from src.core.domain.models import ProductDetails
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.embedding_generation.uow.create_embedding import create_embedding
from src.core.embedding_generation.uow.update_embedding import update_embedding
from src.core.facet_inference.concurrency import AsyncConcurrencyManager
from src.core.infrastructure.database.embeddings.repository import (
    ProductEmbeddingRepository,
)

logger = logging.getLogger(__name__)


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
    logger.debug(f"Starting embedding for product: {product_key}")
    try:
        with SessionLocal() as session:
            facet_repo = FacetIdentificationRepository(session)
            product_details = facet_repo.get_product_details(product_key)
            description = _get_product_description(product_details)
            embedding_repo = ProductEmbeddingRepository(session)
            found_embedding = embedding_repo.find(product_key)

        if found_embedding is not None:
            if found_embedding.product_description == description:
                logger.debug(f"Product {product_key}: skipped (no change)")
                return "skipped"
            await update_embedding(product_key, description, found_embedding)
            logger.debug(f"Product {product_key}: updated")
            return "updated"

        await create_embedding(product_key, description)
        logger.debug(f"Product {product_key}: created")
        return "created"

    except Exception as e:
        logger.error(f"Product {product_key}: error - {e}")
        return "error"


async def create_embeddings_for_products(max_concurrency: int = 10) -> None:
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

    results = {"created": 0, "updated": 0, "skipped": 0, "error": 0}
    manager = AsyncConcurrencyManager(max_concurrent=max_concurrency)

    statuses = await manager.execute(_embed_product_description, product_keys)
    for status in tqdm(statuses, desc="Embedding products", unit="product"):
        if status == "created":
            results["created"] += 1
        elif status == "updated":
            results["updated"] += 1
        elif status == "skipped":
            results["skipped"] += 1
        else:
            results["error"] += 1


async def embed_single_product(product_key: str) -> None:
    """Embed or update a single product by key"""
    await _embed_product_description(product_key)
