"""
Serverless handler for FastAPI on Vercel
"""
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import main.py
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Import the FastAPI app
    from main import app
    from serverless_http import asgi
    
    # Wrap FastAPI app for serverless
    handler = asgi(app)
    logger.info("FastAPI app initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize FastAPI app: {e}", exc_info=True)
    
    # Fallback handler that returns an error
    async def handler(event, context):
        return {
            'statusCode': 500,
            'body': f'Server initialization failed: {str(e)}'
        }

