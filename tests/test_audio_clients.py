from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
from requests.exceptions import HTTPError

from src.audio.asr_client import ASRClient, ASRConfig
from src.audio.tts_client import TTSClient, TTSConfig


@dataclass
class DummyResponse:
    status_code: int = 200
    json_payload: Optional[Dict[str, Any]] = None
    content: bytes = b""
    headers: Optional[Dict[str, str]] = None
    text: str = ""

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPError(self.text or f"HTTP {self.status_code}")

    def json(self) -> Dict[str, Any]:
        return self.json_payload or {}


class DummySession:
    def __init__(self, *, post_response: DummyResponse, get_response: Optional[DummyResponse] = None):
        self._post_response = post_response
        self._get_response = get_response or post_response
        self.last_post: Dict[str, Any] | None = None
        self.last_get: Dict[str, Any] | None = None

    def post(self, url, files=None, data=None, json=None, timeout=None, headers=None):
        self.last_post = {
            "url": url,
            "files": files,
            "data": data,
            "json": json,
            "timeout": timeout,
            "headers": headers,
        }
        return self._post_response

    def get(self, url, timeout=None):
        self.last_get = {"url": url, "timeout": timeout}
        return self._get_response


def test_asr_client_transcribe_bytes_parses_segments():
    payload = {
        "text": "Patient is hypotensive.",
        "language": "en",
        "segments": [
            {"text": "Patient is hypotensive.", "start": 0.0, "end": 1.8, "confidence": 0.92},
        ],
    }
    session = DummySession(post_response=DummyResponse(json_payload=payload))
    client = ASRClient(config=ASRConfig(base_url="http://asr.local:9001"), session=session)

    result = client.transcribe_bytes(b"fake-audio")

    assert result.text == payload["text"]
    assert result.language == payload["language"]
    assert len(result.segments) == 1
    assert session.last_post is not None
    assert session.last_post["url"] == "http://asr.local:9001/asr"
    assert "file" in session.last_post["files"]
    assert session.last_post["files"]["file"][2] == "audio/wav"


def test_tts_client_speak_uses_defaults_and_returns_audio(tmp_path):
    audio_bytes = b"WAVE" * 10
    session = DummySession(
        post_response=DummyResponse(
            content=audio_bytes,
            headers={"Content-Type": "audio/wav"},
        )
    )
    config = TTSConfig(base_url="http://tts.local:8880", default_voice="af_v0bella")
    client = TTSClient(config=config, session=session)

    response = client.speak("We should reassess airway status.", speed=1.2)

    assert response.content == audio_bytes
    assert response.voice == "af_v0bella"
    assert response.response_format == config.response_format
    assert response.content_type == "audio/wav"

    assert session.last_post is not None
    assert session.last_post["url"] == "http://tts.local:8880/audio/speech"
    assert session.last_post["json"]["stream"] is False
    assert session.last_post["headers"]["Accept"] == "audio/wav"

    output_path = tmp_path / "output.wav"
    response.save(output_path.as_posix())
    assert output_path.read_bytes() == audio_bytes
