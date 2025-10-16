"""
Run an SBAR scene through the LLM-backed significance monitor.

Usage:
    python -m src.utils.run_sbar_scene --scene scenes/tension_pneumo/dialogue.jsonl
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from src.llm.llm_client import LLMClient
from src.llm.lmstudio_runtime import LMStudioRuntime
from src.utils.sbar_monitor import LLMChangeDetector, SBARMonitor, print_snapshot
from src.utils.scene_player import SceneEvent, play_scene


def build_detector(client: LLMClient) -> Callable[[SceneEvent, object], bool]:
    def llm_callable(prompt: str) -> str:
        return client.ask(prompt)

    return LLMChangeDetector(llm_callable)


def run_scene(scene_path: Path, speed: float, realtime: bool) -> None:
    runtime = LMStudioRuntime.from_env()
    active_model = runtime.ensure_model_loaded()
    print(f"[LM Studio] Active model: {active_model}")

    client = LLMClient(
        api_url=f"{runtime.base_url.rstrip('/')}/v1/chat/completions",
        system_prompt=(
            "You monitor a patient during surgery. When given context and a new observation, "
            "reply strictly with 'SIGNIFICANT' if the observation reflects a notable change in patient status, "
            "otherwise reply with 'NO CHANGE'."
        ),
        model=runtime.target_model,
        temperature=0.0,
    )

    monitor = SBARMonitor(change_detector=build_detector(client), output_fn=print_snapshot)

    def callback(event: SceneEvent) -> None:
        monitor.process_event(event)

    play_scene(scene_path, callback, realtime=realtime, speed=speed)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SBAR scene harness runner.")
    parser.add_argument(
        "--scene",
        type=Path,
        default=Path("scenes/tension_pneumo/dialogue.jsonl"),
        help="Path to the scene JSONL file.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Playback speed multiplier (only applies when --realtime).",
    )
    parser.add_argument(
        "--no-realtime",
        dest="realtime",
        action="store_false",
        help="Disable realtime sleeping between events.",
    )
    parser.set_defaults(realtime=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.scene.exists():
        raise SystemExit(f"Scene file not found: {args.scene}")
    run_scene(args.scene, speed=args.speed, realtime=args.realtime)


if __name__ == "__main__":
    main()
