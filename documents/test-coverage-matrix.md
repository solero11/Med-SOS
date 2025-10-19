## Test Coverage Matrix – Emergency Medical Assistant

_Last updated: 2025-10-17 (post async harness run)_

### 1. Test Suite Inventory

| Test File | Focus Area | External Dependencies | Last Run Status | Notes |
|-----------|------------|-----------------------|-----------------|-------|
| `tests/test_protocol_ingest.py` | YAML protocol save/load & lookup | None | ✅ Pass (2025-10-17) | Covers basic ingest/retrieval happy path. |
| `tests/test_llm_client.py` | LLM client payload construction | None | ✅ Pass (2025-10-17) | Verifies OpenAI-compatible request/response handling. |
| `tests/test_sbar_builder.py` | SBAR data structure utilities | None | ✅ Pass (2025-10-17) | Validates completeness/missing fields logic. |
| `tests/test_asr_enrichment.py` | ASR metadata enrichment | None | ✅ Pass (2025-10-17) | Validates enrichment helper logic. |
| `tests/test_audio_clients.py` | Audio device client behavior | None | ✅ Pass (2025-10-17) | Exercises mock audio clients. |
| `tests/test_clinician_data_store.py` | Clinician datastore operations | None | ✅ Pass (2025-10-17) | Pure unit test now green. |
| `tests/test_clinician_query.py` | Clinician query logic | None | ✅ Pass (2025-10-17) | Pure unit test now green. |
| `tests/test_dashboard_ws.py` | Dashboard WebSocket interface | Running orchestrator | ✅ Pass (2025-10-17) | WebSocket ping/pong via local orchestrator. |
| `tests/test_discovery_pairing.py` | Pairing/mDNS workflows | None (mDNS mocked) | ✅ Pass (2025-10-17) | Verifies QR/mDNS pairing helpers. |
| `tests/test_generate_sbar_report.py` | SBAR report generator | File I/O | ✅ Pass (2025-10-17) | Validates export scaffolding. |
| `tests/test_health_endpoints.py` | ASR/TTS/Orchestrator health | Running services, `pytest-asyncio` | ✅ Pass (2025-10-17) | Hit /health with services + LLM stub. |
| `tests/test_lmstudio_runtime.py` | LM Studio runtime helper | HTTP mocks | ✅ Pass (2025-10-17) | Ensures runtime setup/resume paths. |
| `tests/test_mobile_bridge.py` | Mobile bridge pairing | `aiohttp` | ✅ Pass (2025-10-17) | Runs against local orchestrator (HTTP mode). |
| `tests/test_registry_loader.py` | Registry loader | File I/O | ✅ Pass (2025-10-17) | Pure unit test now green. |
| `tests/test_sbar_monitor.py` | SBAR monitoring harness | None | ✅ Pass (2025-10-17) | Confirms monitor loop behavior. |
| `tests/test_scene_harness.py` | Scene simulation harness | File assets | ✅ Pass (2025-10-17) | CLI harness smoke coverage. |
| `tests/test_scene_player.py` | Scene player logic | File assets | ✅ Pass (2025-10-17) | Player logic validated. |
| `tests/test_scene_scaffolder.py` | Scene scaffolding CLI | CLI env | ✅ Pass (2025-10-17) | CLI scaffolder exercised. |
| `tests/test_stress_recovery.py` | Orchestrator stress tests | Async clients, services | ✅ Pass (2025-10-17) | Runs with local ASR/TTS + LLM stub. |
| `tests/test_turn_audio_smoke.py` | End-to-end audio turn | Async clients, services | ✅ Pass (2025-10-17) | Requires `_validation/test_ping.wav`. |
| `tests/test_turn_text_smoke.py` | End-to-end text turn | Async clients, services | ✅ Pass (2025-10-17) | Uses local orchestrator with LLM stub. |
| `tests/test_windows_orchestrator.py` | Windows orchestrator harness | Windows-specific deps | ✅ Pass (2025-10-17) | Validates Windows bundle interactions. |

### 2. PRD Checklist Crosswalk (Snapshot)

| PRD Item | Description | Current Evidence | Status |
|----------|-------------|------------------|--------|
| FR-2 | Map inputs to relevant YAML protocols | `tests/test_protocol_ingest.py` | ✅ Covered (unit) |
| FR-4 | Maintain multi-turn conversation context | `tests/test_llm_client.py` (partial) | ⚠ Partial – tests payload assembly only |
| FR-5 | Ask clarifying questions for ambiguous input | `tests/test_turn_text_smoke.py::test_turn_text_clarifying_when_input_empty` | ✅ Covered (integration) |
| FR-7 | Expand protocol library quickly | `tests/test_protocol_ingest.py` (basic CRUD) | ⚠ Partial – lacks index/version tests |
| FR-8 | Log interactions/YAML changes | _None_ | ❌ Gap |
| FR-9 | CLI tool for protocol ingestion | `tests/test_scene_scaffolder.py` | ✅ Covered (CLI smoke) |
| FR-11 | Fallback messaging when no protocol | `tests/test_turn_text_smoke.py::test_turn_text_fallback_when_llm_returns_blank` | ✅ Covered (integration) |
| FR-14 | Telemetry regression harness | `tests/test_stress_recovery.py` | ⚠ Partial – exercises stress turns, telemetry assertions TBD |
| CR-1 | LLM only poses questions | _None_ | ❌ Gap |
| SM-3 | Protocol retrieval accuracy ≥95% | _None_ | ❌ Gap |

_Note:_ All other PRD items currently have no automated evidence attached. Populate the “Current Evidence” column as additional tests, manual validations, or telemetry reports become available.

### 3. Next Steps
1. Add telemetry/audit assertions (FR-14/TC-13) to ensure parse failures are recorded.  
2. Build harnesses for performance metrics (G-1, SM-1) and protocol accuracy (SM-3).  
3. Keep the PRD checklist (`tasks/prd-execution-checklist.md`) in sync by recording new evidence as features land.  
