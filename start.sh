#!/bin/bash

echo "🚀 Starting Pillar Protocol..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if requirements are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "✅ Dependencies installed"
echo ""
echo "🔧 Starting FastAPI server on http://localhost:8000"
echo "📊 API docs available at http://localhost:8000/docs"
echo ""
echo "To view the dashboard:"
echo "  1. Open another terminal"
echo "  2. Run: python3 -m http.server 8080"
echo "  3. Open http://localhost:8080 in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 backend/main.py
