import logging

from src.core.facet_inference.models import FacetPrediction
from src.core.facet_inference.prompts import PRODUCT_FACET_PREDICTION_PROMPT
from src.core.llm.client import Llm
from src.core.llm.models import LlmModel
from src.core.models import ProductAttributeGap, ProductDetails, ProductGaps

logger = logging.getLogger(__name__)


class ProductFacetPredictor:
    """Predicts values for missing product attributes."""

    def __init__(
        self,
        product_details: ProductDetails,
        product_gaps: ProductGaps,
        llm_model: LlmModel = LlmModel.O3_MINI_HIGH,
    ) -> None:
        self.product_details = product_details
        self.product_gaps = product_gaps
        self._llm = Llm(llm_model)
        self._system_prompt = PRODUCT_FACET_PREDICTION_PROMPT

    def predict_single_gap(
        self,
        gap: ProductAttributeGap,
    ) -> FacetPrediction:
        """
        Predict a value for a single gap.

        Parameters:
        - gap (ProductAttributeGap): The gap to predict a value for

        Returns:
        - FacetPrediction: The prediction result
        """
        logger.info(
            f"Predicting {gap.attribute} (choosing from "
            f"{len(gap.allowable_values)} values)"
        )
        human_prompt = self._format_human_prompt(gap)
        return self._llm.invoke(
            self._system_prompt, human_prompt, FacetPrediction
        )

    async def apredict_single_gap(
        self,
        gap: ProductAttributeGap,
    ) -> FacetPrediction:
        """
        Asynchronously predict a value for a single gap.

        Parameters:
        - gap (ProductAttributeGap): The gap to predict a value for

        Returns:
        - FacetPrediction: The prediction result
        """
        logger.info(
            f"Predicting {gap.attribute} (choosing from "
            f"{len(gap.allowable_values)} values)"
        )
        human_prompt = self._format_human_prompt(gap)
        prediction = await self._llm.ainvoke(
            self._system_prompt, human_prompt, FacetPrediction
        )
        logger.debug(
            f"Prediction for {prediction.attribute}: "
            f"{prediction.predicted_value} (confidence: "
            f"{prediction.confidence:.2f})"
        )
        return prediction

    def _format_human_prompt(self, gap: ProductAttributeGap) -> str:
        """Format the human prompt for a single gap."""
        return "\n".join(
            [
                "Product Information:",
                self.product_details.get_llm_prompt(),
                "",
                "Missing Attribute:",
                f"Attribute: {gap.attribute}",
                f"Allowed values: {', '.join(gap.allowable_values)}",
            ]
        )
