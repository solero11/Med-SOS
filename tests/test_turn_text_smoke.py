import os
import time

import httpx
import pytest

ORCH_URL = os.getenv("ORCH_API_URL", "http://127.0.0.1:8000")
TIMEOUT = float(os.getenv("ORCH_TEST_TIMEOUT", "15"))


@pytest.mark.asyncio
async def test_turn_text_smoke():
    """Text-only turn: verifies 200 OK, JSON shape, and sane latency."""
    payload = {"text": "Patient desaturating in OR. What should we assess first?"}
    t0 = time.time()
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(f"{ORCH_URL}/turn_text", json=payload)
    elapsed = time.time() - t0

    assert response.status_code == 200, f"turn_text failed: {response.text}"
    data = response.json()
    assert isinstance(data, dict), "Response is not JSON object"
    assert "reply" in data and isinstance(data["reply"], str) and len(data["reply"]) > 0
    if "tts_url" in data and data["tts_url"]:
        assert data["tts_url"].startswith("http"), "tts_url must be a URL when present"
    assert elapsed < 5.0, f"turn_text too slow: {elapsed:.2f}s"
