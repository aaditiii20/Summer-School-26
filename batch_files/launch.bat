@echo off
echo ====================================
echo   AYUSH FHIR Terminology Server
echo   Production Launch
echo ====================================
echo.

echo Starting AYUSH FHIR Terminology Microservice...
echo Server will be available at: http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo.

cd /d "%~dp0"
venv\Scripts\uvicorn app.main_production:app --host 127.0.0.1 --port 8000

pause
