from src.core.facet_inference.models import (
    FacetDefinition,
    FacetPrediction,
    ProductInfo,
)
from src.core.facet_inference.prompts import PRODUCT_FACET_PREDICTION_PROMPT
from src.core.llm.client import Llm
from src.core.llm.models import LlmModel


class ProductFacetPredictor:
    """Predicts labels for a single product facet."""

    def __init__(self, llm_model: LlmModel = LlmModel.GPT_4O_MINI):
        self._chat = Llm(llm_model)
        self._system_prompt = PRODUCT_FACET_PREDICTION_PROMPT

    async def predict(
        self,
        product: ProductInfo,
        facet: FacetDefinition,
    ) -> FacetPrediction:
        human_prompt = self._format_human_prompt(product, facet)

        return await self._chat.ainvoke(
            system=self._system_prompt,
            human=human_prompt,
            output_type=FacetPrediction,
        )

    def _format_human_prompt(
        self,
        product: ProductInfo,
        facet: FacetDefinition,
    ) -> str:
        product_info = [
            f"Name: {product.name}",
            f"Description: {product.description}",
            f"Category: {product.category}",
        ]
        for key, value in product.attributes.items():
            product_info.append(f"{key.title()}: {value}")

        facet_info = [
            f"Facet to predict: {facet.name}",
            f"Acceptable labels: {', '.join(facet.acceptable_labels)}",
            "Facet Rules:",
            facet.get_prompt_description(),
        ]

        return "\n".join(
            [
                "Product Information:",
                *product_info,
                "",
                *facet_info,
            ]
        )
