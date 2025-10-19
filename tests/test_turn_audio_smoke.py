import json
import os
import pathlib
import time

import httpx
import pytest

ORCH_URL = os.getenv("ORCH_API_URL", "http://127.0.0.1:8000")
WAV_PATH = pathlib.Path("_validation/test_ping.wav")
TOKEN_PATH = pathlib.Path("_validation/security/sos_token.txt")


def _auth_headers() -> dict:
    if TOKEN_PATH.exists():
        return {"Authorization": f"Bearer {TOKEN_PATH.read_text(encoding='utf-8').strip()}"}
    return {}


@pytest.mark.asyncio
async def test_turn_audio_smoke():
    assert WAV_PATH.exists(), f"missing {WAV_PATH}, run tools/make_test_wav.py first"
    t0 = time.time()
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        with WAV_PATH.open("rb") as handle:
            files = {"audio": ("test_ping.wav", handle, "audio/wav")}
            response = await client.post(f"{ORCH_URL}/turn", files=files, headers=_auth_headers())
    elapsed = time.time() - t0
    assert response.status_code == 200, f"/turn failed: {response.text}"
    data = response.json()
    assert "reply" in data and isinstance(data["reply"], str)
    if "tts_url" in data and data["tts_url"]:
        assert data["tts_url"].startswith("http")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    assert elapsed < 10.0, f"/turn too slow: {elapsed:.1f}s"

    audio_dir = pathlib.Path("_validation/orchestrator_audio")
    wavs = list(audio_dir.glob("*.wav"))
    assert wavs, "no WAVs saved under _validation/orchestrator_audio/"
