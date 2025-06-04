#!/usr/bin/env python3
import argparse
import asyncio
import logging
from datetime import datetime
from collections import Counter

from src.common.db import SessionLocal
from src.common.logs import setup_logging
from src.core.facet_inference.orchestration.orchestrator import (
    FacetInferenceOrchestrator,
)
from src.core.infrastructure.database.input_data.records import HumanRecommendationRecord
from sqlalchemy import select

logger = logging.getLogger(__name__)
setup_logging()


def count_recommendation_types(session):
    """Count the different types of recommendations in the database."""
    recommendations = session.scalars(select(HumanRecommendationRecord)).all()
    action_counts = Counter(rec.action for rec in recommendations)
    
    logger.info("\nRecommendation type counts:")
    for action, count in action_counts.items():
        logger.info(f"{action}: {count}")
    
    return action_counts


async def main():
    parser = argparse.ArgumentParser(
        description="Run a facet inference experiment"
    )
    parser.add_argument(
        "--description",
        type=str,
        help="Description of the experiment",
        default=None,
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of products to process",
        default=None,
    )
    parser.add_argument(
        "--product",
        type=str,
        help="Run experiment for a single product key",
        default=None,
    )
    args = parser.parse_args()

    with SessionLocal() as session:
        # Count recommendation types before running experiment
        count_recommendation_types(session)
        
        # Create orchestrator
        orchestrator = FacetInferenceOrchestrator(
            session=session,
            description=args.description,
            metadata={
                "start_time": datetime.now().isoformat(),
                "command_line_args": vars(args),
            },
        )

        logger.info("Starting experiment...")
        start_time = datetime.now()

        if args.product:
            logger.info(
                f"Running experiment for single product: {args.product}"
            )
            experiment_key = await orchestrator.run_experiment(limit=1)
        else:
            experiment_key = await orchestrator.run_experiment(
                limit=args.limit
            )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("Experiment completed:")
        logger.info(f"  Key: {experiment_key}")
        logger.info(f"  Duration: {duration:.2f} seconds")

        if args.product:
            logger.info(f"  Processed single product: {args.product}")
        elif args.limit:
            logger.info(f"  Processed {args.limit} products")
        else:
            logger.info("  Processed all products with gaps")


if __name__ == "__main__":
    asyncio.run(main())
