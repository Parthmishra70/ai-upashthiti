@echo off
REM AI Upashthiti API Server Startup Script for Windows

echo 🤖 Starting AI Upashthiti Face Recognition API
echo ==============================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Show Python version
echo ✅ Python version:
python --version

REM Navigate to API directory
cd api

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist "..\registered_faces" mkdir "..\registered_faces"
if not exist "..\test_images" mkdir "..\test_images"

REM Start the server
echo 🚀 Starting FastAPI server...
echo 📍 API will be available at: http://localhost:8000
echo 📖 Interactive docs at: http://localhost:8000/docs
echo 🔄 Press Ctrl+C to stop
echo ----------------------------------------

python main.py

pause