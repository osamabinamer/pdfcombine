"""
Serverless handler for FastAPI on Vercel
"""
from serverless_http import asgi
import sys
from pathlib import Path

# Add parent directory to path so we can import main.py
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from main import app

# Wrap FastAPI app for serverless
handler = asgi(app)
