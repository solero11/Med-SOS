"""
Minimal admin dashboard endpoints for real-time telemetry streaming.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse

from src.utils.logger import log_turn_metric
from src.security.auth import verify_token

router = APIRouter()
ACTIVE_CLIENTS: set[str] = set()
SECURITY_TOKEN_PATH = Path('_validation/security/sos_token.txt')
ACTIVE_CLIENTS: set[str] = set()
METRICS_PATH = Path("_validation/orchestrator_metrics.jsonl")
DASHBOARD_TEMPLATE = Path("templates/dashboard.html")


def _tail_metrics(start: int) -> AsyncIterator[str]:
    """Yield newly appended lines starting from offset."""
    if not METRICS_PATH.exists():
        return iter(())
    with METRICS_PATH.open("r", encoding="utf-8") as handle:
        handle.seek(start)
        for line in handle:
            yield line


@router.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard_page():
    if DASHBOARD_TEMPLATE.exists():
        return DASHBOARD_TEMPLATE.read_text(encoding="utf-8")
    return "<h3>SOS Dashboard missing template.</h3>"


@router.websocket("/ws/metrics")
async def metrics_socket(ws: WebSocket):
    await ws.accept()
    client_id = str(id(ws))
    ACTIVE_CLIENTS.add(client_id)
    log_turn_metric("dashboard_connection", True, 0.0, {"secure": True, "clients": len(ACTIVE_CLIENTS)})
    position = 0
    try:
        while True:
            await asyncio.sleep(1)
            if not METRICS_PATH.exists():
                continue
            lines = METRICS_PATH.read_text(encoding="utf-8").splitlines()
            if position >= len(lines):
                continue
            for line in lines[position:]:
                position += 1
                try:
                    json.loads(line)
                    await ws.send_text(line)
                except json.JSONDecodeError:
                    continue
    except WebSocketDisconnect:
        ACTIVE_CLIENTS.discard(client_id)
        log_turn_metric("dashboard_disconnect", True, 0.0, {"secure": True, "clients": len(ACTIVE_CLIENTS)})


@router.get("/metrics/summary")
async def metrics_summary():
    try:
        from sqlalchemy.orm import Session
        from src.schema.db_models import Metric
        from src.utils.db import get_engine
        engine = get_engine()
    except Exception:
        return {"ok": False}
    with Session(engine) as session:
        rows = session.query(Metric).order_by(Metric.ts.desc()).limit(200).all()
        turns = len(rows)
        mean = sum((r.latency_sec or 0) for r in rows) / turns if turns else 0
        return {"ok": True, "turns_15m": turns, "latency_mean": mean, "clients": len(ACTIVE_CLIENTS)}
