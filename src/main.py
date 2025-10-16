"""
Main Application Entry Point

This module initializes and runs the Emergency Medical Assistant app.

- Loads configuration
- Sets up core services (LLM, protocol library, SBAR, etc.)
- Starts the main event loop or API server

See architecture-overview.md for system context.
"""

# TODO: Implement application startup logic here
from src.llm.lmstudio_runtime import LMStudioRuntime
from src.llm.llm_client import LLMClient


if __name__ == "__main__":
    print("Emergency Medical Assistant app starting...")

    runtime = LMStudioRuntime.from_env()
    try:
        active_model = runtime.ensure_model_loaded()
        print(f"LM Studio ready with model: {active_model}")
    except Exception as exc:  # pragma: no cover - startup diagnostics
        raise SystemExit(f"Failed to prepare LM Studio: {exc}") from exc

    client = LLMClient(
        api_url=f"{runtime.base_url.rstrip('/')}/v1/chat/completions",
        system_prompt="You are a clinical reasoning assistant.",
        model=runtime.target_model,
    )
    response = client.ask("System initialization check: respond with 'ready'.")
    print(f"LLM handshake response: {response}")
    # Initialize core services and start main loop
