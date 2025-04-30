# Create a new file: backend/run.py

#!/usr/bin/env python
import os
import sys
import logging
import uvicorn
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_app(host='127.0.0.1', port=8668, reload=False, workers=1, log_level='info'):
    try:
        # Initialize database first
        from db.database import init_db
        init_db()
        logger.info("Database initialized")
        
        # Import and run application
        import uvicorn
        logger.info(f"Starting ModHub Central on {host}:{port}")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            workers=workers
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ModHub Central Platform")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8668, help='Port to bind the server to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    parser.add_argument('--log-level', type=str, default='info', choices=['debug', 'info', 'warning', 'error', 'critical'],
                        help='Logging level')
    parser.add_argument('--init-db', action='store_true', help='Initialize database only')
    
    args = parser.parse_args()
    
    if args.init_db:
        from db.database import init_db
        init_db()
        logger.info("Database initialized successfully")
        sys.exit(0)
        
    run_app(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level
    )