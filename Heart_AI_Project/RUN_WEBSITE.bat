@echo off
cd /d "%~dp0"
where npm >nul 2>&1
if %errorlevel%==0 (
  echo Building latest website with Node.js...
  cd website
  call npm install
  if not errorlevel 1 call npm run build
  cd ..
) else (
  echo Using included website build ^(install Node.js to rebuild^).
)

echo.
echo Starting CardioRisk AI (website + API) at http://127.0.0.1:8000
echo Press Ctrl+C to stop.
python -m pip install -r requirements.txt -q
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
goto end

:fail
echo Build failed. Install Node.js from https://nodejs.org then try again.
pause
exit /b 1

:end
pause
