@echo off
REM Quick-start launcher for Jarvis on Windows.
REM Double-click this file, or run from a terminal: run.bat

setlocal

cd /d "%~dp0"

REM Create venv on first run
if not exist ".venv\Scripts\python.exe" (
    echo [Jarvis] Creating virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo [Jarvis] Failed to create venv. Make sure Python 3.10+ is installed and on PATH.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

REM Install deps if openai not present
python -c "import openai" 2>NUL
if errorlevel 1 (
    echo [Jarvis] Installing dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [Jarvis] Dependency install failed.
        echo If PyAudio failed, run:
        echo     pip install pipwin
        echo     pipwin install pyaudio
        pause
        exit /b 1
    )
)

if not exist ".env" (
    echo [Jarvis] No .env file found. Copying .env.example -^> .env
    copy /Y ".env.example" ".env" >NUL
    echo [Jarvis] Open .env and paste your OPENAI_API_KEY, then re-run this script.
    notepad .env
    pause
    exit /b 0
)

echo [Jarvis] Starting...
python -m jarvis
endlocal
