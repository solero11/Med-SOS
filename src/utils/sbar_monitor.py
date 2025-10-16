"""
SBAR monitoring utilities.

This module wires scene playback, SBAR updates, and LLM-based significance checks.
The default update strategy relies on simple keyword heuristics so it can run
offline, while allowing callers to plug in richer classifiers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional
from collections import deque

from .sbar_builder import SBAR
from .scene_player import SceneEvent


SignificanceFn = Callable[[SceneEvent, SBAR], bool]
UpdateFn = Callable[[SceneEvent, SBAR], bool]
OutputFn = Callable[[SBAR, SceneEvent], None]


def _normalize(text: str) -> str:
    return " ".join(text.strip().split())


def default_update_strategy(event: SceneEvent, sbar: SBAR) -> bool:
    """
    Basic heuristic mapping from utterances to SBAR fields.

    Returns True if any field was updated.
    """
    text = event.text
    text_lower = text.lower()
    updated = False

    def set_field(field: str, value: str):
        nonlocal updated
        normalized = _normalize(value)
        if getattr(sbar, field) != normalized:
            setattr(sbar, field, normalized)
            updated = True

    if any(keyword in text_lower for keyword in ("sat", "oxygen", "spo2", "vent", "pressure", "etco2")):
        set_field("situation", text)
    elif any(keyword in text_lower for keyword in ("history", "recent", "surgery", "comorbidity", "background")):
        set_field("background", text)
    elif any(keyword in text_lower for keyword in ("diagnosis", "tension", "assessment", "exam", "finding")):
        set_field("assessment", text)
    elif any(keyword in text_lower for keyword in ("prepare", "needle", "decompression", "give", "administer", "recommend", "action", "plan")):
        set_field("recommendation", text)

    return updated


@dataclass
class LLMChangeDetector:
    """
    Wraps an LLM callable to decide if an utterance reflects a significant change.

    The callable must accept a prompt string and return a textual response.
    If the response contains the `positive_token` (case-insensitive), the change
    is treated as significant.
    """

    llm_callable: Callable[[str], str]
    positive_token: str = "significant"
    negative_token: str = "no change"
    instructions: str = (
        "You are monitoring a patient in the OR. Decide if the new observation "
        "indicates a significant change in patient status that should update the SBAR. "
        "Reply with 'SIGNIFICANT' or 'NO CHANGE' only."
    )
    history_depth: int = 2

    def __call__(self, event: SceneEvent, sbar: SBAR) -> bool:
        history_text = self._format_history()
        prompt = (
            f"{self.instructions}\n\n"
            "Recent SBAR history (most recent first):\n"
            f"{history_text}\n\n"
            f"Current SBAR:\n"
            f"- Situation: {sbar.situation or 'None'}\n"
            f"- Background: {sbar.background or 'None'}\n"
            f"- Assessment: {sbar.assessment or 'None'}\n"
            f"- Recommendation: {sbar.recommendation or 'None'}\n\n"
            f"New observation at t={event.t_start:.1f}s:\n"
            f"{event.text}\n\n"
            "Answer:"
        )
        response = self.llm_callable(prompt)
        normalized = response.strip().lower()
        self._append_history(sbar)
        if self.positive_token.lower() in normalized:
            return True
        if self.negative_token.lower() in normalized:
            return False
        # Fallback: treat unknown responses as non-significant to avoid alert storms.
        return False

    def __post_init__(self) -> None:
        self._history = deque(maxlen=self.history_depth)

    def _append_history(self, sbar: SBAR) -> None:
        self._history.append(sbar.to_dict())

    def _format_history(self) -> str:
        if not getattr(self, "_history", None):
            return "None available."
        lines = []
        for idx, snapshot in enumerate(reversed(self._history), 1):
            lines.append(
                f"{idx}. Situation: {snapshot.get('situation') or 'None'} | "
                f"Background: {snapshot.get('background') or 'None'} | "
                f"Assessment: {snapshot.get('assessment') or 'None'} | "
                f"Recommendation: {snapshot.get('recommendation') or 'None'}"
            )
        return "\n".join(lines)


@dataclass
class SBARMonitor:
    """
    Tracks SBAR updates and emits snapshots when significant changes are detected.
    """

    change_detector: SignificanceFn
    update_strategy: UpdateFn = default_update_strategy
    output_fn: OutputFn = print
    sbar: SBAR = field(default_factory=SBAR)
    last_snapshot: Optional[Dict[str, Optional[str]]] = None

    def process_event(self, event: SceneEvent) -> None:
        if not self.update_strategy(event, self.sbar):
            return
        if not self.change_detector(event, self.sbar):
            return
        snapshot = self.sbar.to_dict()
        if snapshot != self.last_snapshot:
            self.output_fn(self.sbar, event)
            self.last_snapshot = snapshot.copy()


def print_snapshot(sbar: SBAR, event: SceneEvent) -> None:
    summary = ", ".join(f"{k}={v}" for k, v in sbar.to_dict().items() if v)
    print(f"[t={event.t_start:.1f}s] Significant change: {summary}")
