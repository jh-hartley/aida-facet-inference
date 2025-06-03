from pydantic import BaseModel


class ProcessingResult(BaseModel):
    """Result of processing a file."""

    rows_processed: int
    rows_skipped: int
    total_processed: int
