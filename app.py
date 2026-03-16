"""
Vercel Entry Point - Routes to FastAPI via Mangum
"""
from main import app
from mangum import Mangum

# Create the serverless handler
handler = Mangum(app)

