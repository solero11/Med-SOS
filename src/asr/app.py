"""
Minimal ASR microservice for the Windows SOS desktop build.

The service can operate in two modes:
1. Proxy mode – forwards requests to an external ASR endpoint specified by
   ``ASR_FORWARD_URL``.
2. Stub mode – returns a simple placeholder transcript so local testing is
   possible without a heavyweight model.
"""

from __future__ import annotations

import audioop
import io
import os
from typing import Any, Dict, Optional
from wave import Error as WaveError
from wave import open as wave_open

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.utils.logger import configure_logger


app = FastAPI(title="SOS ASR Service", version="0.1.0")
logger = configure_logger("sos.asr")

FORWARD_URL = os.environ.get("ASR_FORWARD_URL")
HTTP_TIMEOUT = float(os.environ.get("ASR_HTTP_TIMEOUT", "60"))


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "mode": "proxy" if FORWARD_URL else "stub",
    }


@app.post("/asr")
async def asr_endpoint(
    audio: UploadFile = File(..., description="Input WAV audio"),
    language: Optional[str] = Form(default=None),
) -> JSONResponse:
    audio_bytes = await audio.read()

    if FORWARD_URL:
        return await _forward_to_backend(audio_bytes, audio.filename, audio.content_type, language)

    text = _stub_transcript(audio_bytes)
    payload: Dict[str, Any] = {
        "text": text,
        "language": language or "en",
        "segments": [
            {
                "text": text,
                "start": 0.0,
                "end": max(len(audio_bytes) / (16_000 * 2), 0.1),
            }
        ],
    }
    return JSONResponse(content=payload)


async def _forward_to_backend(
    audio_bytes: bytes,
    filename: Optional[str],
    content_type: Optional[str],
    language: Optional[str],
) -> JSONResponse:
    files = {
        "file": (
            filename or "input.wav",
            audio_bytes,
            content_type or "audio/wav",
        )
    }
    data: Dict[str, Any] = {}
    if language:
        data["language"] = language
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            response = await client.post(f"{FORWARD_URL.rstrip('/')}/asr", files=files, data=data)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("ASR backend request failed: %s", exc)
            raise HTTPException(status_code=502, detail="ASR backend unavailable") from exc
    return JSONResponse(content=response.json())


def _stub_transcript(audio_bytes: bytes) -> str:
    """
    Cheap RMS-based heuristic: if we detect energy, emit a canned transcript;
    otherwise report silence.
    """
    if not audio_bytes:
        return ""
    try:
        with wave_open(io.BytesIO(audio_bytes), "rb") as wav:
            frames = wav.readframes(wav.getnframes())
            rms = audioop.rms(frames, wav.getsampwidth())
    except (WaveError, audioop.error) as exc:
        logger.warning("Unable to parse audio payload: %s", exc)
        return ""

    if rms < 150:
        return ""
    if rms < 500:
        return "Patient breathing quietly."
    if rms < 1500:
        return "Patient reports chest tightness."
    return "Severe distress noted, prepare for airway support."


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    import uvicorn

    uvicorn.run("src.asr.app:app", host="0.0.0.0", port=9001, reload=False)
