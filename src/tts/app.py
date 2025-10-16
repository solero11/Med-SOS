"""
Lightweight TTS microservice for the Windows SOS desktop build.

When no external TTS engine is available the service synthesizes a simple tone
representing the requested text. If ``TTS_FORWARD_URL`` is set, the request is
proxied to a remote Kokoro-compatible endpoint.
"""

from __future__ import annotations

import math
import os
import struct
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from src.utils.logger import configure_logger


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    voice: Optional[str] = Field(default=None)
    format: str = Field(default="wav")


app = FastAPI(title="SOS TTS Service", version=0.1)
logger = configure_logger("sos.tts")

FORWARD_URL = os.environ.get("TTS_FORWARD_URL")
HTTP_TIMEOUT = float(os.environ.get("TTS_HTTP_TIMEOUT", "120"))
AUDIO_DIR = Path(os.environ.get("TTS_AUDIO_DIR", "_validation/audio")).resolve()
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "mode": "proxy" if FORWARD_URL else "stub",
        "audio_dir": str(AUDIO_DIR),
    }


@app.post("/tts")
async def tts_endpoint(body: TTSRequest) -> JSONResponse:
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    if FORWARD_URL:
        return await _forward_to_backend(body)

    file_path = _synthesize_stub_audio(text, body.format)
    download_url = f"/audio/{file_path.name}"
    payload = {
        "status": "ok",
        "audio_url": download_url,
        "format": body.format,
        "voice": body.voice or "stub",
    }
    return JSONResponse(content=payload)


@app.get("/audio/{file_name}")
async def download_audio(file_name: str):
    file_path = (AUDIO_DIR / file_name).resolve()
    if not file_path.exists() or AUDIO_DIR not in file_path.parents:
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(file_path, media_type="audio/wav")


async def _forward_to_backend(body: TTSRequest) -> JSONResponse:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{FORWARD_URL.rstrip('/')}/tts",
                json=body.model_dump(),
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("TTS backend request failed: %s", exc)
            raise HTTPException(status_code=502, detail="TTS backend unavailable") from exc
    return JSONResponse(content=response.json())


def _synthesize_stub_audio(text: str, fmt: str) -> Path:
    """
    Generate a simple sine wave clip whose pitch varies with the characters in
    the text. This keeps the pipeline functional without a real TTS engine.
    """
    sample_rate = 24_000
    duration = max(1.0, min(len(text) * 0.1, 6.0))
    amplitude = 0.3
    total_frames = int(sample_rate * duration)
    buffer = bytearray()
    base_freq = 220.0

    for i in range(total_frames):
        char = text[i % len(text)]
        freq = base_freq + (ord(char) % 40) * 5
        sample = amplitude * math.sin(2 * math.pi * freq * (i / sample_rate))
        packed = struct.pack("<h", int(sample * 32767))
        buffer.extend(packed)

    file_name = f"{uuid.uuid4().hex}.wav"
    file_path = AUDIO_DIR / file_name
    with file_path.open("wb") as handle:
        handle.write(_wav_header(sample_rate, len(buffer)))
        handle.write(buffer)
    logger.info("Stub TTS generated %s (duration %.2fs)", file_path.name, duration)
    return file_path


def _wav_header(sample_rate: int, data_size: int) -> bytes:
    """
    Construct a minimal PCM WAV header for mono 16-bit audio.
    """
    byte_rate = sample_rate * 2
    block_align = 2
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        1,
        sample_rate,
        byte_rate,
        block_align,
        16,
        b"data",
        data_size,
    )
    return header


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    import uvicorn

    uvicorn.run("src.tts.app:app", host="0.0.0.0", port=8880, reload=False)
