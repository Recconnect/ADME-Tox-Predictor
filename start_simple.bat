@echo off
chcp 65001 >nul
title ADMETox.AI
cd /d "%~dp0"

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

.\venv\Scripts\streamlit.exe run app.py --server.port=8501 --server.address=0.0.0.0

pause
