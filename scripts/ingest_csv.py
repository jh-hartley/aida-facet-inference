#!/usr/bin/env python3
import argparse
import logging

from src.log_utils import setup_logging
from src.raw_csv_ingest import ingest_csv_files

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

    args = parser.parse_args()

    try:
        ingest_csv_files(directory=args.directory, batch_size=args.batch_size)
    except Exception as e:
        logging.error(f"Error during CSV ingestion: {str(e)}")
        raise


if __name__ == "__main__":
    main()
