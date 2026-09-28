"""One-line logging setup so every module logs the same way."""
import logging

from recruitme.config import load_settings


def setup_logging() -> None:
    logging.basicConfig(
        level=load_settings().log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
