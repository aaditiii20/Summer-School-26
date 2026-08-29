@echo off
echo ===================================================
echo AYUSH FHIR Microservice - Development Mode
echo Smart India Hackathon 2025
echo ===================================================
echo.
echo Starting development server with debug mode...
echo Access the application at: http://localhost:8004
echo.
cd /d "%~dp0\.."
python dev.py
pause
