@echo off
setlocal EnableDelayedExpansion

:: AYUSH FHIR Terminology Portal - Windows Deployment Script
title AYUSH FHIR Portal Deployment

echo.
echo ========================================
echo   AYUSH FHIR Portal Deployment
echo ========================================
echo.

:: Configuration
set APP_NAME=ayush-fhir-portal
set DOCKER_IMAGE=%APP_NAME%:latest
set CONTAINER_NAME=%APP_NAME%-container
if "%PORT%"=="" set PORT=8000
if "%ENVIRONMENT%"=="" set ENVIRONMENT=production

:: Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is available

:: Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker Compose is available

:: Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "ssl" mkdir ssl
if not exist "data\backups" mkdir data\backups
echo [SUCCESS] Directories created

:: Generate SSL certificates (for development)
if not exist "ssl\cert.pem" (
    echo [INFO] Generating SSL certificates...
    openssl req -x509 -newkey rsa:4096 -keyout ssl\key.pem -out ssl\cert.pem -days 365 -nodes -subj "/C=IN/ST=India/L=City/O=AYUSH/OU=FHIR/CN=localhost"
    if errorlevel 1 (
        echo [WARNING] OpenSSL not found. Using HTTP only mode.
        echo # HTTP only mode > ssl\http_mode.txt
    ) else (
        echo [SUCCESS] SSL certificates generated
    )
) else (
    echo [SUCCESS] SSL certificates already exist
)

:: Parse command line arguments
if "%1"=="start" goto :start_services
if "%1"=="stop" goto :stop_services
if "%1"=="restart" goto :restart_services
if "%1"=="logs" goto :show_logs
if "%1"=="status" goto :show_status
if "%1"=="backup" goto :backup_data
if "%1"=="build" goto :build_image
if "%1"=="deploy" goto :deploy
if "%1"=="" goto :deploy

goto :show_usage

:deploy
echo [INFO] Starting full deployment...
call :stop_services
call :build_image
call :start_services
call :wait_for_health
call :show_status
echo.
echo [SUCCESS] Deployment completed successfully!
echo [INFO] Access your portal at: https://localhost
goto :end

:build_image
echo [INFO] Building Docker image...
docker build -t %DOCKER_IMAGE% .
if errorlevel 1 (
    echo [ERROR] Failed to build Docker image
    exit /b 1
)
echo [SUCCESS] Docker image built successfully
goto :end

:stop_services
echo [INFO] Stopping existing containers...
docker-compose down --remove-orphans >nul 2>&1
echo [SUCCESS] Existing containers stopped
goto :end

:start_services
echo [INFO] Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    exit /b 1
)
echo [SUCCESS] Services started successfully
goto :end

:restart_services
call :stop_services
call :start_services
call :wait_for_health
call :show_status
goto :end

:wait_for_health
echo [INFO] Waiting for services to be healthy...
set /a attempts=0
set /a max_attempts=30

:health_loop
set /a attempts+=1
curl -f http://localhost:%PORT%/health >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Service is healthy
    goto :end
)
if !attempts! geq !max_attempts! (
    echo [ERROR] Service failed to become healthy
    goto :end
)
echo [WARNING] Attempt !attempts!/!max_attempts!: Service not ready yet...
timeout /t 10 /nobreak >nul
goto :health_loop

:show_status
echo.
echo [INFO] Deployment Status:
echo ----------------------------------------
echo  Portal URL: https://localhost
echo  API Docs: https://localhost/docs
echo  Health Check: https://localhost/health
echo  Container Status:
docker-compose ps
echo ----------------------------------------
goto :end

:show_logs
echo [INFO] Showing recent logs...
docker-compose logs --tail=50 -f
goto :end

:backup_data
echo [INFO] Creating data backup...
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set timestamp=%datetime:~0,8%_%datetime:~8,6%
set backup_file=data\backups\backup_%timestamp%.zip
powershell Compress-Archive -Path "data\*" -DestinationPath "%backup_file%" -Exclude "data\backups"
echo [SUCCESS] Backup created: %backup_file%
goto :end

:show_usage
echo Usage: %0 [command]
echo.
echo Commands:
echo   deploy   - Full deployment (build, start, configure)
echo   start    - Start services
echo   stop     - Stop services
echo   restart  - Restart services
echo   logs     - Show service logs
echo   status   - Show deployment status
echo   backup   - Create data backup
echo   build    - Build Docker image
echo.
goto :end

:end
if "%1"=="" (
    echo.
    echo Press any key to exit...
    pause >nul
)
endlocal
