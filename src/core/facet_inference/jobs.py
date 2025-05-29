from uuid import uuid4

from sqlalchemy.orm import Session

from src.core.facet_inference.data import FacetInferenceDataLoader
from src.core.facet_inference.service import FacetInferenceService
from src.core.models import ProductGaps
from src.core.repositories import FacetIdentificationRepository
from src.core.types import ProductAttributeGap
from src.raw_csv_ingestion.records import (
    PredictionExperimentRecord,
    PredictionResultRecord,
)
from src.raw_csv_ingestion.repositories import (
    PredictionExperimentRepository,
    PredictionResultRepository,
)


class FacetPredictionJob:
    """Job for predicting missing attribute values for products."""

    def __init__(
        self,
        session: Session,
        service: FacetInferenceService | None = None,
        metadata: dict | None = None,
    ):
        self.session = session
        self.repository = FacetIdentificationRepository(session)
        self.experiment_repo = PredictionExperimentRepository(session)
        self.prediction_repo = PredictionResultRepository(session)
        self.service = service or FacetInferenceService()
        self.data_loader = FacetInferenceDataLoader(self.repository)
        self.metadata = metadata or {}

    async def run(self) -> str:
        """
        Run the prediction job for all products with missing attributes.

        This will:
        1. Create a new experiment
        2. Load all products with gaps
        3. Make predictions for each gap
        4. Store predictions in the database

        Returns:
            The experiment key for this run
        """
        # Create new experiment
        experiment_key = str(uuid4())
        experiment = PredictionExperimentRecord(
            experiment_key=experiment_key,
            metadata=self.metadata,
        )
        self.experiment_repo.add(experiment)

        # Load and process products
        dataset = self.data_loader.load_dataset(
            self.repository.get_products_with_gaps()
        )

        for sample in dataset.samples:
            predictions = await self.service.predict_multiple_attributes(
                product=sample.product_details,
                gaps=[
                    ProductGaps(
                        product_code=sample.product_details.product_code,
                        product_name=sample.product_details.product_name,
                        gaps=[
                            ProductAttributeGap(
                                attribute=gap.attribute,
                                allowable_values=gap.allowable_values,
                            )
                            for gap in sample.gaps
                        ],
                    )
                ],
            )

            for prediction in predictions:
                result = PredictionResultRecord(
                    prediction_key=str(uuid4()),
                    experiment_key=experiment_key,
                    product_key=sample.product_details.product_code,
                    attribute_key=(
                        self.repository.attribute_repo.get_by_friendly_name(
                            prediction.attribute
                        ).attribute_key
                    ),
                    value=prediction.predicted_value,
                    confidence=prediction.confidence,
                )
                self.prediction_repo.add(result)

            self.session.commit()

        return experiment_key

    async def run_for_product(self, product_key: str) -> str:
        """
        Run predictions for a single product.

        Args:
            product_key: The product key to predict values for

        Returns:
            The experiment key for this run
        """
        try:
            # Create new experiment
            experiment_key = str(uuid4())
            experiment = PredictionExperimentRecord(
                experiment_key=experiment_key,
                metadata=self.metadata,
            )
            self.experiment_repo.add(experiment)

            # Load product details and gaps
            product_details = self.repository.get_product_details(product_key)
            product_gaps = self.repository.get_product_gaps(product_key)

            # Make predictions
            predictions = await self.service.predict_multiple_attributes(
                product=product_details,
                gaps=[product_gaps],
            )

            # Store predictions
            for prediction in predictions:
                result = PredictionResultRecord(
                    prediction_key=str(uuid4()),
                    experiment_key=experiment_key,
                    product_key=product_key,
                    attribute_key=(
                        self.repository.attribute_repo.get_by_friendly_name(
                            prediction.attribute
                        ).attribute_key
                    ),
                    value=prediction.predicted_value,
                    confidence=prediction.confidence,
                )
                self.prediction_repo.add(result)

            self.session.commit()
            return experiment_key

        except ValueError as e:
            print(f"Warning: Could not process product {product_key}: {e}")
            self.session.rollback()
            raise
