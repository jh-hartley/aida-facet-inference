import csv
import logging
from pathlib import Path
from typing import Any, Callable

from tqdm import tqdm

from src.core.csv_ingestion.processors.types import ProcessingResult

logger = logging.getLogger(__name__)


def process_csv_file(
    file_path: Path,
    create_func: Callable[..., Any],
    batch_size: int = 1000,
    column_mapping: dict[str, str] | None = None,
    row_limit: int | None = None,
) -> ProcessingResult:
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

    return ProcessingResult(
        rows_processed=rows_processed,
        rows_skipped=rows_skipped,
        total_processed=total_processed,
    )
