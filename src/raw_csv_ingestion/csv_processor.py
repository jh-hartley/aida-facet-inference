import csv
import logging
from pathlib import Path
from typing import Any, Callable, Type, cast

from openpyxl import load_workbook
from tqdm import tqdm

from src.raw_csv_ingestion.config import CSVConfig

logger = logging.getLogger(__name__)


def validate_directory(directory: Path) -> None:
    """
    Validate that the directory contains all required files.
    Only checks for files that are explicitly configured in
    CSVConfig.FILE_CONFIGS.
    """
    missing_files = []
    for filename, config in CSVConfig.FILE_CONFIGS.items():
        if not config:
            continue
        if (
            not (directory / f"{filename}.csv").exists()
            and not (directory / f"{filename}.xlsx").exists()
        ):
            missing_files.append(filename)

    if missing_files:
        raise ValueError(
            f"Missing required files in {directory}: "
            f"{', '.join(missing_files)}"
        )


def count_lines(file_path: Path) -> int:
    """Count the number of lines in a file, excluding the header."""
    with open(file_path, "rb") as f:
        return sum(1 for _ in f) - 1


def process_csv_file(
    file_path: Path,
    create_func: Callable[..., Any],
    batch_size: int = 1000,
    column_mapping: dict[str, str] | None = None,
    row_limit: int | None = None,
) -> tuple[int, int]:
    """
    Process a single CSV file in batches and return
    the number of rows processed and skipped.
    """
    rows_processed = 0
    rows_skipped = 0
    total_processed = 0

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
        total=None,
    )

    with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

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

            for record in batch:
                if row_limit and total_processed >= row_limit:
                    break

                result = create_func(**record)
                if result is None:
                    rows_skipped += 1
                else:
                    rows_processed += 1
                total_processed += 1
                pbar.update(1)

            if row_limit and total_processed >= row_limit:
                break

    pbar.close()
    logger.info(
        f"Processed {rows_processed} rows from {file_path.name} "
        f"({rows_skipped} duplicates skipped)"
    )

    return rows_processed, rows_skipped


def process_excel_file(
    file_path: Path,
    create_func: Callable[..., Any],
    batch_size: int = 1000,
    column_mapping: dict[str, str] | None = None,
    row_limit: int | None = None,
) -> tuple[int, int]:
    """
    Process a single Excel file in batches and return
    the number of rows processed and skipped.
    """
    rows_processed = 0
    rows_skipped = 0
    total_processed = 0

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
        total=None,
    )

    wb = load_workbook(filename=file_path, read_only=True)
    ws = wb.active
    if ws is None:
        raise ValueError(f"No active worksheet found in {file_path}")

    headers = [
        str(cell.value) if cell.value is not None else ""
        for cell in next(ws.rows)
    ]

    batch = []
    for row in ws.rows:
        if row_limit and total_processed >= row_limit:
            break

        row_dict: dict[str, str] = dict(
            zip(
                headers,
                [
                    str(cell.value) if cell.value is not None else ""
                    for cell in row
                ],
            )
        )

        if column_mapping:
            mapped_row = {
                param_name: row_dict[col_name]
                for col_name, param_name in column_mapping.items()
            }
        else:
            mapped_row = row_dict

        batch.append(mapped_row)

        if len(batch) >= batch_size:
            for record in batch:
                if row_limit and total_processed >= row_limit:
                    break

                result = create_func(**record)
                if result is None:
                    rows_skipped += 1
                else:
                    rows_processed += 1
                total_processed += 1
                pbar.update(1)

            batch = []  # Clear batch after processing

    for record in batch:
        if row_limit and total_processed >= row_limit:
            break

        result = create_func(**record)
        if result is None:
            rows_skipped += 1
        else:
            rows_processed += 1
        total_processed += 1
        pbar.update(1)

    pbar.close()
    logger.info(
        f"Processed {rows_processed} rows from {file_path.name} "
        f"({rows_skipped} duplicates skipped)"
    )

    return rows_processed, rows_skipped


def ingest_csv_files(
    directory: Path | str = Path("data"),
    batch_size: int = 1000,
    row_limit: int | None = None,
    code_type: str | None = None,
) -> None:
    """
    Ingest all files from the specified directory into the database.
    Only processes files that are explicitly configured in
    CSVConfig.FILE_CONFIGS.

    Args:
        directory: Directory containing CSV files
        batch_size: Number of rows to process in each batch
        row_limit: Maximum number of rows to process per file
        code_type: Optional code type to use for all products
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

            create_func = cast(Callable[..., Any], config["create_func"])
            column_mapping = cast(
                dict[str, str] | None, config.get("column_mapping")
            )

            if filename == "Product" and code_type is not None:
                create_func = cast(
                    Callable[..., Any],
                    lambda **kwargs: create_func(
                        **kwargs, code_type=code_type
                    ),
                )

            if file_path.suffix.lower() == ".xlsx":
                process_excel_file(
                    file_path,
                    create_func,
                    batch_size,
                    column_mapping,
                    row_limit,
                )
            else:
                process_csv_file(
                    file_path,
                    create_func,
                    batch_size,
                    column_mapping,
                    row_limit,
                )
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            raise
