from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.utils.llm_runtime import LMStudioRuntime
from src.utils.logger import METRICS_PATH
from src.utils.sbar_scene_harness import SBARChaosHarness


def test_sbar_chaos_harness_produces_markdown_and_metrics() -> None:
    runtime = LMStudioRuntime()
    if not runtime.is_available():
        pytest.skip("LM Studio unavailable; skip SBAR chaos harness test.")

    dialogue_path = Path("_validation/test_dialogue.jsonl")
    dialogue_turns = sum(1 for line in dialogue_path.read_text(encoding="utf-8").splitlines() if line.strip())

    harness = SBARChaosHarness(dialogue_path=dialogue_path, retain_runs=3)
    results = harness.run(iters=1, with_llm=True, runtime=runtime)
    assert results, "Harness should return at least one result."

    result = results[0]
    report_path = Path(result["report_path"])
    assert report_path.exists(), "Expected SBAR chaos report to be generated."
    assert result["with_llm"], "Harness should record that the LLM completed the request."
    assert result["tokens"] > 0, "Expected token usage to be recorded for LLM run."
    assert result.get("progress_path"), "Expected progressive SBAR log path to be recorded."
    run_dir = Path(result.get("run_dir", "") or Path(report_path).parent)
    assert run_dir.exists(), "Run directory should exist for organized outputs."

    markdown = report_path.read_text(encoding="utf-8")
    assert "## Situation" in markdown
    assert "Differential:" in markdown
    assert "Clinical Supervisor Critique" in markdown
    assert "## 🩺 Final Scene Summary" in markdown

    progress_path = Path(result["progress_path"])
    assert progress_path.exists(), "Progressive SBAR log should be created."
    progress_content = progress_path.read_text(encoding="utf-8")
    snapshot_count = progress_content.count("## SBAR Snapshot")
    critique_count = progress_content.count("### Clinical Supervisor Critique")
    assert snapshot_count >= dialogue_turns, "Progress log should include a snapshot per dialogue turn."
    assert critique_count >= snapshot_count, "Each snapshot should be followed by a critique."
    assert "## 🩺 Final Scene Summary" in progress_content
    assert "**Overall Summary:**" in progress_content
    assert "**Lessons:**" in progress_content
    assert "**Final Recommendation:**" in progress_content

    assert METRICS_PATH.exists(), "Metrics file should exist after harness run."

    with METRICS_PATH.open("r", encoding="utf-8") as handle:
        entries = [
            json.loads(line)
            for line in handle
            if line.strip()
        ]

    run_entries = [
        entry
        for entry in entries
        if entry.get("event") == "sbar_chaos" and entry.get("run_id") == result["run_id"]
    ]
    assert run_entries, "Metrics should include entries for the current run."
    for entry in run_entries:
        assert entry["latency_sec"] < 3.0, "Latency should be under 3 seconds."
        assert entry.get("with_llm") is True, "Metrics should indicate the run used the LLM."
        assert entry.get("tokens", 0) > 0, "Metrics should capture token usage."

    summary_entries = [
        entry
        for entry in entries
        if entry.get("event") == "sbar_scene_summary" and entry.get("run_id") == result["run_id"]
    ]
    assert summary_entries, "Expected scene-level summary metrics."
    for entry in summary_entries:
        assert entry.get("tokens", 0) >= 0
        assert entry.get("latency_sec", 0) >= 0

    # Run a second harness execution to ensure a new run directory is created with a fresh progress file.
    second_results = harness.run(iters=1, with_llm=True, runtime=runtime)
    second_progress = Path(second_results[0]["progress_path"])
    assert second_progress.parent != progress_path.parent or second_progress != progress_path
    assert second_progress.exists(), "Second run should produce its own progress log."
    second_content = second_progress.read_text(encoding="utf-8")
    assert "## 🩺 Final Scene Summary" in second_content
