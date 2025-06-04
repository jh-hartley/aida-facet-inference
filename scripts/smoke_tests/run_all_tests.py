#!/usr/bin/env python3
"""
Runs all smoke tests in sequence using the same product key and output
directory.

To use, run:
    python -m scripts.smoke_tests.run_all_tests [optional product_key]
"""

import importlib.util
import sys
from pathlib import Path

from scripts.smoke_tests.utils import get_output_dir, get_product_key


def import_module_from_path(module_name: str, file_path: str):
    """Dynamically imports a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not find module spec for {file_path}")
    if spec.loader is None:
        raise ImportError(f"Could not find loader for {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_test(
    module_name: str, file_path: str, product_key: str, output_dir: Path
):
    """
    Runs a single test script with the given product key and output directory.
    """
    module = import_module_from_path(module_name, file_path)
    if hasattr(module, "main"):
        if asyncio := getattr(module, "asyncio", None):
            asyncio.run(module.main(product_key, output_dir))
        else:
            module.main(product_key, output_dir)


def main(product_key: str | None = None) -> None:
    """Run all smoke tests in sequence."""
    try:
        if not product_key:
            product_key = get_product_key(
                None, require_gaps=True, randomise=True
            )
        print(f"Using product key: {product_key}")

        output_dir = get_output_dir(product_key)
        print(f"Output directory: {output_dir}")

        test_scripts = [
            (
                "test_product_details",
                "scripts/smoke_tests/test_product_details.py",
            ),
            ("test_product_gaps", "scripts/smoke_tests/test_product_gaps.py"),
            ("test_llm_prompts", "scripts/smoke_tests/test_llm_prompts.py"),
            (
                "test_llm_predictions",
                "scripts/smoke_tests/test_llm_predictions.py",
            ),
            (
                "test_similarity_search",
                "scripts/smoke_tests/test_similarity_search.py",
            ),
        ]

        for module_name, file_path in test_scripts:
            print(f"\nRunning {module_name}...")
            run_test(module_name, file_path, product_key, output_dir)

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
