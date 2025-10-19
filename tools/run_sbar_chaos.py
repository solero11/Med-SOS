"""
Command-line runner for the SBAR chaos harness.
"""

from __future__ import annotations

import argparse
import statistics
import os
from pathlib import Path
from typing import List

from src.utils.llm_runtime import LMStudioRuntime
from src.utils.sbar_scene_harness import SBARChaosHarness

SUMMARY_PATH = Path("_validation/sbar_chaos_summary.md")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SBAR chaos harness locally.")
    parser.add_argument("--iters", type=int, default=1, help="Number of iterations to execute.")
    parser.add_argument(
        "--scene",
        type=Path,
        default=Path("_validation/test_dialogue.jsonl"),
        help="Path to the dialogue JSONL to replay.",
    )
    parser.add_argument(
        "--retain",
        type=int,
        default=int(os.environ.get("SBAR_CHAOS_RETAIN", "5")),
        help="Number of most recent runs to keep per scene before archiving older runs.",
    )
    parser.add_argument(
        "--with-llm",
        dest="with_llm",
        action="store_true",
        help="Force enable the Medicine LLM even if availability check fails.",
    )
    parser.add_argument(
        "--no-llm",
        dest="with_llm",
        action="store_false",
        help="Disable the Medicine LLM and use stubbed SBAR output.",
    )
    parser.set_defaults(with_llm=None)
    return parser.parse_args()


def _heartbeat_label(result: dict) -> str:
    mode = "[LLM]" if result.get("with_llm") else "[stub]"
    return f"{mode} {result.get('scene', 'unknown')}"


def _write_summary(results: List[dict], runtime_available: bool, requested_llm: bool) -> None:
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        SUMMARY_PATH.write_text(
            "# SBAR Chaos Summary\n\n_No runs executed._\n",
            encoding="utf-8",
        )
        return

    run_id = results[0].get("run_id", "unknown")
    scene = results[0].get("scene", "unknown")
    success_count = sum(1 for item in results if item.get("ok"))
    latency_values = [float(item.get("latency", 0.0)) for item in results]
    token_values = [int(item.get("tokens", 0)) for item in results]

    avg_latency = statistics.mean(latency_values) if latency_values else 0.0
    avg_tokens = statistics.mean(token_values) if token_values else 0.0

    llm_active = any(item.get("with_llm") for item in results)
    status = "PASS" if success_count == len(results) else "FAIL"

    lines = [
        "# SBAR Chaos Summary",
        "",
        f"- Run id: `{run_id}`",
        f"- Scene: `{scene}`",
        f"- Iterations: {len(results)}",
        f"- Average latency: {avg_latency:.3f}s",
        f"- Average tokens: {avg_tokens:.1f}",
        f"- Success rate: {success_count}/{len(results)} ({status})",
        f"- LLM active: {'yes' if llm_active else 'no'}",
        f"- LLM requested: {'yes' if requested_llm else 'no'}",
        f"- LLM reachable: {'yes' if runtime_available else 'no'}",
    ]

    report_path = results[-1].get("report_path")
    if report_path:
        lines.append(f"- Report log: `{report_path}`")
    progress_path = results[-1].get("progress_path")
    if progress_path:
        lines.append(f"- Progress log: `{progress_path}`")
    run_dir = results[-1].get("run_dir")
    if run_dir:
        lines.append(f"- Run directory: `{run_dir}`")

    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = _parse_args()
    runtime = LMStudioRuntime()
    runtime_available = runtime.is_available()

    if args.with_llm is None:
        with_llm = runtime_available
    else:
        with_llm = bool(args.with_llm)

    harness = SBARChaosHarness(dialogue_path=args.scene, retain_runs=args.retain)
    results = harness.run(iters=args.iters, with_llm=with_llm, runtime=runtime, scene_path=args.scene)

    for item in results:
        label = _heartbeat_label(item)
        scene_summary_tokens = int(item.get("scene_summary_tokens", 0) or 0)
        scene_summary_latency = float(item.get("scene_summary_latency", 0.0) or 0.0)
        summary_segment = ""
        if "scene_summary_tokens" in item:
            summary_segment = (
                f"  |  🩺 scene-summary Δt={scene_summary_latency:.2f}s, tokens={scene_summary_tokens}"
            )
        print(
            f"🫀 {label} Δt={item.get('latency', 0.0):.2f}s, tokens={int(item.get('tokens', 0))}"
            f"{summary_segment}"
        )
        summary_path = item.get("report_path")
        if summary_path:
            print(f"   Summary written to {summary_path}")

    _write_summary(results, runtime_available=runtime_available, requested_llm=with_llm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
