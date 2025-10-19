"""
Run the SBAR simulation harness against synthetic dialogue.

When WITH_LLM=1 is set in the environment the script delegates to
``generate_sbar_report`` which uses the configured LM Studio instance to supply
assessment differentials and a clinical supervisor critique. Otherwise an
offline harness generates deterministic Markdown output so the script can be run
without any external services.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Iterable, Optional, Sequence

from src.utils.logger import log_turn_metric
from src.utils.sbar_builder import SBAR
from src.utils.sbar_scene_harness import SBARSceneHarness
from src.utils.scene_player import SceneEvent
from src.utils.sbar_reporting import SBARSnapshot
from src.utils.generate_sbar_report import generate_report, LMStudioRuntime

SCENE_PATH = Path("_validation/test_dialogue.jsonl")
REPORT_PATH = Path("_validation/sbar_report_sim.md")
QUESTIONS_PATH = Path("_validation/sbar_questions_sim.md")


def _ensure_inputs() -> None:
    if not SCENE_PATH.exists():
        raise SystemExit(
            f"Synthetic dialogue missing: {SCENE_PATH}. "
            "Provide a JSONL stream of simulated ASR text before running this harness."
        )


def _significant_change(event: SceneEvent, sbar: SBAR) -> bool:
    trigger_words: Iterable[str] = ("pressure", "sat", "decompress", "code", "tension")
    text = event.text.lower()
    return any(word in text for word in trigger_words)


def _offline_assessment(
    sbar: SBAR,
    event: SceneEvent,
    _snapshots: Sequence[SBARSnapshot],
) -> Optional[str]:
    if "decompress" in event.text.lower():
        sbar.assessment = "Differential: 1) Tension pneumothorax 2) Bronchospasm 3) Equipment failure"
    elif "pressure" in event.text.lower():
        sbar.assessment = "Differential: 1) Hypovolemia 2) Anesthetic depth 3) Allergic reaction"
    return sbar.assessment


def _offline_question_generator(
    sbar: SBAR,
    event: SceneEvent,
    _protocols,
    _snapshots,
) -> Sequence[str]:
    return [f"What immediate action stabilises: {event.text.strip()}?"]


def run_offline() -> float:
    harness = SBARSceneHarness(
        change_detector=_significant_change,
        question_generator=_offline_question_generator,
        assessment_generator=_offline_assessment,
        realtime=False,
    )
    harness.run(
        SCENE_PATH,
        report_path=REPORT_PATH,
        questions_path=QUESTIONS_PATH,
    )
    return len(REPORT_PATH.read_text(encoding="utf-8").split())


def run_with_llm() -> float:
    runtime = LMStudioRuntime.from_env()
    generate_report(
        scene_path=SCENE_PATH,
        output_path=REPORT_PATH,
        realtime=False,
        speed=1.0,
        runtime=runtime,
    )
    # Generate questions using the offline harness so both artefacts are present.
    harness = SBARSceneHarness(
        change_detector=_significant_change,
        question_generator=_offline_question_generator,
        assessment_generator=_offline_assessment,
        realtime=False,
    )
    tmp_report = REPORT_PATH.with_suffix(".offline.tmp")
    result = harness.run(
        SCENE_PATH,
        report_path=tmp_report,
        questions_path=QUESTIONS_PATH,
    )
    if tmp_report.exists():
        tmp_report.unlink()
    # token estimate based on word count – LM Studio does not expose usage stats
    return len(REPORT_PATH.read_text(encoding="utf-8").split())


def main() -> int:
    _ensure_inputs()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUESTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with_llm = os.environ.get("WITH_LLM") == "1"
    start = time.time()
    try:
        token_estimate = run_with_llm() if with_llm else run_offline()
    except Exception as exc:
        log_turn_metric(
            "sbar_simulation",
            ok=False,
            latency_sec=time.time() - start,
            extra={"secure": False, "with_llm": with_llm, "error": str(exc)},
        )
        raise
    else:
        duration = time.time() - start
        log_turn_metric(
            "sbar_simulation",
            ok=True,
            latency_sec=duration,
            extra={
                "secure": False,
                "with_llm": with_llm,
                "report_path": str(REPORT_PATH),
                "token_estimate": int(token_estimate),
            },
        )
        print(f"SBAR simulation complete in {duration:.2f}s (token estimate={token_estimate}).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
