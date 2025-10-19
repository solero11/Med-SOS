# LLM Module


Handles all communication with the remote LLM (e.g., LM Studio Medicine 13B on http://100.111.223.74:1234).
- API client
- Prompt construction
- System prompt enforcement (question-based output)
- **Tested via the chaos harness and monitored for parse compliance/telemetry.**
-
**Deployment Note:**
All orchestrator and LLM runtime code is now configured to use the remote LM Studio server (http://100.111.223.74:1234) by default. Update the LLM_API_URL environment variable if the server address changes.

Each submodule should have a README and tests.