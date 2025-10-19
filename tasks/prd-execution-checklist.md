## Emergency Medical Assistant – PRD Execution Checklist

Derived from `documents/prd-emergency-medical-assistant.md` (2025-10-15). Each row captures implementation status and current evidence or gaps.

### 1. Goals & Outcomes
| Item | Description | Evidence / Status |
|------|-------------|-------------------|
| [ ] G-1 | Sub-second (≤1 s) end-to-end response time for protocol guidance. | Gap – no performance harness yet. |
| [ ] G-2 | Maintain Real-Time Factor (RTF) ≤ 1 for every conversational turn. | Gap – RTF measurement tooling absent. |
| [ ] G-3 | Support hands-free, voice-first interaction throughout the workflow. | Gap – voice UI/wake word not implemented. |
| [ ] G-4 | Provide rapid retrieval and stepwise navigation of emergency protocols. | Partial – `tests/test_protocol_ingest.py` covers CRUD only. |
| [ ] G-5 | Broaden differential diagnosis via clarifying prompts to avoid tunnel vision. | Gap – clarifying-question logic unbuilt. |
| [ ] G-6 | Deliver production-ready cloud deployment with autoscaling, telemetry, and OTA updates. | Gap – infrastructure tasks outstanding. |
| [ ] G-7 | Preserve compliance-ready audit trails and PHI de-identification. | Gap – audit/PHI workflows unverified. |

### 2. Functional Requirements
| Item | Description | Evidence / Status |
|------|-------------|-------------------|
| [ ] FR-1 | Accept physician input via voice (and optional text) channels. | Gap – voice capture pipeline absent. |
| [ ] FR-2 | Map inputs to relevant YAML protocols using the library + JSON index. | Partial – `tests/test_protocol_ingest.py`; index/version coverage missing. |
| [ ] FR-3 | Meet <1 s guidance/clinical reasoning response SLA. | Gap – no latency tests. |
| [ ] FR-4 | Maintain multi-turn conversational context. | Partial – `tests/test_llm_client.py` verifies payload structure only. |
| ✅ FR-5 | Ask clarifying questions when input is ambiguous/incomplete. | `tests/test_turn_text_smoke.py::test_turn_text_clarifying_when_input_empty` |
| [ ] FR-6 | Support wake word (“Hermes” / “Hey Hermes”) and SOS button triggers. | Gap – feature pending. |
| [ ] FR-7 | Allow rapid expansion of protocol library (YAML additions + index updates). | Partial – ingest tests; index/version management untested. |
| [ ] FR-8 | Log interactions and YAML changes for analysis/compliance. | Gap – audit logging absent. |
| [ ] FR-9 | Provide CLI tooling to ingest/generate protocols and load into ChromaDB. | ✅ `tests/test_scene_scaffolder.py` |
| [ ] FR-10 | Route new/updated YAMLs through admin email approval prior to activation. | Gap – workflow unimplemented. |
| ✅ FR-11 | Supply fallback message when no relevant protocol is found. | `tests/test_turn_text_smoke.py::test_turn_text_fallback_when_llm_returns_blank` |
| [ ] FR-12 | Enable OTA updates for Windows & Android clients with signed artifacts. | Gap – OTA validation missing. |
| [ ] FR-13 | Expose secure pairing/discovery workflows (QR codes + mDNS). | ✅ `tests/test_discovery_pairing.py` |
| [ ] FR-14 | Log LLM parse success/failure; enable regression analysis via chaos telemetry. | Partial – `tests/test_stress_recovery.py`; telemetry assertions pending. |
| [ ] FR-15 | Maintain tamper-evident audit logs for pairing, turns, updates, admin actions. | Gap – not implemented. |
| [ ] FR-16 | De-identify PHI before telemetry/audit storage. | Gap – no coverage. |
| [ ] FR-17 | Deliver live observability dashboards and `/metrics/summary` endpoints. | Gap – monitoring endpoints untested. |

### 3. Technical Considerations / Implementation Tasks
| Item | Description | Evidence / Status |
|------|-------------|-------------------|
| [ ] TC-1 | Containerize orchestrator with Traefik TLS, Postgres, Redis, object storage. | Gap – deployment not validated. |
| [ ] TC-2 | Secure client communication via HTTPS + bearer/JWT tokens; implement QR pairing. | Gap – pending implementation/tests. |
| [ ] TC-3 | Support LM Studio/Ollama when `USE_LOCAL_LLM=true`, fallback to hosted LLMs otherwise. | ✅ `tests/test_lmstudio_runtime.py` |
| [ ] TC-4 | Persist YAML protocols + JSON index, integrate with ChromaDB/vectors. | Partial – ingest tests; ChromaDB integration missing. |
| [ ] TC-5 | Persist telemetry to Postgres + `_validation/orchestrator_metrics.jsonl` (+ S3 uploads). | Gap – telemetry pipeline untested. |
| [ ] TC-6 | Implement hash-chained `_validation/audit_log.jsonl`. | Gap – feature absent. |
| [ ] TC-7 | Publish Prometheus metrics (port 9464) and provision Grafana dashboards. | Gap – monitoring stack unverified. |
| [ ] TC-8 | Serve OTA manifest at `/updates/manifest.json` and validate installer/APK signatures. | Gap – OTA workflow not validated. |
| [ ] TC-9 | Provide mDNS advertisement + manual host fallback. | ✅ `tests/test_discovery_pairing.py` |
| [ ] TC-10 | Deliver `yaml_protocol_generator.py` CLI for ingestion workflows. | ✅ `tests/test_scene_scaffolder.py` |
| [ ] TC-11 | Integrate admin approval email pipeline. | Gap – not yet built. |
| [ ] TC-12 | Enforce privacy & security controls aligned with medical data handling. | Gap – no verification. |
| [ ] TC-13 | Deploy tolerant LLM output parsing plus telemetry-driven prompt/model tuning. | Gap – chaos harness tests blocked. |

### 4. Clinical Reasoning & Regulatory Safeguards
| Item | Description | Evidence / Status |
|------|-------------|-------------------|
| [ ] CR-1 | Ensure LLM prompt enforces “question/clarify only” behavior (no directives). | Gap – prompt enforcement not tested. |
| [ ] CR-2 | Display legal disclaimer at SOS session start and login. | Gap – UI workflow missing. |
| [ ] CR-3 | Embed disclaimer in SBAR exports and admin approval emails. | Gap – export pipeline unverified. |
| [ ] CR-4 | Guarantee module avoids autonomous clinical decisions (CDS exemption posture). | Gap – depends on CR-1/CR-2 completion. |
| [ ] CR-5 | Log interactions in JSON for optional audit trail without prescribing treatment. | Gap – audit logging absent. |

### 5. Success Metrics Tracking
| Item | Description | Evidence / Status |
|------|-------------|-------------------|
| [ ] SM-1 | Median response time verified <1 s in load testing. | Gap – no load testing yet. |
| [ ] SM-2 | Real-Time Factor measurements ≤ 1 across benchmark scenarios. | Gap – RTF measurement pending. |
| [ ] SM-3 | ≥95 % protocol retrieval accuracy in validation suite. | Gap – accuracy suite not developed. |
| [ ] SM-4 | Collect qualitative feedback from pilot physicians (target positive sentiment). | Gap – pilot not started. |
| [ ] SM-5 | Demonstrate expansion to additional emergency protocols post-launch. | Gap – expansion plan untested. |
| [ ] SM-6 | Verify all YAML changes recorded in auditable logs. | Gap – audit logging not implemented. |

### 6. Open Questions & Follow-Ups
| Item | Description | Evidence / Status |
|------|-------------|-------------------|
| [ ] OQ-1 | Finalize admin approval workflow (currently email-based) for scalability. | Product decision pending. |
| [ ] OQ-2 | Define process for validating and rolling out large protocol library updates. | Product decision pending. |
| ✅ OQ-3 | Confirm fallback flows when LLM cannot locate a protocol remain acceptable. | Covered by clarifying/fallback integration tests. |
