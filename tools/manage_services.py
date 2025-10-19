"""
Unified launcher for ASR, TTS, and orchestrator FastAPI services.

The script guarantees deterministic start/stop semantics by:
  * Clearing stale pidfiles and, when requested, terminating listeners
    occupying well-known ports.
  * Streaming stdout/stderr to ``_validation/logs`` for quick triage.
  * Polling health endpoints so callers know when a service is ready.

Usage examples:
    python tools/manage_services.py start asr tts
    python tools/manage_services.py restart orchestrator --force
    python tools/manage_services.py status
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import service_guard


LOG_DIR = Path("_validation/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class ServiceConfig:
    name: str
    module: str
    host: str
    port: int
    health_url: str
    factory: bool = False
    extra_args: Sequence[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def uvicorn_command(self) -> List[str]:
        cmd = [sys.executable, "-m", "uvicorn", self.module]
        if self.factory:
            cmd.append("--factory")
        cmd.extend(["--host", self.host, "--port", str(self.port)])
        cmd.extend(self.extra_args)
        return cmd


SERVICES: Dict[str, ServiceConfig] = {
    "asr": ServiceConfig(
        name="asr",
        module="src.asr.app:app",
        host="127.0.0.1",
        port=9001,
        health_url="http://127.0.0.1:9001/health",
    ),
    "tts": ServiceConfig(
        name="tts",
        module="src.tts.app:app",
        host="127.0.0.1",
        port=8880,
        health_url="http://127.0.0.1:8880/health",
    ),
    "orchestrator": ServiceConfig(
        name="orchestrator",
        module="src.orchestrator.app:create_app",
        host="127.0.0.1",
        port=8000,
        health_url="http://127.0.0.1:8000/health",
        factory=True,
        env={"LLM_API_URL": "http://127.0.0.1:1234/v1/chat/completions"},
    ),
}


def iter_services(selection: Optional[Iterable[str]]) -> List[ServiceConfig]:
    if selection:
        configs: List[ServiceConfig] = []
        for name in selection:
            key = name.lower()
            if key not in SERVICES:
                available = ", ".join(sorted(SERVICES))
                raise SystemExit(f"Unknown service '{name}'. Available: {available}")
            configs.append(SERVICES[key])
        return configs
    return list(SERVICES.values())


def wait_for_health(url: str, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=2.0, verify=False)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def start_service(config: ServiceConfig, *, force: bool, health_timeout: float) -> None:
    try:
        service_guard.ensure_port_available(config.port, config.host, config.name, force=force)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    stdout_path = LOG_DIR / f"{config.name}.out.log"
    stderr_path = LOG_DIR / f"{config.name}.err.log"
    stdout_handle = stdout_path.open("a", encoding="utf-8")
    stderr_handle = stderr_path.open("a", encoding="utf-8")

    env = os.environ.copy()
    env.update(config.env)

    cmd = config.uvicorn_command()
    process = subprocess.Popen(cmd, stdout=stdout_handle, stderr=stderr_handle, env=env)
    stdout_handle.close()
    stderr_handle.close()
    if not wait_for_health(config.health_url, timeout=health_timeout):
        raise SystemExit(
            f"Started {config.name} (pid={process.pid}) but /health did not respond within {health_timeout}s."
        )

    listener_pid = service_guard.find_listener_pid(config.port, host=config.host) or process.pid
    service_guard.write_pid(config.name, listener_pid)

    print(f"{config.name} ready on {config.host}:{config.port} (pid={process.pid})")


def stop_service(config: ServiceConfig, *, force: bool) -> None:
    pid = service_guard.read_pid(config.name)
    stopped = False
    if pid and service_guard.is_process_running(pid):
        if service_guard.terminate_process(pid):
            stopped = True
    elif pid:
        stopped = True

    current_pid = service_guard.find_listener_pid(config.port, host=config.host)
    if current_pid:
        if not force and current_pid != pid:
            desc = service_guard.describe_process(current_pid) or "unknown"
            raise SystemExit(
                f"Port {config.port} is held by PID {current_pid} ({desc}). Use --force to terminate it."
            )
        if service_guard.terminate_process(current_pid):
            stopped = True

    service_guard.clear_pid(config.name)
    service_guard.wait_for_port_free(config.port, host=config.host, timeout=5.0)

    if stopped:
        print(f"{config.name} stopped.")
    else:
        print(f"{config.name} was not running.")


def status_service(config: ServiceConfig) -> None:
    pid = service_guard.read_pid(config.name)
    alive = pid if pid and service_guard.is_process_running(pid) else None
    listener_pid = service_guard.find_listener_pid(config.port, host=config.host)
    health_ok = False
    try:
        response = httpx.get(config.health_url, timeout=1.5, verify=False)
        health_ok = response.status_code == 200
    except Exception:
        pass

    summary = [
        f"name={config.name}",
        f"port={config.port}",
        f"pidfile={pid or '-'}",
        f"listening_pid={listener_pid or '-'}",
        f"health={'ok' if health_ok else 'down'}",
    ]
    if alive:
        summary.append("status=running")
    else:
        summary.append("status=stopped")
    print(", ".join(summary))


def restart_service(config: ServiceConfig, *, force: bool, health_timeout: float) -> None:
    stop_service(config, force=force)
    start_service(config, force=force, health_timeout=health_timeout)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Manage SOS microservices.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_service_args(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "services",
            nargs="*",
            help="Subset of services to act on (default: all).",
        )
        subparser.add_argument(
            "--force",
            action="store_true",
            help="Terminate unknown listeners holding required ports.",
        )

    parser_start = subparsers.add_parser("start", help="Start one or more services.")
    add_service_args(parser_start)
    parser_start.add_argument(
        "--health-timeout",
        type=float,
        default=15.0,
        help="Seconds to wait for /health readiness (default: 15).",
    )

    parser_stop = subparsers.add_parser("stop", help="Stop one or more services.")
    add_service_args(parser_stop)

    parser_restart = subparsers.add_parser("restart", help="Restart services.")
    add_service_args(parser_restart)
    parser_restart.add_argument(
        "--health-timeout",
        type=float,
        default=15.0,
        help="Seconds to wait for /health on restart (default: 15).",
    )

    parser_status = subparsers.add_parser("status", help="Show service status.")
    parser_status.add_argument(
        "services",
        nargs="*",
        help="Subset of services to inspect (default: all).",
    )

    args = parser.parse_args(argv)
    selected = iter_services(args.services)

    if args.command == "start":
        for config in selected:
            start_service(config, force=args.force, health_timeout=args.health_timeout)
        return 0
    if args.command == "stop":
        for config in selected:
            stop_service(config, force=args.force)
        return 0
    if args.command == "restart":
        for config in selected:
            restart_service(config, force=args.force, health_timeout=args.health_timeout)
        return 0
    if args.command == "status":
        for config in selected:
            status_service(config)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
