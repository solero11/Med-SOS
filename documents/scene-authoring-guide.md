# Scene Authoring Guide

This quick-start outlines how to spin up new emergency scenarios using the scaffolder and scene harness.

## 1. Generate scaffolding

Run the scaffolder against a topic id from `data/emergencies/`:

```bash
python -m src.tools.scene_scaffolder \
  --topic failed_airway \
  --output-dir scenes/failed_airway \
  --dry-run --validate
```

* `--dry-run` prints the prompts so you can copy them into your LLM UI if you prefer.
* Drop `--dry-run` to let the tool call LM Studio directly (make sure LM Studio is running).
* `--validate` checks the generated files; add `--smoke-test` to run the SBAR scene harness.

The tool expects to emit three files:

* `dialogue.jsonl` – chaotic ASR-style timeline.
* `clinician_data.yaml` – structured vitals, medications, procedures, labs/imaging, etc.
* `scene_metadata.yaml` – phases, duration, tags, participants.

The prompts borrow structure from `scenes/tension_pneumo/` to keep format consistent.

## 2. Review & iterate

1. Inspect `dialogue.jsonl` for clinical plausibility and timing.
2. Open `clinician_data.yaml` to ensure follow-up answers look realistic (vital trends, med responses, lab results).
3. Adjust `scene_metadata.yaml` phases to match the narrative.
4. Re-run the scaffolder with `--validate --smoke-test` to confirm SBAR playback, question/answer logging, and schema checks pass.

## 3. Enrich clinician data

The harness can answer questions about:

* Vitals (`blood_pressure`, `spo2`, `heart_rate`, `etco2`, and additional metrics you add)
* `medications`, `procedures`, `evaluations`
* `labs` (e.g., ABG, lactate) and `imaging` (POCUS, CXR)

Add more sections (e.g., `consults`, `devices`) as needed; the `ClinicianDataStore` can be extended with new keyword handlers.

## 4. Commit the scene

Include the three scene files plus any supporting assets (e.g., prompt notes). Consider adding a short README in the scene directory describing learning objectives or tricky decision points.

## 5. Regression tip

Use the harness to regenerate Markdown reports whenever you update the scene:

```bash
python -m src.utils.registry_loader  # ensure emergency YAMLs validate
python -m src.utils.sbar_scene_harness --scene scenes/failed_airway/dialogue.jsonl --speed 0 --no-realtime
```

This keeps SBAR evolution, Socratic prompts, and clinician answers in sync as the scenario evolves.
