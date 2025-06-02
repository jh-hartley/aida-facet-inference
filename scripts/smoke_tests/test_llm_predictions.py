#!/usr/bin/env python3
"""
Tests LLM predictions for individual product gaps asynchronously.

To use, run:
    python -m scripts.smoke_tests.test_llm_predictions [optional product_key]
"""

import asyncio
import json
from pathlib import Path

from scripts.smoke_tests.utils import (
    format_section,
    get_output_dir,
    get_product_key,
    write_output,
)
from src.core.facet_inference.inference import ProductFacetPredictor
from src.core.llm.models import LlmModel
from src.core.repositories import FacetIdentificationRepository
from src.db.connection import SessionLocal


async def main(
    product_key: str | None = None, output_dir: Path | None = None
) -> None:
    """Run the LLM predictions test."""
    try:
        if not product_key:
            product_key = get_product_key(None, require_gaps=True)
        print(f"Using product key: {product_key}")

        output_dir = get_output_dir(product_key, output_dir)
        print(f"Output directory: {output_dir}")

        with SessionLocal() as session:
            repository = FacetIdentificationRepository(session)
            product_details = repository.get_product_details(product_key)
            product_gaps = repository.get_product_gaps(product_key)

            predictor = ProductFacetPredictor(LlmModel.GPT_4O_MINI)

            tasks = []
            for gap in product_gaps.gaps:
                tasks.append(
                    predictor.predict_single_gap(product_details, gap)
                )

            predictions = await asyncio.gather(*tasks)

            # Format output
            output = [
                format_section(
                    "Product Information",
                    f"Product Key: {product_key}\n"
                    f"Product Name: {product_details.product_name}\n"
                    f"Product Code: {product_details.product_code}",
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
                        f"Predicted Value: {pred.predicted_value}\n"
                        f"Confidence: {pred.confidence}\n"
                        f"Reasoning: {pred.reasoning}"
                        for pred in predictions
                    ),
                ),
            ]

            content = "\n\n".join(output)
            write_output(output_dir, "04_llm_predictions.txt", content)

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
