"""
Local microphone capture utilities for the SOS UI.

The recorder streams PCM chunks from the default microphone using ``sounddevice``.
Each chunk is inspected with a minimal RMS-based VAD heuristic so the UI can
react (e.g. pulse the SOS button) when the user is speaking.
"""

from __future__ import annotations

import audioop
import io
import threading
import time
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Callable, List, Optional
from wave import open as wave_open


class MicrophoneUnavailableError(RuntimeError):
    """Raised when ``sounddevice`` is not installed or no input device exists."""


@dataclass(slots=True)
class VoiceActivityEvent:
    """Event payload emitted for each processed audio chunk."""

    rms: float
    is_speech: bool
    timestamp: float


class MicrophoneRecorder:
    """
    Capture PCM audio from the default microphone on a background thread.

    Example usage:

    ```python
    recorder = MicrophoneRecorder()
    recorder.start()
    ...
    audio_bytes = recorder.consume_wav()
    recorder.stop()
    ```
    """

    def __init__(
        self,
        *,
        sample_rate: int = 16_000,
        channels: int = 1,
        block_size: int = 2_048,
        vad_threshold: int = 1200,
        level_callback: Optional[Callable[[VoiceActivityEvent], None]] = None,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.block_size = block_size
        self.vad_threshold = vad_threshold
        self._level_callback = level_callback

        self._queue: "Queue[bytes]" = Queue()
        self._buffer = io.BytesIO()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._stream = None
        self._listeners: List[Callable[[VoiceActivityEvent], None]] = []
        if level_callback:
            self._listeners.append(level_callback)

    # ----------------------------------------------------------------- Control
    def start(self) -> None:
        """Begin capturing audio on a dedicated thread."""
        if self._running:
            return
        try:
            import sounddevice as sd  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise MicrophoneUnavailableError(
                "sounddevice is required for microphone capture. Install with `pip install sounddevice`."
            ) from exc

        if self.channels != 1:
            raise ValueError("Only mono recording is supported at the moment.")

        self._running = True
        self._buffer = io.BytesIO()

        def _callback(indata, frames, _time_info, status):  # pragma: no cover - hardware specific
            if status:
                # sounddevice uses repr for status; keep it minimal.
                print(f"Microphone stream warning: {status}")
            self._queue.put_nowait(indata.tobytes())

        try:
            self._stream = sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype="int16",
                blocksize=self.block_size,
                callback=_callback,
            )
            self._stream.start()
        except Exception as exc:  # pragma: no cover - hardware specific
            self._running = False
            self._stream = None
            raise MicrophoneUnavailableError(f"Unable to open microphone: {exc}") from exc

        self._thread = threading.Thread(target=self._drain_loop, name="MicrophoneRecorder", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Terminate recording and close the underlying stream."""
        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None

        if self._stream is not None:
            try:  # pragma: no branch - best effort cleanup
                self._stream.stop()
                self._stream.close()
            finally:
                self._stream = None

    def add_listener(self, callback: Callable[[VoiceActivityEvent], None]) -> None:
        """Subscribe to VAD events."""
        self._listeners.append(callback)

    # ------------------------------------------------------------------ Output
    def consume_wav(self) -> bytes:
        """Return the captured audio as a WAV byte buffer and reset storage."""
        raw = self._buffer.getvalue()
        with io.BytesIO() as output:
            with wave_open(output, "wb") as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # int16
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(raw)
            return output.getvalue()

    def reset(self) -> None:
        """Clear buffered audio without stopping the stream."""
        self._buffer = io.BytesIO()

    # -------------------------------------------------------------- Internal OK
    def _drain_loop(self) -> None:
        """Worker loop that aggregates PCM chunks and emits VAD events."""
        while self._running:
            try:
                chunk = self._queue.get(timeout=0.2)
            except Empty:
                continue

            self._buffer.write(chunk)
            rms = audioop.rms(chunk, 2)
            is_speech = rms >= self.vad_threshold
            event = VoiceActivityEvent(rms=rms, is_speech=is_speech, timestamp=time.time())
            for listener in list(self._listeners):
                try:
                    listener(event)
                except Exception:
                    # Keep listeners best-effort; UI should guard its own callbacks.
                    continue
