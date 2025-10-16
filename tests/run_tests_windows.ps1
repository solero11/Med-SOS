# PowerShell script to run pytest with PYTHONPATH set to project root
$env:PYTHONPATH = (Get-Location)
pytest tests/test_windows_orchestrator.py --maxfail=5 --disable-warnings -v
