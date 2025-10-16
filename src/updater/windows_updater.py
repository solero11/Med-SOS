"""
Windows update helper for the SOS desktop application.

This module checks a remote manifest for newer versions, downloads installers,
verifies SHA-256, and triggers silent upgrades.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any, Dict, Optional

import os

import requests
from packaging import version as packaging_version

from src.utils.logger import log_turn_metric
from src.utils.audit_logger import append_audit

DEFAULT_MANIFEST_URL = "https://example.com/sos/updates/manifest.json"
DOWNLOAD_DIR = pathlib.Path("_validation/updates")
VERIFY_SSL = os.environ.get("SOS_UPDATE_VERIFY", "true").lower() not in {"0", "false", "no"}


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_manifest(manifest_url: str) -> Dict[str, Any]:
    response = requests.get(manifest_url, timeout=10, verify=VERIFY_SSL)
    response.raise_for_status()
    return response.json()


def check_for_update(manifest: Dict[str, Any], current_version: str) -> Optional[Dict[str, Any]]:
    info = manifest.get("windows")
    if not info:
        return None
    current = packaging_version.parse(current_version)
    available = packaging_version.parse(info.get("version", "0.0.0"))
    if available > current:
        return info
    return None


def download_installer(info: Dict[str, Any]) -> pathlib.Path:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"SOS_Button_Installer_{info['version']}.exe"
    destination = DOWNLOAD_DIR / file_name
    with requests.get(info["download_url"], stream=True, timeout=30, verify=VERIFY_SSL) as response:
        response.raise_for_status()
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1 << 20):
                handle.write(chunk)
    expected_hash = info.get("sha256", "")
    if expected_hash and _sha256(destination).lower() != expected_hash.lower():
        destination.unlink(missing_ok=True)
        raise ValueError("Installer hash mismatch.")
    return destination


def install_silently(installer: pathlib.Path) -> None:
    subprocess.Popen(
        [str(installer), "/VERYSILENT", "/SUPPRESSMSGBOXES"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def check_and_update(manifest_url: str, current_version: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"update_available": False, "secure": True}
    try:
        manifest = fetch_manifest(manifest_url)
        info = check_for_update(manifest, current_version)
        log_turn_metric("update_check", True, 0.0, {"available": bool(info), "manifest_url": manifest_url})
        append_audit("update_check", "desktop", {"available": bool(info), "manifest_url": manifest_url})
        if not info:
            return result
        result["update_available"] = True
        installer = download_installer(info)
        log_turn_metric("update_download", True, 0.0, {"version": info["version"], "path": str(installer)})
        append_audit("update_download", "desktop", {"version": info["version"], "path": str(installer)})
        install_silently(installer)
        log_turn_metric("update_install_triggered", True, 0.0, {"version": info["version"]})
        append_audit("update_install_triggered", "desktop", {"version": info["version"]})
        # Exit current process to allow installer to replace files.
        sys.exit(0)
    except requests.RequestException as exc:
        log_turn_metric("update_check", False, 0.0, {"error": str(exc), "manifest_url": manifest_url})
        append_audit("update_error", "desktop", {"error": str(exc)})
        result["error"] = str(exc)
    except Exception as exc:  # noqa: BLE001
        log_turn_metric("update_download", False, 0.0, {"error": str(exc)})
        append_audit("update_error", "desktop", {"error": str(exc)})
        result["error"] = str(exc)
    return result
