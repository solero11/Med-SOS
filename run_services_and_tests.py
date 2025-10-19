import subprocess
import sys
import time
from pathlib import Path
import httpx

TOKEN = 'test-admin-token'
security_dir = Path('_validation/security')
security_dir.mkdir(parents=True, exist_ok=True)
(security_dir / 'sos_token.txt').write_text(TOKEN, encoding='utf-8')

processes = []
commands = [
    [sys.executable, '-m', 'uvicorn', 'src.tts.app:app', '--host', '127.0.0.1', '--port', '8880'],
    [sys.executable, '-m', 'uvicorn', 'src.asr.app:app', '--host', '127.0.0.1', '--port', '9001'],
    [sys.executable, '-m', 'uvicorn', 'src.orchestrator.app:create_app', '--host', '127.0.0.1', '--port', '8000']
]

try:
    for cmd in commands:
        processes.append(subprocess.Popen(cmd))

    urls = [
        'http://127.0.0.1:8880/health',
        'http://127.0.0.1:9001/health',
        'http://127.0.0.1:8000/health'
    ]
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            if all(httpx.get(url, timeout=1, verify=False).status_code == 200 for url in urls):
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        raise SystemExit('Services did not become healthy in time')

    result = subprocess.run([sys.executable, '-m', 'pytest',
                             'tests/test_turn_text_smoke.py',
                             'tests/test_turn_audio_smoke.py',
                             'tests/test_health_endpoints.py',
                             'tests/test_mobile_bridge.py',
                             'tests/test_stress_recovery.py'], check=False)
    exit_code = result.returncode
finally:
    for proc in processes:
        proc.terminate()
    for proc in processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

sys.exit(exit_code)
