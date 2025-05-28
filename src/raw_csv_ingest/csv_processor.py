import csv
import logging
from pathlib import Path
from typing import Any, Callable, Type, cast

from src.raw_csv_ingest.config import CSVConfig
from src.raw_csv_ingest.models import Base

logger = logging.getLogger(__name__)


def validate_directory(directory: Path) -> None:
    """
    Validate that the directory contains all expected CSV files.
    """
    missing_files = []
    for filename in CSVConfig.FILE_CONFIGS:
        if not (directory / filename).exists():
            missing_files.append(filename)

    if missing_files:
        raise ValueError(
            f"Missing required CSV files in {directory}: "
            f"{', '.join(missing_files)}"
        )


def process_csv_file(
    file_path: Path,
    model_type: Type[Base],
    create_func: Callable[[dict], None],
    batch_size: int = 1000,
) -> int:
    """
    Process a single CSV file, streaming it line by line and return
    the number of rows processed.
    """
    rows_processed = 0
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        batch = []
        for line in reader:
            batch.append(line)

            if len(batch) >= batch_size:
                for line in batch:
                    create_func(line)
                    rows_processed += 1
                batch = []

        for line in batch:
            create_func(line)
            rows_processed += 1

    return rows_processed


def ingest_csv_files(
    directory: Path | str = Path("data"),
    batch_size: int = 1000,
) -> None:
    """
    Ingest all CSV files from the specified directory into the database.
    """
    directory = Path(directory)
    validate_directory(directory)

    for filename, config in CSVConfig.FILE_CONFIGS.items():
        try:
            logger.info(f"Starting to process {filename}")
            file_path = directory / filename
            model = cast(Type[Base], config["model"])
            # Workaround as mypy does not like the config
            create_func = cast(
                Callable[[dict[str, Any]], None], config["create_func"]
            )
            rows_processed = process_csv_file(
                file_path, model, create_func, batch_size
            )
            logger.info(f"Processed {rows_processed} rows from {filename}")
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            raise
