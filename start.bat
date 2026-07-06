@echo off
title ADMETox.AI
cd /d "%~dp0"

if /i "%1"=="-dev" goto dev
if /i "%1"=="--dev" goto dev
if /i "%1"=="-h" goto help
if /i "%1"=="--help" goto help

:ui
echo.
echo ========================================
echo   ADMETox.AI v2 - AI Drug Screener
echo ========================================
echo.
echo   Starting Streamlit UI...
echo   Open in browser: http://localhost:8501
echo.
echo ========================================
echo.

call .\venv\Scripts\activate.bat
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
goto end

:dev
echo.
echo ========================================
echo   ADMETox.AI v3 - AMD ROCm Dev Environment
echo ========================================
echo.
echo   Starting Docker dev container...
echo.
echo   docker compose -f deploy\docker\docker-compose.dev.yml run dev
echo.
echo ========================================
echo.

docker compose -f deploy\docker\docker-compose.dev.yml run dev
goto end

:help
echo.
echo ADMETox.AI - Launch Script
echo.
echo   start.bat           Start Streamlit UI
echo   start.bat -dev      Start Docker dev environment (ROCm)
echo   start.bat -h        Show this help
echo.

:end
