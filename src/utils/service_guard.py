"""
Utilities to manage local uvicorn service processes in a resilient way.

These helpers make it easy to discover which process owns a TCP port,
terminate stale listeners, and track PID files under ``_validation/run``.
"""

from __future__ import annotations

import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


PID_DIR = Path("_validation/run")
PID_DIR.mkdir(parents=True, exist_ok=True)


def pid_file(service_name: str) -> Path:
    """Return the pidfile location for a service."""
    return PID_DIR / f"{service_name}.pid"


def read_pid(service_name: str) -> Optional[int]:
    """Read a stored PID for a service, if present."""
    path = pid_file(service_name)
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def write_pid(service_name: str, pid: int) -> None:
    """Persist the PID for a started service."""
    pid_file(service_name).write_text(str(pid), encoding="utf-8")


def clear_pid(service_name: str) -> None:
    """Remove a stored PID."""
    try:
        pid_file(service_name).unlink()
    except FileNotFoundError:
        pass


def is_process_running(pid: Optional[int]) -> bool:
    """Return True if a PID is alive."""
    if not pid:
        return False
    system = platform.system()
    if system == "Windows":
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Id",
        ]
        try:
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            return bool(output.strip())
        except subprocess.CalledProcessError:
            return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def terminate_process(pid: int, timeout: float = 5.0) -> bool:
    """
    Attempt to terminate the given PID.

    Returns True if the process exited, False otherwise.
    """
    if pid <= 0:
        return False

    system = platform.system()
    if system == "Windows":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return True

    deadline = time.time() + timeout
    while time.time() < deadline:
        if not is_process_running(pid):
            return True
        time.sleep(0.1)

    if system != "Windows":
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            return True
        time.sleep(0.2)
        return not is_process_running(pid)

    return not is_process_running(pid)


def find_listener_pid(port: int, host: str = "127.0.0.1") -> Optional[int]:
    """
    Return the PID listening on ``host:port`` if any.
    """
    system = platform.system()

    if system == "Windows":
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"$c = Get-NetTCPConnection -LocalPort {port} "
            "-State Listen -ErrorAction SilentlyContinue; "
            "if ($c) { ($c | Select-Object -First 1).OwningProcess }",
        ]
    else:
        cmd = [
            "sh",
            "-c",
            f"lsof -nPi TCP@{host}:{port} -sTCP:LISTEN -t 2>/dev/null || "
            f"netstat -anp 2>/dev/null | grep ':{port} ' | awk '{{print $7}}' | cut -d/ -f1",
        ]

    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    output = output.strip()
    if not output:
        return None

    try:
        return int(output.splitlines()[0].strip())
    except ValueError:
        return None


def wait_for_port_free(port: int, host: str = "127.0.0.1", timeout: float = 5.0) -> bool:
    """Block until the port is free, returning True if it frees within timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if find_listener_pid(port, host=host) is None:
            return True
        time.sleep(0.1)
    return False


def describe_process(pid: int) -> Optional[str]:
    """Return a short description for a PID (command line or process name)."""
    if pid <= 0:
        return None
    system = platform.system()
    if system == "Windows":
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"$p = Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\"; "
            "if ($p) { $p.CommandLine }",
        ]
    else:
        cmd = ["ps", "-p", str(pid), "-o", "command="]
    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    return output.strip() or None


def ensure_port_available(port: int, host: str, service_name: str, *, force: bool = False) -> None:
    """
    Make sure ``host:port`` is available for binding.

    If an existing instance (tracked by pidfile) is running, it is terminated.
    If the listener belongs to an unknown process, raise RuntimeError.
    """
    stored_pid = read_pid(service_name)
    if stored_pid and is_process_running(stored_pid):
        terminate_process(stored_pid)
    clear_pid(service_name)

    current_pid = find_listener_pid(port, host=host)
    if current_pid:
        if force:
            terminate_process(current_pid)
            wait_for_port_free(port, host=host, timeout=5.0)
            return
        known_cmd = describe_process(current_pid) or ""
        raise RuntimeError(
            f"Port {host}:{port} is already in use by PID {current_pid} ({known_cmd})."
        )


__all__ = [
    "clear_pid",
    "describe_process",
    "ensure_port_available",
    "find_listener_pid",
    "is_process_running",
    "pid_file",
    "read_pid",
    "terminate_process",
    "wait_for_port_free",
    "write_pid",
]
