@echo off
echo ===== Voice Conversation Assistant =====
echo.

REM Check if Poetry is installed
where poetry >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Poetry is not installed. Installing Poetry...
    powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install Poetry. Please install it manually from https://python-poetry.org/docs/#installation
        pause
        exit /b 1
    )
)

echo Installing dependencies with Poetry...
poetry install

echo.
echo Starting Voice Conversation Assistant...
poetry run python main.py

pause
