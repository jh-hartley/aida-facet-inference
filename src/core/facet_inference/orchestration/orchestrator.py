"""Orchestrates the facet inference workflow."""

import logging
import time
from typing import Any

from sqlalchemy.orm import Session

from src.core.facet_inference.components.experiment_manager import ExperimentManager
from src.core.facet_inference.components.prediction_store import PredictionStore
from src.core.facet_inference.components.product_processor import ProductProcessor
from src.core.facet_inference.data_loading.prediction_loader import PredictionLoader

logger = logging.getLogger(__name__)

class FacetInferenceOrchestrator:
    """Orchestrates the facet inference workflow."""
    
    def __init__(
        self,
        session: Session,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize the orchestrator.
        
        Args:
            session: SQLAlchemy session
            description: Optional description of the experiment
            metadata: Optional metadata for the experiment
        """
        self.session = session
        self.experiment_manager = ExperimentManager(
            session,
            description=description,
            metadata=metadata
        )
        self.product_processor = ProductProcessor(session)
        self.prediction_store = PredictionStore(session)
        self.prediction_loader = PredictionLoader(session)
    
    async def run_experiment(self, limit: int | None = None) -> str:
        """Run a prediction experiment for multiple products.
        
        Args:
            limit: Optional limit on number of products to process
            
        Returns:
            The experiment key for this run
        """
        start_time = time.time()
        total_predictions = 0
        total_products = 0
        
        experiment_key = self.experiment_manager.create_experiment()
        logger.info(f"Created experiment {experiment_key}")
        
        try:
            accepted_recommendations = self.product_processor.get_accepted_recommendations()
            logger.info(f"Found {len(accepted_recommendations)} accepted recommendations")
            
            for product_ref, recommendations in accepted_recommendations.items():
                if limit and total_products >= limit:
                    logger.info(f"Reached limit of {limit} products")
                    break
                    
                try:
                    product_key, predictions = await self.product_processor.process_product(
                        product_ref, recommendations
                    )
                    
                    if not product_key:
                        logger.error(f"No product key found for {product_ref}")
                        continue
                    
                    self.prediction_store.store_predictions(
                        experiment_key,
                        product_key,
                        predictions
                    )
                    
                    total_predictions += len(predictions)
                    total_products += 1
                    
                except Exception as e:
                    logger.error(f"Error processing product {product_ref}: {str(e)}")
                    continue
            
            # Load and validate all predictions for this experiment
            predictions = self.prediction_loader.get_predictions_by_experiment(experiment_key)
            
            if not predictions:
                logger.warning(f"No predictions found for experiment {experiment_key}")
                self.experiment_manager.update_metrics(
                    experiment_key,
                    total_predictions=0,
                    validated_predictions=0,
                    correct_predictions=0,
                    accuracy=0.0
                )
                return experiment_key
                
            self.prediction_loader.validate_predictions(predictions)
            validated_count, accuracy = self.prediction_loader.calculate_accuracy(predictions)
            
            # Calculate correct predictions
            correct_predictions = int(validated_count * accuracy) if validated_count > 0 else 0
            
            elapsed_time = time.time() - start_time
            self.experiment_manager.update_metrics(
                experiment_key,
                total_predictions=total_predictions,
                validated_predictions=validated_count,
                correct_predictions=correct_predictions,
                accuracy=accuracy
            )
            
            # Mark experiment as completed with timestamp
            self.experiment_manager.complete_experiment(experiment_key)
            
            logger.info(
                f"Experiment {experiment_key} completed: "
                f"{total_predictions} total predictions, "
                f"{validated_count} validated, "
                f"{correct_predictions} correct, "
                f"{accuracy:.2%} accuracy"
            )
            
            return experiment_key
            
        except Exception as e:
            logger.error(f"Error running experiment: {str(e)}")
            raise 