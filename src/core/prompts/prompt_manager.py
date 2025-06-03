from pathlib import Path

from src.common.read_files import read_text_file
from src.core.domain import FacetPrediction


class ProductFacetPrompt:
    def __init__(self) -> None:
        self._templates_dir = Path(__file__).parent / "templates"
        self._system_prompt_template = read_text_file(
            self._templates_dir / "system_prompt.txt"
        )
        self._human_prompt_template = read_text_file(
            self._templates_dir / "human_prompt.txt"
        )
        self._confidence_examples = read_text_file(
            self._templates_dir / "confidence_examples.txt"
        )

    def get_system_prompt(self, product_context: str) -> str:
        return self._system_prompt_template.format(
            response_format=FacetPrediction.get_prompt_description(),
            examples=self._confidence_examples,
            product_context=product_context,
            comparable_products="",  # Reserved for future RAG implementation
        )

    def get_human_prompt(
        self, attribute: str, allowed_values: list[str]
    ) -> str:
        return self._human_prompt_template.format(
            attribute=attribute,
            allowed_values=", ".join(allowed_values),
        )


PRODUCT_FACET_PROMPT = ProductFacetPrompt()
