
from __future__ import annotations
import sys, os
# Add project root to sys.path for package imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import io
import json
import time
import wave
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from src.orchestrator import app


def _make_wav() -> bytes:
    with io.BytesIO() as buffer:
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16_000)
            wav.writeframes(b"\x00" * 3200)
        return buffer.getvalue()


class StubAsyncClient:
    def __init__(self):
        self.audio_bytes = _make_wav()

    async def post(self, url: str, **kwargs):
        request = httpx.Request("POST", url)
        if url.endswith("/asr"):
            payload = {
                "text": "test case",
                "language": "en",
                "segments": [{"text": "test case", "start": 0.0, "end": 1.0}],
            }
            return httpx.Response(status_code=200, json=payload, request=request)

        if url.endswith("/tts"):
            payload = {
                "status": "ok",
                "audio_url": "http://stub-tts/audio/test.wav",
                "format": "wav",
            }
            return httpx.Response(status_code=200, json=payload, request=request)

        # LLM endpoint
        payload = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "This is a stub response.",
                    }
                }
            ]
        }
        return httpx.Response(status_code=200, json=payload, request=request)

    async def get(self, url: str, **kwargs):
        request = httpx.Request("GET", url)
        return httpx.Response(status_code=200, content=self.audio_bytes, request=request)

    async def close(self):  # pragma: no cover
        return


def test_windows_orchestrator(tmp_path, monkeypatch):
    # Point orchestrator globals at stub endpoints/directories
    from src.orchestrator import app as orchestrator_app, config as orchestrator_config
    orchestrator_config.ASR_API_URL = "http://stub-asr"
    orchestrator_config.KOKORO_API_URL = "http://stub-tts"
    orchestrator_config.ORCHESTRATOR_AUDIO_DIR = tmp_path
    monkeypatch.setattr(orchestrator_config, "get_llm_url", lambda: "http://stub-llm")

    metrics_path = Path("_validation/orchestrator_metrics.jsonl")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    token_path = Path("_validation/security/sos_token.txt")
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text("test-admin-token", encoding="utf-8")

    with TestClient(orchestrator_app) as client:
        client.app.state.http = StubAsyncClient()
        start = time.perf_counter()
        response = client.post(
            "/turn_text",
            data={"transcript": "test case", "enable_tts": "true"},
            headers={"Authorization": "Bearer test-admin-token"},
        )
        latency = time.perf_counter() - start

    assert response.status_code == 200
    payload = response.json()
    assert "reply" in payload
    assert payload["reply"] == "This is a stub response."

    entry = {"endpoint": "/turn_text", "status": response.status_code, "latency": latency}
    with metrics_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")
