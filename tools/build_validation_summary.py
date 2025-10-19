"""
Aggregate SBAR chaos metrics into a validation summary report.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

METRICS_PATH = Path("_validation/orchestrator_metrics.jsonl")
REPORT_PATH = Path("_validation/validation_report.md")


def _parse_ts(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return datetime.min


def _load_metrics(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    entries: List[Dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict) and payload.get("event") == "sbar_chaos":
                entries.append(payload)
    return entries


def _group_by_run(entries: Iterable[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    grouped: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for entry in entries:
        run_id = entry.get("run_id")
        if not run_id:
            continue
        grouped[str(run_id)].append(entry)
    return grouped


def _summarise(run_id: str, entries: List[Dict[str, object]]) -> Dict[str, object]:
    scenes = {entry.get("scene", "unknown") for entry in entries}
    tokens = [int(entry.get("tokens", 0)) for entry in entries]
    latencies = [float(entry.get("latency_sec", 0.0)) for entry in entries]
    ok_count = sum(1 for entry in entries if entry.get("ok"))
    llm_active = any(bool(entry.get("with_llm")) for entry in entries)
    report_paths = {entry.get("report_path") for entry in entries if entry.get("report_path")}

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    avg_tokens = sum(tokens) / len(tokens) if tokens else 0.0

    return {
        "run_id": run_id,
        "scene": ", ".join(sorted(scene for scene in scenes if scene)),
        "iterations": len(entries),
        "avg_latency": avg_latency,
        "avg_tokens": avg_tokens,
        "ok_count": ok_count,
        "total": len(entries),
        "pass_rate": ok_count / len(entries) if entries else 0.0,
        "llm_active": llm_active,
        "report_paths": sorted(report_paths),
        "timestamp": max((_parse_ts(str(entry.get("ts"))) for entry in entries), default=datetime.min),
    }


def _format_summary(label: str, summary: Dict[str, object]) -> List[str]:
    lines = [
        f"## {label}",
        "",
        f"- Run id: `{summary['run_id']}`",
        f"- Scene(s): `{summary['scene'] or 'unknown'}`",
        f"- Iterations: {summary['iterations']}",
        f"- Average latency: {summary['avg_latency']:.3f}s",
        f"- Average tokens: {summary['avg_tokens']:.1f}",
        f"- Success rate: {summary['ok_count']}/{summary['total']} ({summary['pass_rate'] * 100:.1f}%)",
        f"- LLM active: {'yes' if summary['llm_active'] else 'no'}",
    ]
    for path in summary["report_paths"]:
        lines.append(f"- Report log: `{path}`")
    lines.append("")
    return lines


def _format_delta(current: Dict[str, object], previous: Dict[str, object]) -> List[str]:
    latency_delta = current["avg_latency"] - previous["avg_latency"]
    tokens_delta = current["avg_tokens"] - previous["avg_tokens"]
    pass_delta = (current["pass_rate"] - previous["pass_rate"]) * 100
    lines = [
        "## Delta",
        "",
        f"- Delta average latency: {latency_delta:+.3f}s",
        f"- Delta average tokens: {tokens_delta:+.1f}",
        f"- Delta success rate: {pass_delta:+.1f}%",
        f"- LLM status changed: {'yes' if current['llm_active'] != previous['llm_active'] else 'no'}",
        "",
    ]
    return lines


def build_report(entries: List[Dict[str, object]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not entries:
        REPORT_PATH.write_text(
            "# Validation Report\n\n_No SBAR chaos metrics available. Run the harness first._\n",
            encoding="utf-8",
        )
        return

    grouped = _group_by_run(entries)
    if not grouped:
        REPORT_PATH.write_text(
            "# Validation Report\n\n_No SBAR chaos runs recorded yet._\n",
            encoding="utf-8",
        )
        return

    summaries = sorted(
        (_summarise(run_id, run_entries) for run_id, run_entries in grouped.items()),
        key=lambda item: item["timestamp"],
    )
    current = summaries[-1]
    previous = summaries[-2] if len(summaries) > 1 else None

    lines = ["# Validation Report", ""]
    lines.extend(_format_summary("Latest Run", current))
    if previous:
        lines.extend(_format_summary("Previous Run", previous))
        lines.extend(_format_delta(current, previous))

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build validation summary for SBAR chaos runs.")
    parser.parse_args()
    entries = _load_metrics(METRICS_PATH)
    build_report(entries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
