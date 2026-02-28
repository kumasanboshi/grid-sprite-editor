@echo off
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo Python が見つかりません。インストールしてください。
    pause
    exit /b 1
)

python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo 依存パッケージをインストールします...
    pip install -r requirements.txt
)

python main.py
