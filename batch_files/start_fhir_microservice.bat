@echo off
echo.
echo =============================================
echo  AYUSH FHIR R4 Terminology Microservice
echo =============================================
echo.
echo  FHIR R4 Compliant
echo  India's 2016 EHR Standards
echo  NAMASTE ↔ ICD-11 TM2 Integration
echo  ABHA OAuth 2.0 Ready
echo  Audit Trails & Compliance
echo.
echo Starting FHIR microservice on port 8003...
echo.

python fhir_r4_microservice.py

echo.
echo Server stopped. Press any key to exit...
pause > nul
