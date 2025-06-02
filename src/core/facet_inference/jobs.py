# import logging
# import time
# from typing import Any
# from uuid import uuid4

# from sqlalchemy.orm import Session

# from src.core.facet_inference.data import FacetInferenceDataLoader
# from src.core.facet_inference.service import FacetInferenceService
# from src.core.models import ProductGaps
# from src.core.records import (
#     PredictionExperimentRecord,
#     PredictionResultRecord,
# )
# from src.core.repositories import (
#     FacetIdentificationRepository,
#     PredictionExperimentRepository,
#     PredictionResultRepository,
# )
# from src.core.types import ProductAttributeGap
# from src.db.connection import db_session
# from src.utils.clock import clock

# logger = logging.getLogger(__name__)


# def create_prediction_experiment(
#     description: str | None = None,
#     metadata: dict[str, Any] | None = None,
# ) -> PredictionExperimentRecord:
#     """Create a new prediction experiment record."""
#     with db_session().begin() as session:
#         repo = PredictionExperimentRepository(session)

#         experiment_key = str(uuid4())
#         experiment = PredictionExperimentRecord(
#             experiment_key=experiment_key,
#             metadata={
#                 "description": description or "No description provided",
#                 "timestamp": clock.now().isoformat(),
#                 **(metadata or {}),
#             },
#             started_at=clock.now(),
#         )
#         return repo.create(experiment)


# def update_experiment_metrics(
#     experiment_key: str,
#     total_predictions: int,
#     total_products: int,
#     elapsed_time: float,
# ) -> None:
#     """Update experiment metrics after completion."""
#     with db_session().begin() as session:
#         repo = PredictionExperimentRepository(session)
#         experiment = repo.get_by_experiment_key(experiment_key)

#         experiment.completed_at = clock.now()
#         experiment.total_predictions = total_predictions
#         experiment.total_products = total_products
#         experiment.average_time_per_prediction = (
#             elapsed_time / total_predictions
#             if total_predictions > 0
#             else None
#         )

#         session.add(experiment)


# def create_prediction_result(
#     experiment_key: str,
#     product_key: str,
#     attribute_key: str,
#     value: str,
#     confidence: float,
# ) -> PredictionResultRecord:
#     """Create a new prediction result record."""
#     with db_session().begin() as session:
#         repo = PredictionResultRepository(session)

#         result = PredictionResultRecord(
#             prediction_key=str(uuid4()),
#             experiment_key=experiment_key,
#             product_key=product_key,
#             attribute_key=attribute_key,
#             value=value,
#             confidence=confidence,
#         )
#         return repo.create(result)


# class FacetPredictionJob:
#     """Job for predicting missing attribute values for products."""

#     def __init__(
#         self,
#         session: Session,
#         service: FacetInferenceService | None = None,
#         description: str | None = None,
#         metadata: dict[str, Any] | None = None,
#     ):
#         self.session = session
#         self.repository = FacetIdentificationRepository(session)
#         self.service = service  # We'll create the service per product
#         self.data_loader = FacetInferenceDataLoader(self.repository)
#         self.description = description
#         self.metadata = metadata or {}

#     def add_metadata(self, key: str, value: Any) -> None:
#         """Add a key-value pair to the experiment metadata."""
#         self.metadata[key] = value

#     def set_description(self, description: str) -> None:
#         """Set the experiment description."""
#         self.description = description

#     async def run(self, limit: int | None = None) -> str:
#         """
#         Run the prediction job for products with missing attributes.

#         This will:
#         1. Create a new experiment
#         2. Load products with gaps (optionally limited to first N products)
#         3. Make predictions for each gap
#         4. Store predictions in the database
#         5. Update experiment metrics with timing information

#         Args:
#             limit: Optional number of products to process. If None, process
#                 all products.

#         Returns:
#             The experiment key for this run
#         """
#         start_time = time.time()
#         experiment = create_prediction_experiment(
#             description=self.description,
#             metadata=self.metadata,
#         )
#         experiment_key = experiment.experiment_key

#         product_keys = self.repository.get_products_with_gaps()
#         if limit is not None:
#             product_keys = product_keys[:limit]
#             logger.debug(
#                 f"Limited to first {limit} products "
#                 f"out of {len(product_keys)} total"
#             )

#         dataset = self.data_loader.load_dataset(product_keys)
#         logger.info(
#             f"Starting prediction job for {len(dataset.samples)} products"
#         )

#         processed_count = 0
#         error_count = 0
#         total_predictions = 0

#         for sample in dataset.samples:
#             try:
#                 # Create a new service instance for each product
#                 service = FacetInferenceService(
#                     product_details=sample.product_details,
#                     product_gaps=ProductGaps(
#                         product_code=sample.product_details.product_code,
#                         product_name=sample.product_details.product_name,
#                         gaps=[
#                             ProductAttributeGap(
#                                 attribute=gap.attribute,
#                                 allowable_values=gap.allowable_values,
#                             )
#                             for gap in sample.gaps
#                         ],
#                     ),
#                 )

#                 predictions = await service.predict_multiple_attributes(
#                     gaps=[
#                         ProductAttributeGap(
#                             attribute=gap.attribute,
#                             allowable_values=gap.allowable_values,
#                         )
#                         for gap in sample.gaps
#                     ],
#                 )

#                 for prediction in predictions:
#                     attribute_key = (
#                         self.repository.attribute_repo.get_by_friendly_name(
#                             prediction.attribute
#                         ).attribute_key
#                     )

#                     create_prediction_result(
#                         experiment_key=experiment_key,
#                         product_key=sample.product_details.product_code,
#                         attribute_key=attribute_key,
#                         value=prediction.predicted_value,
#                         confidence=prediction.confidence,
#                     )
#                     total_predictions += 1

#                 processed_count += 1

#             except Exception as e:
#                 error_count += 1
#                 logger.warning(
#                     f"Error processing product "
#                     f"{sample.product_details.product_code}: {e}"
#                 )
#                 continue

#         elapsed_time = time.time() - start_time

#         # Update experiment metrics
#         update_experiment_metrics(
#             experiment_key=experiment_key,
#             total_predictions=total_predictions,
#             total_products=processed_count,
#             elapsed_time=elapsed_time,
#         )

#         if error_count > 0:
#             logger.warning(
#                 f"Completed with {error_count} errors out of "
#                 f"{processed_count} products"
#             )
#         else:
#             logger.info(f"Successfully processed {processed_count} products")

#         logger.info(
#             f"Average time per prediction: "
#             f"{elapsed_time/total_predictions:.2f}s "
#             f"({total_predictions/elapsed_time:.2f} predictions/second)"
#         )

#         return experiment_key

#     async def run_for_product(self, product_key: str) -> str:
#         """
#         Run predictions for a single product.

#         Args:
#             product_key: The product key to predict values for

#         Returns:
#             The experiment key for this run
#         """
#         start_time = time.time()
#         try:
#             experiment = create_prediction_experiment(
#                 description=self.description,
#                 metadata=self.metadata,
#             )
#             experiment_key = experiment.experiment_key

#             product_details = self.repository.get_product_details(
#                 product_key
#             )
#             product_gaps = self.repository.get_product_gaps(product_key)

#             # Create a new service instance for this product
#             service = FacetInferenceService(
#                 product_details=product_details,
#                 product_gaps=product_gaps,
#             )

#             predictions = await service.predict_multiple_attributes(
#                 gaps=product_gaps.gaps,
#             )

#             total_predictions = 0
#             for prediction in predictions:
#                 attribute_key = (
#                     self.repository.attribute_repo.get_by_friendly_name(
#                         prediction.attribute
#                     ).attribute_key
#                 )

#                 create_prediction_result(
#                     experiment_key=experiment_key,
#                     product_key=product_key,
#                     attribute_key=attribute_key,
#                     value=prediction.predicted_value,
#                     confidence=prediction.confidence,
#                 )
#                 total_predictions += 1

#             elapsed_time = time.time() - start_time

#             # Update experiment metrics
#             update_experiment_metrics(
#                 experiment_key=experiment_key,
#                 total_predictions=total_predictions,
#                 total_products=1,
#                 elapsed_time=elapsed_time,
#             )

#             logger.info(
#                 f"Successfully processed product {product_key} "
#                 f"({total_predictions} predictions in {elapsed_time:.2f}s)"
#             )
#             return experiment_key

#         except Exception as e:
#             logger.warning(f"Error processing product {product_key}: {e}")
#             raise
