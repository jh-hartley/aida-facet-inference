#!/usr/bin/env python3
"""
Shows how a product's information is formatted for LLM consumption,
including both raw and formatted views.

To use, run:
    python -m scripts.smoke_tests.test_llm_prompts [optional product_key]
"""

import logging
from pathlib import Path

from scripts.smoke_tests.utils import (
    format_section,
    get_output_dir,
    get_product_key,
    write_output,
)
from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.models import ProductGaps
from src.core.repositories import FacetIdentificationRepository
from src.db.connection import SessionLocal

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text string.

    Uses a rough approximation where:
    - Average token length is ~4 characters
    - Average word length is ~5.3 characters
    - Therefore, ~0.75 words per token
    """
    word_count = len(text.split())
    return int(word_count / 0.75)


def estimate_response_tokens(prediction: dict) -> int:
    """Estimate tokens in a FacetPrediction response.

    Based on typical response structure:
    - attribute: ~5 tokens
    - predicted_value: ~3-5 tokens
    - confidence: ~2 tokens
    - reasoning: ~20-30 tokens
    """
    return estimate_tokens(prediction.get("reasoning", "")) + 10


def main(
    product_key: str | None = None, output_dir: Path | None = None
) -> None:
    """Run the LLM prompts test."""
    try:
        if not product_key:
            product_key = get_product_key(None, require_gaps=True)

        output_dir = get_output_dir(product_key, output_dir)

        with SessionLocal() as session:
            repository = FacetIdentificationRepository(session)
            product_details = repository.get_product_details(product_key)
            product_gaps = repository.get_product_gaps(product_key)

            predictor = ProductFacetPredictor(
                product_details=product_details,
                product_gaps=product_gaps,
            )
            model_name = predictor._llm.llm_model.value

            system_prompt = predictor._system_prompt
            system_prompt_words = len(system_prompt.split())
            system_prompt_tokens = estimate_tokens(system_prompt)
            total_allowed_values = sum(
                len(gap.allowable_values) for gap in product_gaps.gaps
            )

            human_prompt_tokens = []
            for gap in product_gaps.gaps:
                human_prompt = predictor._format_human_prompt(gap)
                human_prompt_tokens.append(estimate_tokens(human_prompt))

            avg_human_prompt_tokens = sum(human_prompt_tokens) / len(
                human_prompt_tokens
            )
            avg_response_tokens = estimate_response_tokens(
                {
                    "attribute": "example",
                    "predicted_value": "example",
                    "confidence": 0.5,
                    "reasoning": "This is an example reasoning that might "
                    "be longer in practice.",
                }
            )

            total_tokens_per_gap = (
                system_prompt_tokens
                + avg_human_prompt_tokens
                + avg_response_tokens
            )
            total_tokens_per_gap_cached = (
                avg_human_prompt_tokens + avg_response_tokens
            )

            token_summary = [
                format_section(
                    "Token Cost Analysis",
                    f"Model Information:\n"
                    f"- Model: {model_name}\n"
                    f"- Provider: OpenAI\n"
                    f"- Note: This model is used for all predictions in this "
                    "product\n\n"
                    f"System Prompt:\n"
                    f"- Words: {system_prompt_words}\n"
                    f"- Estimated tokens: {system_prompt_tokens}\n"
                    f"- Note: OpenAI caches system prompts when using the same "
                    "model instance\n"
                    f"- Note: Cached system prompts are charged at 25% of the "
                    "normal rate\n"
                    f"- Note: This applies to both sync and async requests\n\n"
                    f"Per Gap (averaged across {len(product_gaps.gaps)} "
                    "gaps):\n"
                    f"- Human prompt tokens: {avg_human_prompt_tokens:.1f}\n"
                    f"- Response tokens: {avg_response_tokens:.1f}\n"
                    f"- Total tokens (including system prompt): "
                    f"{total_tokens_per_gap:.1f}\n"
                    f"- Total tokens (with cached system prompt): "
                    f"{total_tokens_per_gap_cached + (system_prompt_tokens * 0.25):.1f}\n\n"
                    f"Cost Estimation Notes:\n"
                    f"- OpenAI automatically caches system prompts for the same "
                    "model instance\n"
                    f"- Cached system prompts are charged at 25% of the normal "
                    "rate\n"
                    f"- This caching works for both synchronous and "
                    "asynchronous requests\n"
                    f"- Response tokens are estimated based on typical "
                    "response structure\n"
                    f"- Multiply these numbers by OpenAI's token costs for "
                    "total cost estimation\n"
                    f"- For batch processing, using a single model instance "
                    "per product\n"
                    f"  ensures system prompt caching and reduced costs",
                )
            ]

            write_output(
                output_dir, "00_token_analysis.txt", "\n\n".join(token_summary)
            )

            logger.info(
                f"Product {product_details.product_name}: "
                f"{len(product_gaps.gaps)} gaps, "
                f"{total_allowed_values} total allowed values, "
                f"{system_prompt_words} words ({system_prompt_tokens} "
                "est. tokens) in system prompt, "
                f"{avg_human_prompt_tokens:.1f} avg tokens per human prompt"
            )

            output = [
                format_section(
                    "Product Information",
                    f"Product Key: {product_key}\n"
                    f"Product Name: {product_details.product_name}\n"
                    f"Product Code: {product_details.product_code}",
                ),
                format_section(
                    "System Prompt",
                    f"Word count: {system_prompt_words}\n"
                    f"Estimated tokens: {system_prompt_tokens}\n\n"
                    f"{system_prompt}",
                ),
            ]

            for i, gap in enumerate(product_gaps.gaps, 1):
                human_prompt = predictor._format_human_prompt(gap)
                prompt_words = len(human_prompt.split())
                prompt_tokens = estimate_tokens(human_prompt)

                output.append(
                    format_section(
                        f"Human Prompt for Gap {i}: {gap.attribute}",
                        f"Word count: {prompt_words}\n"
                        f"Estimated tokens: {prompt_tokens}\n\n"
                        f"{human_prompt}",
                    )
                )

            content = "\n\n".join(output)
            write_output(output_dir, "03_llm_prompts.txt", content)

    except ValueError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
