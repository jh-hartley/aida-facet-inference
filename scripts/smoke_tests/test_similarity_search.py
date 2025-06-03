#!/usr/bin/env python3
"""
Tests the similarity search functionality by finding similar products for a given
product key and displaying their details and similarity scores.

To use, run:
    python -m scripts.smoke_tests.test_similarity_search [optional product_key]
"""

import logging
from pathlib import Path

from scripts.smoke_tests.utils import (
    format_section,
    get_output_dir,
    get_product_key,
    write_output,
)
from src.core.similarity_search.service import SimilaritySearchService

logger = logging.getLogger(__name__)


def format_similar_product(result) -> str:
    """Formats a single similar product result with its details."""
    product = result.product
    return (
        f"Product: {product.product_name}\n"
        f"Code: {product.product_code}\n"
        f"Categories: {', '.join(product.categories)}\n"
        f"Distance: {result.similarity_score:.3f} "
        f"(0.0 = identical, 2.0 = completely different)\n"
        f"Attributes:\n"
        + "\n".join(f"  • {attr.attribute}: {attr.value}" for attr in product.attributes)
        + "\n"
        f"Descriptions:\n"
        + "\n".join(
            f"  • {desc.descriptor}: {desc.value}"
            for desc in product.product_description
        )
    )


def main(
    product_key: str | None = None, output_dir: Path | None = None
) -> None:
    """Run the similarity search test."""
    try:
        if not product_key:
            product_key = get_product_key(None, require_gaps=False)

        output_dir = get_output_dir(product_key, output_dir)
        logger.info(f"Starting similarity search for product: {product_key}")

        service = SimilaritySearchService()
        results = service.find_similar_products(
            product_key=product_key,
            limit=5,
            max_distance=1.8,  # Very lax threshold - only exclude completely different products
        )

        if not results.results:
            logger.warning("No similar products found within the maximum distance threshold")
            return

        min_score = min(r.similarity_score for r in results.results)
        max_score = max(r.similarity_score for r in results.results)
        avg_score = sum(r.similarity_score for r in results.results) / len(results.results)

        logger.info(
            f"Found {results.total_results} similar products "
            f"with distances ranging from {min_score:.3f} to {max_score:.3f} "
            f"(average: {avg_score:.3f})"
        )

        output = [
            format_section(
                "Source Product",
                f"Product Key: {product_key}",
            ),
            format_section(
                "Similarity Search Results",
                "\n\n".join(
                    f"Result {i+1}:\n{format_similar_product(result)}"
                    for i, result in enumerate(results.results)
                ),
            ),
            format_section(
                "Summary",
                f"Total Results: {results.total_results}\n"
                f"Distance Range: {min_score:.3f} to {max_score:.3f}\n"
                f"Average Distance: {avg_score:.3f}\n\n"
                f"Note: Distances range from 0.0 (identical) to 2.0 (completely different). "
                f"Lower distances indicate more similar products.",
            ),
        ]

        write_output(
            output_dir,
            "05_similarity_search.txt",
            "\n\n".join(output),
        )

    except ValueError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main() 