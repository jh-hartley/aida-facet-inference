#!/usr/bin/env python3
"""
This smoke test prints the system and human prompts that are sent to the LLM
during facet inference.

Usage:
    python scripts/smoke_tests/test_llm_prompts.py [product_key]

    product key is optional
"""

import argparse

from scripts.smoke_tests.utils import get_product_key
from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.facet_inference.prompts import PRODUCT_FACET_PREDICTION_PROMPT
from src.core.repositories import FacetIdentificationRepository
from src.db.connection import SessionLocal


def format_prompt_section(title: str, content: str) -> str:
    """Format a prompt section with a clear title and separator."""
    separator = "=" * 80
    return f"\n{separator}\n{title}\n{separator}\n\n{content}\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test LLM prompts used in facet inference"
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
            product_gaps = repository.get_product_gaps(product_key)

            predictor = ProductFacetPredictor()
            human_prompt = predictor._format_human_prompt(
                product_details, product_gaps
            )

            print(
                format_prompt_section(
                    "System Prompt",
                    PRODUCT_FACET_PREDICTION_PROMPT,
                )
            )

            print(
                format_prompt_section(
                    "Human Prompt",
                    human_prompt,
                )
            )

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
