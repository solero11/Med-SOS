"""
HTTP client for the Kokoro FastAPI text-to-speech microservice.

Default configuration follows the OpenAI-compatible ``/audio/speech`` endpoint
with non-streaming responses so the UI can play audio once synthesis completes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from requests import Session
from requests.exceptions import HTTPError


@dataclass(slots=True)
class TTSConfig:
    """Configuration for connecting to the Kokoro FastAPI server."""

    base_url: str = os.environ.get("KOKORO_API_URL", "http://127.0.0.1:8880")
    default_model: str = os.environ.get("KOKORO_MODEL", "kokoro")
    default_voice: str = os.environ.get("KOKORO_VOICE", "af_v0bella")
    response_format: str = os.environ.get("KOKORO_FORMAT", "wav")
    timeout: int = int(os.environ.get("KOKORO_API_TIMEOUT", "120"))


@dataclass(slots=True)
class TTSAudio:
    """Wrapper for synthesized audio content returned by Kokoro."""

    content: bytes
    content_type: str
    voice: str
    response_format: str

    def save(self, path: str) -> None:
        """Persist the generated audio to disk."""
        with open(path, "wb") as handle:
            handle.write(self.content)


class TTSClient:
    """Helper responsible for issuing speech synthesis requests."""

    def __init__(self, config: Optional[TTSConfig] = None, session: Optional[Session] = None):
        self.config = config or TTSConfig()
        self.session = session or requests.Session()

    # --------------------------------------------------------------------- API
    def health(self) -> Dict[str, Any]:
        """Invoke ``GET /health`` to ensure Kokoro is available."""
        url = f"{self.config.base_url.rstrip('/')}/health"
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def list_voices(self) -> Dict[str, Any]:
        """Fetch the available voices from ``GET /audio/voices``."""
        url = f"{self.config.base_url.rstrip('/')}/audio/voices"
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def speak(
        self,
        text: str,
        *,
        voice: Optional[str] = None,
        model: Optional[str] = None,
        response_format: Optional[str] = None,
        speed: float = 1.0,
        lang_code: Optional[str] = None,
        volume_multiplier: Optional[float] = None,
        normalization_options: Optional[Dict[str, Any]] = None,
    ) -> TTSAudio:
        """
        Convert text into speech and return the audio payload.

        The method uses non-streaming generation to simplify playback in the UI.
        """
        payload: Dict[str, Any] = {
            "model": model or self.config.default_model,
            "input": text,
            "voice": voice or self.config.default_voice,
            "response_format": response_format or self.config.response_format,
            "speed": speed,
            "stream": False,
        }
        if lang_code:
            payload["lang_code"] = lang_code
        if volume_multiplier is not None:
            payload["volume_multiplier"] = volume_multiplier
        if normalization_options:
            payload["normalization_options"] = normalization_options

        url = f"{self.config.base_url.rstrip('/')}/audio/speech"
        headers = {"Accept": f"audio/{payload['response_format']}"}
        response = self.session.post(url, json=payload, timeout=self.config.timeout, headers=headers)
        try:
            response.raise_for_status()
        except HTTPError as exc:
            raise HTTPError(f"TTS request failed: {exc} | payload: {response.text}") from exc

        content_type = response.headers.get("Content-Type", headers["Accept"])
        return TTSAudio(
            content=response.content,
            content_type=content_type,
            voice=payload["voice"],
            response_format=payload["response_format"],
        )
