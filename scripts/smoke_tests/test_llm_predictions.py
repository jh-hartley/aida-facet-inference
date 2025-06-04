#!/usr/bin/env python3
"""
Tests LLM predictions for individual product gaps asynchronously and analyzes
token usage.

To use, run:
    python -m scripts.smoke_tests.test_llm_predictions [optional product_key]
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

from scripts.smoke_tests.utils import (
    format_section,
    get_output_dir,
    get_product_key,
    write_output,
)
from src.common.db import SessionLocal
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.facet_inference.service import FacetInferenceService

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


def format_token_analysis(
    system_prompt: str,
    product_context: str,
    predictions: list[dict],
    model_name: str,
) -> str:
    """Format token analysis for output."""
    system_prompt_tokens = estimate_tokens(system_prompt)
    product_context_tokens = estimate_tokens(product_context)

    response_tokens = sum(
        estimate_tokens(pred["reasoning"]) + 10  # +10 for JSON structure
        for pred in predictions
    ) / len(predictions)

    total_tokens = (
        system_prompt_tokens + product_context_tokens + response_tokens
    )
    total_tokens_cached = (
        system_prompt_tokens * 0.25  # System prompt is cached
        + product_context_tokens * 0.25  # Product context is cached
        + response_tokens
    )

    return format_section(
        "Token Cost Analysis",
        f"Model Information:\n"
        f"- Model: {model_name}\n"
        f"- Provider: OpenAI\n\n"
        f"System Prompt:\n"
        f"- Estimated tokens: {system_prompt_tokens}\n"
        f"- Note: This is cached at 25% rate\n\n"
        f"Product Context:\n"
        f"- Estimated tokens: {product_context_tokens}\n"
        f"- Note: This is cached at 25% rate\n\n"
        f"Response:\n"
        f"- Average tokens: {response_tokens:.1f}\n"
        f"- Based on {len(predictions)} actual predictions\n\n"
        f"Total Tokens:\n"
        f"- Without caching: {total_tokens:.1f}\n"
        f"- With caching: {total_tokens_cached:.1f}\n\n"
        f"Cost Estimation Notes:\n"
        f"- System prompt and product context are cached at 25% rate\n"
        f"- Response tokens are based on actual predictions\n"
        f"- Multiply these numbers by OpenAI's token costs for total cost "
        f"estimation",
    )


async def main(
    product_key: str | None = None, output_dir: Path | None = None
) -> None:
    """Run the LLM predictions test."""
    try:
        if not product_key:
            product_key = get_product_key(None, require_gaps=True)
        logger.info(f"Starting predictions for product: {product_key}")

        output_dir = get_output_dir(product_key, output_dir)
        logger.debug(f"Output directory: {output_dir}")

        with SessionLocal() as session:
            repository = FacetIdentificationRepository(session)
            service = FacetInferenceService(repository)
            predictions = await service.predict_for_product_key(
                product_key, evaluation_mode=False
            )

            confidence_summary = ", ".join(
                f"{pred.attribute}: {pred.confidence:.2f}"
                for pred in predictions
            )
            logger.info(
                f"Completed {len(predictions)} predictions with "
                f"confidence levels: "
                f"{confidence_summary}"
            )

            predictions_output = [
                format_section(
                    "Product Information",
                    f"Product Key: {product_key}\n"
                    f"Predictions: {len(predictions)}",
                ),
                format_section(
                    "Raw Predictions",
                    json.dumps(
                        [pred.model_dump() for pred in predictions],
                        indent=2,
                    ),
                ),
                format_section(
                    "Formatted Predictions",
                    "\n\n".join(
                        f"Attribute: {pred.attribute}\n"
                        f"Predicted Value: {pred.recommendation}\n"
                        f"Confidence: {pred.confidence}\n"
                        f"Reasoning: {pred.reasoning}"
                        for pred in predictions
                    ),
                ),
            ]
            write_output(
                output_dir,
                "04_llm_predictions.txt",
                "\n\n".join(predictions_output),
            )

    except ValueError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    product_key = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(product_key))
