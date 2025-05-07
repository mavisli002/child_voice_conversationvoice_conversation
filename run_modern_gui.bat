@echo off
title Modern Voice Assistant GUI
echo Starting Modern Voice Assistant GUI...
echo.

:: Run the application
python modern_gui.py

:: If there's an error, don't close the window immediately
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%
    echo.
    pause
)
