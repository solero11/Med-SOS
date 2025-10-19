
# -*- coding: utf-8 -*-
"""
FastAPI application providing a local dashboard for SBAR chaos harness runs.
"""

from __future__ import annotations

import json
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

DASHBOARD_PORT = 8010
BASE_DIR = Path("_validation/sbar_chaos_logs")
METRICS_PATH = Path("_validation/orchestrator_metrics.jsonl")
TEMPLATES = Jinja2Templates(directory="templates")


@dataclass
class RunRecord:
    scene: str
    run: str
    run_dir: Path
    summary_path: Path
    progress_path: Path
    tokens: int = 0
    latency: float = 0.0
    snapshots: int = 0
    with_llm: bool = False

    @property
    def started(self) -> Optional[str]:
        try:
            summary_text = self.summary_path.read_text(encoding="utf-8")
        except OSError:
            return None
        for line in summary_text.splitlines():
            if line.strip().startswith("_Run started:"):
                return line.strip().strip("_Run started:").strip("_ ")
        return None


def _iter_scene_dirs(base_dir: Path) -> Iterable[Path]:
    if not base_dir.exists():
        return []
    return sorted([p for p in base_dir.iterdir() if p.is_dir()], key=lambda p: p.name)


def _iter_run_dirs(scene_dir: Path) -> Iterable[Path]:
    run_dirs = [p for p in scene_dir.iterdir() if p.is_dir()]
    return sorted(run_dirs, key=lambda p: p.name, reverse=True)


def _load_metrics() -> Dict[str, dict]:
    metrics: Dict[str, dict] = {}
    if not METRICS_PATH.exists():
        return metrics
    try:
        lines = METRICS_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return metrics
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("event") != "sbar_chaos":
            continue
        run_dir = record.get("run_dir")
        if not run_dir:
            continue
        metrics[run_dir.replace("\\", "/")] = record
    return metrics


def _collect_runs() -> List[RunRecord]:
    metrics = _load_metrics()
    runs: List[RunRecord] = []

    for scene_dir in _iter_scene_dirs(BASE_DIR):
        scene = scene_dir.name
        for run_dir in _iter_run_dirs(scene_dir):
            run_name = run_dir.name
            summary_path = run_dir / "summary.md"
            progress_path = run_dir / "progress.md"
            if not summary_path.exists() or not progress_path.exists():
                continue
            record = RunRecord(
                scene=scene,
                run=run_name,
                run_dir=run_dir,
                summary_path=summary_path,
                progress_path=progress_path,
            )
            metrics_key = str(run_dir).replace("\\", "/")
            metric_entry = metrics.get(metrics_key)
            if metric_entry:
                record.tokens = int(metric_entry.get("tokens", 0) or 0)
                record.latency = float(metric_entry.get("latency_sec", 0.0) or 0.0)
                record.snapshots = int(metric_entry.get("snapshots_logged", 0) or 0)
                record.with_llm = bool(metric_entry.get("with_llm"))
            runs.append(record)

    runs.sort(key=lambda r: (r.scene, r.run), reverse=True)
    return runs


app = FastAPI(title="SBAR Chaos Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_runs() -> List[RunRecord]:
    return _collect_runs()


@app.get("/api/runs")
def api_runs(records: List[RunRecord] = Depends(get_runs)) -> JSONResponse:
    payload = []
    for record in records:
        payload.append(
            {
                "scene": record.scene,
                "run": record.run,
                "tokens": record.tokens,
                "latency": record.latency,
                "snapshots": record.snapshots,
                "with_llm": record.with_llm,
                "summary": f"/api/run/{record.scene}/{record.run}/file/summary.md",
                "progress": f"/api/run/{record.scene}/{record.run}/file/progress.md",
            }
        )
    return JSONResponse(content={"runs": payload})


@app.get("/api/run/{scene}/{timestamp}/file/{filename}")
def api_run_file(scene: str, timestamp: str, filename: str) -> FileResponse:
    target = BASE_DIR / scene / timestamp / filename
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target, media_type="text/markdown", filename=f"{scene}-{timestamp}-{filename}")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    runs = _collect_runs()
    scenes: Dict[str, List[RunRecord]] = {}
    for record in runs:
        scenes.setdefault(record.scene, []).append(record)
    return TEMPLATES.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "scenes": scenes,
        },
    )


@app.get("/")
async def root(request: Request) -> HTMLResponse:
    return await dashboard(request)


def launch_browser(port: int = DASHBOARD_PORT) -> None:
    url = f"http://127.0.0.1:{port}/dashboard"
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main() -> None:
    import uvicorn

    launch_browser(DASHBOARD_PORT)
    uvicorn.run("src.sbar_dashboard.app:app", host="127.0.0.1", port=DASHBOARD_PORT, reload=False)


if __name__ == "__main__":
    main()
