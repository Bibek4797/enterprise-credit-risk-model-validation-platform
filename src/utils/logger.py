"""Enterprise Rotating File Logger Module."""

from __future__ import annotations

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str = "credit_risk_platform",
    log_dir: str | Path = "logs",
    log_level: str = "INFO",
) -> logging.Logger:
    """Set up structured rotating file and console logger."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Application Log Handler
    app_handler = RotatingFileHandler(
        log_path / "app.log", maxBytes=10 * 1024 * 1024, backupCount=5
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)
    logger.addHandler(app_handler)

    # Error Log Handler
    error_handler = RotatingFileHandler(
        log_path / "error.log", maxBytes=10 * 1024 * 1024, backupCount=5
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger
