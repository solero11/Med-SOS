"""
SQLAlchemy models for persistent telemetry storage.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ts = Column(DateTime, default=datetime.utcnow)
    event = Column(String)
    ok = Column(String)
    latency_sec = Column(Float)
    extra = Column(JSON)
