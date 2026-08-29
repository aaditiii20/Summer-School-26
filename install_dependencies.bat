@echo off
REM ============================================================
REM NAMASTE-ICD11 Portal - Dependency Installer
REM Smart India Hackathon 2025
REM ============================================================

echo.
echo ========================================================
echo    Installing NAMASTE-ICD11 Portal Dependencies
echo    Smart India Hackathon 2025
echo ========================================================
echo.

echo  Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo  Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo  Installing required packages...
echo This may take a few minutes...
echo.

pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo  Dependencies installed successfully!
    echo.
    echo  Ready to start the portal:
    echo    Run: start_ultra_precision_portal.bat
    echo.
) else (
    echo.
    echo  Error installing dependencies
    echo Please check your internet connection and try again
    echo.
)

pause
