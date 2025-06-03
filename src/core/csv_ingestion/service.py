import logging
from pathlib import Path
from typing import Any, Callable, cast

from pydantic import BaseModel

from src.core.csv_ingestion.config import CSVConfig
from src.core.csv_ingestion.processors import process_csv_file, process_excel_file

logger = logging.getLogger(__name__)


class RequiredFiles(BaseModel):
    """Configuration for required files in a directory."""

    files: dict[str, bool]

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "RequiredFiles":
        """Create RequiredFiles from a config dictionary."""
        return cls(
            files={
                filename: bool(config) for filename, config in config.items()
            }
        )


def _validate_required_files(
    directory: Path, required_files: RequiredFiles
) -> None:
    """
    Validate that the directory contains all required files in the config.
    """
    missing_files = []
    for filename, is_required in required_files.files.items():
        if not is_required:
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


def ingest_files(
    directory: Path | str = Path("data"),
    batch_size: int = 1000,
    row_limit: int | None = None,
    identifier_type: str | None = None,
) -> None:
    """
    Ingest all files from the specified directory into the database.
    Only processes files that are explicitly configured in
    CSVConfig.FILE_CONFIGS.
    """
    directory = Path(directory)
    _validate_required_files(
        directory,
        RequiredFiles.from_config(CSVConfig.FILE_CONFIGS),
    )

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

            if filename == "Product" and identifier_type is not None:
                create_func = cast(
                    Callable[..., Any],
                    lambda **kwargs: create_func(
                        **kwargs, code_type=identifier_type
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
