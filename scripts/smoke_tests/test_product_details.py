#!/usr/bin/env python3
"""
Displays a product's complete information including attributes,
categories, and descriptions.

To use, run:
    python -m scripts.smoke_tests.test_product_details [optional product_key]
"""

import argparse
import logging
from pathlib import Path

from scripts.smoke_tests.utils import (
    format_section,
    get_output_dir,
    get_product_key,
    write_output,
)
from src.common.db import SessionLocal
from src.core.repositories import FacetIdentificationRepository

logger = logging.getLogger(__name__)


def format_attribute_details(product_details) -> str:
    """Formats each attribute with its value."""
    return "\n".join(
        f"• {attr.attribute}: {attr.value}"
        for attr in product_details.attributes
    )


def main(
    product_key: str | None = None, output_dir: Path | None = None
) -> None:
    """Run the product details test."""
    parser = argparse.ArgumentParser(
        description="Display product details and attributes"
    )
    parser.add_argument(
        "product_key", nargs="?", help="Optional product key to test"
    )
    args = parser.parse_args()

    try:
        product_key = args.product_key or product_key
        if not product_key:
            product_key = get_product_key(None, require_gaps=False)

        output_dir = get_output_dir(product_key, output_dir)

        with SessionLocal() as session:
            repository = FacetIdentificationRepository(session)
            product_details = repository.get_product_details(product_key)

            logger.info(
                f"Product {product_details.product_name}: "
                f"{len(product_details.attributes)} attributes, "
                f"{len(product_details.categories)} categories, "
                f"{len(product_details.product_description)} descriptions"
            )

            output = [
                format_section(
                    "Product Information",
                    f"Name: {product_details.product_name}\n"
                    f"Code: {product_details.product_code}\n"
                    f"Categories: {', '.join(product_details.categories)}",
                ),
                format_section(
                    "Attribute Details",
                    format_attribute_details(product_details),
                ),
                format_section(
                    "Attribute Coverage",
                    f"Total Attributes: {len(product_details.attributes)}",
                ),
            ]

            content = "\n\n".join(output)
            write_output(output_dir, "01_product_details.txt", content)

    except ValueError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
