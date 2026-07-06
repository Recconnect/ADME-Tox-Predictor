@echo off
title ADMETox.AI — Launch
cd /d "%~dp0"

echo ========================================
echo  ADMETox.AI — AI Drug Screener
echo ========================================
echo.
echo  [1] Streamlit UI     ^(главный интерфейс^)
echo  [2] FastAPI API      ^(REST + Swagger^)
echo  [3] Docker Compose   ^(все сервисы^)
echo  [4] Тесты            ^(pytest^)
echo  [Q] Выход
echo.
choice /c 1234Q /n /m "Выбери режим: "

if errorlevel 5 goto :eof
if errorlevel 4 goto tests
if errorlevel 3 goto docker
if errorlevel 2 goto api
if errorlevel 1 goto ui

:ui
echo.
echo ^>^> Запуск Streamlit UI...
echo ^>^> Открой в браузере: http://localhost:8501
echo.
call .\venv\Scripts\activate.bat
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
goto :eof

:api
echo.
echo ^>^> Запуск FastAPI API...
echo ^>^> Документация: http://localhost:8000/docs
echo.
call .\venv\Scripts\activate.bat
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
goto :eof

:docker
echo.
echo ^>^> Сборка и запуск Docker Compose...
echo.
docker compose up -d --build
echo.
echo ^>^> Landing:  http://localhost/
echo ^>^> UI:       http://localhost/ui/
echo ^>^> API docs: http://localhost/docs
goto :eof

:tests
echo.
echo ^>^> Запуск тестов...
echo.
call .\venv\Scripts\activate.bat
python -m pytest tests/ -v
echo.
pause
goto :eof
