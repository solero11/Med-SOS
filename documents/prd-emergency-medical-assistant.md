
# PRD: Emergency Medical Assistant Chatbot (2025-10-15)

## 1. Introduction/Overview

This project aims to build a physician-facing emergency assistant chatbot, initially focused on anesthesia/OR emergencies. The chatbot will help physicians overcome cognitive overload during acute events by providing rapid, context-aware protocol guidance and clinical reasoning support. It will combine structured protocol libraries (YAML), real-time physician input, and a quantized LLM to deliver actionable recommendations and clarifying questions in high-stress scenarios.

## 2. Goals

- Deliver protocol guidance and clinical reasoning support in <1 second response time.
- Achieve a Real-Time Factor (RTF) of 1 or less for all conversational interactions.
- Enable hands-free, voice-first interaction for physicians in emergency settings.
- Support rapid retrieval and stepwise navigation of emergency protocols (starting with anesthesia/OR, then expanding).
- Help physicians broaden differential diagnosis and avoid tunnel vision during crises.
- Provide production-ready cloud deployment with autoscaling, telemetry, and OTA update mechanisms.
- Maintain compliance-ready audit trails and PHI de-identification so the platform can operate in regulated environments.

## 3. User Stories

- As an anesthesiologist, I want to describe a sudden change in patient vitals so the assistant can help me quickly identify possible causes and next steps.
- As a physician, I want to trigger the assistant hands-free during an emergency so I can keep working on the patient.
- As a physician, I want the assistant to ask clarifying questions if my input is ambiguous, so I don’t miss critical considerations.
- As a physician, I want the assistant to retrieve and walk me through the relevant emergency protocol step-by-step.
- As an admin, I want to generate new or updated YAML protocols from trusted sources and approve them via email before they are added to the library.


## 4. Functional Requirements (updated)

1. The system must accept physician input via voice (and optionally text).
2. The system must process input and identify the relevant protocol(s) using a YAML library and JSON index.
3. The system must deliver protocol guidance and clinical reasoning support in real time (<1s RTF).
4. The system must support context-aware, multi-turn conversations (retain session context).
5. The system must ask clarifying questions if input is ambiguous or incomplete.
6. The system must allow the physician to trigger the assistant with a wake word (“Hermes” or “Hey Hermes”) or SOS button.
7. The system must allow for easy expansion of the protocol library (add new YAML files and update JSON index).
8. The system must log interactions and YAML changes for future analysis and compliance.
9. The system must include a CLI tool to generate YAML protocols from PDFs, web pages, or LLM prompts, and insert them into ChromaDB.
10. The system must send new/updated YAMLs to an admin for approval via email; only approved YAMLs are added to the library.
11. The system must provide a fallback response if no relevant YAML is found: “I am not sure how to help, but continue to provide more information as I might find relevant clinical information to help you.”
12. The system must support OTA updates for Windows and Android clients, including signed installers/APKs and manifest checks.
13. The system must expose pairing and discovery workflows (QR + mDNS) to securely onboard new clients.
14. The system must log LLM parse success/failure and enable regression analysis of prompt/model changes via a chaos harness and telemetry logger.
15. The system must maintain tamper-evident audit logs for pairing, turns, updates, and admin operations.
16. The system must de-identify PHI before storing telemetry or audit payloads.
17. The system must provide live observability dashboards (Prometheus + Grafana) and programmatic `/metrics/summary` endpoints.

## 5. Non-Goals (Out of Scope)

- Chronic disease management or non-emergency medical advice.
- Direct integration with patient EHRs (for initial version).
- On-device LLM inference for production (initially cloud-based for performance).
- Internet search integration (may be considered in future versions).

## 6. Design Considerations

- Minimal UI: primary interface is voice, with a single SOS button and optional text input.
- Hands-free operation is critical; text input is secondary.
- Wake word (“Hermes” or “Hey Hermes”) to trigger assistant.
- Accessible, mobile-first design for Android/iOS.
- SBAR (Situation, Background, Assessment, Recommendation) conversational flow, with the LLM prompting for each section and building a structured SBAR object.
- Completed SBAR can be shown on-screen, exported for documentation, or used to trigger protocol retrieval.


## 7. Technical Considerations (updated)

- Cloud-native orchestrator containerized (Docker) with Traefik TLS proxy, Postgres, Redis, and object storage (S3/GCS) integrations.
- Windows/Android clients communicate via HTTPS with bearer/JWT tokens; QR pairing issues time-limited clinician credentials.
- Use LM Studio/Ollama locally when `USE_LOCAL_LLM=true`; otherwise default to OpenRouter or hosted LLM endpoints.
- Protocols stored as YAML files, indexed by a JSON “card catalog” and retrievable via ChromaDB or future vector service.
- Telemetry persisted to Postgres (`metrics` table) + `_validation/orchestrator_metrics.jsonl` (+ S3 uploads); audit log hash-chained in `_validation/audit_log.jsonl`.
- Prometheus exporter for OpenTelemetry metrics (`/metrics`, port 9464) with Grafana dashboards provisioned via compose stack.
- OTA manifest served at `/updates/manifest.json`; Windows updater verifies SHA-256 and launches silent installer, Android app validates APK hash and triggers package installer.
- mDNS discovery advertises orchestrator when on LAN; fallback manual host entry supported.
- Local testing; production will be cloud-based for compute needs.
- Python CLI tool (`yaml_protocol_generator.py`) for protocol ingestion and YAML generation.
- Admin approval workflow via email.
- Privacy and security: ensure all data is handled per medical data standards.
- All LLM output is parsed via a tolerant extractor; telemetry is used to drive prompt and model improvements.

---

## 8. Regulatory Addendum — Question-Based Clinical Reasoning Assistant

### Module: Clinical Reasoning Assistant (LLM)

**Purpose:**  
This module enables the app to function as a clinical thought partner during medical emergencies, helping licensed physicians arrive at informed decisions. The assistant facilitates interactive questioning, not treatment directives.

### FDA Regulatory Considerations

**Strategy:**  
This module is explicitly designed to avoid classification as a regulated “Software as a Medical Device (SaMD)” per FDA guidelines by:
- Not making autonomous clinical decisions
- Framing all clinical outputs as questions, possibilities, or hypotheses
- Providing transparent clinical logic the physician can verify
- Including disclaimers and maintaining user autonomy

**Example Prompts:**  
Instead of:  
> "Insert chest tube immediately."  
The app will say:  
> "Could this be a tension pneumothorax given the hypotension and absent breath sounds?"  
> "Would you like to review ATLS decompression protocols?"

### System Prompt Constraints for LLM

```yaml
system_prompt:
  role: "You are a clinical reasoning assistant."
  behavior: |
    You never give orders, only ask questions.
    You do not diagnose, prescribe, or recommend.
    You encourage physicians to reflect on possibilities.
    You may retrieve supporting guidelines, references, or YAML protocols.
```

### Legal Disclaimer Display

- At the start of every SOS session, display a brief reminder:  
  > “This software is not the clinician and does not make clinical decisions.”
- During login and startup, require users to acknowledge full legal disclaimers.
- In all SBAR exports and admin approval emails, include:  
  > “This software is intended for use by licensed medical professionals. It does not diagnose or prescribe treatment. Final decisions must be made by the physician. This tool provides questions, hypotheses, and access to medical references only.”

### Functional Outcomes (Without FDA Regulation)

- Suggests possible conditions via Socratic dialogue
- Retrieves YAML-based protocols on request
- Logs interactions in JSON (optional audit trail)
- Never initiates, confirms, or implies medical treatment

### Conclusion

This design enables the app to:
- Deliver life-saving clinical support
- Avoid the burden of full FDA clearance
- Stay within the safe zone of Clinical Decision Support (CDS) exemption
- Emulate a human assistant rather than a directive medical device

---

## 9. Success Metrics

- Median response time <1 second.
- Real-Time Factor (RTF) of 1 or less for all conversational interactions.
- 95%+ protocol retrieval accuracy in test scenarios.
- Positive feedback from pilot users (physicians).
- Successful expansion to additional emergency protocols after anesthesia/OR launch.
- All YAML changes are logged and auditable.

## 10. Open Questions

- What is the final admin approval workflow for YAMLs (currently via email)?
- How will protocol library updates be managed and validated at scale?
- What fallback should occur if the LLM cannot identify a protocol or answer? (Current: “I am not sure how to help, but continue to provide more information as I might find relevant clinical information to help you.”)
