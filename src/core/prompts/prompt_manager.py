from pathlib import Path

from src.common.read_files import read_text_file
from src.core.domain import FacetPrediction
from src.core.domain.models import ProductDetails
from src.core.similarity_search.models import SimilaritySearchResult
from src.core.similarity_search.service import SimilaritySearchService


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
        self._similarity_service = SimilaritySearchService()

    def _format_similar_product(self, result: SimilaritySearchResult) -> str:
        """Format a single similar product for the prompt."""
        product = result.product
        return (
            f"Product: {product.product_name}\n"
            f"Code: {product.product_code}\n"
            f"Categories: {', '.join(product.categories)}\n"
            f"Distance: {result.similarity_score:.3f}\n"
            "Attributes:\n"
            + "\n".join(
                f"  • {attr.attribute}: {attr.value}"
                for attr in product.attributes
            )
            + "\n"
            "Descriptions:\n"
            + "\n".join(
                f"  • {desc.descriptor}: {desc.value}"
                for desc in product.product_description
            )
        )

    def _get_similar_products_section(
        self,
        product_key: str,
        max_similar_products: int = 5,
        max_distance: float = 0.6,
    ) -> str:
        """
        Get the similar products section for the prompt, or empty string if
        none found.
        """
        try:
            results = self._similarity_service.find_similar_products(
                product_key=product_key,
                limit=max_similar_products,
                max_distance=max_distance,
            )

            if not results.results:
                return ""

            similar_products = "\n\n".join(
                f"Similar Product {i+1}:\n"
                f"{self._format_similar_product(result)}"
                for i, result in enumerate(results.results)
            )

            return (
                f"\n\nUse the next {len(results.results)} similar "
                f"products to help you answer the question if applicable:\n"
                f"{similar_products}"
            )
        except Exception:
            return ""

    def get_system_prompt(
        self,
        product_details: ProductDetails,
        max_similar_products: int = 3,
        max_distance: float = 0.6,
    ) -> str:
        """
        Get the full system prompt including similar products if available.
        """
        similar_products = self._get_similar_products_section(
            product_details.product_key,
            max_similar_products=max_similar_products,
            max_distance=max_distance,
        )

        return self._system_prompt_template.format(
            response_format=FacetPrediction.get_prompt_description(),
            examples=self._confidence_examples,
            product_context=product_details.get_llm_prompt(),
            comparable_products=similar_products,
        )

    def get_human_prompt(
        self, attribute: str, allowed_values: list[str]
    ) -> str:
        return self._human_prompt_template.format(
            attribute=attribute,
            allowed_values=", ".join(allowed_values),
        )


PRODUCT_FACET_PROMPT = ProductFacetPrompt()
