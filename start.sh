#!/bin/bash

# Railway Startup Script for Kolekt
# This script handles Railway's PORT environment variable

echo "🚂 Railway: Starting Kolekt..."

# Get port from Railway environment
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "🌍 Environment: ${ENVIRONMENT:-production}"
echo "🔗 Host: $HOST"
echo "🚪 Port: $PORT"

# Start the application
exec python -c "
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path('.').parent / 'src'))

# Set port from environment
port = int(os.getenv('PORT', 8000))
host = os.getenv('HOST', '0.0.0.0')

# Import and run
import uvicorn
from start_kolekt import app

uvicorn.run(app, host=host, port=port, log_level='info')
"
