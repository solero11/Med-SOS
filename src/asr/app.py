"""
Minimal ASR proxy for the Windows SOS desktop build.

This service now always forwards requests to a real ASR backend. Configure the
target via ``ASR_FORWARD_URL``.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.utils.logger import configure_logger


app = FastAPI(title="SOS ASR Service", version="0.1.0")
logger = configure_logger("sos.asr")

FORWARD_URL_RAW = os.environ.get("ASR_FORWARD_URL")
FORWARD_URL = FORWARD_URL_RAW.rstrip("/") if FORWARD_URL_RAW else None
HTTP_TIMEOUT = float(os.environ.get("ASR_HTTP_TIMEOUT", "60"))


@app.get("/health")
async def health() -> Dict[str, Any]:
    if not FORWARD_URL:
        return {
            "status": "error",
            "mode": "unconfigured",
            "detail": "ASR_FORWARD_URL not set; configure a real ASR backend.",
        }

    backend_info: Dict[str, Any] = {}
    backend_status = "ok"
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(f"{FORWARD_URL}/health")
            response.raise_for_status()
            backend_info = response.json()
    except httpx.HTTPError as exc:
        backend_status = "unreachable"
        logger.error("ASR backend health check failed: %s", exc)
    return {
        "status": "ok" if backend_status == "ok" else "degraded",
        "mode": "proxy",
        "forward_url": FORWARD_URL,
        "backend_status": backend_status,
        "backend_info": backend_info,
    }


@app.post("/asr")
async def asr_endpoint(
    audio: UploadFile = File(..., description="Input WAV audio"),
    language: Optional[str] = Form(default=None),
) -> JSONResponse:
    audio_bytes = await audio.read()

    if not FORWARD_URL:
        logger.error("ASR request received but ASR_FORWARD_URL is not configured")
        raise HTTPException(status_code=503, detail="ASR backend not configured")

    return await _forward_to_backend(audio_bytes, audio.filename, audio.content_type, language)


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
            response = await client.post(f"{FORWARD_URL}/asr", files=files, data=data)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("ASR backend request failed: %s", exc)
            raise HTTPException(status_code=502, detail="ASR backend unavailable") from exc
    return JSONResponse(content=response.json())


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    import uvicorn

    uvicorn.run("src.asr.app:app", host="0.0.0.0", port=9001, reload=False)
