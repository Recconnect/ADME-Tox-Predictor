@echo off
title ADMETox.AI — Outreach Agents
cd /d "%~dp0"

echo ========================================
echo  ADMETox.AI — Outreach Agents
echo ========================================
echo.
echo  [1] GitHub Release    (changelog + release)
echo  [2] Write Article     (generate via LLM)
echo  [3] Investor Outreach (send emails)
echo  [4] Investor Follow-up (reminder emails)
echo  [5] Collect Metrics   (weekly report)
echo  [6] Run All Tasks     (full cycle)
echo  [7] Start Scheduler   (continuous mode)
echo  [Q] Exit
echo.
choice /c 1234567Q /n /m "Choose task: "

if errorlevel 8 goto :eof
if errorlevel 7 goto scheduler
if errorlevel 6 goto all
if errorlevel 5 goto metrics
if errorlevel 4 goto followup
if errorlevel 3 goto outreach
if errorlevel 2 goto article
if errorlevel 1 goto release

:release
echo.
echo ^>^> Running GitHub auto-release...
echo.
call ..\venv\Scripts\activate.bat
python coordinator.py release
goto :eof

:article
echo.
echo ^>^> Generating article via LLM...
echo.
call ..\venv\Scripts\activate.bat
python coordinator.py article
goto :eof

:outreach
echo.
echo ^>^> Sending investor outreach emails...
echo.
call ..\venv\Scripts\activate.bat
python coordinator.py outreach
goto :eof

:followup
echo.
echo ^>^> Sending follow-up emails...
echo.
call ..\venv\Scripts\activate.bat
python coordinator.py followup
goto :eof

:metrics
echo.
echo ^>^> Collecting metrics and generating report...
echo.
call ..\venv\Scripts\activate.bat
python coordinator.py metrics
goto :eof

:all
echo.
echo ^>^> Running all tasks...
echo.
call ..\venv\Scripts\activate.bat
python coordinator.py all
goto :eof

:scheduler
echo.
echo ^>^> Starting scheduler (press Ctrl+C to stop)...
echo.
call ..\venv\Scripts\activate.bat
python coordinator.py schedule
goto :eof
