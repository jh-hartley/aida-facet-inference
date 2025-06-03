import logging
from typing import Sequence

from core.infrastructure.database.predictions.repositories import PredictionResultRepository
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from src.common.db import uuid
from src.core.domain.models import FacetPrediction
from src.core.domain.repositories import (
    FacetIdentificationRepository,
)
from src.core.infrastructure.database.input_data.records import (
    HumanRecommendationRecord,
    RawAttributeRecord,
)
from src.core.infrastructure.database.input_data.repositories import (
    RawAttributeRepository,
    RawProductRepository,
)
from src.core.infrastructure.database.predictions.records import (
    PredictionResultRecord,
)

logger = logging.getLogger(__name__)


class PredictionStore:
    """Stores predictions and links them to recommendations."""

    def __init__(self, session: Session):
        self.session = session
        self.repo = PredictionResultRepository(session)
        self.facet_repo = FacetIdentificationRepository(session)
        self.product_repo = RawProductRepository(session)
        self.attribute_repo = RawAttributeRepository(session)

    def store_predictions(
        self,
        experiment_key: str,
        product_key: str,
        predictions: Sequence[FacetPrediction],
    ) -> None:
        """Store all predictions for a product in a single transaction."""
        # Get gaps with ground truth to link to recommendations
        gaps_with_truth = self.facet_repo.get_product_gaps_with_ground_truth(
            product_key
        )
        logger.info(f"Found {len(gaps_with_truth)} gaps with ground truth")

        # Get the product to get its system_name
        product = self.product_repo.get_by_id(product_key)
        if not product:
            logger.error(f"Product not found for key: {product_key}")
            return
        logger.info(f"Product system_name: {product.system_name}")

        # Get accepted recommendations for this product using system_name
        recommendations = self.session.scalars(
            select(HumanRecommendationRecord).where(
                HumanRecommendationRecord.product_reference == product.system_name,
                HumanRecommendationRecord.action == "Accept Recommendation",
            )
        ).all()
        logger.info(
            f"Found {len(recommendations)} recommendations "
            f"for product {product_key}"
        )

        attribute_to_recommendation = {}
        for rec in recommendations:
            attribute = self.attribute_repo.session.scalars(
                select(RawAttributeRecord).where(
                    RawAttributeRecord.system_name == rec.attribute_reference
                )
            ).first()

            if attribute:
                attribute_to_recommendation[attribute.system_name] = {
                    "id": rec.id,
                    "recommendation": rec,
                }
                logger.info(
                    f"Mapped attribute {rec.attribute_name} "
                    f"(system_name: {rec.attribute_reference}, "
                    f"key: {attribute.attribute_key}) "
                    f"to recommendation id: {rec.id}"
                )
            else:
                logger.warning(
                    f"No attribute found for recommendation "
                    f"attribute_reference: {rec.attribute_reference}"
                )

        logger.info(
            f"Created lookup with {len(attribute_to_recommendation)} entries"
        )

        for prediction in predictions:
            attribute = self.facet_repo.attribute_repo.get_by_friendly_name(
                prediction.attribute
            )
            if not attribute:
                logger.error(
                    f"Attribute not found for name: {prediction.attribute}"
                )
                continue
            logger.info(
                f"Processing prediction for {prediction.attribute} "
                f"(system_name: {attribute.system_name}, "
                f"key: {attribute.attribute_key})"
            )

            recommendation = attribute_to_recommendation.get(
                attribute.system_name
            )
            recommendation_key = (
                recommendation["id"] if recommendation else None
            )

            if recommendation:
                logger.info(
                    f"Found matching recommendation - "
                    f"Product: {rec.product_reference}, "
                    f"Attribute: {rec.attribute_reference}, "
                    f"ID: {recommendation_key}"
                )
            else:
                logger.info(
                    f"No matching recommendation found for "
                    f"product {product.system_name} and "
                    f"attribute {attribute.system_name}"
                )

            result = PredictionResultRecord(
                prediction_key=str(uuid()),
                experiment_key=experiment_key,
                product_key=product_key,
                attribute_key=attribute.attribute_key,
                value=prediction.predicted_value,
                confidence=prediction.confidence,
                recommendation_key=recommendation_key,
            )
            self.repo.create(result)

        self.session.commit()
        logger.info(f"Committed {len(predictions)} predictions to database") 