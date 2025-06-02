import logging

from src.core.facet_inference.models import FacetPrediction
from src.core.facet_inference.prompts import PRODUCT_FACET_PROMPT
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
        llm_model: LlmModel = LlmModel.GPT_4O_MINI,
    ) -> None:
        self.product_details = product_details
        self.product_gaps = product_gaps
        self._llm = Llm(llm_model)
        self._product_context = product_details.get_llm_prompt()
        self._system_prompt = PRODUCT_FACET_PROMPT.get_system_prompt(
            self._product_context
        )

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
        human_prompt = PRODUCT_FACET_PROMPT.get_human_prompt(
            gap.attribute,
            gap.allowable_values,
        )
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
