import json
import re
from pathlib import Path

import requests

ORCH_METRICS_URL = "http://127.0.0.1:8000/metrics"
ORCH_METRICS_SUMMARY_URL = "http://127.0.0.1:8000/metrics/summary"
METRICS_JSONL_PATH = Path("_validation/orchestrator_metrics.jsonl")


def _scrape_metrics_text(url: str) -> str:
    """Try to fetch /metrics-summary first; fall back to /metrics."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass

    response = requests.get(ORCH_METRICS_URL, timeout=5)
    response.raise_for_status()
    return response.text


def _extract_histogram_value(metrics_text: str, metric_name: str):
    """
    Parse Prometheus histogram text for a given metric and return bucket counts.
    Example metric_name: 'latency_seconds_bucket'
    """
    pattern = re.compile(rf"^{metric_name}{{.*}}\s+(\d+)", re.MULTILINE)
    matches = pattern.findall(metrics_text)
    return [int(m) for m in matches] if matches else []


def _read_last_jsonl_entries(n: int = 5):
    if not METRICS_JSONL_PATH.exists():
        return []
    lines = METRICS_JSONL_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-n:] if line.strip()]


def test_latency_observability_after_stress():
    """
    Confirms latency metrics were recorded after stress recovery tests ran.
    1. Scrape /metrics or /metrics/summary for updated histogram values.
    2. Check orchestrator_metrics.jsonl appended recent turn_* entries.
    """
    metrics_text = _scrape_metrics_text(ORCH_METRICS_SUMMARY_URL)
    bucket_counts = _extract_histogram_value(metrics_text, "turn_latency_bucket")
    bucket_total = sum(bucket_counts)
    assert bucket_total > 0, "Prometheus histogram 'turn_latency_bucket' did not record any samples"

    entries = _read_last_jsonl_entries(10)
    assert entries, "No entries found in orchestrator_metrics.jsonl"
    assert any("turn_text" in e.get("event", "") for e in entries), "No 'turn_text' metric logged"
    assert any("turn_audio" in e.get("event", "") for e in entries), "No 'turn_audio' metric logged"

    for entry in entries:
        if "turn_" in entry.get("event", ""):
            assert "latency_sec" in entry or "latency_ms" in entry, f"Missing latency field in entry: {entry}"
            assert "clarifying" in entry, f"Missing clarifying field in entry: {entry}"
            assert "fallback" in entry, f"Missing fallback field in entry: {entry}"

    print(
        f"✅ Observability check passed: histogram sample count={bucket_total}, "
        f"JSONL entries analysed={len(entries)}"
    )
