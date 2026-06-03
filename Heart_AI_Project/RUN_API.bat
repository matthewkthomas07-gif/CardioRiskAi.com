@echo off
cd /d "%~dp0"
echo Starting the AI server on http://127.0.0.1:8000
echo Open http://127.0.0.1:8000/docs in your browser to test.
echo Press Ctrl+C to stop.
python -m pip install -r requirements.txt -q
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
pause
