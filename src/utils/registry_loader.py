"""
Registry Validator for Emergency YAML Library.

Run manually:
    python -m src.utils.registry_loader

Or wire into pytest:
    from src.utils import registry_loader
    def test_registry_valid():
        assert registry_loader.validate_all() == 0
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

import yaml

from src.schema.yaml_schema import EmergencyYAML


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data" / "emergencies" / "registry.yaml"
LIBRARY_DIR = REGISTRY_PATH.parent


def _parse_emergency_yaml(payload: dict) -> EmergencyYAML:
    """
    Support both Pydantic v1 and v2 parsing helpers.
    """
    if hasattr(EmergencyYAML, "model_validate"):
        return EmergencyYAML.model_validate(payload)  # type: ignore[attr-defined]
    return EmergencyYAML.parse_obj(payload)  # type: ignore[call-arg]


def load_registry_slugs(registry_path: Path = REGISTRY_PATH) -> List[str]:
    """
    Return topic ids enumerated in registry.yaml.
    """
    with registry_path.open("r", encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle) or []
    slugs: List[str] = []
    for group in catalog:
        slugs.extend(group.get("children", []) or [])
    return slugs


def validate_yaml_file(
    topic_id: str,
    data_dir: Path = LIBRARY_DIR,
) -> Tuple[str, bool, str | None]:
    """
    Validate a single YAML file against the EmergencyYAML schema.

    Returns (topic_id, success, error_message).
    """
    yaml_path = data_dir / f"{topic_id}.yaml"
    if not yaml_path.exists():
        return topic_id, False, "file missing"
    try:
        with yaml_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        _parse_emergency_yaml(payload)
    except Exception as exc:  # pragma: no cover - surface message for CI logs
        return topic_id, False, str(exc)
    return topic_id, True, None


def validate_all() -> int:
    """
    Validate every YAML referenced in the registry.

    Returns the count of missing or invalid files.
    """
    topic_ids = load_registry_slugs()
    failures: List[str] = []

    for topic_id in topic_ids:
        slug, ok, message = validate_yaml_file(topic_id)
        if ok:
            print(f"✅ {slug}.yaml valid")
        else:
            print(f"❌ {slug}.yaml: {message}")
            failures.append(slug)

    if failures:
        print(f"\nSummary: {len(failures)} file(s) missing or invalid.")
    else:
        print("\n✅ All registry YAMLs validated successfully.")

    return len(failures)


if __name__ == "__main__":
    sys.exit(validate_all())
