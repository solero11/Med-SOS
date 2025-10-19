
from __future__ import annotations

import json
from pathlib import Path

import yaml

from src.utils.sbar_exporter import export_sbar_dataset


def _build_progress_content() -> str:
    return """## SBAR Snapshot 1.1

### Situation
Patient hypotensive post-induction.

### Background
Limited history; general anesthesia underway.

### Assessment
Differential: 1) Tension pneumothorax 2) Hypovolemia 3) Equipment failure

### Recommendation
Initiate decompression kit setup.

### Clinical Supervisor Critique
Emphasize rapid confirmation of pneumothorax before needle decompression.

---
## 🩺 Final Scene Summary

**Overall Summary:** Hemodynamic instability persisted despite supportive measures; likely tension physiology.

**Diagnostic Impression:**
- Tension pneumothorax
- Hypovolemia
- Equipment failure

**Lessons:**
- Confirm differential before invasive intervention.
- Communicate SBAR updates promptly.

**Final Recommendation:** Proceed with needle decompression and monitor for improvement.
"""


def test_export_sbar_dataset_produces_yaml_and_jsonl(tmp_path: Path) -> None:
    log_root = tmp_path / "_validation" / "sbar_chaos_logs"
    scene_dir = log_root / "test_scene"
    run_dir = scene_dir / "20250101-000000Z"
    run_dir.mkdir(parents=True)

    progress_path = run_dir / "progress.md"
    progress_path.write_text(_build_progress_content(), encoding="utf-8")

    metrics_path = tmp_path / "orchestrator_metrics.jsonl"
    run_dir_key = str(run_dir).replace("\\", "/")
    metrics_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "ts": "2025-01-01T00:00:10Z",
                        "event": "sbar_chaos",
                        "run_dir": run_dir_key,
                        "tokens": 120,
                        "latency_sec": 1.5,
                    }
                ),
                json.dumps(
                    {
                        "ts": "2025-01-01T00:00:12Z",
                        "event": "sbar_scene_summary",
                        "run_dir": run_dir_key,
                        "tokens": 20,
                        "latency_sec": 0.4,
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "exports"
    metadata = export_sbar_dataset(log_root, output_dir, ["yaml", "jsonl"], metrics_path=metrics_path)

    assert metadata["records"] == 2
    assert metadata["runs"] == 1
    assert metadata["scenes"] == ["test_scene"]

    yaml_path = output_dir / "sbar_dataset.yaml"
    jsonl_path = output_dir / "sbar_dataset.jsonl"
    assert yaml_path.exists()
    assert jsonl_path.exists()

    yaml_records = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert isinstance(yaml_records, list)
    assert len(yaml_records) == 2

    jsonl_records = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]
    assert len(jsonl_records) == 2

    snapshot_record = next(rec for rec in jsonl_records if rec["snapshot_id"] == "1.1")
    assert snapshot_record["tokens"] == 120
    assert snapshot_record["meta_summary"] is None
    assert "situation" in snapshot_record["sbar"]

    summary_record = next(rec for rec in jsonl_records if rec["snapshot_id"] == "scene-summary")
    assert summary_record["meta_summary"]["diagnostic_impression"][0] == "Tension pneumothorax"
    assert summary_record["tokens"] == 20
    assert summary_record["latency_sec"] == 0.4
