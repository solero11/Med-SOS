"""
Shared logging helpers for microservices and the Windows launcher.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

from src.security.deid import scrub_record

try:
    from src.utils import db as db_utils
except Exception:
    db_utils = None


def configure_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a module-level logger.

    The function is intentionally lightweight so services can call it at import
    time without surprising side effects.
    """
    log_level = (level or os.environ.get("SOS_LOG_LEVEL") or "INFO").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    logger.propagate = False
    return logger


METRICS_PATH = Path("_validation/orchestrator_metrics.jsonl")
METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)


def log_turn_metric(event: str, ok: bool, latency_sec: float, extra: Optional[dict] = None) -> None:
    """
    Append a structured JSON line describing a turn request.
    """
    record: dict = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "ok": bool(ok),
        "latency_sec": round(float(latency_sec), 3),
    }
    if extra:
        record.update(extra)
    record = scrub_record(record)
    METRICS_PATH.touch(exist_ok=True)
    with METRICS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    if db_utils and os.getenv("DATABASE_URL"):
        try:
            db_utils.record_metric(record)
        except Exception:
            pass


__all__ = ["configure_logger", "log_turn_metric", "METRICS_PATH"]
