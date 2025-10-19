from __future__ import annotations

import io
from types import SimpleNamespace

import numpy as np
import pytest

import sos_button_app


class _DummyResponse:
    def __init__(self, json_data=None, content=b""):
        self._json = json_data or {}
        self.content = content

    def raise_for_status(self):
        return None

    def json(self):
        return self._json


def _blank_wav(seconds: float) -> bytes:
    frame_count = int(seconds * sos_button_app.SAMPLE_RATE)
    data = np.zeros((frame_count, 1), dtype=np.int16)
    return sos_button_app._build_wav(data)


@pytest.mark.skipif("CI" in sos_button_app.os.environ, reason="UI smoke test runs only in local environments.")
def test_sos_button_triggers_turn(monkeypatch):
    app = sos_button_app.SOSApp()

    statuses: list[str] = []
    responses: list[str] = []
    monkeypatch.setattr(app, "_set_status", lambda message: statuses.append(message))
    monkeypatch.setattr(app, "_set_response", lambda text: responses.append(text))

    app.build()  # initialises layout and session

    monkeypatch.setattr(app, "_record_audio", lambda: _blank_wav(sos_button_app.RECORD_SECONDS))

    playback_audio = _blank_wav(1.0)
    dummy_json = {
        "transcript": "Patient hypotensive after induction.",
        "response_text": "Begin vasopressor and reassess airway pressures.",
        "audio_url": "http://127.0.0.1:8000/audio/fake.wav",
        "latency_sec": 1.23,
    }

    app.session = SimpleNamespace(
        post=lambda url, files, data, timeout: _DummyResponse(json_data=dummy_json),
        get=lambda url, timeout: _DummyResponse(content=playback_audio),
    )

    monkeypatch.setattr(sos_button_app.sd, "play", lambda *args, **kwargs: None)
    monkeypatch.setattr(sos_button_app.sd, "wait", lambda: None)

    app._run_turn()

    assert any("Response ready" in status for status in statuses), statuses
    assert responses, "UI did not capture the assistant response."
    assert "response_text" in dummy_json
    assert "audio_url" in dummy_json
    assert "latency_sec" in dummy_json
