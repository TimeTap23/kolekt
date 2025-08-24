#!/usr/bin/env python3
import os
import uvicorn

# Get port from Railway
port = int(os.getenv('PORT', 8000))

# Start the app
uvicorn.run('start_kolekt:app', host='0.0.0.0', port=port)
