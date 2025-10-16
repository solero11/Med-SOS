"""
ASR enrichment utilities leveraging the Faster-Whisper medium model.

The goal is to extract high-resolution timing, confidence, and acoustic hints that
can be merged back into the dialogue timeline before feeding the SBAR pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .scene_player import SceneEvent


def _ensure_model(model: Any, model_size: str, device: str, compute_type: str):
    if model is not None:
        return model
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised via tests with stubbed model
        raise RuntimeError(
            "faster-whisper is not installed. Install with `pip install faster-whisper` to enable ASR enrichment."
        ) from exc
    return WhisperModel(model_size_or_path=model_size, device=device, compute_type=compute_type)


@dataclass
class EnrichedSegment:
    t_start: float
    t_end: float
    text: str
    confidence: Optional[float]
    noise_level: Optional[float]
    metadata: Dict[str, Any]


class ASREnrichment:
    """
    Wraps a Faster-Whisper model (medium) and exposes convenience helpers to
    transform audio into enriched dialogue events ready for the SBAR pipeline.
    """

    def __init__(
        self,
        *,
        model: Any = None,
        model_size: str = "medium",
        device: str = "cuda",
        compute_type: str = "float16",
    ):
        self.model = _ensure_model(model, model_size, device, compute_type)

    def transcribe(
        self,
        audio_path: str | Path,
        *,
        beam_size: int = 5,
        vad_filter: bool = True,
        initial_prompt: Optional[str] = None,
    ) -> List[EnrichedSegment]:
        """
        Run transcription and collect enriched metadata from Faster-Whisper segments.
        """
        segments, _info = self.model.transcribe(
            str(audio_path),
            beam_size=beam_size,
            vad_filter=vad_filter,
            word_timestamps=True,
            initial_prompt=initial_prompt,
        )
        enriched: List[EnrichedSegment] = []
        for seg in segments:
            words: Sequence[Any] = getattr(seg, "words", []) or []
            confidences = [getattr(w, "probability", None) for w in words if getattr(w, "probability", None) is not None]
            confidence = sum(confidences) / len(confidences) if confidences else None
            noise_level = None
            no_speech = getattr(seg, "no_speech_prob", None)
            if no_speech is not None:
                noise_level = max(0.0, min(1.0, 1.0 - float(no_speech)))
            enriched.append(
                EnrichedSegment(
                    t_start=float(getattr(seg, "start", 0.0)),
                    t_end=float(getattr(seg, "end", 0.0)),
                    text=str(getattr(seg, "text", "")).strip(),
                    confidence=confidence,
                    noise_level=noise_level,
                    metadata={
                        "avg_logprob": getattr(seg, "avg_logprob", None),
                        "compression_ratio": getattr(seg, "compression_ratio", None),
                        "no_speech_prob": no_speech,
                        "temperature": getattr(seg, "temperature", None),
                        "language": getattr(seg, "language", None),
                        "words": [
                            {
                                "start": float(getattr(w, "start", 0.0)),
                                "end": float(getattr(w, "end", 0.0)),
                                "text": getattr(w, "word", ""),
                                "probability": getattr(w, "probability", None),
                            }
                            for w in words
                        ],
                    },
                )
            )
        return enriched

    @staticmethod
    def to_scene_events(segments: Iterable[EnrichedSegment]) -> List[SceneEvent]:
        """
        Convert enriched segments into `SceneEvent` instances suitable for playback.
        """
        events: List[SceneEvent] = []
        for seg in segments:
            raw: Dict[str, Any] = {
                "t_start": seg.t_start,
                "t_end": seg.t_end,
                "text": seg.text,
                "confidence": seg.confidence,
                "noise_level": seg.noise_level,
                **seg.metadata,
            }
            events.append(SceneEvent(t_start=seg.t_start, t_end=seg.t_end, text=seg.text, raw=raw))
        return events
