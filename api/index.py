"""
Vercel Serverless Function - FastAPI with Mangum
Main entry point for all requests
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from mangum import Mangum

# Create Mangum handler for ASGI
handler = Mangum(app, lifespan="off")



