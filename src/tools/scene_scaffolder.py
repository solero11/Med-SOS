"""
Scene scaffolder: bootstrap ASR dialogue, clinician data, and metadata for new emergencies.

Usage:
    python -m src.tools.scene_scaffolder --topic failed_airway --output-dir scenes/failed_airway

By default, the scaffolder calls the local LM Studio instance through LLMClient.
Pass --dry-run to print prompts without invoking the model.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import yaml

from src.llm.llm_client import LLMClient
from src.llm.lmstudio_runtime import LMStudioRuntime
from src.schema.yaml_schema import EmergencyYAML

SAMPLE_SCENE_ID = "tension_pneumo"
SAMPLE_FILES = ("dialogue.jsonl", "clinician_data.yaml", "scene_metadata.yaml")


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _load_emergency(topic_id: str) -> EmergencyYAML:
    yaml_path = Path("data") / "emergencies" / f"{topic_id}.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"Emergency YAML not found: {yaml_path}")
    payload = _load_yaml(yaml_path)
    if hasattr(EmergencyYAML, "model_validate"):
        return EmergencyYAML.model_validate(payload)  # type: ignore[attr-defined]
    return EmergencyYAML.parse_obj(payload)  # type: ignore[attr-defined]


def _load_sample_scene(scene_id: str = SAMPLE_SCENE_ID) -> Dict[str, str]:
    base = Path("scenes") / scene_id
    data: Dict[str, str] = {}
    for filename in SAMPLE_FILES:
        path = base / filename
        if path.exists():
            data[filename] = _load_text(path)
    return data


def _truncate(text: str, max_chars: int = 600) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _format_list(items: Iterable[str], max_items: int = 6) -> str:
    subset = list(items)[:max_items]
    return ", ".join(subset)


def _parse_dialogue(path: Path) -> List[Dict[str, object]]:
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("dialogue JSONL is empty")
    events: List[Dict[str, object]] = []
    for idx, line in enumerate(content.splitlines(), start=1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {idx}: invalid JSON ({exc})") from exc
        for key in ("t_start", "t_end", "text"):
            if key not in obj:
                raise ValueError(f"line {idx}: missing key '{key}'")
        events.append(obj)
    return events


def _validate_metadata(meta: Dict[str, object]) -> None:
    required_fields = ("case_id", "duration_seconds", "phases")
    for field in required_fields:
        if field not in meta:
            raise ValueError(f"metadata missing '{field}'")
    phases = meta.get("phases") or []
    if not isinstance(phases, list) or not phases:
        raise ValueError("metadata phases must be a non-empty list")


@dataclass
class ScenePrompts:
    dialogue: str
    clinician_data: str
    metadata: str


class SceneScaffolder:
    """
    Construct LLM prompts (and optionally call the model) to scaffold a new scene.
    """

    def __init__(
        self,
        topic_id: str,
        output_dir: Path,
        sample_scene: str = SAMPLE_SCENE_ID,
        client: Optional[LLMClient] = None,
        dry_run: bool = False,
        validate: bool = False,
    ) -> None:
        self.topic_id = topic_id
        self.output_dir = output_dir
        self.sample_scene = sample_scene
        self.client = client
        self.dry_run = dry_run or client is None
        self.validate_outputs_flag = validate

        self.emergency = _load_emergency(topic_id)
        self.sample_assets = _load_sample_scene(sample_scene)

    def build_prompts(self) -> ScenePrompts:
        em = self.emergency
        sample_dialogue = _truncate(self.sample_assets.get("dialogue.jsonl", ""), 800)
        sample_data = _truncate(self.sample_assets.get("clinician_data.yaml", ""), 800)
        sample_meta = self.sample_assets.get("scene_metadata.yaml", "")

        signals = _format_list(em.signals)
        red_flags = _format_list(em.red_flags or [])
        differential = _format_list(em.primary_differential)
        first_checks = _format_list(em.first_checks)

        dialogue_prompt = f"""
You are writing a chaotic intraoperative audio transcript for the emergency: "{em.meta.title}" (id: {em.meta.id}).
Produce JSON Lines (one JSON object per line) with keys t_start, t_end, text, and optional speaker.
Follow these requirements:
- Duration roughly 4-5 minutes in real time (260-320 seconds).
- Cover the crisis arc: early signal, deterioration, diagnosis, intervention, stabilization.
- Weave in signals: {signals}.
- Highlight red flags when appropriate: {red_flags or 'none emphasised'}.
- Reference differential triggers such as {differential}.
- Mention first-line checks/interventions like {first_checks}.
- Include background noise cues occasionally (e.g., [alarm], [suction]) to mimic ASR chaos.
- Keep language terse, present tense, realistic OR cadence.

Example excerpt from an existing scene (same format):
{sample_dialogue}

Return ONLY JSONL with no commentary or code fences.
""".strip()

        clinician_prompt = f"""
Given the newly generated dialogue for "{em.meta.title}", provide structured clinical data in YAML that our harness can use to answer follow-up questions.
Use the following keys mirroring the sample structure: vitals (blood_pressure, spo2, heart_rate, etco2), medications, procedures, evaluations.
Each entry should include 't' (seconds), a value or description, and optional notes.
Ensure the timeline matches the dialogue you created.

Example format:
{sample_data}

Return ONLY YAML (no code fences).
""".strip()

        metadata_prompt = f"""
Create scene_metadata.yaml for the same case "{em.meta.title}" using the format shown below.
Derive phases that mirror the dialogue and clinician data you produced.
Include participants (roles) and tags drawn from the emergency topic.

Reference example:
{sample_meta}

Return ONLY YAML.
""".strip()

        return ScenePrompts(
            dialogue=dialogue_prompt,
            clinician_data=clinician_prompt,
            metadata=metadata_prompt,
        )

    def _call_llm(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("LLM client not configured")
        return self.client.ask(prompt).strip()

    def _write_output(self, filename: str, content: str) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / filename).write_text(content.strip() + "\n", encoding="utf-8")

    def run(self, smoke_test: bool = False) -> Dict[str, str]:
        prompts = self.build_prompts()
        outputs: Dict[str, str] = {}
        for filename, prompt in (
            ("dialogue.jsonl", prompts.dialogue),
            ("clinician_data.yaml", prompts.clinician_data),
            ("scene_metadata.yaml", prompts.metadata),
        ):
            if self.dry_run:
                print(f"\n--- Prompt for {filename} ---\n{prompt}\n")
                continue
            response = self._call_llm(prompt)
            outputs[filename] = response
            self._write_output(filename, response)
            print(f"[scene_scaffolder] Wrote {filename} to {self.output_dir}")
        if self.validate_outputs_flag:
            self.validate_directory(smoke_test=smoke_test)
        return outputs

    # -- Validation helpers ------------------------------------------------

    def validate_directory(self, smoke_test: bool = False) -> None:
        dialogue_path = self.output_dir / "dialogue.jsonl"
        clinician_path = self.output_dir / "clinician_data.yaml"
        metadata_path = self.output_dir / "scene_metadata.yaml"

        errors: List[str] = []
        try:
            events = _parse_dialogue(dialogue_path)
            print(f"[scene_scaffolder] Dialogue OK ({len(events)} events)")
        except Exception as exc:  # pragma: no cover - surfaced in tests
            errors.append(f"dialogue.jsonl invalid: {exc}")

        try:
            data_store = ClinicianDataStore.from_path(clinician_path)
            print(f"[scene_scaffolder] Clinician data OK (fields: {', '.join(data_store.available_fields())})")
        except Exception as exc:
            errors.append(f"clinician_data.yaml invalid: {exc}")

        try:
            meta = _load_yaml(metadata_path)
            _validate_metadata(meta)
            print(f"[scene_scaffolder] Metadata OK (case_id={meta.get('case_id', 'unknown')})")
        except Exception as exc:
            errors.append(f"scene_metadata.yaml invalid: {exc}")

        if errors:
            raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))

        if smoke_test:
            self._run_smoke_test(dialogue_path, clinician_path)

    def _run_smoke_test(self, dialogue_path: Path, clinician_path: Path) -> None:
        try:
            from src.utils.sbar_scene_harness import SBARSceneHarness
            from src.utils.sbar_builder import SBAR
            from src.utils.scene_player import SceneEvent
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(f"Unable to import harness utilities: {exc}") from exc

        def heuristic_change(event: SceneEvent, sbar: SBAR) -> bool:
            text = event.text.lower()
            keywords = ("sat", "pressure", "tension", "needle", "decompress", "med", "drug")
            return any(token in text for token in keywords)

        harness = SBARSceneHarness(
            change_detector=heuristic_change,
            registry_path=Path("data/emergencies/registry.yaml"),
            library_dir=Path("data/emergencies"),
            realtime=False,
        )
        report_dir = self.output_dir / "_validation"
        report_path = report_dir / "sbar_report.md"
        questions_path = report_dir / "llm_questions.md"
        harness.run(dialogue_path, report_path=report_path, questions_path=questions_path)
        print(f"[scene_scaffolder] Smoke test ok; reports in {report_dir}")


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate scene scaffolding via LLM prompts.")
    parser.add_argument("--topic", required=True, help="Emergency topic id (matches data/emergencies/<id>.yaml)")
    parser.add_argument("--output-dir", type=Path, required=True, help="Destination directory for scene files")
    parser.add_argument(
        "--sample-scene",
        default=SAMPLE_SCENE_ID,
        help="Existing scene id to use as structural reference",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling the LLM")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate outputs after generation (or validate an existing directory in dry-run mode)",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run SBARSceneHarness smoke test after validation (implies --validate)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override LM Studio base URL",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override LM Studio model id",
    )
    return parser.parse_args(argv)


def build_client(base_url: Optional[str], model: Optional[str]) -> LLMClient:
    runtime = LMStudioRuntime.from_env()
    if base_url:
        runtime.base_url = base_url
    if model:
        runtime.target_model = model
    runtime.ensure_model_loaded()
    return LLMClient(
        api_url=f"{runtime.base_url.rstrip('/')}/v1/chat/completions",
        system_prompt="You are a simulation author producing realistic intraoperative crisis scenarios.",
        model=runtime.target_model,
        temperature=0.6,
    )


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    client: Optional[LLMClient] = None
    if not args.dry_run:
        client = build_client(args.base_url, args.model)
    scaffolder = SceneScaffolder(
        topic_id=args.topic,
        output_dir=args.output_dir,
        sample_scene=args.sample_scene,
        client=client,
        dry_run=args.dry_run,
        validate=args.validate or args.smoke_test,
    )
    scaffolder.run(smoke_test=args.smoke_test)
    if args.dry_run and (args.validate or args.smoke_test):
        scaffolder.validate_directory(smoke_test=args.smoke_test)


if __name__ == "__main__":
    main()
