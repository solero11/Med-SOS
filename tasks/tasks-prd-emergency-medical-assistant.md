## Relevant Files

- `src/app/main.ts` - Main entry point for the emergency assistant app logic.
- `src/components/SOSButton.tsx` - UI component for the SOS trigger button.
- `src/components/ListeningIndicator.tsx` - Visual indicator that the app is listening (e.g., waveform/avatar).
- `src/components/ChatInterface.tsx` - Handles SBAR chat flow and displays prompts/responses.
- `src/llm/llmClient.ts` - Handles communication with LM Studio’s Medicine 13B model.
- `src/protocols/protocolLibrary.yaml` - YAML library of emergency protocols.
- `src/protocols/protocolIndex.json` - JSON index (“card catalog”) for protocol lookup.
- `src/utils/sbarBuilder.ts` - Utility for building and managing the SBAR data object.
- `src/utils/fallbackHandler.ts` - Handles fallback responses and red flag notifications.
- `src/export/sbarExporter.ts` - Exports completed SBAR for documentation/handoff.
- `src/admin/yamlApprovalHandler.ts` - Handles admin email approval workflow for new/updated YAMLs.
- `src/utils/auditLogger.ts` - Logs all YAML changes and critical events for compliance.
- `src/app/main.test.ts` - Unit tests for main app logic.
- `src/components/ChatInterface.test.tsx` - Unit tests for chat/SBAR flow.
- `src/utils/sbarBuilder.test.ts` - Unit tests for SBAR builder utility.

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `MyComponent.tsx` and `MyComponent.test.tsx` in the same directory).
- Use `npx jest [optional/path/to/test/file]` to run tests. Running without a path executes all tests found by the Jest configuration.

## Tasks

- [ ] 1.0 Implement SOS Button and Listening UI
  - [ ] 1.1 Design and implement the SOS button component for mobile (Android/iOS) interface.
  - [ ] 1.2 Implement the listening indicator (e.g., animated avatar or waveform) that activates when the SOS button is pressed or wake word is detected.
  - [ ] 1.3 Integrate wake word detection (“Hermes” or “Hey Hermes”) to trigger listening mode.
  - [ ] 1.4 Ensure the UI is accessible, mobile-first, and hands-free by default.
  - [ ] 1.5 Write unit tests for the SOS button and listening indicator components.
  - [ ] 1.6 All unit tests for SOS Button and Listening UI must pass successfully.

- [ ] 2.0 Build SBAR Chat Flow and Data Handling
  - [ ] 2.1 Implement the chat interface for physician-LLM interaction.
  - [ ] 2.2 Design and implement the SBAR (Situation, Background, Assessment, Recommendation) prompt sequence.
  - [ ] 2.3 Create the `sbarBuilder.ts` utility to build and manage the SBAR data object as the conversation progresses.
  - [ ] 2.4 Ensure the LLM prompts for missing SBAR fields and asks concise clarifying questions.
  - [ ] 2.5 Display the completed SBAR object on-screen for review.
  - [ ] 2.6 Implement export functionality for SBAR (e.g., for documentation or handoff).
  - [ ] 2.7 Write unit tests for chat flow and SBAR builder utility.
  - [ ] 2.8 All unit tests for SBAR Chat Flow and Data Handling must pass successfully.

- [ ] 3.0 Integrate LLM and Protocol Retrieval
  - [ ] 3.1 Implement the `llmClient.ts` to communicate with LM Studio’s Medicine 13B model via API.
  - [ ] 3.2 Design the protocol retrieval logic: use the SBAR object and protocol index to select relevant YAML protocol(s).
  - [ ] 3.3 Pass YAML protocol content as context to the LLM for response generation.
  - [ ] 3.4 Ensure the LLM always prefers YAML protocol steps when available and phrases outputs as questions, not directives.
  - [ ] 3.5 Handle multi-turn, context-aware conversations with the LLM.
  - [ ] 3.6 Write unit tests for LLM integration and protocol retrieval logic.
  - [ ] 3.7 All unit tests for LLM and Protocol Retrieval must pass successfully.

- [ ] 4.0 Develop Protocol Library Management and YAML Generation Tools
  - [ ] 4.1 Integrate the `yaml_protocol_generator.py` CLI tool for protocol ingestion from PDFs, web pages, or LLM prompts.
  - [ ] 4.2 Define and document the YAML schema for emergency protocols (fields, metadata, tags, etc.).
  - [ ] 4.3 Implement the protocol index (`protocolIndex.json`) for fast lookup and mapping of clinical scenarios to YAMLs.
  - [ ] 4.4 Store YAML protocols in `protocolLibrary.yaml` and ensure ChromaDB integration for retrieval.
  - [ ] 4.5 Implement versioning and audit logging for all YAML changes.
  - [ ] 4.6 Write unit tests for YAML ingestion, indexing, and ChromaDB integration.
  - [ ] 4.7 All unit tests for Protocol Library Management and YAML Generation Tools must pass successfully.

- [ ] 5.0 Implement Admin Approval, Fallback, and Audit Logging Features
  - [ ] 5.1 Implement the admin approval workflow: send new/updated YAMLs to the admin email for review.
  - [ ] 5.2 Parse admin email replies for “approve” or “disapprove” and update the protocol library accordingly.
  - [ ] 5.3 Ensure all YAML changes (creation, edits, approvals) are logged in `auditLogger.ts`.
  - [ ] 5.4 Implement fallback logic: if no relevant YAML is found, Hermes continues to ask clarifying questions; if still unable to help, responds with the fallback message and triggers a red flag notification to the admin.
  - [ ] 5.5 Write unit tests for admin approval, fallback, and audit logging features.
  - [ ] 5.6 All unit tests for Admin Approval, Fallback, and Audit Logging Features must pass successfully.
