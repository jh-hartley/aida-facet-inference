#!/usr/bin/env python3
"""
Shows exactly what is sent to the LLM for a product's facet prediction:
the complete system prompt and the human prompts for each gap.

To use, run:
    python -m scripts.smoke_tests.test_llm_prompts [optional product_key]
"""

import logging
from pathlib import Path

from core.prompts.prompt_manager import PRODUCT_FACET_PROMPT
from scripts.smoke_tests.utils import (
    format_section,
    get_output_dir,
    get_product_key,
    write_output,
)
from src.common.db import SessionLocal
from src.core.domain.repositories import FacetIdentificationRepository

logger = logging.getLogger(__name__)


def main(
    product_key: str | None = None, output_dir: Path | None = None
) -> None:
    """Show the system prompt and human prompts for each gap."""
    try:
        if not product_key:
            product_key = get_product_key(None, require_gaps=True)

        output_dir = get_output_dir(product_key, output_dir)
        logger.info(f"Starting prompt analysis for product: {product_key}")

        with SessionLocal() as session:
            repository = FacetIdentificationRepository(session)
            product_details = repository.get_product_details(product_key)
            product_gaps = repository.get_product_gaps(product_key)

            product_context = product_details.get_llm_prompt()
            system_prompt = PRODUCT_FACET_PROMPT.get_system_prompt(
                product_context
            )

            output = [format_section("System Prompt", system_prompt)]

            for gap in product_gaps.gaps:
                human_prompt = PRODUCT_FACET_PROMPT.get_human_prompt(
                    gap.attribute,
                    gap.allowable_values,
                )
                output.append(
                    format_section(
                        f"Human Prompt for Gap: {gap.attribute}", human_prompt
                    )
                )

            write_output(output_dir, "03_llm_prompts.txt", "\n\n".join(output))

        total_allowed_values = sum(
            len(gap.allowable_values) for gap in product_gaps.gaps
        )
        logger.info(
            f"Product {product_details.product_name}: "
            f"{len(product_gaps.gaps)} gaps, "
            f"{total_allowed_values} total allowed values"
        )

    except ValueError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
