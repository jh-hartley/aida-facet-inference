import csv
import logging
from pathlib import Path
from typing import Any, Callable, Type, cast

from tqdm import tqdm

from src.raw_csv_ingest.config import CSVConfig

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


def count_lines(file_path: Path) -> int:
    """Count the number of lines in a file, excluding the header."""
    with open(file_path, "rb") as f:
        return sum(1 for _ in f) - 1  # Subtract 1 for header


def process_csv_file(
    file_path: Path,
    model_type: Type[Any],
    create_func: Callable[..., Any],
    batch_size: int = 1000,
    column_mapping: dict[str, str] | None = None,
    row_limit: int | None = None,
) -> tuple[int, int]:
    """
    Process a single CSV file, streaming it line by line and return
    the number of rows processed and skipped.
    """
    rows_processed = 0
    rows_skipped = 0
    total_processed = 0

    with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        logger.debug(f"Processing {file_path} (limit: {row_limit or 'none'})")

        pbar = tqdm(
            desc=file_path.name,
            unit="rows",
            leave=True,
            bar_format=(
                "{l_bar}{bar}| {n_fmt}/{total_fmt} "
                "[{elapsed}<{remaining}, {rate_fmt}]"
            ),
            dynamic_ncols=True,
            total=float("inf"),
        )

        while True:
            # Read next batch
            batch = []
            for _ in range(batch_size):
                try:
                    line = next(reader)
                    if column_mapping:
                        mapped_line = {
                            param_name: line[col_name]
                            for col_name, param_name in column_mapping.items()
                        }
                    else:
                        mapped_line = line
                    batch.append(mapped_line)
                except StopIteration:
                    break

            if not batch:
                break

            # Process batch
            for line in batch:
                if row_limit and total_processed >= row_limit:
                    break
                result = create_func(**line)
                if result is None:
                    rows_skipped += 1
                else:
                    rows_processed += 1
                total_processed += 1
                pbar.update(1)

            if row_limit and total_processed >= row_limit:
                break

        pbar.close()

    return rows_processed, rows_skipped


def ingest_csv_files(
    directory: Path | str = Path("data"),
    batch_size: int = 1000,
    row_limit: int | None = None,
) -> None:
    """
    Ingest all CSV files from the specified directory into the database.
    """
    directory = Path(directory)
    validate_directory(directory)

    for filename, config in CSVConfig.FILE_CONFIGS.items():
        try:
            logger.debug(f"Starting to process {filename}")
            file_path = directory / filename
            model = cast(Type[Any], config["model"])
            create_func = cast(Callable[..., Any], config["create_func"])
            column_mapping = cast(
                dict[str, str] | None, config.get("column_mapping")
            )
            rows_processed, rows_skipped = process_csv_file(
                file_path,
                model,
                create_func,
                batch_size,
                column_mapping,
                row_limit,
            )
            logger.info(
                f"Processed {rows_processed} rows from {filename} "
                f"({rows_skipped} duplicates skipped)"
            )
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            raise
