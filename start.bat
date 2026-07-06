@echo off
chcp 65001 >nul
title ADMETox.AI
cd /d "%~dp0"

echo.
echo ========================================
echo   ADMETox.AI — AI Drug Screener
echo ========================================
echo.
echo   Запуск Streamlit UI...
echo   Открой в браузере: http://localhost:8501
echo.
echo ========================================
echo.

call .\venv\Scripts\activate.bat
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
