#!/usr/bin/env python3

import argparse
import logging

from src.log_utils import setup_logging
from src.raw_csv_ingestion import ingest_csv_files
from src.raw_csv_ingestion.code_types import ProductCodeType

logger = logging.getLogger(__name__)
setup_logging()


def main():
    parser = argparse.ArgumentParser(
        description="Ingest CSV files into the database"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="data",
        help="Directory containing CSV files (default: data)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of rows to process in each batch (default: 1000)",
    )
    parser.add_argument(
        "--row-limit",
        type=int,
        default=None,
        help="Maximum number of rows to process per file (default: no limit)",
    )
    parser.add_argument(
        "--code-type",
        type=str,
        choices=[t.value for t in ProductCodeType],
        help=(
            "Force a specific code type for all products "
            "(default: auto-detect)"
        ),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    try:
        ingest_csv_files(
            directory=args.directory,
            batch_size=args.batch_size,
            row_limit=args.row_limit,
            code_type=args.code_type,
        )
    except Exception as e:
        logger.error(f"Error during raw data ingestion: {str(e)}")
        raise


if __name__ == "__main__":
    main()
