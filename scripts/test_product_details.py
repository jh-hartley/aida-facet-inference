#!/usr/bin/env python3
"""Script to test the get_product_details functionality of
FacetIdentificationRepository.

Usage:
    python scripts/test_product_details.py <product_key>

Example:
    python scripts/test_product_details.py 89b9c590-73e6-4916-8231-41fe3b2e0eb9
"""

import argparse
import json
from typing import Any

from src.core.repositories import FacetIdentificationRepository
from src.db.connection import SessionLocal


def format_product_details(details: Any) -> str:
    """Format product details for readable output in the terminal."""
    return json.dumps(
        {
            "product_key": details.product_key,
            "product_code": details.product_code,
            "product_name": details.product_name,
            "code_type": details.code_type,
            "categories": details.categories,
            "attributes": [
                {"attribute": attr.attribute, "value": attr.value}
                for attr in details.attributes
            ],
            "product_description": [
                {"descriptor": desc.descriptor, "value": desc.value}
                for desc in details.product_description
            ],
        },
        indent=2,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test product details retrieval functionality"
    )
    parser.add_argument(
        "product_key",
        help="The product key to retrieve details for",
    )
    args = parser.parse_args()

    try:
        with SessionLocal() as session:
            repository = FacetIdentificationRepository(session)
            details = repository.get_product_details(args.product_key)
            print("\nProduct Details:")
            print(format_product_details(details))
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
