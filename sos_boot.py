"""
Unified launcher for the SOS Windows desktop build.

Responsibilities:
  - Start ASR, TTS, and orchestrator FastAPI services as subprocesses.
  - Verify LM Studio is reachable on localhost:1234.
  - Launch the Kivy SOS UI once services are healthy.
"""

from __future__ import annotations

import os
import pathlib
import signal
import subprocess
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple

import requests
from src.security.bootstrap_certs import CERT_PATH, KEY_PATH, TOKEN_PATH, bootstrap_security
from src.orchestrator.discovery import register_mdns_service
from src.updater import windows_updater

APP_VERSION = "1.0.0"
BASE_DIR = pathlib.Path(__file__).resolve().parent
ASR_PORT = int(os.getenv("ASR_PORT", "9001"))
TTS_PORT = int(os.getenv("TTS_PORT", "8880"))
ORCH_PORT = int(os.getenv("ORCH_PORT", "8000"))
HOST = os.getenv("SOS_HOST", "127.0.0.1")
UVICORN_LOG_LEVEL = os.getenv("SOS_UVICORN_LOG_LEVEL", "warning")
MANIFEST_URL = os.environ.get("SOS_MANIFEST_URL", "https://127.0.0.1:8000/updates/manifest.json")


def wait_health(url: str, timeout: float = 20.0, verify: bool = True) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=2, verify=verify)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            time.sleep(0.5)
            continue
    return False


def start_uvicorn(
    target: str,
    port: int,
    label: str,
    ssl_pair: Optional[Tuple[str, str]] = None,
) -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", os.pathsep.join(filter(None, [env.get("PYTHONPATH"), str(BASE_DIR)])))
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        target,
        "--host",
        HOST,
        "--port",
        str(port),
        "--log-level",
        UVICORN_LOG_LEVEL,
    ]
    if ssl_pair:
        cert_file, key_file = ssl_pair
        command.extend(["--ssl-certfile", cert_file, "--ssl-keyfile", key_file])
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    return subprocess.Popen(
        command,
        env=env,
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )


def verify_lm_studio() -> None:
    url = os.getenv("LLM_API_URL", "http://127.0.0.1:1234/v1/models")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        payload = response.json()
        models = [item.get("id") for item in payload.get("data", []) if isinstance(item, dict)]
        print(f"LM Studio reachable: {', '.join(models) or 'unknown model list'}")
    except requests.RequestException as exc:
        print(f"LM Studio not reachable at {url}: {exc}\nContinuing in offline mode.")


def shutdown_process(label: str, proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            proc.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
            time.sleep(0.5)
        proc.terminate()
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    except Exception as exc:
        print(f"Warning: Failed to stop {label}: {exc}")


def main() -> int:
    print(f"SOS Button App v{APP_VERSION} starting …")
    token = bootstrap_security()
    print(f"Authentication token: {token}")

    ssl_pair = (str(CERT_PATH), str(KEY_PATH)) if CERT_PATH.exists() and KEY_PATH.exists() else None

    services: List[Tuple[str, str, int, Optional[Tuple[str, str]]]] = [
        ("ASR", "src.asr.app:app", ASR_PORT, None),
        ("TTS", "src.tts.app:app", TTS_PORT, None),
        ("Orchestrator", "src.orchestrator.app:create_app", ORCH_PORT, ssl_pair),
    ]
    processes: Dict[str, subprocess.Popen] = {}
    mdns = None

    try:
        print("Launching SOS services...")
        for label, target, port, ssl_opt in services:
            proc = start_uvicorn(target, port, label, ssl_opt)
            processes[label] = proc

        print("Waiting for services to become healthy...")
        for label, _, port, ssl_opt in services:
            scheme = "https" if ssl_opt else "http"
            health_url = f"{scheme}://{HOST}:{port}/health"
            verify = ssl_opt is None
            if wait_health(health_url, verify=verify):
                print(f"  {label} ready at {health_url}")
            else:
                print(f"  Warning: {label} did not report healthy at {health_url}")

        verify_lm_studio()
        mdns = register_mdns_service(ORCH_PORT)
        threading.Thread(
            target=lambda: _background_update_loop(),
            name="UpdateChecker",
            daemon=True,
        ).start()

        print("Launching SOS UI...")
        ui_cmd = [sys.executable, str(BASE_DIR / "sos_button_app.py")]
        ui_proc = subprocess.Popen(ui_cmd, cwd=BASE_DIR)
        ui_proc.wait()
        return 0
    except KeyboardInterrupt:
        print("CTRL+C received, shutting down.")
        return 0
    except Exception as exc:
        print(f"Startup failed: {exc}")
        return 1
    finally:
        print("Shutting down services...")
        for label, proc in processes.items():
            shutdown_process(label, proc)
        if mdns is not None:
            try:
                mdns.close()
            except Exception:
                pass
        print("All processes terminated.")


def _background_update_loop(interval_hours: float = 6.0) -> None:
    while True:
        try:
            windows_updater.check_and_update(MANIFEST_URL, APP_VERSION)
        except SystemExit:
            # Installer triggered, nothing else to do.
            return
        except Exception:
            pass
        time.sleep(max(interval_hours, 1.0) * 3600)


if __name__ == "__main__":
    raise SystemExit(main())
