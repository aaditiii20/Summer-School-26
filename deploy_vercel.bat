@echo off
setlocal EnableDelayedExpansion

:: AYUSH FHIR Portal - Vercel Deployment Script
title AYUSH FHIR Portal - Vercel Deployment

echo.
echo 
echo                                                               
echo             AYUSH FHIR Portal - Vercel Deployment          
echo                                                               
echo 
echo.

:: Check if Vercel CLI is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Vercel CLI not found. Installing Vercel CLI...
    npm install -g vercel
    if errorlevel 1 (
        echo [ERROR] Failed to install Vercel CLI. Please install Node.js first.
        echo Visit: https://nodejs.org/
        pause
        exit /b 1
    )
    echo [SUCCESS] Vercel CLI installed
) else (
    echo [SUCCESS] Vercel CLI found
)

:: Check if user is logged in to Vercel
echo [INFO] Checking Vercel authentication...
vercel whoami >nul 2>&1
if errorlevel 1 (
    echo [INFO] Not logged in to Vercel. Please log in...
    vercel login
    if errorlevel 1 (
        echo [ERROR] Failed to log in to Vercel
        pause
        exit /b 1
    )
)

:: Display deployment options
echo.
echo Choose deployment option:
echo.
echo [1]  Deploy to Production
echo [2]  Deploy to Preview (Development)
echo [3]  View Deployment Status
echo [4]  Configure Environment Variables
echo [5]  Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto deploy_production
if "%choice%"=="2" goto deploy_preview
if "%choice%"=="3" goto deployment_status
if "%choice%"=="4" goto configure_env
if "%choice%"=="5" goto exit
goto invalid_choice

:deploy_production
echo.
echo  Deploying to Vercel Production...
echo.
echo [INFO] This will deploy your portal to production
echo [INFO] The deployment URL will be provided after successful deployment
echo.
vercel --prod
if errorlevel 1 (
    echo [ERROR] Production deployment failed
    pause
    exit /b 1
)
echo.
echo [SUCCESS]  Production deployment completed!
goto show_urls

:deploy_preview
echo.
echo  Deploying to Vercel Preview...
echo.
vercel
if errorlevel 1 (
    echo [ERROR] Preview deployment failed
    pause
    exit /b 1
)
echo.
echo [SUCCESS]  Preview deployment completed!
goto show_urls

:deployment_status
echo.
echo  Checking deployment status...
echo.
vercel ls
echo.
echo [INFO] Use 'vercel inspect <deployment-url>' for detailed information
pause
goto menu

:configure_env
echo.
echo  Configuring Environment Variables...
echo.
echo Setting up production environment variables:
vercel env add ENVIRONMENT production
vercel env add DEBUG false
vercel env add NODE_ENV production
echo.
echo [SUCCESS] Environment variables configured
pause
goto menu

:show_urls
echo.
echo 
echo                      Deployment URLs                        
echo 
echo.
echo  Portal: https://your-project.vercel.app
echo  API Health: https://your-project.vercel.app/health
echo  Search API: https://your-project.vercel.app/api/search
echo  Validation API: https://your-project.vercel.app/api/validation
echo  Insurance API: https://your-project.vercel.app/api/insurance
echo.
echo [INFO] Replace 'your-project' with your actual Vercel domain
echo [INFO] Check your Vercel dashboard for the exact URLs
echo.
echo 
echo                        Features                             
echo 
echo.
echo  Static frontend hosting
echo  Serverless API functions
echo  Automatic HTTPS
echo  Global CDN
echo  Custom domain support
echo  Environment variables
echo  Real-time logs
echo  Analytics dashboard
echo.
goto end

:invalid_choice
echo.
echo  Invalid choice. Please enter 1, 2, 3, 4, or 5.
echo.
pause
goto menu

:menu
cls
goto start

:start
echo.
echo 
echo             AYUSH FHIR Portal - Vercel Deployment          

goto deploy_production

:end
echo.
echo 
echo                     Deployment Complete!                   
echo 
echo.
echo Your AYUSH FHIR Portal is now live on Vercel!
echo.
echo  Next Steps:
echo 1. Visit your Vercel dashboard to get the exact URL
echo 2. Configure custom domain (optional)
echo 3. Set up monitoring and analytics
echo 4. Update API endpoints if needed
echo.

:exit
echo Thank you for using AYUSH FHIR Portal!
pause
