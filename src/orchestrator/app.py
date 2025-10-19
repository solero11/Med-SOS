"""
FastAPI orchestrator that coordinates ASR → LLM → TTS for the SOS desktop build.
"""

from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app

from src.utils.logger import configure_logger, log_turn_metric
from src.utils import storage
from src.security.auth import verify_token
from src.telemetry.otel_config import turns_counter, latency_hist
from src.utils.audit_logger import append_audit

from . import dashboard, pairing

from .config import (
    ASR_API_URL,
    HTTP_TIMEOUT,
    KOKORO_API_URL,
    ORCHESTRATOR_AUDIO_DIR,
    get_llm_url,
)

logger = configure_logger("sos.orchestrator")
SECURITY_TOKEN_PATH = Path("_validation/security/sos_token.txt")
SECURE_MODE = SECURITY_TOKEN_PATH.exists()
UPDATES_MANIFEST = Path("updates/manifest.json")

CLARIFYING_PROMPT = "Could you share more clinical detail so I can narrow the differential?"
FALLBACK_MESSAGE = (
    "I am not sure how to help, but continue to provide more information as I might find relevant "
    "clinical information to help you."
)
_MIN_WORDS_FOR_CONFIDENCE = 3

router = APIRouter()


def require_token(roles: Optional[List[str]] = None):
    async def dependency(request: Request):
        if not SECURE_MODE:
            user = {"sub": "local", "role": "admin"}
        else:
            header = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
            if not header:
                raise HTTPException(status_code=401, detail="Unauthorized")
            try:
                user = verify_token(header, roles)
            except Exception:
                expected = SECURITY_TOKEN_PATH.read_text(encoding="utf-8").strip() if SECURITY_TOKEN_PATH.exists() else ""
                if header != expected:
                    raise HTTPException(status_code=401, detail="Unauthorized")
                user = {"sub": "bootstrap", "role": "admin"}
                if roles and "admin" not in roles:
                    raise HTTPException(status_code=403, detail="Forbidden")
        request.state.user = user
        return user
    return dependency

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = httpx.AsyncClient(timeout=HTTP_TIMEOUT)
    ORCHESTRATOR_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    app.state.http = client
    try:
        yield
    finally:
        await client.aclose()


app = FastAPI(
    title="SOS Orchestrator",
    version="0.2.0",
    summary="Single entry point for the Windows SOS desktop pipeline.",
    lifespan=lifespan,
)


def create_app() -> FastAPI:
    """Convenience factory for uvicorn dotted-path loading."""
    included = getattr(app.state, "included_router_ids", set())
    if not getattr(app.state, "static_mounted", False):
        app.mount("/static", StaticFiles(directory="static"), name="static")
        app.state.static_mounted = True
    if not getattr(app.state, "metrics_mounted", False):
        app.mount("/metrics", make_asgi_app())
        app.state.metrics_mounted = True
    for subrouter in (router, pairing.router, dashboard.router):
        key = id(subrouter)
        if key not in included:
            app.include_router(subrouter)
            included.add(key)
    app.state.included_router_ids = included
    return app



def _compute_summary() -> Dict[str, Any]:
    try:
        from sqlalchemy.orm import Session
        from src.schema.db_models import Metric
        from src.utils.db import get_engine
        engine = get_engine()
    except Exception:
        return {"ok": False}
    with Session(engine) as session:
        rows = session.query(Metric).order_by(Metric.ts.desc()).limit(200).all()
        turns = len(rows)
        mean = sum((r.latency_sec or 0) for r in rows) / turns if turns else 0
    return {"ok": True, "turns_15m": turns, "latency_mean": mean}


@app.get("/health")
async def health() -> Dict[str, Any]:
    summary = _compute_summary()
    summary["clients"] = len(getattr(dashboard, "ACTIVE_CLIENTS", set()))
    return {
        "status": "ok",
        "asr_url": ASR_API_URL,
        "tts_url": KOKORO_API_URL,
        "llm_url": get_llm_url(),
        "secure": SECURE_MODE,
        "summary": summary,
    }




@app.get("/metrics/summary")
async def metrics_summary(_user: dict = Depends(require_token(["admin"]))):
    summary = _compute_summary()
    summary["clients"] = len(getattr(dashboard, "ACTIVE_CLIENTS", set()))
    return summary
@app.post("/turn")
async def turn(
    request: Request,
    user: dict = Depends(require_token(['clinician', 'admin'])),
    audio: UploadFile = File(...),
    enable_tts: bool = Form(default=True),
    language: Optional[str] = Form(default=None),
    history: Optional[str] = Form(default=None),
) -> JSONResponse:
    start = time.time()
    audio_url = None
    audio_format = None
    transcript_payload: Dict[str, Any] = {}
    try:
        audio_bytes = await audio.read()
        transcript_payload = await _call_asr(request.app.state.http, audio_bytes, audio.filename, language)
        transcript = (transcript_payload.get("text") or "").strip()
        messages = _parse_history(history)
        response_text, clarifying, fallback_triggered = await _generate_response(
            request.app.state.http,
            transcript,
            messages,
        )

        if enable_tts and response_text:
            audio_format, audio_url = await _call_tts(request, request.app.state.http, response_text)

        total = time.time() - start
        wav_count = len(list(ORCHESTRATOR_AUDIO_DIR.glob("*.wav")))
        turns_counter.add(1)
        latency_hist.record(total)
        log_turn_metric(
            "turn_audio",
            ok=True,
            latency_sec=total,
            extra={
                "reply_len": len(response_text or ""),
                "wav_count": wav_count,
                "secure": SECURE_MODE,
                "clarifying": clarifying,
                "fallback": fallback_triggered,
            },
        )
        append_audit(
            "turn_audio",
            request.state.user.get("sub", "unknown"),
            {
                "reply_len": len(response_text or ""),
                "wav_count": wav_count,
                "clarifying": clarifying,
                "fallback": fallback_triggered,
            },
        )

        payload = {
            "transcript": transcript,
            "response_text": response_text,
            "reply": response_text,
            "audio_url": audio_url,
            "tts_url": audio_url,
            "audio_format": audio_format,
            "asr": transcript_payload,
            "clarifying": clarifying,
            "fallback": fallback_triggered,
        }
        return JSONResponse(content=payload)
    except HTTPException as exc:
        log_turn_metric(
            "turn_audio",
            ok=False,
            latency_sec=time.time() - start,
            extra={"error": exc.detail if hasattr(exc, "detail") else str(exc), "secure": SECURE_MODE},
        )
        append_audit("turn_audio_error", request.state.user.get("sub", "unknown"), {"error": str(exc)})
        raise
    except Exception as exc:
        log_turn_metric(
            "turn_audio",
            ok=False,
            latency_sec=time.time() - start,
            extra={"error": str(exc), "secure": SECURE_MODE},
        )
        append_audit("turn_audio_error", request.state.user.get("sub", "unknown"), {"error": str(exc)})
        raise


@app.post("/turn_text")
async def turn_text(
    request: Request,
    user: dict = Depends(require_token(["clinician", "admin"]))
) -> JSONResponse:
    start = time.time()
    transcript = ""
    try:
        payload = await _extract_turn_text_payload(request)
        transcript = payload["transcript"]
        messages = _parse_history(payload.get("history"))
        response_text, clarifying, fallback_triggered = await _generate_response(
            request.app.state.http,
            transcript,
            messages,
        )

        audio_url = None
        audio_format = None
        if payload["enable_tts"] and response_text:
            audio_format, audio_url = await _call_tts(request, request.app.state.http, response_text)

        total = time.time() - start
        turns_counter.add(1)
        latency_hist.record(total)
        log_turn_metric(
            event="turn_text",
            ok=True,
            latency_sec=total,
            extra={
                "reply_len": len(response_text or ""),
                "secure": SECURE_MODE,
                "clarifying": clarifying,
                "fallback": fallback_triggered,
            },
        )
        append_audit(
            "turn_text",
            user.get("sub", "unknown"),
            {
                "reply_len": len(response_text or ""),
                "clarifying": clarifying,
                "fallback": fallback_triggered,
            },
        )

        payload_out = {
            "transcript": transcript,
            "response_text": response_text,
            "reply": response_text,
            "audio_url": audio_url,
            "tts_url": audio_url,
            "audio_format": audio_format,
            "clarifying": clarifying,
            "fallback": fallback_triggered,
        }
        return JSONResponse(content=payload_out)
    except HTTPException as exc:
        log_turn_metric(
            event="turn_text",
            ok=False,
            latency_sec=time.time() - start,
            extra={"error": exc.detail if hasattr(exc, "detail") else str(exc), "secure": SECURE_MODE},
        )
        append_audit("turn_text_error", user.get("sub", "unknown"), {"error": str(exc)})
        raise
    except Exception as exc:
        log_turn_metric(
            event="turn_text",
            ok=False,
            latency_sec=time.time() - start,
            extra={"error": str(exc), "secure": SECURE_MODE},
        )
        append_audit("turn_text_error", user.get("sub", "unknown"), {"error": str(exc)})
        raise


@app.get("/audio/{file_name}")
async def download_audio(file_name: str):
    file_path = (ORCHESTRATOR_AUDIO_DIR / file_name).resolve()
    if not file_path.exists() or ORCHESTRATOR_AUDIO_DIR not in file_path.parents:
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(file_path, media_type="audio/wav")


@router.get("/updates/manifest.json")
async def updates_manifest():
    if not UPDATES_MANIFEST.exists():
        raise HTTPException(status_code=404, detail="Update manifest unavailable.")
    return FileResponse(UPDATES_MANIFEST)


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


async def _extract_turn_text_payload(request: Request) -> Dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        data = await request.json()
    else:
        form = await request.form()
        data = {key: form.get(key) for key in form.keys()}

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid request payload.")

    raw_transcript = data.get("text") or data.get("transcript") or ""
    if isinstance(raw_transcript, str):
        transcript = raw_transcript.strip()
    else:
        transcript = str(raw_transcript).strip()

    enable_tts_raw = data.get("enable_tts", True)
    if isinstance(enable_tts_raw, str):
        enable_tts = enable_tts_raw.strip().lower() not in {"0", "false", "no"}
    else:
        enable_tts = bool(enable_tts_raw)

    return {
        "transcript": transcript,
        "enable_tts": enable_tts,
        "history": data.get("history"),
    }


def _parse_history(history: Optional[Any]) -> Optional[List[Dict[str, str]]]:
    if history is None:
        return None

    if isinstance(history, str):
        history = history.strip()
        if not history:
            return None
        try:
            parsed = json.loads(history)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="History payload is not valid JSON.") from exc
    else:
        parsed = history

    if not isinstance(parsed, list):
        return None

    messages: List[Dict[str, str]] = []
    for item in parsed:
        if isinstance(item, dict) and {"role", "content"} <= item.keys():
            messages.append({"role": item["role"], "content": item["content"]})
    return messages or None


def _needs_clarification(transcript: str) -> bool:
    stripped = transcript.strip()
    if not stripped:
        return True
    if len(stripped.split()) < _MIN_WORDS_FOR_CONFIDENCE:
        return True
    return False


async def _call_asr(
    client: httpx.AsyncClient,
    audio_bytes: bytes,
    filename: Optional[str],
    language: Optional[str],
) -> Dict[str, Any]:
    files = {
        "audio": (
            filename or "input.wav",
            audio_bytes,
            "audio/wav",
        )
    }
    data: Dict[str, Any] = {}
    if language:
        data["language"] = language
    try:
        response = await client.post(f"{ASR_API_URL.rstrip('/')}/asr", files=files, data=data)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("ASR request failed: %s", exc)
        raise HTTPException(status_code=502, detail="ASR service unavailable") from exc
    return response.json()


async def _call_llm(
    client: httpx.AsyncClient,
    transcript: str,
    history: Optional[List[Dict[str, str]]],
) -> str:
    messages: List[Dict[str, str]] = [{"role": "system", "content": "You are a calm emergency medicine assistant."}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": transcript})

    payload = {"model": "default", "messages": messages, "temperature": 0.7, "stream": False}

    url = get_llm_url()
    try:
        response = await client.post(url, json=payload)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("LLM request failed: %s", exc)
        raise HTTPException(status_code=502, detail="LLM service unavailable") from exc

    data = response.json()
    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"]
    return data.get("response", "")


async def _generate_response(
    client: httpx.AsyncClient,
    transcript: str,
    history: Optional[List[Dict[str, str]]],
) -> tuple[str, bool, bool]:
    trimmed = transcript.strip()
    clarifying = _needs_clarification(trimmed)
    if clarifying:
        return CLARIFYING_PROMPT, True, False

    response_text = await _call_llm(client, trimmed, history)
    if not response_text or not response_text.strip():
        return FALLBACK_MESSAGE, False, True
    return response_text, False, False


async def _call_tts(
    request: Request,
    client: httpx.AsyncClient,
    text: str,
) -> tuple[str, Optional[str]]:
    payload = {"text": text, "format": "wav"}
    try:
        response = await client.post(f"{KOKORO_API_URL.rstrip('/')}/tts", json=payload)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("TTS request failed: %s", exc)
        raise HTTPException(status_code=502, detail="TTS service unavailable") from exc

    data = response.json()
    download_path = data.get("audio_url")
    if not download_path:
        return data.get("format", "wav"), None

    absolute_url = download_path
    if not download_path.lower().startswith("http"):
        absolute_url = urljoin(f"{KOKORO_API_URL.rstrip('/')}/", download_path.lstrip("/"))

    try:
        audio_response = await client.get(absolute_url)
        audio_response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Failed to download TTS audio: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to fetch TTS audio") from exc

    file_name = f"{uuid.uuid4().hex}.wav"
    file_path = ORCHESTRATOR_AUDIO_DIR / file_name
    file_path.write_bytes(audio_response.content)
    try:
        storage.upload_validation_file(file_path)
    except Exception:
        pass

    return data.get("format", "wav"), str(request.url_for("download_audio", file_name=file_name))


if __name__ == "__main__":  # pragma: no cover - manual launch
    import uvicorn

    uvicorn.run("src.orchestrator.app:app", host="0.0.0.0", port=8000, reload=False)
