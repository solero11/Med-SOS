"""
Chaos Telemetry Logger
----------------------
Collects metrics from chaos_harness runs:
- strict parse success
- tolerant parse fallback
- elapsed time
- LLM model metadata
Writes append-only JSONL for longitudinal analysis.
"""

import json
import time
from pathlib import Path
from datetime import datetime

LOG_PATH = Path("_validation/chaos_metrics.jsonl")


def record_metric(case_id: str,
                  strict_ok: bool,
                  tolerant_ok: bool,
                  llm_model: str,
                  prompt_template: str,
                  response_len: int,
                  elapsed: float):
    """Append a structured metric entry."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "case_id": case_id,
        "strict_ok": strict_ok,
        "tolerant_ok": tolerant_ok,
        "llm_model": llm_model,
        "prompt": prompt_template,
        "response_len": response_len,
        "elapsed_sec": round(elapsed, 3)
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[telemetry] logged: {entry}")


def summarize():
    """Quick summary of recent chaos runs."""
    if not LOG_PATH.exists():
        print("No chaos telemetry yet.")
        return
    total = strict = tolerant = 0
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            total += 1
            rec = json.loads(line)
            if rec.get("strict_ok"):
                strict += 1
            elif rec.get("tolerant_ok"):
                tolerant += 1
    if total:
        print(f"\nChaos Telemetry Summary ({total} runs)")
        print(f"  ✅ Strict parse success:  {strict:3d} ({strict/total:.1%})")
        print(f"  ⚙️  Tolerant parse success: {tolerant:3d} ({tolerant/total:.1%})")
        print(f"  ❌ Total failures:        {total - strict - tolerant:3d} ({(total - strict - tolerant)/total:.1%})")
    else:
        print("Telemetry log empty.")
