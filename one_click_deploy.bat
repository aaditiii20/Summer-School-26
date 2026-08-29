@echo off
setlocal EnableDelayedExpansion

:: One-Click Deployment for AYUSH FHIR Portal
title AYUSH FHIR Portal - One-Click Deployment

echo.
echo 
echo                                                               
echo             AYUSH FHIR Terminology Portal                  
echo                    One-Click Deployment                       
echo                                                               
echo 
echo.

:: Check deployment options
echo Choose your deployment method:
echo.
echo [1]  Docker Deployment (Recommended)
echo [2]  Python Direct Deployment
echo [3]  View Deployment Guide
echo [4]  Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto docker_deployment
if "%choice%"=="2" goto python_deployment
if "%choice%"=="3" goto view_guide
if "%choice%"=="4" goto exit
goto invalid_choice

:docker_deployment
echo.
echo  Starting Docker Deployment...
echo.
call deploy.bat deploy
goto end

:python_deployment
echo.
echo  Starting Python Deployment...
echo.
call start_production.bat
goto end

:view_guide
echo.
echo  Opening Deployment Guide...
echo.
if exist "DEPLOYMENT_GUIDE.md" (
    start notepad.exe DEPLOYMENT_GUIDE.md
) else (
    echo Deployment guide not found!
)
pause
goto menu

:invalid_choice
echo.
echo  Invalid choice. Please enter 1, 2, 3, or 4.
echo.
pause
goto menu

:menu
cls
goto start

:end
echo.
echo  Deployment process completed!
echo.
echo  Access your portal at:
echo    - Portal: https://localhost (Docker) or http://localhost:8000 (Python)
echo    - API Docs: /docs
echo    - Health Check: /health
echo.

:exit
echo Thank you for using AYUSH FHIR Portal!
pause
