@echo off
setlocal EnableDelayedExpansion

:: Simple Vercel Deployment Script
title AYUSH FHIR Portal - Quick Vercel Deploy

echo.
echo ========================================
echo   AYUSH FHIR Portal - Quick Deploy
echo ========================================
echo.

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)
echo [] Node.js found

:: Check/Install Vercel CLI
vercel --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Vercel CLI...
    npm install -g vercel
    if errorlevel 1 (
        echo [ERROR] Failed to install Vercel CLI
        pause
        exit /b 1
    )
)
echo [] Vercel CLI ready

echo.
echo ========================================
echo   Manual Deployment Steps
echo ========================================
echo.
echo 1. First, you need to login to Vercel
echo 2. Then we'll deploy your portal
echo.
echo Press any key to start login process...
pause >nul

echo.
echo [INFO] Opening Vercel login...
echo [INFO] This will open your browser for authentication
echo.

:: Login to Vercel
vercel login

echo.
echo [INFO] Login completed. Now deploying to Vercel...
echo.

:: Deploy to Vercel
echo [INFO] Starting deployment...
vercel --prod --yes

if errorlevel 1 (
    echo.
    echo [ERROR] Deployment failed. Let's try without --yes flag...
    echo.
    vercel --prod
)

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Your portal should now be live on Vercel.
echo Check the URL provided above.
echo.
echo To view your deployments: vercel ls
echo To check logs: vercel logs
echo.
pause
