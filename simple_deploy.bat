@echo off
echo Starting Vercel Deployment...
echo.

echo Step 1: Check if you're logged in
vercel whoami
echo.

echo Step 2: Deploy with minimal configuration
vercel --prod --confirm

echo.
echo If the above didn't work, try:
echo vercel
echo.
pause
