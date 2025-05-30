import csv
import logging
from pathlib import Path
from typing import Any, Callable, Type, cast

import pandas as pd
from tqdm import tqdm

from src.raw_csv_ingestion.config import CSVConfig

logger = logging.getLogger(__name__)


def validate_directory(directory: Path) -> None:
    """
    Validate that the directory contains all required files.
    Only checks for files that are explicitly configured in CSVConfig.FILE_CONFIGS.
    """
    missing_files = []
    for filename, config in CSVConfig.FILE_CONFIGS.items():
        if not config:
            continue
        if not (directory / f"{filename}.csv").exists() and not (directory / f"{filename}.xlsx").exists():
            missing_files.append(filename)

    if missing_files:
        raise ValueError(
            f"Missing required files in {directory}: "
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


def process_excel_file(
    file_path: Path,
    model_type: Type[Any],
    create_func: Callable[..., Any],
    batch_size: int = 1000,
    column_mapping: dict[str, str] | None = None,
    row_limit: int | None = None,
) -> tuple[int, int]:
    """
    Process a single Excel file and return the number of rows processed and skipped.
    """
    rows_processed = 0
    rows_skipped = 0
    total_processed = 0

    df = pd.read_excel(file_path)
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
        total=len(df),
    )

    batch = []
    for _, row in df.iterrows():
        if row_limit and total_processed >= row_limit:
            break

        if column_mapping:
            mapped_line = {
                param_name: str(row[col_name])
                for col_name, param_name in column_mapping.items()
            }
        else:
            mapped_line = {k: str(v) for k, v in row.items()}
        
        batch.append(mapped_line)
        total_processed += 1

        if len(batch) >= batch_size:
            for line in batch:
                result = create_func(**line)
                if result is None:
                    rows_skipped += 1
                else:
                    rows_processed += 1
                pbar.update(1)
            batch = []

    for line in batch:
        result = create_func(**line)
        if result is None:
            rows_skipped += 1
        else:
            rows_processed += 1
        pbar.update(1)

    pbar.close()
    return rows_processed, rows_skipped


def ingest_csv_files(
    directory: Path | str = Path("data"),
    batch_size: int = 1000,
    row_limit: int | None = None,
) -> None:
    """
    Ingest all files from the specified directory into the database.
    Only processes files that are explicitly configured in CSVConfig.FILE_CONFIGS.
    """
    directory = Path(directory)
    validate_directory(directory)

    for filename, config in CSVConfig.FILE_CONFIGS.items():
        if not config:
            logger.info(f"Skipping {filename} as it is not configured")
            continue
            
        try:
            logger.debug(f"Starting to process {filename}")
            file_path = directory / f"{filename}.xlsx"
            if not file_path.exists():
                file_path = directory / f"{filename}.csv"
            
            model = cast(Type[Any], config["model"])
            create_func = cast(Callable[..., Any], config["create_func"])
            column_mapping = cast(
                dict[str, str] | None, config.get("column_mapping")
            )

            if file_path.suffix.lower() == '.xlsx':
                rows_processed, rows_skipped = process_excel_file(
                    file_path,
                    model,
                    create_func,
                    batch_size,
                    column_mapping,
                    row_limit,
                )
            else:
                rows_processed, rows_skipped = process_csv_file(
                    file_path,
                    model,
                    create_func,
                    batch_size,
                    column_mapping,
                    row_limit,
                )

            logger.info(
                f"Processed {rows_processed} rows from {file_path.name} "
                f"({rows_skipped} duplicates skipped)"
            )
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            raise
