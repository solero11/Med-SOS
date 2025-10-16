import os

import httpx
import pytest

ASR_URL = os.getenv("ASR_API_URL", "http://127.0.0.1:9001")
TTS_URL = os.getenv("KOKORO_API_URL", "http://127.0.0.1:8880")
ORCH_URL = os.getenv("ORCH_API_URL", "http://127.0.0.1:8000")
LM_URL = os.getenv("LM_LOCAL_URL", "http://127.0.0.1:1234")

TIMEOUT = 5.0


@pytest.mark.asyncio
async def test_asr_health():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{ASR_URL}/health")
        assert response.status_code == 200, f"ASR /health failed: {response.text}"
        data = response.json()
        assert data.get("status") in {"ok", "ready", "healthy"}


@pytest.mark.asyncio
async def test_tts_health():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{TTS_URL}/health")
        assert response.status_code == 200, f"TTS /health failed: {response.text}"
        data = response.json()
        assert data.get("status") in {"ok", "ready", "healthy"}


@pytest.mark.asyncio
async def test_orchestrator_health():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{ORCH_URL}/health")
        assert response.status_code == 200, f"Orchestrator /health failed: {response.text}"
        data = response.json()
        assert data.get("status") in {"ok", "ready", "healthy"}


@pytest.mark.asyncio
async def test_lm_studio_list_models():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{LM_URL}/v1/models")
        assert response.status_code == 200, f"LM Studio /v1/models failed: {response.text}"
        data = response.json()
        assert isinstance(data, dict) and "data" in data and isinstance(data["data"], list)
