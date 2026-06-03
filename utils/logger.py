"""Structured logging for the pipeline.

A single configured logger is shared across all modules. Keeps console output
consistent and timestamped without each module reconfiguring logging.
"""

import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%H:%M:%S"

_configured = False


def get_logger(name: str = "research") -> logging.Logger:
    """Return a module-level logger, configuring the root handler once."""
    global _configured
    if not _configured:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        # Avoid duplicate handlers if something already attached one.
        if not root.handlers:
            root.addHandler(handler)
        _configured = True
    return logging.getLogger(name)
