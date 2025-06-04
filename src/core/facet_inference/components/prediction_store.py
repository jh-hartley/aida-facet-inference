import logging

from sqlalchemy.orm import Session

from src.core.domain.models import FacetPrediction
from src.core.domain.repositories import FacetIdentificationRepository
from src.core.infrastructure.database.input_data.repositories import (
    RawAttributeRepository,
    RawProductRepository,
)
from src.core.infrastructure.database.predictions.repositories import (
    PredictionResultRepository,
)

logger = logging.getLogger(__name__)


class PredictionStore:
    """Stores predictions and links them to recommendations."""

    def __init__(self, session: Session):
        """Initialize the store.

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.repo = PredictionResultRepository(session)
        self.facet_repo = FacetIdentificationRepository(session)
        self.product_repo = RawProductRepository(session)
        self.attribute_repo = RawAttributeRepository(session)

    def store_predictions(
        self,
        experiment_key: str,
        product_key: str,
        predictions: list[FacetPrediction],
    ) -> None:
        """Store predictions in the database.

        Args:
            experiment_key: Experiment key
            product_key: Product key
            predictions: List of predictions to store
        """
        logger.info(f"Found {len(predictions)} predictions to store")

        for prediction in predictions:
            attribute = self.facet_repo.attribute_repo.get_by_friendly_name(
                prediction.attribute
            )
            if not attribute:
                logger.error(
                    f"Attribute not found for name: {prediction.attribute}"
                )
                continue

            logger.debug(
                "Creating prediction in repository for "
                f"experiment {experiment_key}, "
                f"product {product_key}, attribute {attribute.attribute_key}, "
                f"value {prediction.recommendation}"
            )

            try:
                self.repo.create_prediction(
                    experiment_key=experiment_key,
                    product_key=product_key,
                    attribute_key=attribute.attribute_key,
                    value=prediction.recommendation,
                    confidence=prediction.confidence,
                    recommendation_key=None,  # Will be set later if matched
                    actual_value=prediction.recommendation,
                    correctness_status=None,  # Will be set during validation
                    reasoning=prediction.reasoning,
                    suggested_value=prediction.suggested_value,
                )
                self.session.commit()
                logger.debug(
                    "Successfully created and committed "
                    "prediction in repository"
                )
            except Exception as e:
                logger.error(
                    f"Failed to create prediction in repository: {str(e)}"
                )
                raise

        logger.info(f"Committed {len(predictions)} predictions to database")
