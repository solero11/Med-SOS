"""
Utility to update the release manifest with fresh SHA-256 hashes.

Usage:
    python tools/publish_update.py path/to/installer.exe path/to/app.apk updates/manifest.json

Any positional argument can be omitted to skip updating that entry.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from typing import Optional


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def update_manifest(
    manifest_path: pathlib.Path,
    windows_installer: Optional[pathlib.Path],
    android_apk: Optional[pathlib.Path],
) -> None:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if windows_installer:
        data.setdefault("windows", {})["sha256"] = sha256(windows_installer)
    if android_apk:
        data.setdefault("android", {})["sha256"] = sha256(android_apk)
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str]) -> None:
    windows_path = pathlib.Path(argv[1]).resolve() if len(argv) > 1 else None
    android_path = pathlib.Path(argv[2]).resolve() if len(argv) > 2 else None
    manifest = pathlib.Path(argv[3]).resolve() if len(argv) > 3 else pathlib.Path("updates/manifest.json")
    update_manifest(manifest, windows_path if windows_path and windows_path.exists() else None,
                    android_path if android_path and android_path.exists() else None)
    print(f"Updated manifest at {manifest}")


if __name__ == "__main__":
    main(sys.argv)
