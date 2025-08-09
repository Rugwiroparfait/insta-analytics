#!/bin/bash

# Instagram Analytics Startup Script
echo "🚀 Starting Instagram Analytics Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Initialize database
echo "🗄️  Initializing database..."
python -c "from bot.db import init_db; init_db()"

# Set Flask environment variables
export FLASK_APP=web/app.py
export FLASK_ENV=development

echo "🌐 Starting Flask web server..."
echo "📊 Dashboard will be available at: http://localhost:5000"
echo "� Login with your Instagram username and password"
echo ""
echo "✨ Features:"
echo "   • Real Instagram account tracking"
echo "   • Follower change detection"
echo "   • Beautiful analytics dashboard"
echo "   • Secure session-based authentication"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

# Start the Flask application
python -m web.app
