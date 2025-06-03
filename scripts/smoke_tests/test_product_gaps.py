#!/usr/bin/env python3
"""
Displays a product's missing attributes and their allowed values, along with a
list of complete attributes.

To use, run:
    python -m scripts.smoke_tests.test_product_gaps [optional product_key]
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
from src.core.domain.repositories import FacetIdentificationRepository

logger = logging.getLogger(__name__)


def get_complete_attributes(
    repository: FacetIdentificationRepository, product_key: str
) -> list[str]:
    """Returns attributes that have values (no gaps)."""
    product_details = repository.get_product_details(product_key)
    product_gaps = repository.get_product_gaps(product_key)
    return [
        attr.attribute
        for attr in product_details.attributes
        if attr.attribute not in [gap.attribute for gap in product_gaps.gaps]
    ]


def format_gap_details(
    repository: FacetIdentificationRepository, product_key: str
) -> str:
    """Formats each gap with its allowed values in a JSON-style format."""
    product_gaps = repository.get_product_gaps(product_key)
    formatted_gaps = []
    for gap in product_gaps.gaps:
        values = "\n".join(f'    "{value}",' for value in gap.allowable_values)
        formatted_gaps.append(
            f"{{\n"
            f'  "attribute": "{gap.attribute}",\n'
            f'  "allowed_values": [\n'
            f"{values}\n"
            f"  ]\n"
            f"}}"
        )
    return "\n".join(formatted_gaps)


def main(
    product_key: str | None = None, output_dir: Path | None = None
) -> None:
    """Run the product gaps test."""
    parser = argparse.ArgumentParser(
        description="Display product gaps and their allowable values"
    )
    parser.add_argument(
        "product_key", nargs="?", help="Optional product key to test"
    )
    args = parser.parse_args()

    try:
        product_key = args.product_key or product_key
        if not product_key:
            product_key = get_product_key(None, require_gaps=True)

        output_dir = get_output_dir(product_key, output_dir)

        with SessionLocal() as session:
            repository = FacetIdentificationRepository(session)

            product_gaps = repository.get_product_gaps(product_key)
            complete_attributes = get_complete_attributes(
                repository, product_key
            )

            # Calculate average number of allowed values per gap
            total_allowed_values = sum(
                len(gap.allowable_values) for gap in product_gaps.gaps
            )
            avg_allowed_values = (
                total_allowed_values / len(product_gaps.gaps)
                if product_gaps.gaps
                else 0
            )

            logger.info(
                f"Product {product_gaps.product_name}: "
                f"{len(product_gaps.gaps)} gaps, "
                f"{len(complete_attributes)} complete attributes, "
                f"{avg_allowed_values:.1f} avg allowed values per gap"
            )

            output = [
                format_section(
                    "Product Information", f"Product Key: {product_key}"
                ),
                format_section(
                    "Missing Attributes",
                    "\n".join(
                        f"• {gap.attribute}" for gap in product_gaps.gaps
                    ),
                ),
                format_section(
                    "Complete Attributes",
                    "\n".join(f"• {attr}" for attr in complete_attributes),
                ),
                format_section(
                    "Gap Details with Allowable Values",
                    format_gap_details(repository, product_key),
                ),
            ]

            content = "\n\n".join(output)
            write_output(output_dir, "02_product_gaps.txt", content)

    except ValueError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
