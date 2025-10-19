from __future__ import annotations

import os
from pathlib import Path

import pytest
import requests

TOKEN_FILE = Path("_validation/security/sos_token.txt")
CERT_FILE = Path("_validation/security/cert.pem")
ORCH_URL = os.getenv("ORCH_BASE_URL", "http://127.0.0.1:8000")


def _token() -> str:
    if not TOKEN_FILE.exists():
        pytest.skip("sos_token.txt not found; orchestrator is not running in secure mode.")
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


def _post_turn_text(headers=None) -> requests.Response:
    return requests.post(
        f"{ORCH_URL.rstrip('/')}/turn_text",
        json={"text": "Patient hypotensive in OR, next steps?"},
        headers=headers or {},
        timeout=10,
        verify=False,
    )


def test_security_artifacts_exist():
    if not TOKEN_FILE.exists():
        pytest.skip("Token file missing; create _validation/security/sos_token.txt before running security tests.")
    assert TOKEN_FILE.read_text(encoding="utf-8").strip(), "Token file is empty."
    if not CERT_FILE.exists():
        pytest.skip("cert.pem missing; place the orchestrator certificate in _validation/security/cert.pem.")


def test_turn_text_requires_valid_token():
    token_value = _token()

    response = _post_turn_text()
    assert response.status_code == 403, f"Expected 403 for missing token, got {response.status_code}"

    response = _post_turn_text(headers={"Authorization": "Bearer wrong-token"})
    assert response.status_code == 403, f"Expected 403 for invalid token, got {response.status_code}"

    response = _post_turn_text(headers={"Authorization": f"Bearer {token_value}"})
    assert response.status_code == 200, f"Expected 200 with valid token, got {response.status_code}"


def test_ui_token_env_matches_file():
    token_value = _token()
    env_token = os.environ.get("SOS_TOKEN")
    assert env_token == token_value, "SOS_TOKEN environment variable must match sos_token.txt"
