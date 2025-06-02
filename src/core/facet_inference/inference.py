from src.core.facet_inference.models import FacetPrediction
from src.core.facet_inference.prompts import PRODUCT_FACET_PREDICTION_PROMPT
from src.core.llm.client import Llm
from src.core.llm.models import LlmModel
from src.core.models import ProductAttributeGap, ProductDetails, ProductGaps


class ProductFacetPredictor:
    """Predicts values for missing product attributes."""

    def __init__(self, llm_model: LlmModel = LlmModel.GPT_4O_MINI):
        self._chat = Llm(llm_model)
        self._system_prompt = PRODUCT_FACET_PREDICTION_PROMPT

    async def predict_single_gap(
        self,
        product: ProductDetails,
        gap: ProductAttributeGap,
    ) -> FacetPrediction:
        """Predict a value for a single gap."""
        # Create a single-gap ProductGaps object
        single_gap = ProductGaps(
            product_code=product.product_code,
            product_name=product.product_name,
            gaps=[gap],
        )
        return await self.predict(product, single_gap)

    async def predict(
        self,
        product: ProductDetails,
        gap: ProductGaps,
    ) -> FacetPrediction:
        """Predict values for all gaps in the ProductGaps object."""
        human_prompt = self._format_human_prompt(product, gap)

        return await self._chat.ainvoke(
            system=self._system_prompt,
            human=human_prompt,
            output_type=FacetPrediction,
        )

    def _format_human_prompt(
        self,
        product: ProductDetails,
        gap: ProductGaps,
    ) -> str:
        return "\n".join(
            [
                "Product Information:",
                product.get_llm_prompt(),
                "",
                "Missing Attribute:",
                gap.get_llm_prompt(),
            ]
        )
