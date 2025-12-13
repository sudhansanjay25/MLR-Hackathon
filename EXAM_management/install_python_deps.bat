@echo off
echo ================================================
echo Installing Python Dependencies for Phase 4
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Navigate to modules directory
cd /d "%~dp0modules"

REM Install dependencies
echo Installing required Python packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo Python dependencies installed successfully.
echo You can now test Phase 4 PDF generation.
echo.
pause
