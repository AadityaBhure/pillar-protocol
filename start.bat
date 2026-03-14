@echo off
echo 🚀 Starting Pillar Protocol...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

echo ✅ Dependencies installed
echo.
echo 🔧 Starting FastAPI server on http://localhost:8000
echo 📊 API docs available at http://localhost:8000/docs
echo.
echo To view the dashboard:
echo   1. Open another terminal
echo   2. Run: python -m http.server 8080
echo   3. Open http://localhost:8080 in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python backend/main.py
