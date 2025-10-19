## Emergency Medical Assistant – Delivery Roadmap

This roadmap decomposes the PRD requirements into incremental, verifiable work packages. Each phase focuses on a short list of capabilities with explicit exit criteria and supporting tests.

### Phase 0 – Project Framing & Tooling
1. **Inventory Existing Coverage**
   - Map current repositories, services, and test suites.
   - Produce a coverage table that links PRD checklist items to existing tests or mark gaps.
2. **Test Harness Alignment**
   - Add a column to `tasks/prd-execution-checklist.md` identifying the test(s) (or manual validation) that prove each requirement.
   - Install/enable any missing pytest plugins (e.g., `pytest-asyncio`) to unblock existing smoke tests.
3. **Service Management**
   - Finalize `tools/manage_services.py` usage across the team.
   - Document the health-check workflow and port guard behavior in the README or wiki entry.

**Exit Criteria:** PRD checklist cross-referenced with tests; service lifecycle tooling adopted; async test harness operational.

### Phase 1 – Core Protocol Engine (Text-Only)
1. **Protocol Ingestion & Retrieval**
   - Expand tests for YAML ingest (`tests/test_protocol_ingest.py`) to include validation of index updates, versioning, and error handling.
   - Implement ChromaDB (or stub) integration and cover with unit tests.
2. **SBAR Pipeline**
   - Strengthen SBAR builder tests with edge cases (missing elements, partial updates).
   - Implement structured SBAR storage/export and verify with new tests.
3. **LLM Orchestrator Basics**
   - Assert `test_llm_client.py` meets PRD “question only” behavior via system prompt checks.
   - Add tests for fallback responses when no protocol is found.

**Exit Criteria:** All text-based components (protocol ingest, SBAR, LLM client) fully validated with unit tests; relevant checklist items linked to those tests.

### Phase 2 – Voice & Interaction Layer (Local)
1. **Voice Input Layer**
   - Implement wake word detection stub; write unit/integration tests with recorded samples.
   - Develop ASR stub resilience tests (port guard scenarios, fallback responses).
2. **TTS Feedback**
   - Extend TTS service with deterministic outputs; add tests verifying `/tts` contract and file generation.
3. **Orchestrator Conversational Flow**
   - Re-enable smoke tests (`tests/test_turn_text_smoke.py`, `test_turn_audio_smoke.py`) using `pytest-asyncio`.
   - Add integration tests covering clarifying questions and SBAR completion.

**Exit Criteria:** Local ASR/TTS/orchestrator loop tested end-to-end via automated harness; wake word + SOS trigger flows validated.

### Phase 3 – Admin & Compliance Features
1. **Audit Logging**
   - Implement hash-chained audit log with unit tests simulating tamper detection.
   - Verify PHI de-identification pipeline using synthetic data.
2. **Admin Approval Workflow**
   - Mock email approval loop; write integration tests for approval/rejection paths.
   - Ensure YAML versioning and rollback are covered.
3. **Telemetry & Chaos Harness**
   - Expand telemetry unit tests; add regression tests for chaos harness prompts.
   - Expose `/metrics/summary` endpoint and validate via HTTP tests.

**Exit Criteria:** Compliance and admin features implemented with automated verification; checklist items FR-8..FR-17, CR-1..CR-5 linked to tests.

### Phase 4 – Deployment & OTA
1. **Cloud Deployment Stub**
   - Create Docker-compose or Helm-based smoke environment; add CI job to verify deploy/startup.
2. **OTA Update Pipeline**
   - Automate manifest creation; write tests for Windows/Android installers (checksum validation, download failure handling).
3. **Pairing & Discovery**
   - Unit/test scripts covering QR code generation, token issuance, and mDNS advertisement.

**Exit Criteria:** Deployment scripts validated; OTA workflow testable in CI; pairing/discovery test coverage in place.

### Phase 5 – Performance & Launch Readiness
1. **Performance Benchmarks**
   - Build load-testing harness evaluating response time and RTF.
   - Document results and compare against PRD success metrics.
2. **Pilot Feedback Loop**
   - Define manual/structured pilot testing script.
   - Capture feedback and ensure backlog items are created.
3. **Checklist Sign-off**
   - Ensure all PRD checklist items have linked evidence (tests, docs, manual validation).
   - Review open questions and make go/no-go decisions.

**Exit Criteria:** Performance targets demonstrated; pilot plan executed; PRD checklist all green or explicitly waived.

---

**Usage Tips**
- Treat each phase as a sprint-ready backlog; do not advance until exit criteria are met.
- Update `tasks/prd-execution-checklist.md` as items are verified.
- When new features arise, append them to the relevant phase with acceptance tests.
