#!/usr/bin/env python3
"""
This smoke test prints the raw JSON and formatted LLM output for comparison.

Usage:
    python scripts/smoke_tests/test_product_details.py [product_key]

    product key is optional
"""

import argparse
import json

from scripts.smoke_tests.utils import format_section, get_product_key
from src.core.repositories import FacetIdentificationRepository
from src.db.connection import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test product details formatting"
    )
    parser.add_argument(
        "product_key",
        nargs="?",
        help="Optional product key. If not provided, "
        "uses first product with gaps",
    )
    args = parser.parse_args()

    try:
        product_key = get_product_key(args.product_key)
        print(f"Using product key: {product_key}")

        with SessionLocal() as session:
            repository = FacetIdentificationRepository(session)
            product_details = repository.get_product_details(product_key)

            json_output = json.dumps(
                product_details.model_dump(), indent=2, ensure_ascii=False
            )
            print(format_section("Raw JSON", json_output))

            llm_output = product_details.get_llm_prompt()
            print(format_section("Formatted LLM Output", llm_output))

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
