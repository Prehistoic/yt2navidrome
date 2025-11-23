"""Setup logging utilities for the application."""

import logging
import logging.config
import os

from yt2navidrome.config import PROJECT_NAME


def setup_logging(config_file: str = "logging.conf") -> None:
    """
    Configures the logging for the application using an external conf file.
    """
    # Find config_path in the same directory as this file by default
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    if os.path.exists(config_path):
        # disable_existing_loggers=False is important to keep
        # third-party loggers alive if they were already imported.
        logging.config.fileConfig(config_path, disable_existing_loggers=False)
    else:
        # Fallback if config file is missing
        logging.basicConfig(level=logging.INFO)
        logging.warning(f"Logging configuration file '{config_path}' not found. Using basicConfig.")


def get_logger(module_name: str) -> logging.Logger:
    """
    Creates a child logger of the main application.

    Usage:
        logger = get_logger(__name__)
    """
    if module_name == "__main__":
        return logging.getLogger(PROJECT_NAME)

    if not module_name.startswith(PROJECT_NAME):
        return logging.getLogger(f"{PROJECT_NAME}.{module_name}")

    return logging.getLogger(module_name)


def set_global_logging_level(level=logging.INFO) -> None:  # type: ignore[no-untyped-def]
    """
    Sets the global logging level for the root logger.

    Args:
        level: The new logging level (e.g., logging.DEBUG, logging.INFO).
    """
    logging.getLogger(PROJECT_NAME).setLevel(level)


def disable_all_logging() -> None:
    """
    Disables all logs.
    """
    logging.disable(logging.CRITICAL)
