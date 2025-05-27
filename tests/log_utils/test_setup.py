import logging

from src.log_utils.filters import HealthCheckFilter
from src.log_utils.setup import setup_logging


def test_setup_logging_configuration():
    logging.getLogger().setLevel(logging.WARNING)
    for handler in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(handler)

    setup_logging()

    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO

    assert logging.getLogger("WDM").level == logging.WARNING
    assert logging.getLogger("httpx").level == logging.WARNING

    uvicorn_logger = logging.getLogger("uvicorn.access")
    assert any(
        isinstance(f, HealthCheckFilter) for f in uvicorn_logger.filters
    )


def test_health_check_filter():
    filter = HealthCheckFilter()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="GET /health",
        args=(),
        exc_info=None,
    )

    assert not filter.filter(record)

    record.msg = "GET /api/v1/products"
    assert filter.filter(record)
