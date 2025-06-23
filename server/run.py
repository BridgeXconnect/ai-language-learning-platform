#!/usr/bin/env python3
"""
Main entry point for the Dynamic English Course Creator FastAPI application.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    print(f"🚀 Starting FastAPI application on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"❤️  Health Check: http://{host}:{port}/health")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )