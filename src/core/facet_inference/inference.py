import logging

from src.common.exceptions import PredictionError
from src.core.domain.models import (
    FacetPrediction,
    ProductAttributeGap,
    ProductDetails,
)
from src.core.infrastructure.llm.client import Llm
from src.core.prompts import PRODUCT_FACET_PROMPT

logger = logging.getLogger(__name__)


class ProductFacetPredictor:
    """Predicts values for missing product attributes."""

    def __init__(
        self,
        product_details: ProductDetails,
        llm: Llm,
    ) -> None:
        self.product_details = product_details
        self._llm = llm
        self._system_prompt = PRODUCT_FACET_PROMPT.get_system_prompt()
        print(
            "\n===== SYSTEM PROMPT SENT TO LLM =====\n"
            + self._system_prompt
            + "\n===== END SYSTEM PROMPT =====\n"
        )

    async def predict_gap(
        self,
        gap: ProductAttributeGap,
    ) -> FacetPrediction:
        """Predict a value for a single gap."""
        try:
            human_prompt = await PRODUCT_FACET_PROMPT.get_human_prompt(
                self.product_details,
                gap.attribute,
                gap.allowable_values,
            )
            prediction = await self._llm.ainvoke(
                self._system_prompt, human_prompt, FacetPrediction
            )
            logger.debug(
                f"Prediction for {prediction.attribute}: "
                f"{prediction.recommendation} (confidence: "
                f"{prediction.confidence:.2f})"
            )
            return prediction
        except Exception as e:
            raise PredictionError(
                f"Failed to predict for {gap.attribute}: {str(e)}"
            ) from e
