"""
Integration-style tests for the SBAR scene harness.
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from src.schema.yaml_schema import EmergencyYAML
from src.utils.sbar_builder import SBAR
from src.utils.sbar_scene_harness import SBARSceneHarness
from src.utils.scene_player import SceneEvent
from src.utils.sbar_reporting import QuestionEntry, SBARSnapshot


ROOT = Path(__file__).resolve().parents[1]
SCENE_PATH = ROOT / "scenes" / "tension_pneumo" / "dialogue.jsonl"
REGISTRY_PATH = ROOT / "data" / "emergencies" / "registry.yaml"
LIBRARY_DIR = ROOT / "data" / "emergencies"


def significant_change(event: SceneEvent, sbar: SBAR) -> bool:
    trigger_words = ("sat", "pressure", "tension", "needle", "decompression")
    text = event.text.lower()
    return any(word in text for word in trigger_words)


def fake_assessment(sbar: SBAR, event: SceneEvent, snapshots: Sequence[SBARSnapshot]) -> str:
    diagnosis = "Differential: 1) Tension pneumothorax 2) Bronchospasm 3) Mucus plug"
    sbar.assessment = diagnosis
    return diagnosis


def test_scene_harness_generates_reports(tmp_path: Path) -> None:
    report_path = tmp_path / "reports" / "sbar_report.md"
    question_path = tmp_path / "reports" / "llm_questions.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("prior content", encoding="utf-8")

    harness = SBARSceneHarness(
        change_detector=significant_change,
        assessment_generator=fake_assessment,
        registry_path=REGISTRY_PATH,
        library_dir=LIBRARY_DIR,
        realtime=False,
    )

    result = harness.run(
        SCENE_PATH,
        report_path=report_path,
        questions_path=question_path,
    )

    report_text = report_path.read_text(encoding="utf-8")
    questions_text = question_path.read_text(encoding="utf-8")

    assert report_text != "prior content"
    assert "# SBAR Evolution Report" in report_text
    assert "## Referenced Protocols" in report_text
    assert "Pneumothorax / Tension Pneumothorax" in report_text
    assert "Cognitive prompts" in report_text

    assert questions_text.startswith("# Clinician Reflection Prompts")
    assert "?" in questions_text

    assert result.protocols, "Expected at least one emergency protocol to load"
    assert result.protocols[0].meta.id == "pneumothorax"

    assert result.snapshots, "Expected SBAR snapshots to be captured"
    assert all(isinstance(entry, SBARSnapshot) for entry in result.snapshots)
    assert result.snapshots[0].sbar["assessment"] == "Differential: 1) Tension pneumothorax 2) Bronchospasm 3) Mucus plug"

    assert result.questions, "Expected Socratic prompts to be recorded"
    assert all(isinstance(entry, QuestionEntry) for entry in result.questions)
    assert all(entry.question.endswith("?") for entry in result.questions if entry.question)
    first_entry = result.questions[0]
    assert first_entry.answer is not None
    assert "blood pressure" in first_entry.answer.lower() or "oxygen" in first_entry.answer.lower()

    # Ensure Markdown outputs can be regenerated (overwrite behaviour).
    second_result = harness.run(
        SCENE_PATH,
        report_path=report_path,
        questions_path=question_path,
    )
    assert report_path.read_text(encoding="utf-8") == report_text
    assert question_path.read_text(encoding="utf-8") == questions_text
    assert len(second_result.snapshots) == len(result.snapshots)
