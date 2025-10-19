
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.sbar_dashboard.app import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_api_runs_returns_data(client: TestClient) -> None:
    response = client.get("/api/runs")
    assert response.status_code == 200
    payload = response.json()
    runs = payload.get("runs", [])
    assert isinstance(runs, list)
    assert runs, "Expected at least one SBAR run in the dashboard API."
    sample = runs[0]
    for key in ("scene", "run", "summary", "progress"):
        assert key in sample


def test_run_file_endpoint_serves_markdown(client: TestClient) -> None:
    runs = client.get("/api/runs").json()["runs"]
    sample = runs[0]
    summary_url = sample["summary"]
    progress_url = sample["progress"]

    summary_resp = client.get(summary_url)
    assert summary_resp.status_code == 200
    assert "text/markdown" in summary_resp.headers.get("content-type", "")

    progress_resp = client.get(progress_url)
    assert progress_resp.status_code == 200
    assert "## SBAR Snapshot" in progress_resp.text


def test_dashboard_html(client: TestClient) -> None:
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "<table" in response.text or "No runs detected" in response.text
