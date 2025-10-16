"""
Scene playback utilities for streaming JSONL dialogue timelines into the SBAR pipeline.

The dialogue file should contain one JSON object per line with keys:
  - t_start (seconds from scene start)
  - t_end
  - text
Optional keys such as context_tag or noise_level are preserved and passed through.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional


@dataclass(frozen=True)
class SceneEvent:
    t_start: float
    t_end: float
    text: str
    raw: dict

    @classmethod
    def from_json(cls, payload: dict) -> "SceneEvent":
        return cls(
            t_start=float(payload["t_start"]),
            t_end=float(payload["t_end"]),
            text=str(payload["text"]),
            raw=payload,
        )


def load_scene(path: str | Path) -> List[SceneEvent]:
    """Load a JSONL dialogue timeline and return the events sorted by start time."""
    events: List[SceneEvent] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            events.append(SceneEvent.from_json(payload))
    events.sort(key=lambda e: e.t_start)
    return events


def iter_scene(events: Iterable[SceneEvent], start_offset: float = 0.0) -> Iterator[SceneEvent]:
    """Yield events that begin at or after the specified offset."""
    for event in events:
        if event.t_end < start_offset:
            continue
        yield event


def play_scene(
    scene_path: str | Path,
    callback: Callable[[SceneEvent], None],
    *,
    realtime: bool = True,
    speed: float = 1.0,
    start_offset: float = 0.0,
) -> None:
    """
    Stream scene events to `callback`.

    Args:
        scene_path: JSONL file containing the dialogue timeline.
        callback: Function invoked with each SceneEvent.
        realtime: When True, respects t_start gaps between events.
        speed: Playback multiplier (>1.0 speeds up, <1.0 slows down). Only used when realtime is True.
        start_offset: Skip events that end before this offset (seconds).
    """
    events = iter_scene(load_scene(scene_path), start_offset=start_offset)
    start_time: Optional[float] = None
    for event in events:
        if realtime:
            if start_time is None:
                start_time = time.time() - (event.t_start / max(speed, 1e-6))
            target = start_time + (event.t_start / max(speed, 1e-6))
            delay = target - time.time()
            if delay > 0:
                time.sleep(delay)
        callback(event)
