"""
Clinician data store for simulation responses.

Loads structured scene data (vitals, medications, procedures, evaluations)
and provides lightweight natural-language responses to LLM follow-up questions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import yaml


MetricMap = Dict[str, List[Dict[str, object]]]


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _keyword_match(question: str, keywords: Sequence[str]) -> bool:
    return any(keyword in question for keyword in keywords)


@dataclass
class ClinicianDataStore:
    vitals: Dict[str, List[Dict[str, object]]]
    medications: List[Dict[str, object]]
    procedures: List[Dict[str, object]]
    evaluations: List[Dict[str, object]]
    labs: List[Dict[str, object]] = field(default_factory=list)
    imaging: List[Dict[str, object]] = field(default_factory=list)

    @classmethod
    def from_path(cls, path: Path) -> "ClinicianDataStore":
        payload = _load_yaml(path)
        return cls(
            vitals=_sort_entries(payload.get("vitals", {})),
            medications=sorted(payload.get("medications", []), key=lambda item: item.get("t", 0.0)),
            procedures=sorted(payload.get("procedures", []), key=lambda item: item.get("t", 0.0)),
            evaluations=sorted(payload.get("evaluations", []), key=lambda item: item.get("t", 0.0)),
            labs=sorted(payload.get("labs", []), key=lambda item: item.get("t", 0.0)),
            imaging=sorted(payload.get("imaging", []), key=lambda item: item.get("t", 0.0)),
        )

    def available_fields(self) -> List[str]:
        fields = list(self.vitals.keys())
        if self.medications:
            fields.append("medications")
        if self.procedures:
            fields.append("procedures")
        if self.evaluations:
            fields.append("evaluations")
        if self.labs:
            fields.append("labs")
        if self.imaging:
            fields.append("imaging")
        return fields

    def respond(self, question: str, *, event_time: Optional[float] = None) -> str:
        query = question.lower()
        time_hint = event_time or float("inf")

        vitals_map = {
            "blood_pressure": ("blood pressure", "bp", "pressures"),
            "spo2": ("oxygen", "sat", "spo2"),
            "heart_rate": ("heart rate", "pulse"),
            "etco2": ("etco2", "co2"),
        }
        for metric, keywords in vitals_map.items():
            if _keyword_match(query, keywords):
                return self._format_vital(metric, time_hint)

        if _keyword_match(query, ("medication", "drug", "dose", "phenylephrine", "pressors", "vasopressor")):
            return self._format_medication(time_hint)
        if _keyword_match(
            query,
            ("procedure", "decompression", "needle", "chest tube", "intervention", "line"),
        ):
            return self._format_procedure(time_hint)
        if _keyword_match(query, ("result", "response", "outcome", "evaluation")):
            return self._format_evaluation(time_hint)
        if _keyword_match(query, ("lab", "blood gas", "abg", "lactate", "panel", "potassium", "hemoglobin")):
            return self._format_lab(time_hint)
        if _keyword_match(query, ("imaging", "ultrasound", "tee", "x-ray", "scan")):
            return self._format_imaging(time_hint)

        suggestions = ", ".join(self.available_fields())
        return f"I can provide updates for: {suggestions}."

    def _format_vital(self, metric: str, time_hint: float) -> str:
        readings = self.vitals.get(metric)
        if not readings:
            return f"No {metric.replace('_', ' ')} data recorded."
        latest = _latest_before(readings, time_hint)
        value = latest.get("value", "unknown")
        source = latest.get("source", "unknown source")
        note = latest.get("note")
        t_value = latest.get("t", "unknown")
        suffix = f" ({note})" if note else ""
        return f"{metric.replace('_', ' ').capitalize()} {value} at t={t_value:.1f}s via {source}{suffix}."

    def _format_medication(self, time_hint: float) -> str:
        if not self.medications:
            return "No medications documented yet."
        entry = _latest_before(self.medications, time_hint)
        name = entry.get("name", "medication")
        dose = entry.get("dose", "unspecified dose")
        response = entry.get("response")
        t_value = entry.get("t", "unknown")
        phrase = f"{name} {dose} given at t={t_value:.1f}s."
        if response:
            phrase += f" Response noted: {response}."
        return phrase

    def _format_procedure(self, time_hint: float) -> str:
        if not self.procedures:
            return "No procedures performed yet."
        entry = _latest_before(self.procedures, time_hint)
        name = entry.get("name", "procedure").replace("_", " ")
        t_value = entry.get("t", "unknown")
        detail_parts = []
        for key in ("site", "detail", "response"):
            if entry.get(key):
                detail_parts.append(str(entry[key]))
        details = "; ".join(detail_parts)
        detail_suffix = f" ({details})" if details else ""
        return f"{name.capitalize()} at t={t_value:.1f}s{detail_suffix}."

    def _format_evaluation(self, time_hint: float) -> str:
        if not self.evaluations:
            return "No evaluation findings recorded yet."
        entry = _latest_before(self.evaluations, time_hint)
        focus = entry.get("focus", "assessment").replace("_", " ")
        finding = entry.get("finding", "finding unavailable")
        t_value = entry.get("t", "unknown")
        return f"Evaluation of {focus} at t={t_value:.1f}s: {finding}."

    def _format_lab(self, time_hint: float) -> str:
        if not self.labs:
            return "No laboratory data recorded yet."
        entry = _latest_before(self.labs, time_hint)
        name = entry.get("test", entry.get("name", "lab"))
        result = entry.get("result", "result pending")
        t_value = entry.get("t", "unknown")
        note = entry.get("note")
        suffix = f" ({note})" if note else ""
        return f"{name} at t={t_value:.1f}s: {result}{suffix}."

    def _format_imaging(self, time_hint: float) -> str:
        if not self.imaging:
            return "No imaging assessments recorded yet."
        entry = _latest_before(self.imaging, time_hint)
        modality = entry.get("modality", entry.get("name", "imaging")).upper()
        finding = entry.get("finding", "finding unavailable")
        t_value = entry.get("t", "unknown")
        return f"{modality} at t={t_value:.1f}s: {finding}."


def _sort_entries(vitals: Dict[str, List[Dict[str, object]]]) -> Dict[str, List[Dict[str, object]]]:
    sorted_vitals: Dict[str, List[Dict[str, object]]] = {}
    for metric, readings in vitals.items():
        sorted_vitals[metric] = sorted(readings, key=lambda item: item.get("t", 0.0))
    return sorted_vitals


def _latest_before(entries: List[Dict[str, object]], cutoff: float) -> Dict[str, object]:
    if not entries:
        raise ValueError("No entries available for lookup")
    latest = entries[0]
    for entry in entries:
        if float(entry.get("t", 0.0)) <= cutoff:
            latest = entry
        else:
            break
    return latest


__all__ = ["ClinicianDataStore"]
