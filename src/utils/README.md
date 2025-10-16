# Utils Module


Utility functions and services, including:
- SBAR builder
- Fallback handler
- Audit logger
- Scene playback and SBAR monitoring harness (`scene_player.py`, `sbar_monitor.py`, `run_sbar_scene.py`)
- SBAR markdown report generator with LLM critique (`generate_sbar_report.py`)
- Clinician query assistant & data store (`clinician_query.py`, `clinician_data_store.py`)
- Scene scaffolding helper for LLM-generated scenarios (`../tools/scene_scaffolder.py`)
- **Chaos harness** for LLM/SBAR regression testing (`chaos_harness.py`)
- **Telemetry logger** for parse/latency metrics (`chaos_telemetry.py`)
- **Tolerant JSON parser** for robust LLM output handling (`chaos_json_parser.py`)

Each utility should have a README and tests.
