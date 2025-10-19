from __future__ import annotations

import json
import re
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

METRICS_PATH = Path("_validation/orchestrator_metrics.jsonl")
REQUIRED_EVENTS = {"turn_text", "turn_audio", "sbar_simulation"}
PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\bMRN[:\s]?\d+\b", re.IGNORECASE),
]


def _load_metrics() -> list[dict]:
    if not METRICS_PATH.exists():
        return []
    with METRICS_PATH.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


@pytest.fixture(scope="session", autouse=True)
def ensure_simulation_metrics():
    subprocess.run([sys.executable, "tools/run_sbar_simulation.py"], check=True)
    if not METRICS_PATH.exists():
        pytest.skip("Metrics file not generated; run orchestrator smoke tests first.")


def test_metrics_file_contains_required_events():
    entries = _load_metrics()
    assert entries, "No metrics recorded; run the smoke harness first."

    events = {entry.get("event") for entry in entries}
    missing = REQUIRED_EVENTS - events
    assert not missing, f"Missing expected events in metrics log: {sorted(missing)}"

    assert all("secure" in entry for entry in entries), "Each metric entry must include the 'secure' flag."

    latencies = [float(entry.get("latency_sec", 0.0)) for entry in entries]
    assert all(value >= 0 for value in latencies), "Latencies must be non-negative."
    avg_latency = statistics.mean(latencies)
    assert avg_latency < 2.5, f"Average latency too high: {avg_latency:.2f}s"


def test_metrics_are_monotonic_and_deidentified():
    entries = _load_metrics()
    timestamps = [
        datetime.fromisoformat(entry["ts"].replace("Z", "+00:00")) for entry in entries if "ts" in entry
    ]
    assert timestamps, "No timestamps recorded in metrics."
    assert timestamps == sorted(timestamps), "Metric timestamps are not monotonically increasing."

    serialized = "\n".join(json.dumps(entry, ensure_ascii=False) for entry in entries)
    for pattern in PII_PATTERNS:
        assert not pattern.search(serialized), f"PII pattern detected in metrics: {pattern.pattern}"
