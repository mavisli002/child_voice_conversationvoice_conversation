@echo off
echo ===== Voice Conversation Assistant =====
echo.
echo Installing required packages...
python -m pip install -r requirements.txt

echo.
echo Starting Voice Conversation Assistant...
python main.py

pause
