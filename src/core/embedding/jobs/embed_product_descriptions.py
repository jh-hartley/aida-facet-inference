import asyncio

from tqdm import tqdm

from src.common.db import SessionLocal
from src.core.domain.models import ProductDetails
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.embedding.uow.create_embedding import create_embedding
from src.core.embedding.uow.update_embedding import update_embedding
from src.core.infrastructure.database.embeddings.repository import (
    ProductEmbeddingRepository,
)

semaphore = asyncio.Semaphore(10)


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
        try:
            with SessionLocal() as session:
                facet_repo = FacetIdentificationRepository(session)
                product_details = facet_repo.get_product_details(product_key)
                description = _get_product_description(product_details)
                embedding_repo = ProductEmbeddingRepository(session)
                found_embedding = embedding_repo.find(product_key)

            if found_embedding is not None:
                if found_embedding.product_description == description:
                    return "skipped"
                await update_embedding(
                    product_key, description, found_embedding
                )
                return "updated"

            await create_embedding(product_key, description)
            return "created"

        except Exception:
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


async def embed_single_product(product_key: str) -> None:
    """Embed or update a single product by key"""
    await _embed_product_description(product_key)


if __name__ == "__main__":
    asyncio.run(create_embeddings_for_products())
