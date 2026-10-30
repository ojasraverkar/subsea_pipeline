@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python environment...
    py -3 -m venv .venv
    if errorlevel 1 goto :error
    echo Installing project dependencies...
    .venv\Scripts\python.exe -m pip install --upgrade pip
    if errorlevel 1 goto :error
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto :error
)

echo Starting Subsea Pipeline Insulation dashboard...
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 goto :error
goto :end

:error
echo.
echo The dashboard could not be started. Check the error message above and verify Python and internet access.
pause
exit /b 1

:end
endlocal
