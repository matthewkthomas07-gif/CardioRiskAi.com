@echo off
cd /d "%~dp0"
echo.
echo === Heart AI Project - Easy Start ===
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Install Python from python.org first.
    pause
    exit /b 1
)

echo Step 1: Installing packages (first time may take a minute)...
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo Install failed. Ask an adult to help with pip install.
    pause
    exit /b 1
)

echo.
echo Step 2: Opening the Heart Risk Checker in your browser...
echo        (Close this window or press Ctrl+C to stop.)
echo.
python -m streamlit run ui.py

pause
