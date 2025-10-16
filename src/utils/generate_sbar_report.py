"""
Generate a Markdown report showing SBAR evolution for a scene.

Steps:
1. Ensure LM Studio exposes the Medicine LLM.
2. Stream a dialogue JSONL through the SBAR monitor.
3. Capture each significant SBAR update.
4. Ask the LLM to critique the completed SBAR.
5. Write a Markdown file with the progression and critique.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.llm.llm_client import LLMClient
from src.llm.lmstudio_runtime import LMStudioRuntime
from src.utils.sbar_builder import SBAR
from src.utils.sbar_monitor import LLMChangeDetector, SBARMonitor
from src.utils.scene_player import SceneEvent, play_scene
from src.utils.sbar_reporting import (
    SBARSnapshot,
    build_markdown_body,
    format_sbar_line,
    render_markdown,
)

CRITIQUE_MAX_UPDATES = 12


def build_assessment_prompt(
    event_text: str,
    current_sbar: Dict[str, Optional[str]],
    history: List[Dict[str, Optional[str]]],
) -> str:
    history_lines = [format_sbar_line(entry) for entry in reversed(history)]
    history_block = "\n".join(f"{idx + 1}. {line}" for idx, line in enumerate(history_lines))
    if not history_block:
        history_block = "None available."
    return (
        "You complete the Assessment section of an SBAR during an acute case. "
        "Always provide the top three hypotheses for the differential diagnosis, ranked by likelihood. "
        "Respond with a single concise sentence formatted exactly as "
        "'Differential: 1) <diagnosis> 2) <diagnosis> 3) <diagnosis>'. "
        "If data are insufficient, include 'unknown' for the missing items. "
        "Do not add commentary or additional text.\n\n"
        f"Most recent observation: {event_text.strip() or 'None'}\n\n"
        "Current SBAR snapshot:\n"
        f"{format_sbar_line(current_sbar)}\n\n"
        "Recent SBAR history (most recent first):\n"
        f"{history_block}\n\n"
        "Assessment:"
    )
def collect_snapshots(
    scene_path: Path,
    realtime: bool,
    speed: float,
    runtime: LMStudioRuntime,
) -> Tuple[Dict[str, Optional[str]], List[SBARSnapshot]]:
    active_model = runtime.ensure_model_loaded()
    print(f"[LM Studio] Active model: {active_model}")

    significance_client = LLMClient(
        api_url=f"{runtime.base_url.rstrip('/')}/v1/chat/completions",
        system_prompt="Respond strictly with SIGNIFICANT or NO CHANGE.",
        model=runtime.target_model,
        temperature=0.0,
    )

    assessment_client = LLMClient(
        api_url=f"{runtime.base_url.rstrip('/')}/v1/chat/completions",
        system_prompt=(
            "You populate the Assessment field of an SBAR update. "
            "Always reply with a single line that lists the top three differential diagnoses in order of likelihood."
        ),
        model=runtime.target_model,
        temperature=0.2,
    )

    snapshots: List[SBARSnapshot] = []

    detector = LLMChangeDetector(lambda prompt: significance_client.ask(prompt))

    def update_assessment_with_llm(sbar_obj: SBAR, event: SceneEvent) -> Optional[str]:
        history_payload = [snap.sbar for snap in snapshots[-2:]]
        prompt = build_assessment_prompt(event.text, sbar_obj.to_dict(), history_payload)
        try:
            response = assessment_client.ask(prompt)
        except Exception:
            return None
        assessment_text = response.strip()
        if not assessment_text:
            return None
        sbar_obj.assessment = assessment_text
        return assessment_text

    def capture_snapshot(sbar, event: SceneEvent):
        update_assessment_with_llm(sbar, event)
        snapshots.append(
            SBARSnapshot(
                index=len(snapshots) + 1,
                t_start=event.t_start,
                event_text=event.text,
                sbar=sbar.to_dict(),
            )
        )

    monitor = SBARMonitor(change_detector=detector, output_fn=capture_snapshot)
    initial_state = monitor.sbar.to_dict()

    play_scene(scene_path, monitor.process_event, realtime=realtime, speed=speed)

    return initial_state, snapshots


def generate_report(
    scene_path: Path,
    output_path: Path,
    realtime: bool,
    speed: float,
    runtime: LMStudioRuntime,
) -> Path:
    initial_state, snapshots = collect_snapshots(scene_path, realtime, speed, runtime)

    critique_client = LLMClient(
        api_url=f"{runtime.base_url.rstrip('/')}/v1/chat/completions",
        system_prompt=(
            "You are a clinical supervisor evaluating SBAR documentation. "
            "Provide a concise critique highlighting strengths, gaps, and next steps."
        ),
        model=runtime.target_model,
        temperature=0.4,
    )

    critique_snapshots = snapshots[-CRITIQUE_MAX_UPDATES:] if len(snapshots) > CRITIQUE_MAX_UPDATES else snapshots
    body_without_critique = build_markdown_body(initial_state, snapshots)
    critique_body = build_markdown_body(initial_state, critique_snapshots)
    critique_prompt = (
        "Review the following SBAR progression and critique how well it captures the patient's situation. "
        "Address accuracy, completeness, and clarity. Limit to 3 short paragraphs. "
        "Only the most recent updates are provided below.\n\n"
        f"{critique_body}"
    )
    critique = critique_client.ask(critique_prompt)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(initial_state, snapshots, critique), encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SBAR report with LLM critique.")
    parser.add_argument(
        "--scene",
        type=Path,
        default=Path("scenes/tension_pneumo/dialogue.jsonl"),
        help="Path to dialogue JSONL scene.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/sbar_report.md"),
        help="Destination Markdown file.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Playback speed multiplier (real-time only).",
    )
    parser.add_argument(
        "--no-realtime",
        dest="realtime",
        action="store_false",
        help="Disable real-time delays between events.",
    )
    parser.set_defaults(realtime=True)
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="LM Studio base URL (overrides LM_STUDIO_BASE_URL env).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override LM Studio model id (overrides LM_STUDIO_MODEL env).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.scene.exists():
        raise SystemExit(f"Scene JSONL not found: {args.scene}")
    runtime = LMStudioRuntime.from_env()
    if args.base_url:
        runtime.base_url = args.base_url
    if args.model:
        runtime.target_model = args.model
    path = generate_report(
        args.scene,
        args.output,
        realtime=args.realtime,
        speed=args.speed,
        runtime=runtime,
    )
    print(f"SBAR report written to {path}")


if __name__ == "__main__":
    main()
