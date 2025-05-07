@echo off
echo 正在启动语音对话助手GUI版本...
echo Starting Voice Conversation Assistant GUI...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装或不在PATH中，请安装Python 3.8或以上版本。
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check for required packages and install if missing
echo 检查并安装必要的依赖...
echo Checking and installing required dependencies...
pip install -r requirements.txt
pip install customtkinter pillow sv-ttk python-dotenv

REM Create data directory if it doesn't exist
if not exist data mkdir data
if not exist data\resources mkdir data\resources

REM Run the GUI application
echo 启动GUI界面...
echo Starting GUI interface...
python chatgpt_style_gui.py

pause
