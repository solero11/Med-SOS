
"""
Utilities for exporting SBAR chaos harness logs into structured datasets.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import yaml

METRICS_PATH = Path("_validation/orchestrator_metrics.jsonl")

SNAPSHOT_HEADER = re.compile(r"^## SBAR Snapshot (?P<id>[\d\.]+)")
FINAL_SUMMARY_HEADER = re.compile(r"^## 🩺 Final Scene Summary")


@dataclass
class ParsedSnapshot:
    snapshot_id: str
    sbar: Dict[str, str]
    critique: str


@dataclass
class ParsedProgress:
    snapshots: List[ParsedSnapshot]
    scene_summary: Optional[Dict[str, object]]


def _read_lines(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _split_blocks(lines: Sequence[str]) -> List[List[str]]:
    blocks: List[List[str]] = []
    current: List[str] = []
    for line in lines:
        if line.strip() == "---":
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(current)
    return blocks


def _parse_snapshot_block(lines: Sequence[str]) -> Optional[ParsedSnapshot]:
    if not lines:
        return None
    header = lines[0].strip()
    match = SNAPSHOT_HEADER.match(header)
    if not match:
        return None
    snapshot_id = match.group("id")
    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in lines[1:]:
        stripped = line.rstrip()
        if stripped.startswith("### "):
            current = stripped[4:].strip()
            sections[current] = []
        elif stripped.startswith("_"):
            continue
        else:
            if current:
                sections[current].append(stripped)
    def collect(name: str) -> str:
        return "\n".join(sections.get(name, [])).strip()
    sbar = {
        "situation": collect("Situation"),
        "background": collect("Background"),
        "assessment": collect("Assessment"),
        "recommendation": collect("Recommendation"),
    }
    critique = collect("Clinical Supervisor Critique")
    return ParsedSnapshot(snapshot_id=snapshot_id, sbar=sbar, critique=critique)


def _parse_final_summary_block(lines: Sequence[str]) -> Dict[str, object]:
    summary: Dict[str, object] = {
        "summary": "",
        "diagnostic_impression": [],
        "lessons": [],
        "final_recommendation": "",
    }
    current_list: Optional[str] = None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("## 🩺"):
            continue
        if stripped.startswith("**Overall Summary:**"):
            summary["summary"] = stripped.split("**Overall Summary:**", 1)[1].strip()
            current_list = None
        elif stripped.startswith("**Diagnostic Impression:**"):
            summary["diagnostic_impression"] = []
            current_list = "diagnostic_impression"
        elif stripped.startswith("**Lessons:**"):
            summary["lessons"] = []
            current_list = "lessons"
        elif stripped.startswith("**Final Recommendation:**"):
            summary["final_recommendation"] = stripped.split("**Final Recommendation:**", 1)[1].strip()
            current_list = None
        elif stripped.startswith("- ") and current_list:
            summary[current_list].append(stripped[2:].strip())
    return summary


def _parse_progress(progress_path: Path) -> ParsedProgress:
    lines = _read_lines(progress_path)
    blocks = _split_blocks(lines)
    snapshots: List[ParsedSnapshot] = []
    final_summary: Optional[Dict[str, object]] = None
    for block in blocks:
        if not block:
            continue
        if FINAL_SUMMARY_HEADER.match(block[0].strip()):
            final_summary = _parse_final_summary_block(block)
            continue
        snapshot = _parse_snapshot_block(block)
        if snapshot:
            snapshots.append(snapshot)
    return ParsedProgress(snapshots=snapshots, scene_summary=final_summary)


def _load_metrics(metrics_path: Path) -> Dict[str, Dict[str, dict]]:
    buckets: Dict[str, Dict[str, dict]] = {
        "sbar_chaos": {},
        "sbar_scene_summary": {},
    }
    if not metrics_path.exists():
        return buckets
    for line in metrics_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        event = record.get("event")
        run_dir = record.get("run_dir")
        if not event or not run_dir:
            continue
        key = run_dir.replace("\\", "/")
        if event in buckets:
            buckets[event][key] = record
    return buckets


def _write_yaml(records: List[dict], destination: Path) -> None:
    destination.write_text(
        yaml.safe_dump(records, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _write_jsonl(records: List[dict], destination: Path) -> None:
    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def export_sbar_dataset(
    log_root: Path,
    output_dir: Path,
    formats: Optional[List[str]] = None,
    *,
    metrics_path: Optional[Path] = None,
) -> Dict[str, object]:
    """
    Export SBAR chaos runs into structured datasets.
    """
    formats = formats or ["yaml", "jsonl"]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_lookup = _load_metrics(metrics_path or METRICS_PATH)
    dataset: List[dict] = []
    scenes_processed: List[str] = []
    runs_processed = 0

    log_root = Path(log_root)
    if not log_root.exists():
        raise ValueError(f"Log root not found: {log_root}")

    for scene_dir in sorted(p for p in log_root.iterdir() if p.is_dir()):
        scene = scene_dir.name
        for run_dir in sorted((p for p in scene_dir.iterdir() if p.is_dir()), key=lambda p: p.name):
            progress_path = run_dir / "progress.md"
            if not progress_path.exists():
                continue
            parsed = _parse_progress(progress_path)
            run_key = str(run_dir).replace("\\", "/")
            chaos_metric = metrics_lookup["sbar_chaos"].get(run_key, {})
            summary_metric = metrics_lookup["sbar_scene_summary"].get(run_key, {})
            run_tokens = int(chaos_metric.get("tokens", 0) or 0)
            run_latency = float(chaos_metric.get("latency_sec", 0.0) or 0.0)
            summary_tokens = int(summary_metric.get("tokens", 0) or 0)
            summary_latency = float(summary_metric.get("latency_sec", 0.0) or 0.0)

            for snapshot in parsed.snapshots:
                dataset.append(
                    {
                        "scene": scene,
                        "timestamp": run_dir.name,
                        "snapshot_id": snapshot.snapshot_id,
                        "sbar": snapshot.sbar,
                        "critique": snapshot.critique,
                        "meta_summary": None,
                        "tokens": run_tokens,
                        "latency_sec": run_latency,
                    }
                )

            if parsed.scene_summary:
                dataset.append(
                    {
                        "scene": scene,
                        "timestamp": run_dir.name,
                        "snapshot_id": "scene-summary",
                        "sbar": {},
                        "critique": "",
                        "meta_summary": parsed.scene_summary,
                        "tokens": summary_tokens or run_tokens,
                        "latency_sec": summary_latency or run_latency,
                    }
                )

            runs_processed += 1
            if scene not in scenes_processed:
                scenes_processed.append(scene)

    files_written: List[str] = []
    if not dataset:
        return {
            "records": 0,
            "runs": runs_processed,
            "scenes": scenes_processed,
            "files_written": files_written,
        }

    if "yaml" in formats:
        yaml_path = output_dir / "sbar_dataset.yaml"
        _write_yaml(dataset, yaml_path)
        files_written.append(str(yaml_path))

    if "jsonl" in formats:
        jsonl_path = output_dir / "sbar_dataset.jsonl"
        _write_jsonl(dataset, jsonl_path)
        files_written.append(str(jsonl_path))

    return {
        "records": len(dataset),
        "runs": runs_processed,
        "scenes": scenes_processed,
        "files_written": files_written,
    }


__all__ = ["export_sbar_dataset"]
