"""
Kivy SOS desktop UI for Windows.

The UI displays a single SOS button and status label. When the button is pressed
the app records five seconds of microphone audio, posts it to the orchestrator's
``/turn`` endpoint, and plays back the synthesized WAV response.
"""

from __future__ import annotations

import io
import os
import threading
import time
from functools import partial
from typing import Optional
from wave import Error as WaveError
from wave import open as wave_open

import numpy as np
import requests
import sounddevice as sd  # type: ignore
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Ellipse
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from sos_boot import APP_VERSION
from src.updater import windows_updater

ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_TURN_URL", "http://127.0.0.1:8000")
MANIFEST_URL = os.environ.get("SOS_MANIFEST_URL", "https://127.0.0.1:8000/updates/manifest.json")
RECORD_SECONDS = float(os.environ.get("SOS_RECORD_SECONDS", "5"))
SAMPLE_RATE = int(os.environ.get("SOS_SAMPLE_RATE", "16000"))


def _build_wav(buffer: np.ndarray) -> bytes:
    with io.BytesIO() as output:
        with wave_open(output, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(buffer.tobytes())
        return output.getvalue()


class PulsingButton(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (280, 280)
        self.label = Label(
            text="SOS",
            font_size=72,
            color=(1, 1, 1, 1),
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        with self.canvas:
            Color(1, 0, 0, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.add_widget(self.label)
        self.bind(pos=self._sync, size=self._sync)
        self.on_press = None

    def _sync(self, *_args):
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size
        self.label.pos = self.pos
        self.label.size = self.size
        self.label.text_size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if callable(self.on_press):
                self.on_press()
            return True
        return super().on_touch_down(touch)


class SOSLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = Label(
            text="Checking orchestrator…",
            size_hint=(1, None),
            pos_hint={"center_x": 0.5, "y": 0.1},
            height=40,
            halign="center",
            valign="middle",
        )
        self.status.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.add_widget(self.status)

        self.button = PulsingButton()
        self.button.pos_hint = {"center_x": 0.5, "center_y": 0.55}
        self.add_widget(self.button)

        self.response_label = Label(
            text="",
            size_hint=(0.9, None),
            height=160,
            pos_hint={"center_x": 0.5, "y": 0.35},
            halign="center",
            valign="middle",
        )
        self.response_label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.add_widget(self.response_label)

        self.update_button = Button(
            text="Check for updates…",
            size_hint=(None, None),
            size=(220, 48),
            pos_hint={"center_x": 0.5, "y": 0.02},
        )
        self.add_widget(self.update_button)


class SOSApp(App):
    def build(self):
        self.session = requests.Session()
        self.layout = SOSLayout()
        self.layout.button.on_press = self._handle_press
        self.layout.update_button.bind(on_press=lambda *_: threading.Thread(target=self._handle_update, daemon=True).start())
        Clock.schedule_once(lambda *_: self._check_health(), 0)
        return self.layout

    def _set_status(self, message: str):
        Clock.schedule_once(lambda *_: setattr(self.layout.status, "text", message), 0)

    def _set_response(self, text: str):
        Clock.schedule_once(lambda *_: setattr(self.layout.response_label, "text", text), 0)

    def _handle_press(self):
        threading.Thread(target=self._run_turn, daemon=True).start()

    def _handle_update(self):
        self._set_status("Checking updates…")
        try:
            result = windows_updater.check_and_update(MANIFEST_URL, APP_VERSION)
            if result.get("update_available"):
                self._set_status("Update downloaded. Installer launching…")
            else:
                self._set_status("No updates available.")
        except SystemExit:
            pass
        except Exception as exc:
            self._set_status(f"Update failed: {exc}")

    def _run_turn(self):
        self._set_status("Recording…")
        audio_bytes = self._record_audio()
        if audio_bytes is None:
            self._set_status("Microphone unavailable.")
            return

        self._set_status("Processing…")
        files = {"audio": ("capture.wav", audio_bytes, "audio/wav")}
        data = {"enable_tts": "true"}

        try:
            response = self.session.post(f"{ORCHESTRATOR_URL.rstrip('/')}/turn", files=files, data=data, timeout=120)
            response.raise_for_status()
        except Exception as exc:
            self._set_status(f"Orchestrator error: {exc}")
            return

        payload = response.json()
        transcript = payload.get("transcript", "")
        reply = payload.get("response_text", "")
        self._set_response(f"You: {transcript}\nAssistant: {reply}")
        self._set_status("Response ready.")

        audio_url = payload.get("audio_url")
        if audio_url:
            try:
                audio_response = self.session.get(audio_url, timeout=120)
                audio_response.raise_for_status()
                self._play_audio(audio_response.content)
            except Exception as exc:
                self._set_status(f"Playback failed: {exc}")

    def _record_audio(self) -> Optional[bytes]:
        try:
            recording = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
            sd.wait()
            return _build_wav(recording)
        except Exception as exc:
            self._set_status(f"Recording failed: {exc}")
            return None

    def _play_audio(self, audio_bytes: bytes):
        try:
            with wave_open(io.BytesIO(audio_bytes), "rb") as wav:
                frames = wav.readframes(wav.getnframes())
                data = np.frombuffer(frames, dtype=np.int16)
                sample_rate = wav.getframerate()
            sd.play(data, sample_rate)
            sd.wait()
        except (WaveError, ValueError) as exc:
            Clock.schedule_once(
                lambda *_: self._set_status(f"Unable to decode audio: {exc}"),
                0,
            )

    def _check_health(self):
        try:
            response = self.session.get(f"{ORCHESTRATOR_URL.rstrip('/')}/health", timeout=5)
            response.raise_for_status()
            self._set_status("Connected.")
        except Exception as exc:
            self._set_status(f"Health check failed: {exc}")


if __name__ == "__main__":
    print("Starting SOS button interface...")
    SOSApp().run()
