"""Central logging configuration for fetcherio.

Call setup_logging() once at startup (done in app/main.py).
Every other module just calls get_logger(__name__).

Console  → INFO  (operational summaries, no full LLM prompts)
File     → DEBUG (full LLM request/response, SQL, etc.)
"""
import logging
import logging.handlers
from pathlib import Path

_LOG_DIR = Path(__file__).parent.parent / "logs"

_FMT = "%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s"
_DATE_FMT = "%Y-%m-%dT%H:%M:%S"


def setup_logging() -> None:
    _LOG_DIR.mkdir(exist_ok=True)

    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    root = logging.getLogger()
    if root.handlers:
        return  # already configured (e.g. re-imported in tests)
    root.setLevel(logging.DEBUG)

    # Console — INFO and above
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Rotating file — DEBUG and above, 5 MB × 3
    fh = logging.handlers.RotatingFileHandler(
        _LOG_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # Silence noisy third-party loggers
    for lib in ("httpx", "httpcore", "openai._base_client", "uvicorn.access"):
        logging.getLogger(lib).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
