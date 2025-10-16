from pathlib import Path

from src.tools.scene_scaffolder import SceneScaffolder


def test_scene_scaffolder_builds_prompts(tmp_path: Path):
    scaffolder = SceneScaffolder(
        topic_id="pneumothorax",
        output_dir=tmp_path,
        dry_run=True,
    )
    prompts = scaffolder.build_prompts()
    assert "Pneumothorax / Tension Pneumothorax" in prompts.dialogue
    assert "JSON Lines" in prompts.dialogue
    assert "Return ONLY YAML" in prompts.clinician_data
    assert "scene_metadata.yaml" in prompts.metadata
