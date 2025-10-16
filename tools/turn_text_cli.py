import json
import os
import sys
import time

import httpx


def main() -> int:
    orch_url = os.getenv("ORCH_URL", "http://127.0.0.1:8000")
    text = " ".join(sys.argv[1:]) or "Patient hypotensive after induction. Next checks?"
    t0 = time.time()
    response = httpx.post(f"{orch_url.rstrip('/')}/turn_text", json={"text": text}, timeout=20)
    elapsed = time.time() - t0
    print(f"status={response.status_code} latency={elapsed:.2f}s")
    try:
        payload = response.json()
    except json.JSONDecodeError:
        print(response.text)
        return 1
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if response.status_code == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
