import logging
from pathlib import Path
from typing import Any, Callable

from openpyxl import load_workbook
from tqdm import tqdm

from src.csv_ingestion.processors.types import ProcessingResult

logger = logging.getLogger(__name__)


def process_excel_file(
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

    return ProcessingResult(
        rows_processed=rows_processed,
        rows_skipped=rows_skipped,
        total_processed=total_processed,
    )
