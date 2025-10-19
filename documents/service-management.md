## Local Service Management

Use `tools/manage_services.py` to control the local ASR, TTS, and orchestrator FastAPI apps without fighting over ports.

### Examples

```bash
# Show current state, including port owners and health
python tools/manage_services.py status

# Start the services (force-terminates anything already bound to the ports)
python tools/manage_services.py start asr tts orchestrator --force

# Restart only the orchestrator and verify readiness within 5 seconds
python tools/manage_services.py restart orchestrator --health-timeout 5

# Stop every service cleanly
python tools/manage_services.py stop
```

### Behavior

- Before launching, the script checks the target port, terminates stale listeners when `--force` is set, and records the live PID under `_validation/run/<service>.pid`.
- Stdout/stderr are appended to `_validation/logs/<service>.out.log` and `.err.log` for quick triage.
- The command waits until each `/health` endpoint responds with HTTP 200 (or times out) so you know immediately whether the service is responsive.
