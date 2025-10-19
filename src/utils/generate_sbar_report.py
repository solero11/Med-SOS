"""
Generate SBAR Markdown reports for simulated dialogue streams.

This refactor focuses on a lightweight pipeline that can run entirely offline
or against a locally hosted Medicine LLM exposed via LM Studio.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Sequence, cast

import requests

import requests

from src.utils.llm_runtime import LMStudioRuntime


SBAR_SECTIONS = ("situation", "background", "assessment", "recommendation")


def _read_dialogue(dialogue_path: Path) -> List[Dict[str, object]]:
    segments: List[Dict[str, object]] = []
    with dialogue_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                segments.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return segments


def _format_dialogue(segments: Sequence[Dict[str, object]]) -> str:
    lines: List[str] = []
    for idx, entry in enumerate(segments):
        speaker = str(entry.get("speaker") or f"Speaker {idx + 1}")
        text = entry.get("text") or ""
        lines.append(f"{speaker}: {text}".strip())
    return "\n".join(lines).strip()


def _build_sbar_prompt(dialogue_text: str) -> List[Dict[str, str]]:
    system = textwrap.dedent(
        """
        You are an anesthesiology resident producing a structured SBAR summary based on intra-operative dialogue.
        Return a JSON object with the keys: situation, background, assessment, recommendation, differential.
        The differential must be a list of the top three diagnoses ordered from most to least likely.
        Each field should be short (one to two sentences) and clinically precise.
        Respond with valid JSON only, without prose, markdown, or explanation.
        Example format:
        {
          "situation": "string",
          "background": "string",
          "assessment": "string",
          "recommendation": "string",
          "differential": ["string", "string", "string"]
        }
        """
    ).strip()
    user = textwrap.dedent(
        f"""
        Dialogue transcript:
        {dialogue_text}

        Respond ONLY with JSON.
        """
    ).strip()
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _build_retry_prompt() -> Dict[str, str]:
    return {
        "role": "user",
        "content": (
            "Your previous reply was not valid JSON. Respond again right now with a single JSON object that matches "
            'the schema exactly: {"situation": "...", "background": "...", "assessment": "...", '
            '"recommendation": "...", "differential": ["...", "...", "..."]}. No explanation, only JSON.'
        ),
    }


def _build_critique_prompt(markdown_body: str) -> List[Dict[str, str]]:
    system = "You are a clinical supervisor critiquing an SBAR handoff for accuracy, completeness, and clarity."
    user = f"Evaluate the following SBAR summary and provide a brief critique (max 3 bullets):\n\n{markdown_body}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _strip_json_block(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        parts = content.split("```")
        if len(parts) >= 2:
            block = parts[1]
            if block.lstrip().startswith("json"):
                block = block.split("\n", 1)[1] if "\n" in block else ""
            return block.strip()
    return content


def _safe_json_extract(content: str) -> str:
    snippet = _strip_json_block(content)
    if not snippet:
        return ""
    match = re.search(r"\{.*\}", snippet, re.DOTALL)
    if match:
        return match.group(0)
    snippet = snippet.strip()
    if snippet.startswith("{") and snippet.endswith("}"):
        return snippet
    return ""


def _parse_sbar_payload(content: str) -> Dict[str, object]:
    if not content:
        return {}
    cleaned = _safe_json_extract(content)
    if not cleaned:
        return {}
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _fallback_sbar(segments: Sequence[Dict[str, object]]) -> Dict[str, object]:
    default_differential = [
        "Tension pneumothorax",
        "Hypovolemia",
        "Equipment failure",
    ]
    first_text = str(segments[0].get("text")) if segments else ""
    return {
        "situation": first_text or "Rapid deterioration noted in the OR with limited context available.",
        "background": "Limited chart data available; patient under general anesthesia with new hypotension.",
        "assessment": "Differential: 1) Tension pneumothorax 2) Hypovolemia 3) Equipment failure",
        "recommendation": "Initiate emergency decompression protocol and alert supervising anesthesia.",
        "differential": default_differential,
        "_stub": True,
    }


def _normalize_differential(value: object) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _ensure_assessment(assessment: str, differential: Sequence[str]) -> str:
    if "Differential:" in assessment:
        return assessment.strip()
    formatted = "Differential: " + " ".join(
        [f"{idx + 1}) {item}" for idx, item in enumerate(differential[:3])]
    )
    return f"{assessment.strip()} {formatted}".strip()


def _invoke_sbar(
    runtime: LMStudioRuntime,
    segments: Sequence[Dict[str, object]],
    with_llm: bool,
) -> Dict[str, object]:
    dialogue_text = _format_dialogue(segments)
    tokens = 0
    latency = 0.0
    llm_used = False
    raw_response: Optional[str] = None
    sbar_payload: Dict[str, object] = {}

    if with_llm:
        base_messages = _build_sbar_prompt(dialogue_text)
        attempts = 2
        for attempt in range(attempts):
            messages = list(base_messages)
            if attempt > 0:
                messages.append(_build_retry_prompt())
            try:
                completion = runtime.chat(
                    messages,
                    temperature=0.0,
                    response_format={"type": "json_object"},
                )
            except requests.HTTPError:
                completion = runtime.chat(messages, temperature=0.0)
            content = str(completion.get("content") or "")
            raw_response = content
            payload = _parse_sbar_payload(content)
            latency += float(completion.get("latency", 0.0))
            token_increment = int(completion.get("tokens", 0))
            if token_increment == 0:
                token_increment = _estimate_tokens(content)
            tokens += token_increment
            if payload:
                sbar_payload = payload
                llm_used = True
                break

    if not sbar_payload:
        sbar_payload = _fallback_sbar(segments)
        if with_llm and raw_response:
            sbar_payload["_llm_warning"] = (
                "LLM returned unstructured text; populated SBAR using deterministic fallback."
            )
            llm_used = True

    return {
        "sbar": sbar_payload,
        "tokens": tokens,
        "latency": latency,
        "llm_used": llm_used,
        "raw_response": raw_response,
    }


def _invoke_critique(
    runtime: LMStudioRuntime,
    scene_name: str,
    sbar_payload: Dict[str, object],
    with_llm: bool,
) -> Dict[str, object]:
    tokens = 0
    latency = 0.0
    llm_used = False
    critique: Optional[str] = None

    if with_llm:
        try:
            body = _build_markdown(scene_name, sbar_payload, None, include_critique=False)
            completion = runtime.chat(
                _build_critique_prompt(body),
                temperature=0.2,
            )
            critique = str(completion.get("content") or "")
            latency += float(completion.get("latency", 0.0))
            token_increment = int(completion.get("tokens", 0))
            if token_increment == 0:
                token_increment = _estimate_tokens(critique)
            tokens += token_increment
            llm_used = True
        except Exception:
            critique = None

    if not critique:
        critique = (
            "LLM unavailable; review SBAR entries manually to confirm accuracy and completeness."
            if with_llm
            else "LLM disabled; manual critique required."
        )

    return {
        "critique": critique,
        "tokens": tokens,
        "latency": latency,
        "llm_used": llm_used,
    }


def _render_snapshot_markdown(
    snapshot_label: str,
    sbar_payload: Dict[str, object],
    critique: str,
    *,
    t_start: Optional[float] = None,
    run_id: Optional[str] = None,
) -> str:
    differential_list = _normalize_differential(sbar_payload.get("differential"))
    lines: List[str] = [f"## SBAR Snapshot {snapshot_label}", ""]

    metadata_bits: List[str] = []
    if t_start is not None:
        metadata_bits.append(f"t={float(t_start):.1f}s")
    if run_id:
        metadata_bits.append(f"run={run_id}")
    if metadata_bits:
        lines.append("_" + ", ".join(metadata_bits) + "_")
        lines.append("")

    warning = sbar_payload.get("_llm_warning")
    if warning:
        lines.append(f"_Note: {warning}_")
        lines.append("")

    for section in SBAR_SECTIONS:
        heading = section.capitalize()
        lines.append(f"### {heading}")
        value = str(sbar_payload.get(section) or "").strip()
        if section == "assessment":
            value = _ensure_assessment(value, differential_list or ["Unknown", "Unknown", "Unknown"])
        if not value:
            value = "_No data provided._"
        lines.append(value)
        lines.append("")

    if differential_list:
        differential_text = "; ".join(differential_list[:3])
    else:
        differential_text = "Unknown"
    lines.append("### Differential")
    lines.append(differential_text)
    lines.append("")

    lines.append("### Clinical Supervisor Critique")
    lines.append(critique.strip() or "No critique returned from supervisor model.")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def _build_scene_summary_prompt(scene_name: str, snapshots: Sequence[Dict[str, object]]) -> List[Dict[str, str]]:
    timeline_entries: List[str] = []
    for snap in snapshots[-25:]:
        label = str(snap.get("label") or snap.get("index") or "?")
        sbar = snap.get("sbar") or {}
        situation = str(sbar.get("situation") or "Unknown situation")
        assessment = str(sbar.get("assessment") or "Assessment unavailable")
        recommendation = str(sbar.get("recommendation") or "Recommendation unavailable")
        timeline_entries.append(
            f"{label}: Situation={situation}; Assessment={assessment}; Recommendation={recommendation}"
        )
    timeline_text = "\n".join(timeline_entries) or "No SBAR snapshots were recorded."
    system = (
        "You are a senior clinical supervisor evaluating an SBAR handoff timeline. "
        "Return strictly valid JSON using the provided schema."
    )
    user = (
        f"Scene: {scene_name}\n"
        "SBAR timeline:\n"
        f"{timeline_text}\n\n"
        "Provide:\n"
        "1. Concise overall summary of patient evolution.\n"
        "2. Top three likely root causes or diagnoses.\n"
        "3. Two key lessons or cognitive errors to avoid.\n"
        "4. Final recommendation in 1–2 sentences.\n\n"
        'Respond as JSON: {"summary": "...", "diagnostic_impression": ["..."], "lessons": ["..."], "final_recommendation": "..."}'
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _build_scene_summary_retry_prompt() -> Dict[str, str]:
    return {
        "role": "user",
        "content": (
            "Your previous reply was not valid JSON. Respond immediately with a single JSON object using the schema "
            '{"summary": "...", "diagnostic_impression": ["..."], "lessons": ["..."], "final_recommendation": "..."}'
        ),
    }


def _parse_scene_summary(content: str) -> Dict[str, object]:
    cleaned = _safe_json_extract(content)
    if not cleaned:
        return {}
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _fallback_scene_summary(scene_name: str, snapshots: Sequence[Dict[str, object]]) -> Dict[str, object]:
    if snapshots:
        first = snapshots[0].get("sbar", {})
        last = snapshots[-1].get("sbar", {})
    else:
        first = last = {}
    first_situation = str(first.get("situation") or "Initial presentation not captured.")
    last_recommendation = str(last.get("recommendation") or "Recommendation not captured; ensure follow-up.")
    differential = _normalize_differential(last.get("differential") if isinstance(last, dict) else [])
    if not differential:
        differential = ["Tension pneumothorax", "Hypovolemia", "Equipment failure"]
    lessons = [
        "Validate differential diagnoses continuously against new SBAR data.",
        "Escalate invasive interventions promptly once non-invasive measures plateau.",
    ]
    return {
        "summary": f"Scene {scene_name} captured {len(snapshots)} SBAR updates. Initial situation: {first_situation}",
        "diagnostic_impression": differential[:3],
        "lessons": lessons[:2],
        "final_recommendation": last_recommendation,
    }


def generate_scene_summary(
    scene_name: str,
    snapshots: Sequence[Dict[str, object]],
    runtime: LMStudioRuntime,
    with_llm: bool = True,
) -> Dict[str, object]:
    tokens = 0
    latency = 0.0
    llm_used = False
    summary_payload: Dict[str, object] = {}
    raw_response: Optional[str] = None

    if with_llm and snapshots:
        base_messages = _build_scene_summary_prompt(scene_name, snapshots)
        attempts = 2
        for attempt in range(attempts):
            messages = list(base_messages)
            if attempt > 0:
                messages.append(_build_scene_summary_retry_prompt())
            try:
                completion = runtime.chat(
                    messages,
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
            except requests.HTTPError:
                completion = runtime.chat(messages, temperature=0.2)
            content = str(completion.get("content") or "")
            raw_response = content
            payload = _parse_scene_summary(content)
            latency += float(completion.get("latency", 0.0) or 0.0)
            token_increment = int(completion.get("tokens", 0) or 0)
            if token_increment == 0:
                token_increment = _estimate_tokens(content)
            tokens += token_increment
            if payload:
                summary_payload = payload
                llm_used = True
                break

    if not summary_payload:
        summary_payload = _fallback_scene_summary(scene_name, snapshots)

    markers = {
        "summary": str(summary_payload.get("summary") or "").strip(),
        "diagnostic_impression": _normalize_differential(summary_payload.get("diagnostic_impression")),
        "lessons": [str(item).strip() for item in summary_payload.get("lessons", []) if str(item).strip()],
        "final_recommendation": str(summary_payload.get("final_recommendation") or "").strip(),
    }

    if not markers["lessons"]:
        markers["lessons"] = [
            "Cross-check SBAR elements for consistency to avoid cognitive drift.",
            "Communicate recommendation changes promptly to the whole team.",
        ]

    markdown = _render_scene_summary_markdown(markers)

    return {
        "summary": markers,
        "tokens": int(tokens),
        "latency": round(latency, 3),
        "with_llm": llm_used,
        "markdown": markdown,
        "raw_response": raw_response,
    }


def _render_scene_summary_markdown(summary: Dict[str, object]) -> str:
    lines = ["## 🩺 Final Scene Summary", ""]

    overall = str(summary.get("summary") or "").strip()
    impression = summary.get("diagnostic_impression") or []
    lessons = summary.get("lessons") or []
    recommendation = str(summary.get("final_recommendation") or "").strip()

    lines.append(f"**Overall Summary:** {overall or 'No summary provided.'}")
    lines.append("")

    if impression:
        lines.append("**Diagnostic Impression:**")
        for item in list(impression)[:3]:
            lines.append(f"- {item}")
    else:
        lines.append("**Diagnostic Impression:** _Not provided._")
    lines.append("")

    if lessons:
        lines.append("**Lessons:**")
        for item in list(lessons)[:2]:
            lines.append(f"- {item}")
    else:
        lines.append("**Lessons:** _Not provided._")
    lines.append("")

    lines.append(f"**Final Recommendation:** {recommendation or 'No recommendation provided.'}")
    lines.append("")

    return "\n".join(lines)


def _build_markdown(scene_name: str, sbar: Dict[str, object], critique: Optional[str], include_critique: bool) -> str:
    lines: List[str] = [f"# SBAR Chaos Report — {scene_name}", ""]
    warning = sbar.get("_llm_warning")
    if warning:
        lines.append(f"_Note: {warning}_")
        lines.append("")
    differential = _normalize_differential(sbar.get("differential"))

    for section in SBAR_SECTIONS:
        heading = section.capitalize()
        lines.append(f"## {heading}")
        value = str(sbar.get(section) or "").strip()
        if not value:
            value = "_No data provided._"
        if section == "assessment":
            value = _ensure_assessment(value, differential or ["Unknown", "Unknown", "Unknown"])
        lines.append(value)
        lines.append("")

    if differential:
        formatted = "; ".join(differential[:3])
    else:
        formatted = "Unknown"
    lines.append(f"**Differential:** {formatted}")
    lines.append("")

    if include_critique:
        critique_text = (critique or "").strip() or "No critique returned from the supervisor model."
        lines.append("## Clinical Supervisor Critique")
        lines.append(critique_text)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    words = text.split()
    # Simple heuristic: ~0.75 tokens per word.
    return max(1, int(len(words) / 0.75))


def generate_sbar_report(
    dialogue_path: Path | str,
    output_path: Path | str,
    llm: Optional[LMStudioRuntime] = None,
    with_llm: bool = True,
) -> Dict[str, object]:
    """
    Generate an SBAR Markdown report from a dialogue JSONL stream.
    """
    dialogue_path = Path(dialogue_path)
    output_path = Path(output_path)
    segments = _read_dialogue(dialogue_path)

    runtime = llm or LMStudioRuntime()
    sbar_result = _invoke_sbar(runtime, segments, with_llm)
    sbar_payload = cast(Dict[str, object], sbar_result["sbar"])
    tokens = int(sbar_result.get("tokens", 0) or 0)
    latency = float(sbar_result.get("latency", 0.0) or 0.0)
    llm_used = bool(sbar_result.get("llm_used", False))
    raw_response = sbar_result.get("raw_response")

    critique_result = _invoke_critique(runtime, dialogue_path.stem, sbar_payload, with_llm)
    critique = str(critique_result.get("critique") or "")
    tokens += int(critique_result.get("tokens", 0) or 0)
    latency += float(critique_result.get("latency", 0.0) or 0.0)
    if critique_result.get("llm_used"):
        llm_used = True

    include_critique = bool(with_llm and llm_used)
    markdown = _build_markdown(dialogue_path.stem, sbar_payload, critique, include_critique)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    ok = bool(llm_used) if with_llm else True
    return {
        "latency": round(latency, 3),
        "tokens": int(tokens),
        "ok": ok,
        "with_llm": bool(llm_used),
        "output_path": str(output_path),
        "scene": dialogue_path.stem,
        "raw_response": raw_response,
        "sbar": sbar_payload,
        "critique": critique,
    }


def generate_progressive_sbar_log(
    dialogue_path: Path | str,
    progress_path: Path | str,
    *,
    runtime: Optional[LMStudioRuntime] = None,
    with_llm: bool = True,
    run_id: Optional[str] = None,
    iteration: int = 1,
) -> Dict[str, object]:
    dialogue_path = Path(dialogue_path)
    progress_path = Path(progress_path)
    segments = _read_dialogue(dialogue_path)
    runtime = runtime or LMStudioRuntime()

    progress_path.parent.mkdir(parents=True, exist_ok=True)
    if not progress_path.exists():
        progress_path.write_text(f"# SBAR Chaos Progress — {dialogue_path.stem}\n\n", encoding="utf-8")

    total_tokens = 0
    total_latency = 0.0
    llm_used = False
    appended: List[str] = []
    snapshots: List[Dict[str, object]] = []

    for idx, segment in enumerate(segments):
        subset = segments[: idx + 1]
        sbar_result = _invoke_sbar(runtime, subset, with_llm)
        sbar_payload = cast(Dict[str, object], sbar_result["sbar"])
        total_tokens += int(sbar_result.get("tokens", 0) or 0)
        total_latency += float(sbar_result.get("latency", 0.0) or 0.0)
        if sbar_result.get("llm_used"):
            llm_used = True

        critique_result = _invoke_critique(runtime, dialogue_path.stem, sbar_payload, with_llm)
        critique = str(critique_result.get("critique") or "")
        total_tokens += int(critique_result.get("tokens", 0) or 0)
        total_latency += float(critique_result.get("latency", 0.0) or 0.0)
        if critique_result.get("llm_used"):
            llm_used = True

        label = f"{iteration}.{idx + 1}"
        snapshot_md = _render_snapshot_markdown(
            label,
            sbar_payload,
            critique,
            t_start=float(segment.get("t_start")) if isinstance(segment.get("t_start"), (int, float)) else None,
            run_id=run_id,
        )
        appended.append(snapshot_md)
        snapshots.append(
            {
                "index": idx + 1,
                "label": label,
                "sbar": sbar_payload,
                "critique": critique,
                "t_start": segment.get("t_start"),
            }
        )

    if appended:
        with progress_path.open("a", encoding="utf-8") as handle:
            handle.write("".join(appended))

    scene_summary = generate_scene_summary(dialogue_path.stem, snapshots, runtime, with_llm=with_llm)
    total_tokens += int(scene_summary.get("tokens", 0) or 0)
    total_latency += float(scene_summary.get("latency", 0.0) or 0.0)
    if scene_summary.get("with_llm"):
        llm_used = True

    markdown_block = scene_summary.get("markdown")
    if markdown_block:
        with progress_path.open("a", encoding="utf-8") as handle:
            handle.write(markdown_block.strip() + "\n")

    return {
        "progress_path": str(progress_path),
        "tokens": int(total_tokens),
        "latency": round(total_latency, 3),
        "llm_used": llm_used,
        "snapshots": snapshots,
        "scene_summary": scene_summary,
    }


def generate_report(  # backward compatibility shim
    scene_path: Path,
    output_path: Path,
    realtime: bool,
    speed: float,
    runtime: LMStudioRuntime,
) -> Path:
    result = generate_sbar_report(scene_path, output_path, llm=runtime, with_llm=True)
    return Path(result["output_path"])


def _parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an SBAR Markdown report from a dialogue JSONL.")
    parser.add_argument("--dialogue", type=Path, default=Path("_validation/test_dialogue.jsonl"), help="Dialogue JSONL input.")
    parser.add_argument("--output", type=Path, default=Path("_validation/sbar_report.md"), help="Destination Markdown path.")
    parser.add_argument("--with-llm", dest="with_llm", action="store_true", help="Force enabling the Medicine LLM.")
    parser.add_argument("--no-llm", dest="with_llm", action="store_false", help="Disable LLM usage and use stubs.")
    parser.set_defaults(with_llm=True)
    return parser.parse_args()


def main() -> None:
    args = _parse_cli_args()
    if not args.dialogue.exists():
        raise SystemExit(f"Dialogue JSONL not found: {args.dialogue}")
    runtime = LMStudioRuntime()
    result = generate_sbar_report(args.dialogue, args.output, llm=runtime, with_llm=args.with_llm)
    mode = "LLM" if result["with_llm"] else "stub"
    print(f"SBAR report written to {result['output_path']} ({mode}, latency={result['latency']}s).")


__all__ = [
    "generate_sbar_report",
    "generate_progressive_sbar_log",
    "generate_scene_summary",
    "generate_report",
    "LMStudioRuntime",
]


if __name__ == "__main__":
    main()
