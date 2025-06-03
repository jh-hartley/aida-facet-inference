"""Orchestrates the facet inference workflow."""

import logging
import time
from typing import Any, Optional

from sqlalchemy.orm import Session

from src.common.db import SessionLocal
from .experiment import ExperimentManager
from .prediction_store import PredictionStore
from .product_processor import ProductProcessor

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
    
    async def run_experiment(self, limit: Optional[int] = None) -> str:
        """Run a prediction experiment for multiple products.
        
        Args:
            limit: Optional limit on number of products to process
            
        Returns:
            The experiment key for this run
        """
        start_time = time.time()
        total_predictions = 0
        total_products = 0
        
        # Create experiment
        experiment_key = self.experiment_manager.create_experiment()
        logger.info(f"Created experiment {experiment_key}")
        
        try:
            # Get accepted recommendations
            accepted_recommendations = self.product_processor.get_accepted_recommendations()
            logger.info(f"Found {len(accepted_recommendations)} accepted recommendations")
            
            # Process each product's recommendations
            for product_ref, recommendations in accepted_recommendations.items():
                if limit and total_predictions >= limit:
                    logger.info(f"Reached limit of {limit} predictions")
                    break
                    
                try:
                    # Process product and get predictions
                    product_key, predictions = await self.product_processor.process_product(
                        product_ref, recommendations
                    )
                    
                    if not product_key:
                        logger.error(f"No product key found for {product_ref}")
                        continue
                    
                    # Store predictions
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
            
            # Update experiment metrics
            elapsed_time = time.time() - start_time
            self.experiment_manager.update_metrics(
                experiment_key,
                total_predictions=total_predictions,
                total_products=total_products,
                elapsed_time=elapsed_time
            )
            
            return experiment_key
            
        except Exception as e:
            logger.error(f"Error running experiment: {str(e)}")
            raise 