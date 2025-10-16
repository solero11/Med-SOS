"""
HTTP client for the Faster-Whisper ASR microservice.

The service contract is documented under ``C:\\Users\\k9673\\ASR\\docs\\architecture.md``.
This client focuses on the ``POST /asr`` endpoint, returning a structured
``ASRTranscript`` for downstream consumers.
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests
from requests import Session
from requests.exceptions import HTTPError


@dataclass(slots=True)
class ASRConfig:
    """Configuration for the ASR service."""

    base_url: str = os.environ.get("ASR_API_URL", "http://127.0.0.1:9001")
    timeout: int = int(os.environ.get("ASR_API_TIMEOUT", "60"))


@dataclass(slots=True)
class ASRSegment:
    """Minimal projection of the segment payload from the ASR service."""

    text: str
    start: float
    end: float
    confidence: Optional[float] = None
    speaker: Optional[str] = None


@dataclass(slots=True)
class ASRTranscript:
    """Normalized transcription payload returned by ``ASRClient``."""

    text: str
    language: Optional[str]
    segments: List[ASRSegment]
    raw: Dict[str, Any]

    @property
    def has_audio(self) -> bool:
        """The ASR service never returns audio, maintained for interface parity."""
        return False


class ASRClient:
    """
    Small helper for issuing requests to the ASR HTTP microservice.

    The client exposes convenience helpers for byte buffers, files, and already
    base64-encoded audio payloads so the UI does not need to care about transport
    details.
    """

    def __init__(self, config: Optional[ASRConfig] = None, session: Optional[Session] = None):
        self.config = config or ASRConfig()
        self.session = session or requests.Session()

    # --------------------------------------------------------------------- API
    def health(self) -> Dict[str, Any]:
        """Invoke ``GET /health`` to verify the ASR service is reachable."""
        url = f"{self.config.base_url.rstrip('/')}/health"
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        *,
        language: Optional[str] = None,
        filename: str = "input.wav",
        mime_type: str = "audio/wav",
    ) -> ASRTranscript:
        """Send an in-memory audio buffer to the ASR service."""
        files = {"file": (filename, audio_bytes, mime_type)}
        data: Dict[str, Any] = {}
        if language:
            data["language"] = language
        url = f"{self.config.base_url.rstrip('/')}/asr"
        response = self.session.post(url, files=files, data=data, timeout=self.config.timeout)
        try:
            response.raise_for_status()
        except HTTPError as exc:
            raise HTTPError(f"ASR request failed: {exc} | payload: {response.text}") from exc
        payload = response.json()
        return self._parse_payload(payload)

    def transcribe_file(
        self,
        path: str | Path,
        *,
        language: Optional[str] = None,
        mime_type: str = "audio/wav",
    ) -> ASRTranscript:
        """Read a local file and forward to the ASR service."""
        file_path = Path(path)
        audio_bytes = file_path.read_bytes()
        return self.transcribe_bytes(
            audio_bytes,
            language=language,
            filename=file_path.name,
            mime_type=mime_type,
        )

    def transcribe_base64(
        self,
        audio_base64: str,
        *,
        language: Optional[str] = None,
        filename: str = "input.wav",
        mime_type: str = "audio/wav",
    ) -> ASRTranscript:
        """Helper that accepts already-base64 encoded audio bytes."""
        decoded = base64.b64decode(audio_base64)
        return self.transcribe_bytes(
            decoded,
            language=language,
            filename=filename,
            mime_type=mime_type,
        )

    # ----------------------------------------------------------------- Helpers
    @staticmethod
    def _parse_payload(payload: Dict[str, Any]) -> ASRTranscript:
        segments_payload: Iterable[Dict[str, Any]] = payload.get("segments") or []
        segments: List[ASRSegment] = []
        for seg in segments_payload:
            segments.append(
                ASRSegment(
                    text=str(seg.get("text", "")),
                    start=float(seg.get("start", 0.0)),
                    end=float(seg.get("end", 0.0)),
                    confidence=(
                        float(seg["confidence"]) if seg.get("confidence") is not None else None
                    ),
                    speaker=seg.get("speaker"),
                )
            )
        return ASRTranscript(
            text=str(payload.get("text", "")),
            language=payload.get("language"),
            segments=segments,
            raw=payload,
        )
