#!/usr/bin/env python3
import argparse
import asyncio
import logging
from datetime import datetime

from src.common.db import SessionLocal
from src.core.facet_inference.jobs import ExperimentOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        # Create orchestrator
        orchestrator = ExperimentOrchestrator(
            session=session,
            description=args.description,
            metadata={
                "start_time": datetime.now().isoformat(),
                "command_line_args": vars(args),
            },
        )

        # Run experiment
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
