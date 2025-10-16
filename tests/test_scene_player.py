import json
from pathlib import Path
from typing import List

from src.utils.scene_player import SceneEvent, load_scene, iter_scene, play_scene


def write_temp_scene(tmp_path: Path) -> Path:
    events = [
        {"t_start": 2.0, "t_end": 3.0, "text": "second"},
        {"t_start": 0.0, "t_end": 1.0, "text": "first"},
    ]
    scene_path = tmp_path / "scene.jsonl"
    with scene_path.open("w", encoding="utf-8") as handle:
        for payload in events:
            handle.write(json.dumps(payload) + "\n")
    return scene_path


def test_load_scene_sorted(tmp_path: Path):
    scene_path = write_temp_scene(tmp_path)
    events = load_scene(scene_path)
    assert [e.text for e in events] == ["first", "second"]


def test_iter_scene_applies_start_offset(tmp_path: Path):
    scene_path = write_temp_scene(tmp_path)
    events = load_scene(scene_path)
    filtered = list(iter_scene(events, start_offset=1.5))
    assert [e.text for e in filtered] == ["second"]


def test_play_scene_invokes_callback(tmp_path: Path):
    scene_path = write_temp_scene(tmp_path)
    captured: List[SceneEvent] = []

    def _callback(event: SceneEvent):
        captured.append(event)

    # Use realtime=False to avoid sleeping in unit tests.
    play_scene(scene_path, _callback, realtime=False)
    assert [e.text for e in captured] == ["first", "second"]
