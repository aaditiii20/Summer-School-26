@echo off
setlocal EnableDelayedExpansion

:: AYUSH FHIR Terminology Portal - Production Startup
title AYUSH FHIR Portal - Production Mode

echo.
echo ========================================
echo   AYUSH FHIR Portal - Production
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

:: Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install/update dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

:: Create necessary directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "ssl" mkdir ssl

:: Set production environment variables
set ENVIRONMENT=production
set DEBUG=false
set HOST=0.0.0.0
set PORT=8000

:: Display startup information
echo.
echo ========================================
echo    Starting Production Server
echo ========================================
echo.
echo  Portal URL: http://localhost:%PORT%
echo  API Docs: http://localhost:%PORT%/docs
echo  Health Check: http://localhost:%PORT%/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

:: Start the server
python main.py

echo.
echo [INFO] Server stopped
pause
