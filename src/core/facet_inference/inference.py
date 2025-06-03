import logging

from src.common.exceptions import PredictionError
from src.core.domain.models import (
    FacetPrediction,
    ProductAttributeGap,
    ProductDetails,
    ProductGaps,
)
from src.core.infrastructure.llm.client import Llm
from src.core.infrastructure.llm.models import LlmModel
from src.core.prompts import PRODUCT_FACET_PROMPT

logger = logging.getLogger(__name__)


class ProductFacetPredictor:
    """Predicts values for missing product attributes."""

    def __init__(
        self,
        product_details: ProductDetails,
        product_gaps: ProductGaps,
        llm: Llm | None = None,
        llm_model: LlmModel = LlmModel.GPT_4O_MINI,
    ) -> None:
        self.product_details = product_details
        self.product_gaps = product_gaps
        self._llm = llm or Llm(llm_model)
        self._product_context = product_details.get_llm_prompt()
        self._system_prompt = PRODUCT_FACET_PROMPT.get_system_prompt(
            self._product_context
        )

    async def predict_gap(
        self,
        gap: ProductAttributeGap,
    ) -> FacetPrediction:
        """Predict a value for a single gap."""
        try:
            logger.info(
                f"Predicting {gap.attribute} (choosing from "
                f"{len(gap.allowable_values)} values)"
            )
            human_prompt = PRODUCT_FACET_PROMPT.get_human_prompt(
                gap.attribute,
                gap.allowable_values,
            )
            prediction = await self._llm.ainvoke(
                self._system_prompt, human_prompt, FacetPrediction
            )
            logger.debug(
                f"Prediction for {prediction.attribute}: "
                f"{prediction.predicted_value} (confidence: "
                f"{prediction.confidence:.2f})"
            )
            return prediction
        except Exception as e:
            raise PredictionError(
                f"Failed to predict for {gap.attribute}: {str(e)}"
            ) from e
