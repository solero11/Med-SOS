"""
Test harness for streaming clinical scenes through the SBAR pipeline.

The harness is designed for automated verification. Callers provide lightweight
callables for significance detection, assessment generation, and Socratic
question prompts so that the tests remain offline and deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union

import yaml

from src.schema.yaml_schema import EmergencyYAML
from src.utils.sbar_builder import SBAR
from src.utils.sbar_monitor import SBARMonitor, default_update_strategy
from src.utils.scene_player import SceneEvent, play_scene
from src.utils.clinician_query import ClinicianQueryAssistant
from src.utils.clinician_data_store import ClinicianDataStore
from src.utils.sbar_reporting import (
    QuestionEntry,
    SBARSnapshot,
    build_markdown_body,
    build_questions_markdown,
)

# Type aliases for readability
ChangeDetectorFn = Callable[[SceneEvent, SBAR], bool]
AssessmentFn = Callable[[SBAR, SceneEvent, Sequence[SBARSnapshot]], Optional[str]]
QuestionFn = Callable[
    [SBAR, SceneEvent, Sequence[EmergencyYAML], Sequence[SBARSnapshot]],
    Union[str, Sequence[str]],
]


@dataclass
class HarnessResult:
    """Container for the harness outputs."""

    initial_sbar: Dict[str, Optional[str]]
    snapshots: List[SBARSnapshot]
    questions: List[QuestionEntry]
    protocols: List[EmergencyYAML]
    report_path: Path
    questions_path: Path


def _parse_emergency_yaml(payload: Dict) -> EmergencyYAML:
    """
    Support both Pydantic v1 and v2 data model parsing helpers.
    """
    if hasattr(EmergencyYAML, "model_validate"):
        return EmergencyYAML.model_validate(payload)  # type: ignore[attr-defined]
    return EmergencyYAML.parse_obj(payload)  # type: ignore[call-arg]


class SBARSceneHarness:
    """
    Drive a JSONL scene, capture SBAR snapshots, and emit Markdown artifacts.
    """

    def __init__(
        self,
        change_detector: ChangeDetectorFn,
        question_generator: Optional[QuestionFn] = None,
        *,
        assessment_generator: Optional[AssessmentFn] = None,
        update_strategy: Callable[[SceneEvent, SBAR], bool] = default_update_strategy,
        registry_path: Path | str = Path("data/emergencies/registry.yaml"),
        library_dir: Path | str = Path("data/emergencies"),
        realtime: bool = False,
        speed: float = 1.0,
    ) -> None:
        self.change_detector = change_detector
        self._assistant: Optional[ClinicianQueryAssistant] = None
        if question_generator is None:
            self._assistant = ClinicianQueryAssistant()
            def _default_question_generator(
                sbar_obj: SBAR,
                event_obj: SceneEvent,
                protocol_docs: Sequence[EmergencyYAML],
                _: Sequence[SBARSnapshot],
            ):
                return self._assistant.generate(
                    sbar=sbar_obj,
                    event_text=event_obj.text,
                    protocols=protocol_docs,
                )

            self.question_generator = _default_question_generator
        else:
            self.question_generator = question_generator
        self.assessment_generator = assessment_generator
        self.update_strategy = update_strategy
        self.registry_path = Path(registry_path)
        self.library_dir = Path(library_dir)
        self.realtime = realtime
        self.speed = speed
        self._registry_index = self._load_registry_index()
        self._data_store: Optional[ClinicianDataStore] = None

    def run(
        self,
        scene_path: Path | str,
        *,
        report_path: Path | str,
        questions_path: Path | str,
    ) -> HarnessResult:
        scene_path = Path(scene_path)
        report_path = Path(report_path)
        questions_path = Path(questions_path)

        metadata = self._load_scene_metadata(scene_path)
        topic_ids = self._resolve_topic_ids(metadata)
        protocols = self._load_protocols(topic_ids)

        data_path = Path(scene_path).with_name("clinician_data.yaml")
        if data_path.exists():
            self._data_store = ClinicianDataStore.from_path(data_path)
        else:
            self._data_store = None

        if self._assistant:
            self._assistant.reset()

        snapshots: List[SBARSnapshot] = []
        questions: List[QuestionEntry] = []

        def capture_snapshot(sbar: SBAR, event: SceneEvent) -> None:
            if self.assessment_generator:
                try:
                    self.assessment_generator(sbar, event, snapshots)
                except Exception:
                    # Assessment generation is advisory; swallow errors to keep harness running.
                    pass

            snapshot = SBARSnapshot(
                index=len(snapshots) + 1,
                t_start=event.t_start,
                event_text=event.text,
                sbar=sbar.to_dict(),
            )
            snapshots.append(snapshot)

            try:
                generated = self.question_generator(sbar, event, protocols, snapshots)
            except TypeError:
                generated = self.question_generator(sbar, event, protocols)  # type: ignore[misc]
            except Exception:
                generated = []

            if isinstance(generated, str):
                generated_questions = [generated]
            else:
                generated_questions = list(generated or [])

            if not generated_questions:
                fallback = (
                    self._assistant.default_question
                    if self._assistant
                    else "What additional data would clarify the situation?"
                )
                generated_questions = [fallback]

            for question_text in generated_questions[:1]:
                question = question_text.strip()
                if question and not question.endswith("?"):
                    question = question.rstrip(".")
                    question = f"{question}?".replace("??", "?")
                answer = None
                if self._data_store:
                    answer = self._data_store.respond(question, event_time=event.t_start)
                questions.append(
                    QuestionEntry(
                        index=snapshot.index,
                        t_start=snapshot.t_start,
                        event_text=snapshot.event_text,
                        question=question,
                        answer=answer,
                    )
                )

        monitor = SBARMonitor(
            change_detector=self.change_detector,
            update_strategy=self.update_strategy,
            output_fn=capture_snapshot,
        )
        initial_state = monitor.sbar.to_dict()

        play_scene(scene_path, monitor.process_event, realtime=self.realtime, speed=self.speed)

        report_body = build_markdown_body(initial_state, snapshots).rstrip()
        report_lines = [report_body, "", "## Referenced Protocols", ""]
        if protocols:
            for doc in protocols:
                report_lines.append(
                    f"- **{doc.meta.title}** (`{doc.meta.id}`): {doc.summary}"
                )
                if doc.cognitive_prompts:
                    prompts = "; ".join(doc.cognitive_prompts[:2])
                    report_lines.append(f"  - Cognitive prompts: {prompts}")
                report_lines.append("")
        else:
            report_lines.append("_No protocol references loaded._")
            report_lines.append("")

        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(report_lines), encoding="utf-8")

        questions_path.parent.mkdir(parents=True, exist_ok=True)
        questions_path.write_text(build_questions_markdown(questions), encoding="utf-8")

        return HarnessResult(
            initial_sbar=initial_state,
            snapshots=snapshots,
            questions=questions,
            protocols=protocols,
            report_path=report_path,
            questions_path=questions_path,
        )

    # -- Internal helpers -------------------------------------------------

    def _load_scene_metadata(self, scene_path: Path) -> Dict:
        meta_path = scene_path.with_name("scene_metadata.yaml")
        if not meta_path.exists():
            return {}
        with meta_path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _resolve_topic_ids(self, metadata: Dict) -> List[str]:
        tags: Iterable[str] = metadata.get("tags", []) if metadata else []
        topic_ids: List[str] = []
        for tag in tags:
            normalized = str(tag).strip().lower().replace("-", "_")
            if (self.library_dir / f"{normalized}.yaml").exists():
                topic_ids.append(normalized)
                continue
            mapped = self._registry_index.get(normalized)
            if mapped and (self.library_dir / f"{mapped}.yaml").exists():
                topic_ids.append(mapped)
        # Deduplicate while preserving order
        seen = set()
        ordered = []
        for topic_id in topic_ids:
            if topic_id not in seen:
                seen.add(topic_id)
                ordered.append(topic_id)
        return ordered

    def _load_protocols(self, topic_ids: Sequence[str]) -> List[EmergencyYAML]:
        documents: List[EmergencyYAML] = []
        for topic_id in topic_ids:
            yaml_path = self.library_dir / f"{topic_id}.yaml"
            if not yaml_path.exists():
                continue
            with yaml_path.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
            try:
                documents.append(_parse_emergency_yaml(payload))
            except Exception:
                # Skip malformed YAML entries; the test harness should flag this elsewhere.
                continue
        return documents

    def _load_registry_index(self) -> Dict[str, str]:
        if not self.registry_path.exists():
            return {}
        with self.registry_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or []
        index: Dict[str, str] = {}
        for entry in data:
            if not isinstance(entry, dict):
                continue
            parent = entry.get("id")
            children = entry.get("children", [])
            for child in children or []:
                index[str(child).strip().lower()] = str(child).strip().lower()
            if parent:
                index[str(parent).strip().lower()] = str(parent).strip().lower()
        return index


__all__ = ["SBARSceneHarness", "HarnessResult", "ChangeDetectorFn", "AssessmentFn", "QuestionFn"]
