@echo off
echo ====================================================
echo  AYUSH Master Portal - Complete Integration
echo ====================================================
echo.
echo Starting unified platform with all components...
echo.
echo  Features included:
echo    FHIR R4 Microservice Integration
echo    Excel Data Portal Integration  
echo    Beginner-Friendly Interface
echo    Unified Search Across All Systems
echo    WHO ICD-11 TM2 Mapping
echo    SIH Problem Statement Compliance
echo.
echo  Master Portal will be available at: http://localhost:8005
echo  Individual services:
echo   - FHIR R4 Service: http://localhost:8003
echo   - Excel Portal: http://localhost:8002
echo.
echo Press Ctrl+C to stop the server
echo ====================================================
echo.

python src/api/master_portal.py
