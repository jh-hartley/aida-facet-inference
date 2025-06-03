import logging
import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from src.common.clock import clock
from src.common.db import SessionLocal, db_session, uuid
from src.core.domain.models import FacetPrediction
from src.core.domain.repositories import (
    FacetIdentificationRepository,
    PredictionExperimentRepository,
    PredictionResultRepository,
)
from src.core.domain.types import ProductAttributeGap
from src.core.facet_inference.service import FacetInferenceService
from src.core.infrastructure.database.input_data.records import (
    HumanRecommendationRecord,
    RawAttributeRecord,
    RawProductRecord,
)
from src.core.infrastructure.database.input_data.repositories import (
    RawAttributeRepository,
    RawProductRepository,
)
from src.core.infrastructure.database.predictions.records import (
    PredictionExperimentRecord,
    PredictionResultRecord,
)

logger = logging.getLogger(__name__)


def create_prediction_experiment(
    description: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> PredictionExperimentRecord:
    """Create a new prediction experiment record."""
    with db_session().begin() as session:
        repo = PredictionExperimentRepository(session)

        experiment_key = str(uuid())
        experiment = PredictionExperimentRecord(
            experiment_key=experiment_key,
            metadata={
                "description": description or "No description provided",
                "timestamp": clock.now().isoformat(),
                **(metadata or {}),
            },
            started_at=clock.now(),
        )
        return repo.create(experiment)


def update_experiment_metrics(
    experiment_key: str,
    total_predictions: int,
    total_products: int,
    elapsed_time: float,
) -> None:
    """Update experiment metrics after completion."""
    with db_session().begin() as session:
        repo = PredictionExperimentRepository(session)
        experiment = repo.get_by_experiment_key(experiment_key)

        experiment.completed_at = clock.now()
        experiment.total_predictions = total_predictions
        experiment.total_products = total_products
        experiment.average_time_per_prediction = (
            elapsed_time / total_predictions if total_predictions > 0 else None
        )

        session.add(experiment)


def create_prediction_result(
    experiment_key: str,
    product_key: str,
    attribute_key: str,
    value: str,
    confidence: float,
) -> PredictionResultRecord:
    """Create a new prediction result record."""
    with db_session().begin() as session:
        repo = PredictionResultRepository(session)

        result = PredictionResultRecord(
            prediction_key=str(uuid()),
            experiment_key=experiment_key,
            product_key=product_key,
            attribute_key=attribute_key,
            value=value,
            confidence=confidence,
        )
        return repo.create(result)


class ExperimentOrchestrator:
    """Orchestrates running prediction experiments."""

    def __init__(
        self,
        session: Session,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.session = session
        self.repository = FacetIdentificationRepository(session)
        self.description = description
        self.metadata = metadata or {}

    def _create_experiment(self) -> str:
        """Create a new experiment record and return its key."""
        with SessionLocal() as session:
            repo = PredictionExperimentRepository(session)
            experiment_key = str(uuid())
            experiment = PredictionExperimentRecord(
                experiment_key=experiment_key,
                experiment_metadata={
                    "description": self.description
                    or "No description provided",
                    "timestamp": clock.now().isoformat(),
                    **(self.metadata or {}),
                },
                started_at=clock.now(),
            )
            repo.create(experiment)
            session.commit()  # Explicitly commit the transaction
            return experiment_key

    def _get_accepted_recommendations(
        self, session: Session
    ) -> dict[str, list[HumanRecommendationRecord]]:
        """
        Get all accepted recommendations grouped by product reference.
        Returns a dict of {product_reference: [recommendations]}
        """
        recommendations = session.scalars(
            select(HumanRecommendationRecord).where(
                HumanRecommendationRecord.action == "Accept Recommendation"
            )
        ).all()

        product_recommendations: dict[str, list[HumanRecommendationRecord]] = (
            {}
        )
        for rec in recommendations:
            if rec.product_reference not in product_recommendations:
                product_recommendations[rec.product_reference] = []
            product_recommendations[rec.product_reference].append(rec)

        return product_recommendations

    def _get_product_key_from_system_name(
        self, session: Session, system_name: str
    ) -> str | None:
        """Get product key from system name."""
        product = session.scalars(
            select(RawProductRecord).where(
                RawProductRecord.system_name == system_name
            )
        ).first()
        return product.product_key if product else None

    def _get_attribute_key_from_system_name(
        self, session: Session, system_name: str
    ) -> str | None:
        """Get attribute key from system name."""
        attribute = session.scalars(
            select(RawAttributeRecord).where(
                RawAttributeRecord.system_name == system_name
            )
        ).first()
        return attribute.attribute_key if attribute else None

    def _get_allowable_values(
        self, session: Session, attribute_key: str
    ) -> list[str]:
        """Get allowable values for an attribute."""
        # Get values from category-specific rules
        category_values = list(
            session.scalars(
                select(text("value"))
                .select_from(text("raw_category_allowable_values"))
                .where(text("attribute_key = :attribute_key"))
                .params(attribute_key=attribute_key)
            ).all()
        )

        global_values = list(
            session.scalars(
                select(text("value"))
                .select_from(
                    text(
                        "raw_attribute_allowable_values_"
                        "applicable_in_every_category"
                    )
                )
                .where(text("attribute_key = :attribute_key"))
                .params(attribute_key=attribute_key)
            ).all()
        )

        # Get values from any-category rules
        any_category_values = list(
            session.scalars(
                select(text("value"))
                .select_from(
                    text("raw_attribute_allowable_values_in_any_category")
                )
                .where(text("attribute_key = :attribute_key"))
                .params(attribute_key=attribute_key)
            ).all()
        )

        # Combine all values and remove duplicates
        return sorted(
            list(set(category_values + global_values + any_category_values))
        )

    def _store_predictions(
        self,
        experiment_key: str,
        product_key: str,
        predictions: list[FacetPrediction],
    ) -> None:
        """Store all predictions for a product in a single transaction."""
        with SessionLocal() as session:
            repo = PredictionResultRepository(session)
            facet_repo = FacetIdentificationRepository(session)
            product_repo = RawProductRepository(session)
            attribute_repo = RawAttributeRepository(session)

            # Get gaps with ground truth to link to recommendations
            gaps_with_truth = facet_repo.get_product_gaps_with_ground_truth(
                product_key
            )
            logger.info(f"Found {len(gaps_with_truth)} gaps with ground truth")

            # Get the product to get its system_name
            product = product_repo.get_by_id(product_key)
            if not product:
                logger.error(f"Product not found for key: {product_key}")
                return
            logger.info(f"Product system_name: {product.system_name}")

            # Get recommendations for this product using system_name
            recommendations = session.execute(
                select(text("*"))
                .select_from(text("human_recommendations"))
                .where(text("product_reference = :system_name")),
                {"system_name": product.system_name},
            ).all()
            logger.info(
                f"Found {len(recommendations)} recommendations "
                f"for product {product_key}"
            )

            attribute_to_recommendation = {}
            for rec in recommendations:
                attribute = attribute_repo.session.scalars(
                    select(RawAttributeRecord).where(
                        RawAttributeRecord.system_name
                        == rec.attribute_reference
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
                f"Created lookup with {len(attribute_to_recommendation)} "
                f"entries"
            )

            for prediction in predictions:
                attribute = facet_repo.attribute_repo.get_by_friendly_name(
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
                repo.create(result)

            session.commit()
            logger.info(
                f"Committed {len(predictions)} predictions to database"
            )

    def _update_experiment_metrics(
        self,
        experiment_key: str,
        total_predictions: int,
        total_products: int,
        elapsed_time: float,
    ) -> None:
        """Update experiment metrics."""
        with SessionLocal() as session:
            repo = PredictionExperimentRepository(session)
            experiment = repo.get_by_experiment_key(experiment_key)
            experiment.completed_at = datetime.now(timezone.utc)
            experiment.total_predictions = total_predictions
            experiment.total_products = total_products
            experiment.average_time_per_prediction = (
                elapsed_time / total_predictions
                if total_predictions > 0
                else None
            )
            session.add(experiment)
            session.commit()  # Ensure changes are saved

    async def run_experiment(self, limit: int | None = None) -> str:
        """
        Run a prediction experiment for multiple products.

        Args:
            limit: Optional limit on number of products to process

        Returns:
            The experiment key for this run
        """
        start_time = time.time()

        # Step 1: Create experiment
        experiment_key = self._create_experiment()
        logger.info(f"Created experiment {experiment_key}")

        try:
            with SessionLocal() as session:
                # Step 2: Get all accepted recommendations and group by product
                product_recommendations = self._get_accepted_recommendations(
                    session
                )
                logger.info(
                    f"Found accepted recommendations for "
                    f"{len(product_recommendations)} products"
                )

                # Step 3: Process each product's recommendations
                service = FacetInferenceService.from_session(session)
                total_predictions = 0
                processed_products = 0

                for system_name, recs in product_recommendations.items():
                    if limit and processed_products >= limit:
                        break

                    try:
                        # Get product key from system name
                        product_key = self._get_product_key_from_system_name(
                            session, system_name
                        )
                        if not product_key:
                            logger.warning(
                                f"No product found for system name: "
                                f"{system_name}"
                            )
                            continue

                        logger.info(
                            f"Processing product {product_key} "
                            f"({system_name}) "
                            f"with {len(recs)} accepted recommendations"
                        )

                        # Get gaps that have recommendations
                        gaps = []
                        for rec in recs:
                            # Get attribute key from system name
                            attribute_key = (
                                self._get_attribute_key_from_system_name(
                                    session, rec.attribute_reference
                                )
                            )
                            if attribute_key:
                                # Get attribute details
                                attribute = session.scalars(
                                    select(RawAttributeRecord).where(
                                        RawAttributeRecord.attribute_key
                                        == attribute_key
                                    )
                                ).first()

                                if attribute:
                                    # Get allowable values
                                    allowable_values = (
                                        self._get_allowable_values(
                                            session, attribute_key
                                        )
                                    )

                                    gaps.append(
                                        ProductAttributeGap(
                                            attribute=attribute.friendly_name,
                                            allowable_values=allowable_values,
                                        )
                                    )
                                    logger.info(
                                        f"Added gap for attribute "
                                        f"{attribute.friendly_name} "
                                        f"with {len(allowable_values)} "
                                        f"allowable values"
                                    )
                                else:
                                    logger.warning(
                                        f"No attribute found for key: "
                                        f"{attribute_key}"
                                    )
                            else:
                                logger.warning(
                                    f"No attribute found for system name: "
                                    f"{rec.attribute_reference}"
                                )

                        if not gaps:
                            logger.warning(
                                f"No valid gaps found for product "
                                f"{product_key}"
                            )
                            continue

                        # Process gaps
                        predictions = await service.predict_for_product_key(
                            product_key, evaluation_mode=True
                        )
                        logger.info(
                            f"Generated {len(predictions)} predictions"
                        )

                        # Store predictions
                        self._store_predictions(
                            experiment_key, product_key, list(predictions)
                        )
                        total_predictions += len(predictions)
                        processed_products += 1

                    except Exception as e:
                        logger.error(
                            f"Error processing product {system_name}: {e}"
                        )
                        continue

                # Step 5: Update experiment metrics
                elapsed_time = time.time() - start_time
                self._update_experiment_metrics(
                    experiment_key,
                    total_predictions=total_predictions,
                    total_products=processed_products,
                    elapsed_time=elapsed_time,
                )

                logger.info(
                    f"Successfully processed {processed_products} products "
                    f"({total_predictions} predictions in {elapsed_time:.2f}s)"
                )

                return experiment_key

        except Exception as e:
            logger.error(f"Error running experiment: {e}")
            raise
