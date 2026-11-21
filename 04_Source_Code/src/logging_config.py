"""JSON logs on stderr. The decision log is a separate SQLite record."""

from __future__ import annotations

import logging

try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:  # python-json-logger 2.x
    from pythonjsonlogger import jsonlogger

    JsonFormatter = jsonlogger.JsonFormatter

from src.config import get_settings

_CONFIGURED = False


def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    settings = get_settings()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())
    _CONFIGURED = True
