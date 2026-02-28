@echo off
cd /d "%~dp0"
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python.
    pause
    exit /b 1
)
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)
python main.py
