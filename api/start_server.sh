#!/bin/bash

# AI Upashthiti API Server Startup Script
echo "🤖 Starting AI Upashthiti Face Recognition API"
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $python_version"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p ../registered_faces
mkdir -p ../test_images

# Start the server
echo "🚀 Starting FastAPI server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 Interactive docs at: http://localhost:8000/docs"
echo "🔄 Press Ctrl+C to stop"
echo "----------------------------------------"

python3 main.py