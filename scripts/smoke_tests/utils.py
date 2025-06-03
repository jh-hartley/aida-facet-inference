from datetime import datetime
from pathlib import Path

from src.common.db import SessionLocal
from src.core.domain.repositories import FacetIdentificationRepository


def format_section(title: str, content: str) -> str:
    """Creates a section with 80-character separator lines."""
    separator = "=" * 80
    return f"{separator}\n{title}\n{separator}\n\n{content}"


def get_product_key(
    product_key: str | None, require_gaps: bool = False
) -> str:
    """
    Returns a product key from args if provided, otherwise finds one
    with/without gaps.
    """
    if product_key:
        return product_key

    with SessionLocal() as session:
        repository = FacetIdentificationRepository(session)
        key = repository.get_single_product(with_gaps=require_gaps)
        if not key:
            raise ValueError(
                f"No products {'with' if require_gaps else 'without'} "
                f"gaps found."
            )
        return key


def get_output_dir(product_key: str, output_dir: Path | None = None) -> Path:
    """Creates a timestamped output directory if none provided."""
    if output_dir:
        return output_dir

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path("scripts/smoke_tests/outputs")
    output_dir = base_dir / f"{product_key}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_output(output_dir: Path, filename: str, content: str) -> None:
    """Writes content to a file and prints its location."""
    output_path = output_dir / filename
    output_path.write_text(content)
    print(f"Output written to: {output_path}")
