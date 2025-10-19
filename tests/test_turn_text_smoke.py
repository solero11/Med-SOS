import os
import time
from pathlib import Path

import httpx
import pytest

from src.orchestrator.app import CLARIFYING_PROMPT, FALLBACK_MESSAGE

ORCH_URL = os.getenv("ORCH_API_URL", "http://127.0.0.1:8000")
TIMEOUT = float(os.getenv("ORCH_TEST_TIMEOUT", "15"))
TOKEN_PATH = Path("_validation/security/sos_token.txt")


def _auth_headers() -> dict:
    if TOKEN_PATH.exists():
        return {"Authorization": f"Bearer {TOKEN_PATH.read_text(encoding='utf-8').strip()}"}
    return {}


@pytest.mark.asyncio
async def test_turn_text_smoke():
    """Text-only turn: verifies 200 OK, JSON shape, and sane latency."""
    payload = {"text": "Patient desaturating in OR. What should we assess first?"}
    t0 = time.time()
    async with httpx.AsyncClient(timeout=TIMEOUT, verify=False) as client:
        response = await client.post(f"{ORCH_URL}/turn_text", json=payload, headers=_auth_headers())
    elapsed = time.time() - t0

    assert response.status_code == 200, f"turn_text failed: {response.text}"
    data = response.json()
    assert isinstance(data, dict), "Response is not JSON object"
    assert "reply" in data and isinstance(data["reply"], str) and len(data["reply"]) > 0
    if "tts_url" in data and data["tts_url"]:
        assert data["tts_url"].startswith("http"), "tts_url must be a URL when present"
    assert elapsed < 5.0, f"turn_text too slow: {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_turn_text_clarifying_when_input_empty():
    async with httpx.AsyncClient(timeout=TIMEOUT, verify=False) as client:
        response = await client.post(f"{ORCH_URL}/turn_text", json={"text": "   "}, headers=_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == CLARIFYING_PROMPT
    assert data.get("clarifying") is True
    assert data.get("fallback") is False


@pytest.mark.asyncio
async def test_turn_text_fallback_when_llm_returns_blank():
    payload = {"text": "force fallback __force_fallback__ scenario"}
    async with httpx.AsyncClient(timeout=TIMEOUT, verify=False) as client:
        response = await client.post(f"{ORCH_URL}/turn_text", json=payload, headers=_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == FALLBACK_MESSAGE
    assert data.get("fallback") is True
    assert data.get("clarifying") is False
