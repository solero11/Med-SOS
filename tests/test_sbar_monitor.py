from typing import List

from src.utils.sbar_builder import SBAR
from src.utils.sbar_monitor import LLMChangeDetector, SBARMonitor, default_update_strategy
from src.utils.scene_player import SceneEvent


def make_event(t_start: float, text: str) -> SceneEvent:
    return SceneEvent(t_start=t_start, t_end=t_start + 1.0, text=text, raw={"text": text})


def test_monitor_emits_on_significant_change():
    captured: List[str] = []

    def fake_llm(prompt: str) -> str:
        if "sat seventy three" in prompt.lower():
            return "SIGNIFICANT"
        return "NO CHANGE"

    detector = LLMChangeDetector(fake_llm)

    def output_fn(sbar: SBAR, event: SceneEvent):
        captured.append(f"{event.t_start}:{sbar.situation}")

    monitor = SBARMonitor(change_detector=detector, update_strategy=default_update_strategy, output_fn=output_fn)

    events = [
        make_event(1.0, "sat dropping ninety two"),
        make_event(5.0, "sat seventy three we are losing pressure sixty systolic"),
        make_event(10.0, "sat seventy three we are losing pressure sixty systolic"),  # duplicate should not emit twice
    ]

    for event in events:
        monitor.process_event(event)

    assert captured == ["5.0:sat seventy three we are losing pressure sixty systolic"]


def test_monitor_suppresses_when_llm_says_no_change():
    captured: List[str] = []

    def fake_llm(_prompt: str) -> str:
        return "NO CHANGE"

    monitor = SBARMonitor(change_detector=LLMChangeDetector(fake_llm), output_fn=lambda *args: captured.append("called"))

    monitor.process_event(make_event(2.0, "sat ninety eight stable"))

    assert captured == []
