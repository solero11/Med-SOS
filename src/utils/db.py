"""
Database helpers for telemetry persistence.
"""

from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.schema.db_models import Base, Metric

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL not configured")
        _engine = create_engine(database_url, pool_pre_ping=True)
        Base.metadata.create_all(_engine)
    return _engine


def record_metric(record: dict) -> None:
    engine = get_engine()
    with Session(engine) as session:
        session.add(Metric(**record))
        session.commit()
