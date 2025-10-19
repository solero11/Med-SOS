"""
Test harness for streaming clinical scenes through the SBAR pipeline.

The harness is designed for automated verification. Callers provide lightweight
callables for significance detection, assessment generation, and Socratic
question prompts so that the tests remain offline and deterministic.
"""
from __future__ import annotations

import os
import time
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union
from datetime import datetime

import yaml

from src.schema.yaml_schema import EmergencyYAML
from src.utils.generate_sbar_report import generate_progressive_sbar_log, generate_sbar_report
from src.utils.llm_runtime import LMStudioRuntime
from src.utils.logger import log_turn_metric
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


class SBARChaosHarness:
    """
    Minimal chaos harness that replays dialogue JSONL files through the SBAR generator.
    """

    def __init__(
        self,
        dialogue_path: Path | str = Path("_validation/test_dialogue.jsonl"),
        *,
        output_dir: Path | str = Path("_validation/sbar_chaos_logs"),
        retain_runs: int = 5,
    ) -> None:
        self.dialogue_path = Path(dialogue_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir = self.output_dir / "archive"
        self.retain_runs = max(int(retain_runs), 0)

    def run(
        self,
        *,
        iters: int = 1,
        with_llm: bool = True,
        runtime: Optional[LMStudioRuntime] = None,
        scene_path: Optional[Path | str] = None,
    ) -> List[Dict[str, object]]:
        """
        Execute the chaos harness for the provided number of iterations.
        """
        if iters < 1:
            raise ValueError("iters must be >= 1")
        scene_path = Path(scene_path) if scene_path else self.dialogue_path
        if not scene_path.exists():
            raise FileNotFoundError(f"Dialogue JSONL not found: {scene_path}")

        runtime_obj = runtime or LMStudioRuntime(
            base_url=os.getenv("LLM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
        )
        runtime_available = runtime_obj.is_available() if with_llm else False
        effective_with_llm = bool(with_llm and runtime_available)

        scene_name = scene_path.stem
        scene_dir = self.output_dir / scene_name
        scene_dir.mkdir(parents=True, exist_ok=True)

        run_started_at = datetime.utcnow()
        run_id, run_dir = self._prepare_run_directory(scene_dir)
        run_started_display = run_started_at.strftime("%Y-%m-%d %H:%M:%SZ")
        aggregated_path = run_dir / "summary.md"
        header_lines = [
            f"# SBAR Chaos Log — {scene_name}",
            "",
            f"_Run started: {run_started_display}_",
            "",
        ]
        aggregated_path.write_text("\n".join(header_lines), encoding="utf-8")

        results: List[Dict[str, object]] = []

        for iteration in range(1, iters + 1):
            tmp_output = run_dir / f".{scene_name}_{run_id}_iter{iteration:02d}.md"
            start = time.perf_counter()
            try:
                result = generate_sbar_report(
                    scene_path,
                    tmp_output,
                    llm=runtime_obj if effective_with_llm else None,
                    with_llm=effective_with_llm,
                )
                progress_path = run_dir / "progress.md"
                progress_result = generate_progressive_sbar_log(
                    scene_path,
                    progress_path,
                    runtime=runtime_obj if effective_with_llm else None,
                    with_llm=effective_with_llm,
                    run_id=run_id,
                    iteration=iteration,
                )
            except Exception as exc:  # pragma: no cover - surfaced in tests via failure
                latency = round(time.perf_counter() - start, 3)
                log_turn_metric(
                    "sbar_chaos",
                    ok=False,
                    latency_sec=latency,
                    extra={
                        "scene": scene_name,
                        "iteration": iteration,
                        "run_id": run_id,
                        "with_llm": effective_with_llm,
                        "error": str(exc),
                    },
                )
                raise

            elapsed = time.perf_counter() - start
            reported_latency = float(result.get("latency", 0.0)) + float(
                progress_result.get("latency", 0.0) or 0.0
            )
            latency = round(reported_latency if reported_latency > 0 else elapsed, 3)
            tokens = int(result.get("tokens", 0)) + int(progress_result.get("tokens", 0) or 0)
            ok = bool(result.get("ok", False))
            actual_with_llm = bool(result.get("with_llm", False) or progress_result.get("llm_used", False))
            raw_response = result.get("raw_response")
            progress_path_str = progress_result.get("progress_path")
            snapshot_count = len(progress_result.get("snapshots", []))
            scene_summary = progress_result.get("scene_summary") or {}
            scene_summary_markdown = scene_summary.get("markdown")
            scene_summary_tokens = int(scene_summary.get("tokens", 0) or 0)
            scene_summary_latency = float(scene_summary.get("latency", 0.0) or 0.0)
            scene_summary_with_llm = bool(scene_summary.get("with_llm"))

            report_content = Path(result["output_path"]).read_text(encoding="utf-8")
            with aggregated_path.open("a", encoding="utf-8") as handle:
                handle.write(f"## Iteration {iteration} — {run_started_display}\n\n")
                handle.write(report_content.strip())
                handle.write("\n\n")
                if scene_summary_markdown:
                    handle.write(scene_summary_markdown.strip())
                    handle.write("\n\n")
                handle.write("---\n\n")

            if tmp_output.exists():
                tmp_output.unlink()

            log_turn_metric(
                "sbar_chaos",
                ok=ok,
                latency_sec=latency,
                extra={
                    "scene": scene_name,
                    "iteration": iteration,
                    "run_id": run_id,
                    "with_llm": actual_with_llm,
                    "tokens": tokens,
                    "report_path": str(aggregated_path),
                    "llm_preview": (str(raw_response)[:160] if raw_response else None),
                    "progress_path": str(progress_path_str) if progress_path_str else None,
                    "snapshots_logged": snapshot_count,
                    "run_dir": str(run_dir),
                    "run_started": run_started_display,
                },
            )

            log_turn_metric(
                "sbar_scene_summary",
                ok=True,
                latency_sec=scene_summary_latency,
                extra={
                    "scene": scene_name,
                    "iteration": iteration,
                    "run_id": run_id,
                    "with_llm": scene_summary_with_llm,
                    "tokens": scene_summary_tokens,
                    "summary_path": str(aggregated_path),
                    "progress_path": str(progress_path_str) if progress_path_str else None,
                    "run_dir": str(run_dir),
                    "run_started": run_started_display,
                },
            )

            results.append(
                {
                    "scene": scene_name,
                    "iteration": iteration,
                    "run_id": run_id,
                    "with_llm": actual_with_llm,
                    "latency": latency,
                    "tokens": tokens,
                    "ok": ok,
                    "report_path": str(aggregated_path),
                    "progress_path": str(progress_path_str) if progress_path_str else None,
                    "snapshots": snapshot_count,
                    "run_dir": str(run_dir),
                    "run_started": run_started_display,
                    "scene_summary_tokens": scene_summary_tokens,
                    "scene_summary_latency": scene_summary_latency,
                    "scene_summary_with_llm": scene_summary_with_llm,
                }
            )

        self._enforce_retention(scene_dir)

        return results

    def _prepare_run_directory(self, scene_dir: Path) -> tuple[str, Path]:
        scene_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%SZ")
        run_id = timestamp
        run_dir = scene_dir / run_id
        counter = 2
        while run_dir.exists():
            run_id = f"{timestamp}-{counter:02d}"
            run_dir = scene_dir / run_id
            counter += 1
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_id, run_dir

    def _enforce_retention(self, scene_dir: Path) -> None:
        if self.retain_runs <= 0:
            return
        run_dirs = sorted(
            [path for path in scene_dir.iterdir() if path.is_dir()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for old_dir in run_dirs[self.retain_runs :]:
            archive_target = self.archive_dir / scene_dir.name / old_dir.name
            archive_target.parent.mkdir(parents=True, exist_ok=True)
            if archive_target.exists():
                shutil.rmtree(archive_target)
            shutil.move(str(old_dir), str(archive_target))


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


__all__ = [
    "SBARChaosHarness",
    "SBARSceneHarness",
    "HarnessResult",
    "ChangeDetectorFn",
    "AssessmentFn",
    "QuestionFn",
]
